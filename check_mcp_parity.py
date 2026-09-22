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


def python_tool_names(src: str):
    """只要工具名 —— 参数描述在 Python 里是 Annotated/Field，机械比对成本大于收益。"""
    return re.findall(r"@mcp\.tool\(\)\s*\ndef\s+(\w+)\(", src)


def main():
    fails, warns = [], []

    with tempfile.TemporaryDirectory() as d:
        tmp = pathlib.Path(d) / "t.js"
        npm = npm_tools(tmp)
        has_worker = WORKER_TS.exists()
        worker = worker_tools(tmp) if has_worker else npm

    py_names = python_tool_names(PY_SERVER.read_text(encoding="utf-8"))

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

    # ---- 描述文字不一致只警告（措辞可以不同，但得知道它不同了）----
    for name in sorted(set(w) & set(n)):
        for label, x, y in [
            ("工具描述", w[name].get("description"), n[name].get("description"))
        ]:
            if x and y and x.strip() != y.strip():
                warns.append(f"{name} 的{label} ②③ 措辞不同")
        pa = (w[name].get("inputSchema") or {}).get("properties") or {}
        pb = (n[name].get("inputSchema") or {}).get("properties") or {}
        for p in sorted(set(pa) & set(pb)):
            x, y = pa[p].get("description"), pb[p].get("description")
            if x and y and x.strip() != y.strip():
                warns.append(f"{name}.{p} 的参数描述 ②③ 措辞不同")

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
