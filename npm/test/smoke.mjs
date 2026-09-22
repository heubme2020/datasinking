/**
 * 端到端冒烟测试 —— 用**真实的 MCP 客户端**通过 stdio 连本包，不是打桩。
 *
 *   node test/smoke.mjs                          # 只测握手 + tools/list（不需要 key）
 *   DATASINK_API_KEY=xxx node test/smoke.mjs     # 连真实 API 走完整链路
 *
 * 为什么要真的握手：这个项目已经被「声明了但没落地」坑过四次（工具描述没到客户端、
 * 参数描述全空、端点漂移 19 天）。工具定义改完必须**从客户端侧**确认它真的到了，
 * 对着源码看是看不出来的。
 */

import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

const EXPECTED_TOOLS = [
  "list_exchanges",
  "list_stocks",
  "list_reports",
  "get_report",
  "list_sections",
  "get_section",
];

let failures = 0;

function check(label, ok, detail = "") {
  console.log(`  ${ok ? "✅" : "❌"} ${label}${detail ? ` — ${detail}` : ""}`);
  if (!ok) failures++;
}

function textOf(result) {
  return (result?.content ?? [])
    .filter((c) => c.type === "text")
    .map((c) => c.text)
    .join("\n");
}

const hasKey = Boolean(process.env.DATASINK_API_KEY);

const transport = new StdioClientTransport({
  command: process.execPath,
  args: [new URL("../index.js", import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, "$1")],
  env: { ...process.env },
  stderr: "inherit",
});

const client = new Client({ name: "datasinking-smoke", version: "1.0.0" });

try {
  await client.connect(transport);
  console.log("connected\n");

  const info = client.getServerVersion();
  console.log("server:", JSON.stringify(info));
  check("serverInfo.version 不是空/占位", Boolean(info?.version) && info.version !== "0.0.0", info?.version);
  check("serverInfo.title 存在", Boolean(info?.title), info?.title);

  const instructions = client.getInstructions();
  check("instructions 下发了", Boolean(instructions && instructions.length > 50),
    instructions ? `${instructions.length} chars` : "缺失");
  check("instructions 提到 get_section（关键用法）",
    typeof instructions === "string" && instructions.includes("get_section"));

  const { tools } = await client.listTools();
  const names = tools.map((t) => t.name);
  check(`tools/list 返回 6 个工具`, tools.length === 6, names.join(", "));
  check("工具名与另两份实现一致", EXPECTED_TOOLS.every((n) => names.includes(n)));

  const byName = Object.fromEntries(tools.map((t) => [t.name, t]));
  const missingDesc = tools
    .flatMap((t) =>
      Object.entries(t.inputSchema?.properties ?? {})
        .filter(([, s]) => !s.description)
        .map(([p]) => `${t.name}.${p}`)
    );
  check("每个参数都有 description", missingDesc.length === 0, missingDesc.join(", ") || "全部到位");

  // get_section.section 必须带中文示例 —— 匹配的是报告原文标题，只有英文等于必然传错。
  const sectionDesc = byName["get_section"]?.inputSchema?.properties?.section?.description ?? "";
  check("get_section.section 含中文示例", /管理层讨论与分析/.test(sectionDesc));

  if (!hasKey) {
    console.log("\n未设 DATASINK_API_KEY —— 只跑握手 + tools/list。");
    const res = await client.callTool({ name: "list_exchanges", arguments: {} });
    check("缺 key 时返回 isError 且说清原因",
      res.isError === true && /DATASINK_API_KEY/.test(textOf(res)));
  } else {
    console.log("\n带 key，走真实 API：");

    const exchanges = await client.callTool({ name: "list_exchanges", arguments: {} });
    const exList = JSON.parse(textOf(exchanges));
    check("list_exchanges 返回交易所列表", Array.isArray(exList) && exList.length > 0, `${exList.length} 个`);

    const reports = await client.callTool({
      name: "list_reports",
      arguments: { symbol: "2330.TW", doc_type: "annual", size: 3 },
    });
    const rep = JSON.parse(textOf(reports));
    check("list_reports 查到 2330.TW", (rep.total ?? 0) > 0, `total=${rep.total}`);
    check("list_reports 带 source 署名", Boolean(rep.items?.[0]?.source), rep.items?.[0]?.source);

    const docId = rep.items?.[0]?.id;
    if (docId) {
      const sections = await client.callTool({ name: "list_sections", arguments: { document_id: docId } });
      const sec = JSON.parse(textOf(sections));
      check("list_sections 返回章节", Array.isArray(sec.sections) && sec.sections.length > 0,
        `${sec.sections?.length} 节`);
      check("list_sections 带 estimated_tokens（省 context 用）",
        sec.section_details?.[0]?.estimated_tokens > 0);

      const one = await client.callTool({
        name: "get_section",
        arguments: { document_id: docId, section: sec.sections[0] },
      });
      const body = textOf(one);
      check("get_section 取到正文", !one.isError && body.length > 200, `${body.length} chars`);
    }
  }
} catch (err) {
  console.error("\n💥 冒烟测试抛错:", err);
  failures++;
} finally {
  await client.close().catch(() => {});
}

console.log(`\n${failures === 0 ? "全部通过 ✅" : `${failures} 项失败 ❌`}`);
process.exit(failures === 0 ? 0 : 1);
