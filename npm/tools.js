/**
 * DataSinking MCP server — tool definitions + REST calls.
 *
 * ⚠️ **三份平行实现，改一处必须改三处**
 *   ① `datasinking/mcp_server.py`      pip 包（本地 stdio）
 *   ② `worker/src/index.ts` 的 MCP_TOOLS   远程端点 https://api.datasink.ing/mcp
 *   ③ 本文件                          npm 包（本文件，本地 stdio）
 *
 * 为什么要有第 ③ 份：[`npx`](https://docs.npmjs.com/cli/v10/commands/npx) 比 `uvx` 普及得多 ——
 * 装 ① 要先有 Python + uv，装 ③ 只要有 Node。MCP 客户端用户里相当一部分走 `npx`，
 * 没有 npm 包就直接流失。
 *
 * 为什么三份而不是让 npm 包代理远程端点：目录站（Glama / LobeHub / 官方 registry）
 * 会静态扫描包里的工具定义。转发式的壳子扫不出工具，也过不了需要鉴权的探活。
 *
 * **工具名、工具描述、参数名、参数描述**四项必须三边一致；
 * 跑 `python check_mcp_parity.py`（项目根）可以机械比对 ② 和 ③。
 *
 * 描述一律英文：模型端 tool-calling 是拿描述决定「要不要调」的，用户和 agent 以英文为主。
 * 唯一的例外是 `get_section` 的 section 示例 —— **必须留中文**，因为匹配的是报告原文标题
 * （A 股是「第三节管理层讨论与分析」），不是我们自己的文案。
 */

import { readFileSync } from "node:fs";

const pkg = JSON.parse(readFileSync(new URL("./package.json", import.meta.url), "utf8"));

/** 版本号唯一来源 = 本包的 package.json（由项目根的 sync_versions.py 从 _version.py 同步过来）。 */
export const VERSION = pkg.version;

export const SERVER_NAME = "DataSinking";
export const SERVER_TITLE = "DataSinking — Full-text Asian Financial Reports";
export const WEBSITE_URL = "https://datasink.ing";

/** initialize 时下发给客户端的 instructions（会进模型上下文，别写废话） */
export const INSTRUCTIONS =
  "DataSinking serves full-text financial reports (annual / semi-annual / quarterly) from " +
  "China, Korea, Japan and Taiwan as clean Markdown, ready for LLM reading and RAG. " +
  "Use FMP-style symbols: 600519.SS (Kweichow Moutai), 005930.KS (Samsung Electronics), " +
  "7203.T (Toyota), 2330.TW (TSMC). To save tokens, prefer get_section to pull one chapter " +
  "(e.g. MD&A) instead of get_report for the whole document.";

const API_URL = (process.env.DATASINK_API_URL || "https://api.datasink.ing").replace(/\/+$/, "");
const API_KEY = process.env.DATASINK_API_KEY || "";

const DOCUMENT_ID_DESC = "Report id, from list_reports items[].id";

export const TOOLS = [
  {
    name: "list_exchanges",
    description:
      "List the exchanges DataSinking covers. Returns exchange codes (sse / szse / bj / ksc / koe / knx / jpx / twse / tpex) with the number of reports available per exchange. Call this first to discover coverage. Sources: A-shares = cninfo.com.cn, Korea = DART, Japan = EDINET, Taiwan = MOPS.",
    inputSchema: { type: "object", properties: {} },
  },
  {
    name: "list_stocks",
    description: "List the stocks on one exchange, including the report count per company.",
    inputSchema: {
      type: "object",
      properties: {
        exchange: {
          type: "string",
          description: "Exchange code, e.g. sse / szse / bj / ksc / koe / knx / jpx / twse / tpex",
        },
        limit: {
          type: "integer",
          description: "Return only the first N companies (default 20) to keep the response short.",
          default: 20,
        },
      },
      required: ["exchange"],
    },
  },
  {
    name: "list_reports",
    description:
      "List a company's reports — metadata only (id, title, period), no body text. Each item carries a `source` field naming the official disclosure platform; keep that attribution when you cite it.",
    inputSchema: {
      type: "object",
      properties: {
        symbol: {
          type: "string",
          description: "FMP-style symbol, e.g. 600519.SS / 005930.KS / 7203.T / 2330.TW",
        },
        doc_type: {
          type: "string",
          enum: ["annual", "semiannual", "q1", "q3"],
          description: "Report type to filter on. Defaults to annual.",
          default: "annual",
        },
        size: {
          type: "integer",
          description: "Number of reports to return (default 10).",
          default: 10,
        },
      },
      required: ["symbol"],
    },
  },
  {
    name: "get_report",
    description:
      "Fetch one report's full text (metadata + Markdown body). The `source` field names the official disclosure platform; keep that attribution when you cite it. Expensive in tokens — prefer get_section when you only need one chapter.",
    inputSchema: {
      type: "object",
      properties: { document_id: { type: "integer", description: DOCUMENT_ID_DESC } },
      required: ["document_id"],
    },
  },
  {
    name: "list_sections",
    description:
      "List every section of a report with its size, before you decide what to pull. Returns `sections` (titles, in order) plus `section_details` — same order, one entry per section with `title`, `has_tables`, `chars` and `estimated_tokens`. Use `estimated_tokens` to avoid pulling a chapter that would blow your context, and `has_tables` to know whether the chapter needs special handling (tables are the part RAG pipelines usually get wrong). Then call get_section with a heading keyword — the headings are in the report's own language.",
    inputSchema: {
      type: "object",
      properties: { document_id: { type: "integer", description: DOCUMENT_ID_DESC } },
      required: ["document_id"],
    },
  },
  {
    name: "get_section",
    description:
      "Fetch only one section of a report by keyword — much cheaper than get_report, best for RAG.",
    inputSchema: {
      type: "object",
      properties: {
        document_id: { type: "integer", description: DOCUMENT_ID_DESC },
        section: {
          type: "string",
          description:
            "Heading keyword, matched as a substring against the report's OWN headings, so pass it " +
            "in the report's language. A-share reports have Chinese headings (e.g. 第三节管理层讨论与分析) — " +
            "use 管理层讨论与分析 / 财务报告 there. For English-language filings, \"MD&A\" / " +
            "\"financial statements\" / \"notes\" work. If nothing matches, the API returns 404 " +
            "with the real headings — retry with one of those, or call list_sections first.",
        },
      },
      required: ["document_id", "section"],
    },
  },
];

