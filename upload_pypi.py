# -*- coding: utf-8 -*-
"""把 dist/ 里的包上传到 PyPI —— 交互式输入 token, 不回显、不写进任何文件。

为什么做成脚本: PyPI 上传必须带 token, 而 token 不该出现在对话记录 / 日志里。
getpass 不回声, 脚本也不落盘, 跑完即忘。

用法(在你的终端里跑, 不是在对话里):
    cd C:/Users/admin/Desktop/datasinking/github-repo
    python upload_pypi.py

token 去 https://pypi.org/manage/account/token/ 建, scope 选
「Entire account」或只勾 datasinking 这个项目。
"""
import getpass
import pathlib
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = pathlib.Path(__file__).resolve().parent
DIST = HERE / "dist"


def main():
    files = sorted(DIST.glob("*")) if DIST.is_dir() else []
    files = [f for f in files if f.suffix in (".whl", ".gz")]
    if not files:
        sys.exit(f"dist/ 里没有待上传的文件: {DIST}")

    print("将上传:")
    for f in files:
        print(f"   {f.name}  ({f.stat().st_size:,} 字节)")
    print()

    token = getpass.getpass("PyPI token (输入时不回显, 直接回车取消): ").strip()
    if not token:
        sys.exit("已取消。")
    if not token.startswith("pypi-"):
        # 不打印 token 本身, 只提示格式, 免得手滑粘错东西
        sys.exit("这不像 PyPI token（应以 pypi- 开头）。已取消, 什么都没上传。")

    cmd = [sys.executable, "-m", "twine", "upload", *[str(f) for f in files],
           "--username", "__token__", "--password", token]
    print("\n上传中...\n")
    r = subprocess.run(cmd, cwd=str(HERE))
    if r.returncode == 0:
        print("\n✅ 上传成功。")
        print("   验证: pip install -U datasinking")
        print("   页面: https://pypi.org/project/datasinking/")
    else:
        print(f"\n❌ 上传失败（twine 退出码 {r.returncode}）。")
        print("   常见原因: token 无效 / 该版本号已存在(不能覆盖已发布的版本) / 网络")
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
