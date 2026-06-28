"""
LangGraph 工作流图
文档 5.2: 节点流程
  load_task -> classify_and_extract -> validate_required_fields ->
  query_business_data -> retrieve_rules -> check_eligibility ->
  generate_recommendation -> validate_recommendation -> risk_gate ->
  complete / wait_for_approval / fail

注意: 不使用开放式无限 ReAct 循环
"""
from langgraph.graph import StateGraph, END
from app.agent.state import AgentState
from app.agent.nodes import (
    classify_and_extract,
    validate_required_fields,
    query_business_data,
    retrieve_rules,
    check_eligibility,
    generate_recommendation,
    risk_gate,
)


def create_workflow() -> StateGraph:
    """创建 LangGraph 工作流"""

    # 创建状态图
    workflow = StateGraph(AgentState)

    # 添加节点（文档 5.2 流程）
    workflow.add_node("classify_and_extract", classify_and_extract)
    workflow.add_node("validate_required_fields", validate_required_fields)
    workflow.add_node("query_business_data", query_business_data)
    workflow.add_node("retrieve_rules", retrieve_rules)
    workflow.add_node("check_eligibility", check_eligibility)
    workflow.add_node("generate_recommendation", generate_recommendation)
    workflow.add_node("risk_gate", risk_gate)

    # 设置入口点
    workflow.set_entry_point("classify_and_extract")

    # 添加边 - 线性流程
    workflow.add_edge("classify_and_extract", "validate_required_fields")
    workflow.add_edge("validate_required_fields", "query_business_data")
    workflow.add_edge("query_business_data", "retrieve_rules")
    workflow.add_edge("retrieve_rules", "check_eligibility")
    workflow.add_edge("check_eligibility", "generate_recommendation")
    workflow.add_edge("generate_recommendation", "risk_gate")
    workflow.add_edge("risk_gate", END)

    return workflow


# 创建全局工作流实例
graph = create_workflow()
