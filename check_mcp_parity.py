# -*- coding: utf-8 -*-
"""比对 MCP server **三份平行实现**的工具定义。

  ① `github-repo/datasinking/mcp_server.py`   pip 包（本地 stdio）
  ② `worker/src/index.ts` 的 `MCP_TOOLS`      远程端点 https://api.datasink.ing/mcp
  ③ `github-repo/npm/tools.js`                npm 包 datasinking-mcp（本地 stdio）

**为什么需要**：这个项目已经因为「改了一份忘了另一份」踩过四次 ——
  · 09-03 工具描述英文化只改了 ①，**漏了 ②**，两边漂移 19 天
  · 09-22 `server.json` 声明 PyPI 0.2.8，而那个版本根本没发到 PyPI 上
  · 09-22 `github-repo/` 落后 GitHub 10 个文件、`client.py` 上写着已删除的错误码
  · 09-22 加 npm 包时发现 ② 的 4 个参数**没有 description**，而 ① 有

最后那条就是本脚本存在的直接原因：**工具描述只有真的到了客户端才算数**，
而它到没到，靠人眼看源码是看不出来的。

用法:
    python check_mcp_parity.py          # 比对，不一致退出码 1

> 本文件在 `github-repo/` 里（跟着 `sync_versions.py` 一起发到公开仓库），
> 但 ② 在**项目根**的 `worker/` —— 那是私有区，公开仓库里没有。
> 公开仓库里只有 ①③ 时脚本会自动降级成「只查 npm 那一份有没有漏参数描述」，不报错。
"""
import json
import pathlib
import re
import subprocess
import sys
import tempfile

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

def _norm(s: str) -> str:
    """比对前把空白归一 —— 排版换行不算差异，改词才算。"""
    return re.sub(r"\s+", " ", s or "").strip()


HERE = pathlib.Path(__file__).resolve().parent
WORKER_TS = HERE.parent / "worker" / "src" / "index.ts"
NPM_TOOLS = HERE / "npm" / "tools.js"
PY_SERVER = HERE / "datasinking" / "mcp_server.py"


def _node_json(js_source: str, tmp: pathlib.Path):
    """把一段 JS 求值成 JSON —— 用真的 node 解析，别拿正则去啃对象字面量。"""
    tmp.write_text(
        f"const v = {js_source};\nconsole.log(JSON.stringify(v));\n", encoding="utf-8"
    )
    r = subprocess.run(
        ["node", str(tmp)], capture_output=True, text=True, encoding="utf-8", timeout=60
    )
    if r.returncode != 0:
        sys.exit(f"❌ node 解析失败:\n{r.stderr[:800]}")
    return json.loads(r.stdout)


def _extract_array(src: str, anchor: str) -> str:
    """从 `anchor` 那行的 `=` 之后的第一个 `[` 起做括号配对，取出整个数组字面量。

    注意不能直接从 anchor 往后找第一个 `[` —— TS 的类型标注 `const MCP_TOOLS: any[] = [`
    里就有一个 `[]`，会取到空数组。
    """
    i = src.index("[", src.index("=", src.index(anchor)))
    depth, j, quote, esc = 0, i, None, False
    while j < len(src):
        c = src[j]
        if quote:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == quote:
                quote = None
        elif c in "\"'`":
            quote = c
        elif c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0:
                return src[i : j + 1]
        j += 1
    sys.exit("❌ 找不到数组结尾 —— 文件结构变了？")


def worker_tools(tmp: pathlib.Path):
    src = WORKER_TS.read_text(encoding="utf-8")
    arr = _extract_array(src, "const MCP_TOOLS")
    # 数组里会引用文件级的字符串常量（如 DOCUMENT_ID_DESC），先把它们取出来一起求值，
    # 否则 node 报 ReferenceError。只取简单字面量，复杂表达式就该人工看了。
    consts = "\n".join(
        f'const {name} = {json.dumps(value)};'
        for name, value in re.findall(r'^const ([A-Z][A-Z0-9_]*) = "([^"]*)";', src, re.M)
        if re.search(rf"\b{name}\b", arr)
    )
    return _node_json(f"(() => {{\n{consts}\nreturn {arr};\n}})()", tmp)


def npm_tools(tmp: pathlib.Path):
    mjs = tmp.with_suffix(".mjs")
    mjs.write_text(
        f"import {{ TOOLS }} from {json.dumps(NPM_TOOLS.as_uri())};\n"
        "console.log(JSON.stringify(TOOLS));\n",
        encoding="utf-8",
    )
    r = subprocess.run(
        ["node", str(mjs)], capture_output=True, text=True, encoding="utf-8", timeout=60
    )
    if r.returncode != 0:
        sys.exit(f"❌ node 导入 {NPM_TOOLS.name} 失败:\n{r.stderr[:800]}")
    return json.loads(r.stdout)


def _is_tool_decorator(d):
    """`@mcp.tool` 和 `@mcp.tool()` 都要认 —— 后者是 Call，不是 Attribute。

    踩过：只判 `isinstance(d, ast.Attribute)` 时，`@mcp.tool()` 一个都匹配不上，
    于是 ① 被解析成「0 个工具」、比对**空跑一遍还报成功** —— 比不检查更危险。
    """
    import ast

    if isinstance(d, ast.Call):
        d = d.func
    return isinstance(d, ast.Attribute) and d.attr == "tool"


