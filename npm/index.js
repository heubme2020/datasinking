#!/usr/bin/env node
/**
 * DataSinking MCP server — stdio transport.
 *
 * Usage:
 *   npx -y datasinking-mcp
 *
 * Requires DATASINK_API_KEY (free key at https://datasink.ing). In an MCP client:
 *
 *   {
 *     "mcpServers": {
 *       "datasinking": {
 *         "command": "npx",
 *         "args": ["-y", "datasinking-mcp"],
 *         "env": { "DATASINK_API_KEY": "<your-key>" }
 *       }
 *     }
 *   }
 *
 * 为什么用低层 `Server` 而不是高层 `McpServer`：工具的 inputSchema 是**手写的 JSON Schema**，
 * 和远程端点 `worker/src/index.ts` 的 `MCP_TOOLS`、以及 PyPI 包的 `Annotated[..., Field(...)]`
 * 逐字同源。`McpServer.registerTool` 只吃 zod，输出的 JSON Schema 是 zod 转出来的，
 * 和另两份对不上 —— 这个项目已经因为「多份实现悄悄漂移」踩过四次（见 sync_versions.py
 * 和 worker/src/index.ts 顶部的注释），能机械比对就别靠人眼。
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";

import {
  INSTRUCTIONS,
  SERVER_NAME,
  SERVER_TITLE,
  TOOLS,
  VERSION,
  WEBSITE_URL,
  callTool,
  DataSinkingError,
} from "./tools.js";

const server = new Server(
  {
    name: SERVER_NAME,
    title: SERVER_TITLE,
    version: VERSION,
    websiteUrl: WEBSITE_URL,
  },
  {
    capabilities: { tools: {} },
    instructions: INSTRUCTIONS,
  }
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({ tools: TOOLS }));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  try {
    const result = await callTool(name, args ?? {});
    return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
  } catch (err) {
    // 把服务端/配置的真实原因透给模型和用户，别包装成一句 "tool failed"。
    // 缺 key 是配置问题，其他是调用问题 —— 两者都该让用户看见原文。
    const hint =
      err instanceof DataSinkingError
        ? ""
        : `\n\n(${err?.name ?? "Error"}: ${err?.message ?? err})`;
    return {
      content: [{ type: "text", text: `Error calling ${name}: ${err?.message ?? err}${hint}` }],
      isError: true,
    };
  }
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);

  // ⚠️ **永远不要往 stdout 写日志** —— stdio 传输里 stdout 是 JSON-RPC 通道，
  // 多打一行非 JSON 的内容就会让客户端解析失败。要输出信息一律走 stderr。
  process.stderr.write(`datasinking-mcp ${VERSION} ready (API: ${process.env.DATASINK_API_URL || "https://api.datasink.ing"})\n`);
}

process.on("SIGINT", () => process.exit(0));
process.on("SIGTERM", () => process.exit(0));

main().catch((err) => {
  process.stderr.write(`datasinking-mcp failed to start: ${err?.stack ?? err}\n`);
  process.exit(1);
});
