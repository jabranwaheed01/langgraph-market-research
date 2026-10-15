
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.graph import research_graph

app = FastAPI(
    title="LangGraph AI Market Research API",
    version="1.0.0",
)


class ResearchRequest(BaseModel):
    company: str = Field(
        ...,
        min_length=1,
        description="Name of the company to research",
    )


@app.get("/")
def root():
    return {
        "status": "API is running",
        "framework": "LangGraph",
    }


@app.post("/research")
def research(request: ResearchRequest):
    company = request.company.strip()

    if not company:
        raise HTTPException(
            status_code=422,
            detail="Company name cannot be empty.",
        )

    initial_state = {
        "company": company,
        "company_research": "",
        "competitor_research": "",
        "market_trends": "",
        "data_analysis": "",
        "strategy": "",
        "report": "",
        "qa_feedback": "",
        "revision_count": 0,
        "status": "running",
        "error": "",
    }

    try:
        result = research_graph.invoke(initial_state)

        return {
            "company": result["company"],
            "status": "completed",
            "report": result["report"],
            "qa_feedback": result["qa_feedback"],
            "revision_count": result["revision_count"],
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Research failed: {str(exc)}",
        )
