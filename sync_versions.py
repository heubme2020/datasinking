# -*- coding: utf-8 -*-
"""把 `datasinking/_version.py` 的版本号同步到两个 MCP manifest。

**为什么需要**：版本号有 3 个落点 ——
  ① `datasinking/_version.py`   唯一来源（pyproject 用 `dynamic` 从它读，
                                client.py 的 UA 和 mcp_server.py 也读它）
  ② `lhm.plugin.json`           给 LobeHub 之类的 MCP 目录读
  ③ `server.json`               给官方 MCP registry 读

②③ 是外部注册表读的 **JSON 字面量**，没法像 pyproject 那样动态引用，只能跟着改。
2026-09-14 就漂过一次：包已经到 0.2.4~0.2.7，这两个文件还停在 0.2.3。

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
JSON_FILES = ["lhm.plugin.json", "server.json"]


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

    if check_only and stale:
        print(f"\n有 {len(stale)} 个文件版本号不一致。跑一次 `python sync_versions.py` 修掉。")
        sys.exit(1)
    print("\n完成。" if not check_only else "\n全部一致。")


if __name__ == "__main__":
    main()
