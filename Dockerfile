# DataSinking MCP server（stdio）—— 给 Glama 的自动构建 / 探活用
#
# 为什么需要这个文件：
#   `awesome-mcp-servers` 的维护要求是「服务器先列在 Glama 上、owner 认领、通过质量评分」，
#   而 Glama 是从 GitHub 仓库构建并自动检查（能构建 → 能启动 → 能响应 MCP introspection）。
#   所以 Dockerfile 必须放在仓库根目录。
#
# ⚠️ 一个关键事实（决定了探活能不能过）：
#   introspection（`initialize` / `tools/list`）**不需要 DATASINK_API_KEY** ——
#   `datasinking/mcp_server.py` 里 API_KEY 只在**工具调用路径**上检查，不在启动时。
#   所以不带 key 也能通过 Glama 的检查；真正调用工具时才需要 key（由客户端自己配）。
#
# 本地验证方式（不需要装 Python 依赖，也不需要 key）：
#   docker build -t datasinking-mcp .
#   # 然后对着容器走一遍 initialize → tools/list，应看到 6 个工具的列表

FROM python:3.12-slim

WORKDIR /app

# 只拷打包真正需要的东西 —— 不拷 dist/ npm/ docs/ research/，镜像更小、构建更快。
# README.md 必须拷：pyproject.toml 里 readme = "README.md"，缺了 setuptools 会报错。
COPY pyproject.toml README.md ./
COPY datasinking/ ./datasinking/

# 版本号是 dynamic 的（读 datasinking/_version.py），所以必须先拷包目录再 install。
# [mcp] 这个 extra 带来 mcp SDK + requests（主包刻意保持零依赖）。
RUN pip install --no-cache-dir ".[mcp]"

# stdio 传输：不监听任何端口，通过 stdin/stdout 收发 JSON-RPC。
# 这也是 `pip install "datasinking[mcp]"` 之后 `datasinking-mcp` 的行为。
ENTRYPOINT ["datasinking-mcp"]
