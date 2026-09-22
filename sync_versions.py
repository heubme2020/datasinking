# -*- coding: utf-8 -*-
"""把 `datasinking/_version.py` 的版本号同步到各 MCP manifest。

**为什么需要**：版本号有 5 个落点 ——
  ① `datasinking/_version.py`   唯一来源（pyproject 用 `dynamic` 从它读，
                                client.py 的 UA 和 mcp_server.py 也读它）
  ② `lhm.plugin.json`           给 LobeHub 之类的 MCP 目录读
  ③ `server.json`               给官方 MCP registry 读
  ④ `../worker/src/index.ts`    远程 MCP 端点 initialize 时回的 serverInfo.version
  ⑤ `npm/package.json`          给 npm 上的 datasinking-mcp 发版（`npx` 那条路）

②③④⑤ 都是**字面量**，没法像 pyproject 那样动态引用，只能跟着改：
- ②③ 是外部注册表读的 JSON，改不到就发不出去；
- ④ 跑在 Workers 的 V8 里，**根本读不到 Python 包的 `__version__`**，没有自动同步的可能；
- ⑤ 是另一个语言的包，npm 也不认 Python 的 pyproject。

漂移史：
- 2026-09-14：包已经到 0.2.4~0.2.7，②③ 还停在 0.2.3。
- 2026-09-22：④ 停在 `0.2.0` 整整 19 天 —— 包早就 0.2.8 了，而**配远程 URL 的
  客户端看到的正是 ④ 这一份**。就是这次加的检查。

用法:
    python sync_versions.py          # 同步并报告
    python sync_versions.py --check  # 只检查；不一致则退出码 1（可挂进发版脚本/CI）
"""
import json
import pathlib
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = pathlib.Path(__file__).resolve().parent
VERSION_FILE = HERE / "datasinking" / "_version.py"
JSON_FILES = ["lhm.plugin.json", "server.json", "npm/package.json"]
# Worker 远程 MCP 端点（见 index.ts 顶部关于「两个平行实现」的注释）
WORKER_TS = HERE.parent / "worker" / "src" / "index.ts"
WORKER_RE = re.compile(r'^const MCP_SERVER_VERSION = "([^"]+)";', re.M)


def current_version():
    m = re.search(r'^__version__\s*=\s*"([^"]+)"', VERSION_FILE.read_text(encoding="utf-8"), re.M)
    if not m:
        sys.exit(f"从 {VERSION_FILE} 里读不到 __version__")
    return m.group(1)


def main():
    check_only = "--check" in sys.argv
    ver = current_version()
    print(f"单一来源 {VERSION_FILE.name} → {ver}\n")

    stale = []
    for name in JSON_FILES:
        path = HERE / name
        if not path.exists():
            print(f"  {name}: 文件不存在，跳过")
            continue
        raw = path.read_text(encoding="utf-8")
        found = re.findall(r'"version"\s*:\s*"([^"]+)"', raw)
        wrong = [v for v in found if v != ver]
        if not wrong:
            print(f"  {name}: 已是 {ver}（{len(found)} 处）")
            continue
        stale.append((name, found, wrong))
        if check_only:
            print(f"  ❌ {name}: 仍是 {sorted(set(wrong))}（{len(found)} 处）")
            continue
        # 只替换 version 字段的值，别误伤别的字符串
        new = re.sub(r'("version"\s*:\s*)"[^"]+"', lambda m: m.group(1) + f'"{ver}"', raw)
        json.loads(new)  # 写之前先校验，免得把 JSON 弄坏
        path.write_text(new, encoding="utf-8")
        print(f"  ✅ {name}: {sorted(set(wrong))} → {ver}（{len(found)} 处）")

    # ---- ④ Worker 远程 MCP 端点 ----
    if not WORKER_TS.exists():
        print(f"  {WORKER_TS.name}: 文件不存在，跳过（只在本地同时有两份代码时可查）")
    else:
        raw = WORKER_TS.read_text(encoding="utf-8")
        m = WORKER_RE.search(raw)
        if not m:
            print(f"  ❌ {WORKER_TS.name}: 找不到 `const MCP_SERVER_VERSION = \"...\";`，需人工确认")
            stale.append((WORKER_TS.name, [], ["(未找到)"]))
        elif m.group(1) != ver:
            stale.append((WORKER_TS.name, [m.group(1)], [m.group(1)]))
            if check_only:
                print(f"  ❌ {WORKER_TS.name}: MCP_SERVER_VERSION 仍是 {m.group(1)}")
            else:
                new = WORKER_RE.sub(f'const MCP_SERVER_VERSION = "{ver}";', raw, count=1)
                WORKER_TS.write_text(new, encoding="utf-8")
                print(f"  ✅ {WORKER_TS.name}: MCP_SERVER_VERSION {m.group(1)} → {ver}")
        else:
            print(f"  {WORKER_TS.name}: 已是 {ver}（MCP_SERVER_VERSION）")

    if check_only and stale:
        print(f"\n有 {len(stale)} 个文件版本号不一致。跑一次 `python sync_versions.py` 修掉。")
        sys.exit(1)
    print("\n完成。" if not check_only else "\n全部一致。")


if __name__ == "__main__":
    main()
