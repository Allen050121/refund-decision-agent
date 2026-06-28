"""
LangGraph 工作流节点
文档 5.2: 节点定义
  - 每个节点有明确的输入、输出和退出条件
  - 通过 Port 接口调用 LLM 和检索，方便替换 Fake 实现
"""
import json
import logging
from typing import Dict, Any, Optional

from app.agent.state import AgentState, IntentEnum, ReasonCodeEnum, DecisionEnum
from app.application.ports import LLMPort, RetrievalPort

logger = logging.getLogger(__name__)

# ============================================================
# 全局 Port 实例（由 main.py 启动时注入）
# 文档 4.4: LangGraph Node 通过 Port 接口调用
# ============================================================
_llm_port: Optional[LLMPort] = None
_retrieval_port: Optional[RetrievalPort] = None


def set_ports(llm: Optional[LLMPort] = None, retrieval: Optional[RetrievalPort] = None) -> None:
    """注入 Port 实例（在 main.py 启动时调用）"""
    global _llm_port, _retrieval_port
    if llm is not None:
        _llm_port = llm
    if retrieval is not None:
        _retrieval_port = retrieval


def get_llm_port() -> Optional[LLMPort]:
    return _llm_port


def get_retrieval_port() -> Optional[RetrievalPort]:
    return _retrieval_port


# ============================================================
# 节点 1: 分类和提取
# ============================================================
async def classify_and_extract(state: AgentState) -> Dict[str, Any]:
    """
    节点 1: 分类和提取
    识别用户意图和退款原因
    文档 5.2: load_task -> classify_and_extract
    """
    ticket_content = state.ticket_content or ""
    result: Dict[str, Any] = {}

    # 尝试使用 LLM 进行意图识别
    llm = get_llm_port()
    if llm and ticket_content.strip():
        try:
            from app.agent.prompts import classify_messages, ClassifyOutput

            messages = classify_messages(ticket_content)
            response = await llm.chat_with_structured_output(
                messages=messages,
                response_schema=ClassifyOutput.model_json_schema(),
            )

            data = json.loads(response.content)
            intent = IntentEnum(data.get("intent", "OTHER"))
            reason_code = ReasonCodeEnum(data.get("reason_code", "GENERAL"))
            order_id = data.get("order_id") or state.order_id

            result = {
                "intent": intent,
                "reason_code": reason_code,
                "order_id": order_id,
            }
            logger.info(f"LLM 意图识别 | intent={intent} | reason_code={reason_code}")

        except Exception as e:
            logger.warning(f"LLM 意图识别失败，回退到规则匹配: {e}")
            result = _rule_based_classify(ticket_content, state.order_id)
    else:
        # 回退到规则匹配
        result = _rule_based_classify(ticket_content, state.order_id)

    # 更新预算
    budget = state.budget.copy()
    budget["used_model_calls"] = budget.get("used_model_calls", 0) + (1 if llm else 0)

    return {**result, "budget": budget}


def _rule_based_classify(ticket_content: str, order_id: Optional[str]) -> Dict[str, Any]:
    """规则匹配回退方案"""
    intent = IntentEnum.OTHER
    reason_code = ReasonCodeEnum.GENERAL

    # 判断是否为退款请求（包含退款关键词或明显的售后问题关键词）
    is_refund = (
        "退款" in ticket_content
        or "refund" in ticket_content.lower()
        or "售后" in ticket_content
        or "投诉" in ticket_content
    )

    # 检测具体原因
    has_specific_reason = False
    if "打不开" in ticket_content or "无法观看" in ticket_content or "故障" in ticket_content or "加载中" in ticket_content:
        reason_code = ReasonCodeEnum.COURSE_UNAVAILABLE
        has_specific_reason = True
    elif "重复" in ticket_content or "买重了" in ticket_content or "买重" in ticket_content:
        reason_code = ReasonCodeEnum.DUPLICATE_PURCHASE
        has_specific_reason = True
    elif "不想学了" in ticket_content or "无理由" in ticket_content or "不想学" in ticket_content:
        reason_code = ReasonCodeEnum.NO_REASON
        has_specific_reason = True
    elif ("超过" in ticket_content and ("天" in ticket_content or "日" in ticket_content)) or "超期" in ticket_content:
        reason_code = ReasonCodeEnum.EXPIRED_REFUND_WINDOW
        has_specific_reason = True

    # 如果有具体原因或明确的退款关键词，设为退款意图
    if is_refund or has_specific_reason:
        intent = IntentEnum.REFUND_REQUEST

    return {"intent": intent, "reason_code": reason_code, "order_id": order_id}


# ============================================================
# 节点 2: 验证必填字段
# ============================================================
async def validate_required_fields(state: AgentState) -> Dict[str, Any]:
    """
    节点 2: 验证必填字段
    检查是否缺少必要信息
    文档 5.2: 缺失字段 -> missing_fields
    """
    missing_fields = []

    if not state.order_id:
        missing_fields.append("order_id")

    if not state.user_id:
        missing_fields.append("user_id")

    if not state.ticket_content:
        missing_fields.append("ticket_content")

    errors = state.errors.copy()
    if missing_fields:
        errors.append(f"缺少必要字段：{', '.join(missing_fields)}")

    return {
        "missing_fields": missing_fields,
        "errors": errors,
    }


