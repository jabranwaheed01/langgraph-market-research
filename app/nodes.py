
from app.llm import get_llm
from datetime import datetime


def _ask(prompt: str) -> str:
    print(
        f"\n[{datetime.now():%H:%M:%S}] Ollama request started...",
        flush=True,
    )

    response = get_llm().invoke(prompt)

    print(
        f"[{datetime.now():%H:%M:%S}] Ollama response received.",
        flush=True,
    )
    return str(response.content).strip()


def company_research_node(state: dict) -> dict:
    company = state["company"]

    result = _ask(f"""
Research the company: {company}

Cover:
- Company overview and history
- Main products and services
- Target customers and business model
- Revenue sources and geographic presence
- Major strengths and challenges

Use clear headings. Do not invent facts.
Mark unavailable information as not verified.
""")

    return {"company_research": result}


def competitor_research_node(state: dict) -> dict:
    result = _ask(f"""
Company: {state["company"]}

Company research:
{state["company_research"]}

Identify relevant competitors, their products, target customers,
strengths, weaknesses, and competitive differences.

Use meaningful comparisons. Do not invent exact figures.
Clearly mark uncertain information.
""")

    return {"competitor_research": result}


def market_trends_node(state: dict) -> dict:
    result = _ask(f"""
Analyze market trends relevant to {state["company"]}.

Company research:
{state["company_research"]}

Competitor research:
{state["competitor_research"]}

Cover industry changes, customer preferences, technology,
opportunities, risks, and likely future developments.

Distinguish general analysis from verified facts.
Do not invent statistics or sources.
""")

    return {"market_trends": result}


def data_analysis_node(state: dict) -> dict:
    result = _ask(f"""
Prepare a structured business analysis for {state["company"]}.

Company research:
{state["company_research"]}

Competitor research:
{state["competitor_research"]}

Market trends:
{state["market_trends"]}

Extract available quantitative information, compare findings,
identify evidence gaps, and explain important limitations.

Never fabricate statistics or financial figures.
Clearly identify information that could not be verified.
""")

    return {"data_analysis": result}


def strategy_node(state: dict) -> dict:
    result = _ask(f"""
Develop practical strategic recommendations for {state["company"]}.

Company research:
{state["company_research"]}

Competitor research:
{state["competitor_research"]}

Market trends:
{state["market_trends"]}

Data analysis:
{state["data_analysis"]}

Provide:
1. Strategic priorities
2. Growth opportunities
3. Competitive improvements
4. Risks and mitigation
5. Suggested next steps

Explain the reasoning behind each recommendation.
Avoid unsupported claims and unrealistic suggestions.
""")

    return {"strategy": result}


def report_writer_node(state: dict) -> dict:
    result = _ask(f"""
Write a professional market research report about {state["company"]}.

Use the following research findings:

COMPANY RESEARCH:
{state["company_research"]}

COMPETITOR RESEARCH:
{state["competitor_research"]}

MARKET TRENDS:
{state["market_trends"]}

DATA ANALYSIS:
{state["data_analysis"]}

STRATEGY:
{state["strategy"]}

REQUIRED REPORT STRUCTURE:
1. Executive Summary
2. Company Overview
3. Competitor Analysis
4. Market Trends
5. Data Analysis and Limitations
6. Strategic Recommendations
7. Conclusion

IMPORTANT REPORT RULES:
- Write each section exactly once.
- Include only one Strategic Recommendations section.
- Do not repeat the same recommendations in multiple sections.
- Group related recommendations under clear subheadings.
- Include meaningful competitor comparisons where supported
  by the available research.
- Do not present unverified statistics as established facts.
- Do not invent facts, financial figures, sources, or citations.
- Clearly disclose important data limitations.
- End with one concise conclusion.
- Do not include QA decisions such as APPROVED or
  REVISION_REQUIRED anywhere inside the report.
- Return only the complete report.
""")

    return {"report": result}


def qa_review_node(state: dict) -> dict:
    report = state.get("report", "").strip()

    if len(report) < 600:
        feedback = (
            "REVISION_REQUIRED\n"
            "The report is too short or incomplete. Review the required "
            "sections, competitor comparisons, market trends, data "
            "limitations, recommendations, and conclusion. Return a "
            "complete report without repeated sections."
        )

        print("\n--- QA REVIEW FEEDBACK ---\n", feedback, flush=True)
        return {"qa_feedback": feedback}

    result = _ask(f"""
Review the following market research report for {state["company"]}.

REPORT:
{report}

Evaluate these points:
- Are all seven required sections present and complete?
- Are competitor names and comparisons meaningful?
- Are market trends, opportunities, and risks discussed?
- Are data limitations and unverified figures disclosed?
- Are recommendations practical, relevant, and supported?
- Are any sections or recommendations unnecessarily repeated?
- Are there unsupported or potentially inaccurate claims?
- Does the report end cleanly with a conclusion?

Do not demand fabricated statistics, facts, or sources.
Do not reject a report merely because unavailable information
has been clearly identified as unverified.

If the report is complete and acceptable, the FIRST line must be:
APPROVED

Otherwise, the FIRST line must be:
REVISION_REQUIRED

After the first line, briefly explain the review findings.
Return QA feedback only. Do not rewrite the report here.
""")

    result = result.strip()

    # Normalize the first line so graph routing can read the decision.
    first_line = result.splitlines()[0].strip().upper() if result else ""

    if first_line.startswith("APPROVED"):
        feedback = "APPROVED\n" + "\n".join(result.splitlines()[1:]).strip()
    elif first_line.startswith("REVISION_REQUIRED"):
        feedback = (
            "REVISION_REQUIRED\n"
            + "\n".join(result.splitlines()[1:]).strip()
        )
    else:
        feedback = (
            "REVISION_REQUIRED\n"
            "The QA response did not contain a valid decision on its first "
            "line. Review the report for completeness, repetition, and "
            "unsupported claims."
        )

    print("\n--- QA REVIEW FEEDBACK ---\n", feedback, flush=True)
    return {"qa_feedback": feedback}


def qa_decision(state: dict) -> str:
    feedback = state.get("qa_feedback", "").strip().upper()

    if feedback.startswith("APPROVED"):
        return "approved"

    if state.get("revision_count", 0) < 2:
        return "revise"

    return "finish"


def revise_report_node(state: dict) -> dict:
    revised_report = _ask(f"""
Revise the market research report for {state["company"]}.

CURRENT REPORT:
{state["report"]}

QA FEEDBACK:
{state["qa_feedback"]}

Return the complete revised report, not a list of changes.

Required sections:
1. Executive Summary
2. Company Overview
3. Competitor Analysis
4. Market Trends
5. Data Analysis and Limitations
6. Strategic Recommendations
7. Conclusion

Revision rules:
- Write each section exactly once.
- Include one Strategic Recommendations section only.
- Remove repeated recommendations and duplicate conclusions.
- Address the QA feedback.
- Preserve important limitations and uncertainty.
- Do not invent facts, statistics, or sources.
- Do not include APPROVED or REVISION_REQUIRED in the report.
- Return only the revised report.
""")

    return {
        "report": revised_report,
        "revision_count": state.get("revision_count", 0) + 1,
    }
