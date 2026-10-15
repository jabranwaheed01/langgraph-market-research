
from langgraph.graph import StateGraph, START, END

from app.state import ResearchState
from app.nodes import (
    company_research_node,
    competitor_research_node,
    market_trends_node,
    data_analysis_node,
    strategy_node,
    report_writer_node,
    qa_review_node,
    qa_decision,
    revise_report_node,
)


def build_research_graph():
    builder = StateGraph(ResearchState)

    # Register research nodes
    builder.add_node("company_research", company_research_node)
    builder.add_node("competitor_research", competitor_research_node)
    builder.add_node("market_trends", market_trends_node)
    builder.add_node("data_analysis", data_analysis_node)
    builder.add_node("strategy", strategy_node)
    builder.add_node("report_writer", report_writer_node)
    builder.add_node("qa_review", qa_review_node)
    builder.add_node("revise_report", revise_report_node)

    # Sequential research workflow
    builder.add_edge(START, "company_research")
    builder.add_edge("company_research", "competitor_research")
    builder.add_edge("competitor_research", "market_trends")
    builder.add_edge("market_trends", "data_analysis")
    builder.add_edge("data_analysis", "strategy")
    builder.add_edge("strategy", "report_writer")
    builder.add_edge("report_writer", "qa_review")

    # QA approval or revision loop
    builder.add_conditional_edges(
        "qa_review",
        qa_decision,
        {
            "approved": END,
            "revise": "revise_report",
            "finish": END,
        },
    )

    builder.add_edge("revise_report", "qa_review")

    return builder.compile()


research_graph = build_research_graph()