def python_descriptions(src: str):
    """从 `mcp_server.py` 里取出 {工具名: (工具描述, {参数名: 参数描述})}。

    参数描述只能是 `Annotated[T, Field(description="...")]`（docstring 的 Args 段在 mcp v2
    根本不到客户端，见 mcp_server.py 顶部注释），所以这里只认 Field。
    """
    import ast

    out = {}
    for node in ast.parse(src).body:
        if not isinstance(node, ast.FunctionDef):
            continue
        if not any(_is_tool_decorator(d) for d in node.decorator_list):
            continue
        params = {}
        for a in node.args.args:
            desc = ""
            for sub in ast.walk(a.annotation) if a.annotation else []:
                if isinstance(sub, ast.Call):
                    for kw in sub.keywords:
                        if kw.arg == "description" and isinstance(kw.value, ast.Constant):
                            desc = kw.value.value
            params[a.arg] = desc
        out[node.name] = (ast.get_docstring(node) or "", params)
    return out


def python_tools_for_compare(src: str):
    """把 ① 的取值整理成和 ②③ 同构的形状，好让同一段比对逻辑复用。"""
    return [
        {
            "name": name,
            "description": desc,
            "inputSchema": {
                "properties": {p: {"description": d} for p, d in params.items()}
            },
        }
        for name, (desc, params) in python_descriptions(src).items()
    ]


def main():
    fails, warns = [], []

    with tempfile.TemporaryDirectory() as d:
        tmp = pathlib.Path(d) / "t.js"
        npm = npm_tools(tmp)
        has_worker = WORKER_TS.exists()
        worker = worker_tools(tmp) if has_worker else npm

    py = {t["name"]: t for t in python_tools_for_compare(PY_SERVER.read_text(encoding="utf-8"))}
    py_names = list(py)

    w = {t["name"]: t for t in worker}
    n = {t["name"]: t for t in npm}

    print(f"① mcp_server.py    {len(py_names)} 个工具")
    if has_worker:
        print(f"② worker MCP_TOOLS  {len(w)} 个工具")
    else:
        print("② worker MCP_TOOLS  跳过（公开仓库里没有私有区的 worker/，只用 ③ 自检）")
    print(f"③ npm/tools.js      {len(n)} 个工具\n")

    # ---- 工具名 ----
    # 没有 ② 时 w 就是 n，① vs ② 这一条自动变成「① vs ③」—— 该有的检查一个没少。
    if set(py_names) != set(w):
        fails.append(f"① 与 ② 工具名不同：仅在 ① {sorted(set(py_names) - set(w))}，仅在 ② {sorted(set(w) - set(py_names))}")
    if set(w) != set(n):
        fails.append(f"② 与 ③ 工具名不同：仅在 ② {sorted(set(w) - set(n))}，仅在 ③ {sorted(set(n) - set(w))}")
    if not fails:
        print(f"  ✅ 工具名一致（{len(n)} 个）")

    # ---- 逐工具比对结构 ----
    for name in sorted(set(w) & set(n)):
        a, b = w[name], n[name]
        sa, sb = a.get("inputSchema") or {}, b.get("inputSchema") or {}
        pa, pb = sa.get("properties") or {}, sb.get("properties") or {}

        if set(pa) != set(pb):
            fails.append(f"{name}: 参数名不同 ②{sorted(pa)} vs ③{sorted(pb)}")
        if sorted(sa.get("required") or []) != sorted(sb.get("required") or []):
            fails.append(f"{name}: required 不同 ②{sa.get('required')} vs ③{sb.get('required')}")

        for p in sorted(set(pa) & set(pb)):
            ta, tb = pa[p].get("type"), pb[p].get("type")
            if ta != tb:
                fails.append(f"{name}.{p}: 类型不同 ②{ta} vs ③{tb}")
            # 这条就是 2026-09-22 抓出的真问题：参数描述没到客户端，模型只能瞎猜。
            for label, spec in (("②", pa[p]), ("③", pb[p])):
                if not (spec.get("description") or "").strip():
                    fails.append(f"{name}.{p}: {label} 没有 description")

        if not (a.get("description") or "").strip():
            fails.append(f"{name}: ② 没有工具描述")
        if not (b.get("description") or "").strip():
            fails.append(f"{name}: ③ 没有工具描述")

    # ---- 描述文字必须**逐字一致** ----
    # 三条路（pip / 远程 / npx）交给模型的是同一批工具。措辞不一致 = 装哪条路决定了模型
    # 看到的能力说明，没有正当理由不一致 —— 所以这是硬失败，不是警告。
    # 2026-09-22 加这条时实测：①③ 已经完全一致（0 处差异）。
    def _d(tool, param=None):
        if param is None:
            return _norm(tool.get("description"))
        return _norm(((tool.get("inputSchema") or {}).get("properties") or {}).get(param, {}).get("description"))

    def _all_same(label, vals, where):
        uniq = set(v for v in vals.values() if v)
        if len(uniq) > 1:
            fails.append(
                f"{where} 的{label}三份措辞不同：" +
                " / ".join(f"{k}={v[:60]!r}" for k, v in vals.items())
            )

    for name in sorted(set(py) & set(w) & set(n)):
        trio = [("①", py[name]), ("②", w[name]), ("③", n[name])]
        _all_same("工具描述", {k: _d(t) for k, t in trio}, name)
        params = set.intersection(*[
            set((t.get("inputSchema") or {}).get("properties") or {}) for _, t in trio
        ])
        for p in sorted(params):
            _all_same(f"参数 {p} 的描述", {k: _d(t, p) for k, t in trio}, name)

    for msg in fails:
        print(f"  ❌ {msg}")
    if warns:
        print()
        for msg in warns:
            print(f"  ⚠️  {msg}（不一定是错，但两边该是同一句话）")

    if fails:
        print(f"\n{len(fails)} 项不一致。三份实现必须同步改 —— 见本文件顶部注释。")
        sys.exit(1)
    tail = f"（有 {len(warns)} 处措辞差异）" if warns else ""
    print(f"\n{'三份' if has_worker else '两份（缺 worker/）'}实现一致 ✅{tail}")


if __name__ == "__main__":
    main()