# ============================================================
# 节点 3: 查询业务数据
# ============================================================
async def query_business_data(state: AgentState) -> Dict[str, Any]:
    """
    节点 3: 查询业务数据
    调用 Java API 获取订单、学习进度、课程状态
    文档 3.2: 业务数据查询工具
    """
    from app.infrastructure.java_api import JavaApiClient

    # 如果缺少必要字段，跳过查询
    if state.missing_fields:
        logger.warning(f"缺少字段，跳过业务数据查询: {state.missing_fields}")
        return {
            "order_snapshot": None,
            "learning_progress": None,
            "course_status": None,
        }

    client = JavaApiClient()
    errors = state.errors.copy()
    evidence = state.evidence.copy()
    order_snapshot = None
    learning_progress = None
    course_status = None
    budget = state.budget.copy()

    # 查询订单
    if state.order_id and state.user_id:
        try:
            order_data = await client.get_order(state.order_id, state.user_id)
            if order_data.get("code") == 200:
                order_snapshot = order_data.get("data", {})
                evidence.append("ORDER_PAID")
                logger.info(f"订单查询成功 | order_id={state.order_id}")
            else:
                errors.append(f"订单查询失败：{order_data.get('message')}")
        except Exception as e:
            errors.append(f"订单查询异常：{str(e)}")
            logger.error(f"订单查询异常: {e}")

    # 查询学习进度
    if state.order_id and state.user_id:
        try:
            progress_data = await client.get_learning_progress(state.order_id, state.user_id)
            if progress_data.get("code") == 200:
                learning_progress = progress_data.get("data", {})
                logger.info(f"学习进度查询成功 | order_id={state.order_id}")
        except Exception as e:
            logger.error(f"学习进度查询异常: {e}")

    # 查询课程状态（根据订单中的 courseId）
    if order_snapshot and order_snapshot.get("courseId"):
        try:
            course_data = await client.get_course_status(order_snapshot.get("courseId"))
            if course_data.get("code") == 200:
                course_status = course_data.get("data", {})
                if course_status.get("isPromotional"):
                    evidence.append("PROMOTIONAL_COURSE")
                if course_status.get("status") == "UNAVAILABLE":
                    evidence.append("COURSE_UNAVAILABLE")
                logger.info(f"课程状态查询成功 | course_id={order_snapshot.get('courseId')}")
        except Exception as e:
            logger.error(f"课程状态查询异常: {e}")

    # 更新工具调用预算
    budget["used_tool_calls"] = budget.get("used_tool_calls", 0) + 3

    return {
        "order_snapshot": order_snapshot,
        "learning_progress": learning_progress,
        "course_status": course_status,
        "evidence": evidence,
        "errors": errors,
        "budget": budget,
    }


# ============================================================
# 节点 4: 检索规则 (RAG)
# ============================================================
async def retrieve_rules(state: AgentState) -> Dict[str, Any]:
    """
    节点 4: 检索退款规则
    文档 3.3: RAG 规则检索
      - 元数据过滤：场景匹配
      - BM25 检索
      - 返回 Top-K 规则
    """
    retrieval = get_retrieval_port()
    if not retrieval:
        logger.warning("检索 Port 未配置，跳过规则检索")
        return {"retrieved_rules": []}

    query = state.ticket_content or ""
    scenario = state.reason_code.value if state.reason_code else None

    try:
        rules = await retrieval.search_rules(
            query=query,
            scenario=scenario,
            top_k=5,
        )
        logger.info(f"规则检索完成 | 找到 {len(rules)} 条规则")

        # 文档 3.3: 规则冲突检测 -> 人工审批
        risk_hints = state.risk_hints.copy()
        if _has_conflicting_rules(rules):
            risk_hints.append("存在冲突规则，需人工审批")

        rule_citations = state.rule_citations.copy()
        for rule in rules:
            rule_id = rule.get("ruleId", "")
            if rule_id and rule_id not in rule_citations:
                rule_citations.append(rule_id)

        return {
            "retrieved_rules": rules,
            "risk_hints": risk_hints,
            "rule_citations": rule_citations,
        }

    except Exception as e:
        logger.error(f"规则检索失败: {e}")
        return {
            "retrieved_rules": [],
            "errors": state.errors + [f"规则检索失败：{str(e)}"],
        }


def _has_conflicting_rules(rules: list) -> bool:
    """检测是否存在冲突规则"""
    if len(rules) < 2:
        return False
    # 简化：如果同一场景有多条规则且建议不同决策，视为冲突
    scenarios = {}
    for rule in rules:
        scenario = rule.get("scenario", "")
        if scenario in scenarios:
            return True
        scenarios[scenario] = rule
    return False


