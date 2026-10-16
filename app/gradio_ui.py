
import gradio as gr

from app.graph import research_graph


def run_research(company):
    if not company or not company.strip():
        return "Please enter a company name.", "", ""

    initial_state = {
        "company": company.strip(),
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

        return (
            result.get("report", "No report generated."),
            result.get("qa_feedback", ""),
            f"Status: Completed | Revisions: {result.get('revision_count', 0)}",
        )
    except Exception as exc:
        return "", str(exc), "Status: Failed"


with gr.Blocks(title="AI Market Research") as demo:
    gr.Markdown("# AI-Powered Market Research")
    gr.Markdown("Generate a company research report using LangGraph and Ollama.")

    company = gr.Textbox(
        label="Company Name",
        placeholder="Enter a company name.",
    )

    generate_btn = gr.Button("Generate Research", variant="primary")

    status = gr.Textbox(label="Status", interactive=False)
    report = gr.Markdown(label="Research Report")
    qa_feedback = gr.Textbox(
        label="QA Review Feedback",
        lines=8,
        interactive=False,
    )

    generate_btn.click(
        fn=run_research,
        inputs=[company],
        outputs=[report, qa_feedback, status],
    )

demo.launch(server_name="127.0.0.1", server_port=7860)
 