class DataSinkingError extends Error {}

async function get(path, params) {
  if (!API_KEY) {
    throw new DataSinkingError(
      "Missing DATASINK_API_KEY environment variable. " +
        "Get a free key at https://datasink.ing and set it in your MCP client config's `env` block."
    );
  }
  const url = new URL(API_URL + path);
  for (const [k, v] of Object.entries(params || {})) {
    if (v !== undefined && v !== null) url.searchParams.set(k, String(v));
  }

  let res;
  try {
    // 90s: 全量年报正文可以很大，给足时间；别用默认的无超时，那会挂死客户端。
    res = await fetch(url, {
      headers: { Authorization: `Bearer ${API_KEY}`, Accept: "application/json" },
      signal: AbortSignal.timeout(90_000),
    });
  } catch (err) {
    throw new DataSinkingError(`Could not reach ${API_URL} (${err.name}: ${err.message})`);
  }

  const text = await res.text();
  if (!res.ok) {
    // 服务端把「该怎么做」写在 body 里，两个字段各有用途，**都要带上**：
    //   detail    —— 一句人话（「未找到章节「X」」）
    //   available —— 那份报告的**全部真实标题**。get_section 的描述明确让模型
    //                「retry with one of those」，所以这个列表必须跟着错误走。
    //
    // ⚠️ 这里原本的注释就写着「404 会带上真实标题，原样透给模型」，但代码只取了
    //    `.detail` —— 真实标题在 `available` 里，于是那句承诺从未兑现
    //    （2026-09-22 用真 key 实测确认）。注释和实现不一致，就是 bug 的藏身处。
    let body = null;
    try {
      body = JSON.parse(text);
    } catch {
      /* 不是 JSON 就原样用 */
    }
    const detail = body?.detail ?? text;
    const available = Array.isArray(body?.available)
      ? `\nAvailable sections: ${JSON.stringify(body.available)}`
      : "";
    throw new DataSinkingError(`HTTP ${res.status}: ${String(detail).slice(0, 2000)}${available}`);
  }
  try {
    return JSON.parse(text);
  } catch {
    throw new DataSinkingError(`Expected JSON from ${API_URL}${path}, got: ${text.slice(0, 200)}`);
  }
}

/** 执行一次工具调用，返回给客户端的结果对象（已按工具裁剪）。 */
export async function callTool(name, args = {}) {
  switch (name) {
    case "list_exchanges":
      return (await get("/exchanges")).exchanges ?? [];

    case "list_stocks": {
      const limit = Number.isInteger(args.limit) ? args.limit : 20;
      const data = await get("/stocks", { exchange: args.exchange });
      return {
        exchange: args.exchange,
        total: data.total ?? 0,
        items: (data.items ?? []).slice(0, limit),
      };
    }

    case "list_reports":
      return get("/documents", {
        symbol: args.symbol,
        doc_type: args.doc_type ?? "annual",
        size: Number.isInteger(args.size) ? args.size : 10,
      });

    case "get_report":
      return get(`/documents/${args.document_id}`);

    case "list_sections":
      return get(`/documents/${args.document_id}/sections`);

    case "get_section":
      return get(`/documents/${args.document_id}`, { section: args.section });

    default:
      throw new DataSinkingError(`Unknown tool: ${name}`);
  }
}

export { DataSinkingError };