# ============================================================
# 节点 5: 检查退款资格
# ============================================================
async def check_eligibility(state: AgentState) -> Dict[str, Any]:
    """
    节点 5: 检查退款资格
    使用领域策略 + 检索到的规则进行判定
    """
    from app.domain.policies import evaluate_refund_eligibility

    reason_code = state.reason_code.value if state.reason_code else "GENERAL"
    order_snapshot = state.order_snapshot or {}
    learning_progress = state.learning_progress or {}
    retrieved_rules = state.retrieved_rules or []
    course_status = state.course_status or {}

    eligibility = evaluate_refund_eligibility(
        reason_code=reason_code,
        order_snapshot=order_snapshot,
        learning_progress=learning_progress,
        retrieved_rules=retrieved_rules,
        course_status=course_status,
    )

    logger.info(f"资格校验完成 | eligible={eligibility.eligible} | code={eligibility.decision_code}")

    return {
        "eligibility_result": eligibility.model_dump(),
        "evidence": list(set(state.evidence + eligibility.evidence)),
    }


# ============================================================
# 节点 6: 生成处理建议
# ============================================================
async def generate_recommendation(state: AgentState) -> Dict[str, Any]:
    """
    节点 6: 生成处理建议
    综合资格校验结果和 LLM 判断生成最终建议
    """
    eligibility = state.eligibility_result or {}

    # 尝试使用 LLM 生成建议
    llm = get_llm_port()
    if llm and state.retrieved_rules:
        try:
            from app.agent.prompts import recommend_messages, RecommendOutput

            messages = recommend_messages(
                intent=state.intent.value if state.intent else "OTHER",
                reason_code=state.reason_code.value if state.reason_code else "GENERAL",
                order_snapshot=state.order_snapshot,
                learning_progress=state.learning_progress,
                retrieved_rules=state.retrieved_rules,
            )

            response = await llm.chat_with_structured_output(
                messages=messages,
                response_schema=RecommendOutput.model_json_schema(),
            )

            data = json.loads(response.content)
            decision = DecisionEnum(data.get("decision", "NEED_MORE_INFORMATION"))
            risk_hints = state.risk_hints + data.get("risk_hints", [])
            rule_citations = list(set(state.rule_citations + data.get("rule_citations", [])))

            budget = state.budget.copy()
            budget["used_model_calls"] = budget.get("used_model_calls", 0) + 1

            logger.info(f"LLM 决策建议 | decision={decision}")

            return {
                "decision": decision,
                "risk_hints": risk_hints,
                "rule_citations": rule_citations,
                "budget": budget,
            }

        except Exception as e:
            logger.warning(f"LLM 决策建议失败，使用规则决策: {e}")

    # 回退到规则决策
    return _rule_based_recommend(state, eligibility)


def _rule_based_recommend(state: AgentState, eligibility: dict) -> Dict[str, Any]:
    """基于规则的决策回退"""
    if eligibility.get("approval_required"):
        decision = DecisionEnum.WAIT_FOR_APPROVAL
    elif eligibility.get("eligible"):
        decision = DecisionEnum.REFUND_RECOMMENDED
    else:
        decision = DecisionEnum.REFUND_REJECTED

    return {"decision": decision}


# ============================================================
# 节点 7: 风险检查
# ============================================================
async def risk_gate(state: AgentState) -> Dict[str, Any]:
    """
    节点 7: 风险检查
    文档 5.3:
      - 权限失败 -> 立即终止
      - 规则冲突 -> 人工审批
      - Token 超预算 -> 降级
    """
    risk_hints = state.risk_hints.copy()
    errors = state.errors.copy()
    decision = state.decision or DecisionEnum.NEED_MORE_INFORMATION

    # 检查是否有权限错误 -> 立即终止
    permission_errors = [e for e in errors if "PERMISSION_DENIED" in e]
    if permission_errors:
        logger.warning("检测到权限错误，终止处理")
        return {
            "decision": DecisionEnum.REFUND_REJECTED,
            "risk_hints": risk_hints + ["权限验证失败"],
        }

    # 检查规则冲突 -> 人工审批
    if "存在冲突规则" in " ".join(risk_hints):
        return {
            "decision": DecisionEnum.WAIT_FOR_APPROVAL,
            "risk_hints": risk_hints,
        }

    # 检查资格结果中的审批需求
    eligibility = state.eligibility_result or {}
    if eligibility.get("approval_required"):
        return {
            "decision": DecisionEnum.WAIT_FOR_APPROVAL,
            "risk_hints": risk_hints + ["需人工审批"],
        }

    # 检查预算
    budget = state.budget
    if budget.get("used_model_calls", 0) >= budget.get("max_model_calls", 10):
        risk_hints.append("模型调用次数已达上限")
        logger.warning("Token 超预算，降级处理")

    return {
        "decision": decision,
        "risk_hints": risk_hints,
    }
