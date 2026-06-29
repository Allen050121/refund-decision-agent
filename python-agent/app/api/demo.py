"""Browser demo console for the refund decision Agent."""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse


router = APIRouter()


@router.get("", response_class=HTMLResponse)
async def demo_console() -> HTMLResponse:
    return HTMLResponse(DEMO_HTML)


DEMO_HTML = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>售后退款决策 Agent 控制台</title>
  <style>
    :root {
      color-scheme: light;
      --ink: #172026;
      --muted: #61707d;
      --line: #d8e0e6;
      --panel: #f7f9fb;
      --surface: #ffffff;
      --accent: #0f766e;
      --accent-ink: #ffffff;
      --ok: #0f7a4f;
      --ok-bg: #e4f6ed;
      --bad: #b42318;
      --bad-bg: #fde7e5;
      --warn: #996500;
      --warn-bg: #fff3cf;
      --info: #1456a0;
      --info-bg: #e8f1ff;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--surface);
      color: var(--ink);
      font-family: Inter, "Segoe UI", "Microsoft YaHei", Arial, sans-serif;
    }
    button, input, textarea { font: inherit; }
    .shell {
      min-height: 100vh;
      display: grid;
      grid-template-rows: auto 1fr;
    }
    .topbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 18px;
      padding: 16px 24px;
      border-bottom: 1px solid var(--line);
      background: var(--surface);
      position: sticky;
      top: 0;
      z-index: 5;
    }
    .brand h1 {
      margin: 0;
      font-size: 20px;
      line-height: 1.2;
      letter-spacing: 0;
    }
    .brand p {
      margin: 4px 0 0;
      color: var(--muted);
      font-size: 13px;
    }
    .health {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      justify-content: flex-end;
    }
    .layout {
      display: grid;
      grid-template-columns: 320px minmax(360px, 1fr) 420px;
      min-height: 0;
    }
    aside, section {
      min-width: 0;
    }
    .sidebar {
      border-right: 1px solid var(--line);
      padding: 18px;
      background: var(--panel);
    }
    .workspace {
      padding: 20px;
      border-right: 1px solid var(--line);
    }
    .result {
      padding: 20px;
      background: #fbfcfd;
    }
    h2 {
      margin: 0 0 12px;
      font-size: 16px;
      letter-spacing: 0;
    }
    .case-list {
      display: grid;
      gap: 10px;
    }
    .case-button {
      width: 100%;
      text-align: left;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--surface);
      padding: 12px;
      cursor: pointer;
    }
    .case-button:hover,
    .case-button.active {
      border-color: var(--accent);
      box-shadow: inset 3px 0 0 var(--accent);
    }
    .case-button strong {
      display: block;
      font-size: 14px;
      margin-bottom: 4px;
    }
    .case-button span {
      color: var(--muted);
      font-size: 12px;
    }
    .field {
      display: grid;
      gap: 6px;
      margin-bottom: 14px;
    }
    label {
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
    }
    input, textarea {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 10px 11px;
      background: var(--surface);
      color: var(--ink);
    }
    textarea {
      min-height: 156px;
      resize: vertical;
      line-height: 1.6;
    }
    .actions {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      align-items: center;
    }
    .primary {
      border: 0;
      border-radius: 8px;
      background: var(--accent);
      color: var(--accent-ink);
      padding: 10px 14px;
      cursor: pointer;
      font-weight: 700;
    }
    .secondary {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--surface);
      color: var(--ink);
      padding: 9px 13px;
      cursor: pointer;
    }
    .primary:disabled,
    .secondary:disabled {
      cursor: not-allowed;
      opacity: .55;
    }
    .status-line {
      margin-top: 12px;
      color: var(--muted);
      font-size: 13px;
      min-height: 20px;
    }
    .badge {
      display: inline-flex;
      align-items: center;
      min-height: 24px;
      border-radius: 999px;
      padding: 3px 9px;
      font-size: 12px;
      font-weight: 700;
      white-space: nowrap;
    }
    .ok { color: var(--ok); background: var(--ok-bg); }
    .bad { color: var(--bad); background: var(--bad-bg); }
    .warn { color: var(--warn); background: var(--warn-bg); }
    .info { color: var(--info); background: var(--info-bg); }
    .muted { color: var(--muted); }
    .summary-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
      margin-bottom: 18px;
    }
    .metric {
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      background: var(--surface);
      min-width: 0;
    }
    .metric span {
      display: block;
      color: var(--muted);
      font-size: 12px;
      margin-bottom: 6px;
    }
    .metric strong {
      overflow-wrap: anywhere;
      font-size: 15px;
    }
    .section {
      border-top: 1px solid var(--line);
      padding-top: 14px;
      margin-top: 14px;
    }
    .chips {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }
    .chip {
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 5px 9px;
      background: var(--surface);
      font-size: 12px;
    }
    pre {
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      overflow: auto;
      background: #0f1720;
      color: #e7eef5;
      font-size: 12px;
      line-height: 1.5;
      max-height: 260px;
    }
    .history {
      display: grid;
      gap: 8px;
    }
    .history-item {
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 10px;
      background: var(--surface);
      font-size: 13px;
    }
    @media (max-width: 1100px) {
      .layout {
        grid-template-columns: 280px 1fr;
      }
      .result {
        grid-column: 1 / -1;
        border-top: 1px solid var(--line);
      }
    }
    @media (max-width: 760px) {
      .topbar {
        align-items: flex-start;
        flex-direction: column;
      }
      .layout {
        grid-template-columns: 1fr;
      }
      .sidebar,
      .workspace {
        border-right: 0;
        border-bottom: 1px solid var(--line);
      }
      .summary-grid {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>
<body>
  <div class="shell">
    <header class="topbar">
      <div class="brand">
        <h1>售后退款决策 Agent 控制台</h1>
        <p>真实调用 Python Agent 任务接口，结果由当前服务配置的 LLM、RAG 和 Java 工具链共同生成。</p>
      </div>
      <div class="health" id="health"></div>
    </header>

    <main class="layout">
      <aside class="sidebar">
        <h2>Demo 工单</h2>
        <div class="case-list" id="caseList"></div>
      </aside>

      <section class="workspace">
        <h2>工单输入</h2>
        <div class="field">
          <label for="userId">用户 ID</label>
          <input id="userId" autocomplete="off">
        </div>
        <div class="field">
          <label for="orderId">订单 ID</label>
          <input id="orderId" autocomplete="off">
        </div>
        <div class="field">
          <label for="ticketContent">工单内容</label>
          <textarea id="ticketContent"></textarea>
        </div>
        <div class="actions">
          <button class="primary" id="runButton">运行决策</button>
          <button class="secondary" id="refreshButton">刷新健康状态</button>
        </div>
        <div class="status-line" id="statusLine"></div>

        <div class="section">
          <h2>最近任务</h2>
          <div class="history" id="history"></div>
        </div>
      </section>

      <section class="result">
        <h2>决策结果</h2>
        <div class="summary-grid">
          <div class="metric"><span>任务状态</span><strong id="taskStatus">-</strong></div>
          <div class="metric"><span>最终决策</span><strong id="decision">-</strong></div>
          <div class="metric"><span>原因代码</span><strong id="reasonCode">-</strong></div>
          <div class="metric"><span>任务 ID</span><strong id="taskId">-</strong></div>
        </div>

        <div class="section">
          <h2>规则引用</h2>
          <div class="chips" id="rules"></div>
        </div>
        <div class="section">
          <h2>证据</h2>
          <div class="chips" id="evidence"></div>
        </div>
        <div class="section">
          <h2>风险提示</h2>
          <div class="chips" id="risks"></div>
        </div>
        <div class="section">
          <h2>原始响应</h2>
          <pre id="raw">{}</pre>
        </div>
      </section>
    </main>
  </div>

  <script>
    const cases = [
      {
        id: "DEMO-001",
        title: "课程无法观看，建议退款",
        userId: "U1002",
        orderId: "O20260622003",
        ticketContent: "React 前端课程一直打不开，视频服务故障，订单号 O20260622003，想退款"
      },
      {
        id: "DEMO-002",
        title: "重复购买，建议退款",
        userId: "U1002",
        orderId: "O20260622005",
        ticketContent: "我不小心买重了同一门 Java 课程，想退掉重复购买的订单 O20260622005"
      },
      {
        id: "DEMO-003",
        title: "无理由退款，转人工审批",
        userId: "U1001",
        orderId: "O20260622001",
        ticketContent: "刚买的课程还没开始学，但我不想学了，申请无理由退款，订单 O20260622001"
      },
      {
        id: "DEMO-004",
        title: "超过退款窗口，拒绝退款",
        userId: "U1001",
        orderId: "O20260622008",
        ticketContent: "这个订单已经超过 30 天了，现在还想退款，订单 O20260622008"
      },
      {
        id: "DEMO-005",
        title: "缺少订单号，要求补充信息",
        userId: "U1001",
        orderId: "",
        ticketContent: "我买的课程打不开，想退款"
      },
      {
        id: "DEMO-006",
        title: "非退款咨询，不进入退款链路",
        userId: "U1001",
        orderId: "",
        ticketContent: "我想咨询一下 Java 课程大纲和上课时间"
      }
    ];

    const state = {
      selectedCase: cases[0],
      running: false,
      history: []
    };

    const el = (id) => document.getElementById(id);

    function badge(text, tone) {
      const safe = text || "-";
      return `<span class="badge ${tone}">${safe}</span>`;
    }

    function decisionTone(decision) {
      return {
        REFUND_RECOMMENDED: "ok",
        REFUND_REJECTED: "bad",
        WAIT_FOR_APPROVAL: "warn",
        NEED_MORE_INFORMATION: "info"
      }[decision] || "info";
    }

    function renderCases() {
      el("caseList").innerHTML = cases.map((item) => `
        <button class="case-button ${item.id === state.selectedCase.id ? "active" : ""}" data-case="${item.id}">
          <strong>${item.title}</strong>
          <span>${item.id} · ${item.userId}${item.orderId ? " · " + item.orderId : ""}</span>
        </button>
      `).join("");

      document.querySelectorAll("[data-case]").forEach((button) => {
        button.addEventListener("click", () => {
          const next = cases.find((item) => item.id === button.dataset.case);
          if (next) {
            state.selectedCase = next;
            fillCase(next);
            renderCases();
          }
        });
      });
    }

    function fillCase(item) {
      el("userId").value = item.userId;
      el("orderId").value = item.orderId;
      el("ticketContent").value = item.ticketContent;
      el("statusLine").textContent = `已选择 ${item.id}`;
    }

    function renderChips(id, items) {
      const values = Array.isArray(items) ? items : [];
      el(id).innerHTML = values.length
        ? values.map((item) => `<span class="chip">${item}</span>`).join("")
        : `<span class="muted">-</span>`;
    }

    function renderResult(payload) {
      const result = payload?.result || {};
      el("taskStatus").innerHTML = badge(payload?.status || "-", payload?.status === "COMPLETED" ? "ok" : "info");
      el("decision").innerHTML = badge(result.decision || payload?.decision || "-", decisionTone(result.decision || payload?.decision));
      el("reasonCode").textContent = result.reason_code || "-";
      el("taskId").textContent = payload?.taskId || "-";
      renderChips("rules", result.rule_citations);
      renderChips("evidence", result.evidence);
      renderChips("risks", result.risk_hints);
      el("raw").textContent = JSON.stringify(payload || {}, null, 2);
    }

    function renderHistory() {
      el("history").innerHTML = state.history.length
        ? state.history.map((item) => `
          <div class="history-item">
            <strong>${item.taskId}</strong>
            <div>${badge(item.decision || item.status, decisionTone(item.decision))}</div>
          </div>
        `).join("")
        : `<span class="muted">-</span>`;
    }

    async function refreshHealth() {
      const health = el("health");
      health.innerHTML = badge("checking", "info");
      try {
        const [base, ready] = await Promise.all([
          fetch("/health").then((r) => r.json()),
          fetch("/health/ready").then((r) => r.json())
        ]);
        const checks = ready.checks || {};
        health.innerHTML = [
          badge(`Python ${base.status || "-"}`, base.status === "OK" ? "ok" : "bad"),
          badge(`Ready ${ready.status || "-"}`, ready.status === "ready" ? "ok" : "warn"),
          badge(`Java ${checks.java_api?.status || "-"}`, checks.java_api?.status === "ok" ? "ok" : "bad"),
          badge(`RAG ${checks.elasticsearch?.status || "-"}`, checks.elasticsearch?.status === "ok" ? "ok" : "warn"),
          badge(`Redis ${checks.redis?.status || "-"}`, checks.redis?.status === "ok" ? "ok" : "warn")
        ].join("");
      } catch (error) {
        health.innerHTML = badge("health failed", "bad");
      }
    }

    async function pollTask(taskId) {
      for (let i = 0; i < 20; i += 1) {
        const response = await fetch(`/tasks/${taskId}`);
        const payload = await response.json();
        renderResult(payload);
        if (["COMPLETED", "FAILED"].includes(payload.status)) {
          state.history.unshift({
            taskId,
            status: payload.status,
            decision: payload.decision
          });
          state.history = state.history.slice(0, 6);
          renderHistory();
          return payload;
        }
        await new Promise((resolve) => setTimeout(resolve, 800));
      }
      throw new Error("任务轮询超时");
    }

    async function runDecision() {
      if (state.running) return;
      state.running = true;
      el("runButton").disabled = true;
      el("statusLine").textContent = "正在创建 Agent 任务...";
      try {
        const body = {
          userId: el("userId").value.trim(),
          ticketContent: el("ticketContent").value.trim()
        };
        const orderId = el("orderId").value.trim();
        if (orderId) body.orderId = orderId;

        const response = await fetch("/tasks", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body)
        });
        if (!response.ok) {
          throw new Error(`创建任务失败: HTTP ${response.status}`);
        }
        const created = await response.json();
        el("statusLine").textContent = `任务已创建：${created.taskId}，正在等待结果...`;
        renderResult({ taskId: created.taskId, status: created.status, result: {} });
        const finalResult = await pollTask(created.taskId);
        el("statusLine").textContent = `任务完成：${finalResult.taskId}`;
      } catch (error) {
        el("statusLine").textContent = error.message || String(error);
      } finally {
        state.running = false;
        el("runButton").disabled = false;
      }
    }

    el("runButton").addEventListener("click", runDecision);
    el("refreshButton").addEventListener("click", refreshHealth);

    renderCases();
    fillCase(state.selectedCase);
    renderHistory();
    renderResult(null);
    refreshHealth();
  </script>
</body>
</html>
"""
