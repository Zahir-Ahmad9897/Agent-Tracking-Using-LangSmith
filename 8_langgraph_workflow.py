import os
import operator
from typing import TypedDict, Annotated, List
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langsmith import traceable
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END

# --- Environment Setup ---
load_dotenv()
os.environ['LANGCHAIN_PROJECT'] = 'Deep-Content-Audit-Workflow'
base_model = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

# --- Audit Schema Definition ---
class QualityAssessment(BaseModel):
    audit_notes: str = Field(description="Comprehensive feedback on the specific dimension")
    numeric_rating: int = Field(description="Numerical score from 1 to 10", ge=1, le=10)

# Wrap the model for structured output
audit_specialist = base_model.with_structured_output(QualityAssessment)

# --- New Sample Data: The Future of Space Exploration ---
sample_content = """The Cosmic Frontier: India's Vision for Space

Space exploration has entered a new era. India, through ISRO, is now a major global player. The success of Chandrayaan-3 proved that cost-effective lunar missions are possible. However, the path forward requires more than just successful landings.

We have great talent in our space sector. Private players like Skyroot and Agnikul are changing the game. They bring agility and private investment. This is good because the government cannot do everything alone. But we need better space laws to protect these companies and our national interests.

In the future, missions to Mars (Mangalyaan-2) and the Gaganyaan human spaceflight mission will define our status. We also need to think about space debris. If we don't clean up our orbit, future missions will be impossible. Also, international collaboration with NASA and ESA is vital. We must learn and also teach.

Ultimately, space is not just about rockets. It's about data, satellites for farmers, and global connectivity. If we use space technology correctly, it will improve life on Earth for everyone. But it requires long-term planning and consistent funding from the center.
"""

# --- Audit Workflow State ---
class ContentAuditState(TypedDict, total=False):
    content: str
    linguistic_review: str
    logical_analysis: str
    strategic_feedback: str
    executive_summary: str
    aggregated_scores: Annotated[List[int], operator.add]
    final_score: float

# --- Traced Audit Nodes ---
@traceable(name="assess_linguistic_quality", tags=["audit", "linguistics"])
def assess_linguistic_quality(state: ContentAuditState):
    instruction = (
        "Analyze the linguistic quality and tone of the following text. "
        "Provide detailed audit notes and a rating.\n\n" + state["content"]
    )
    result = audit_specialist.invoke(instruction)
    return {"linguistic_review": result.audit_notes, "aggregated_scores": [result.numeric_rating]}

@traceable(name="assess_logical_coherence", tags=["audit", "logic"])
def assess_logical_coherence(state: ContentAuditState):
    instruction = (
        "Evaluate the logical flow and coherence of arguments in this text. "
        "Provide audit notes and a rating.\n\n" + state["content"]
    )
    result = audit_specialist.invoke(instruction)
    return {"logical_analysis": result.audit_notes, "aggregated_scores": [result.numeric_rating]}

@traceable(name="assess_strategic_depth", tags=["audit", "strategy"])
def assess_strategic_depth(state: ContentAuditState):
    instruction = (
        "Assess the strategic depth and vision expressed in this text. "
        "Provide audit notes and a rating.\n\n" + state["content"]
    )
    result = audit_specialist.invoke(instruction)
    return {"strategic_feedback": result.audit_notes, "aggregated_scores": [result.numeric_rating]}

@traceable(name="compile_executive_report", tags=["audit", "reporting"])
def compile_executive_report(state: ContentAuditState):
    summary_instruction = (
        "Synthesize the following audit reviews into a high-level executive report:\n\n"
        f"Linguistic Review: {state.get('linguistic_review','')}\n"
        f"Logical Analysis: {state.get('logical_analysis','')}\n"
        f"Strategic Assessment: {state.get('strategic_feedback','')}\n"
    )
    report = base_model.invoke(summary_instruction).content
    scores = state.get("aggregated_scores", [])
    average = (sum(scores) / len(scores)) if scores else 0.0
    return {"executive_summary": report, "final_score": average}

# --- Workflow Orchestration ---
def build_audit_workflow():
    builder = StateGraph(ContentAuditState)

    # Register nodes
    builder.add_node("linguistics_audit", assess_linguistic_quality)
    builder.add_node("logic_audit", assess_logical_coherence)
    builder.add_node("strategy_audit", assess_strategic_depth)
    builder.add_node("report_generation", compile_executive_report)

    # Define edges (Parallel Fan-out)
    builder.add_edge(START, "linguistics_audit")
    builder.add_edge(START, "logic_audit")
    builder.add_edge(START, "strategy_audit")

    # Fan-in (Merge)
    builder.add_edge("linguistics_audit", "report_generation")
    builder.add_edge("logic_audit", "report_generation")
    builder.add_edge("strategy_audit", "report_generation")
    builder.add_edge("report_generation", END)

    return builder.compile()

# --- Main Execution ---
if __name__ == "__main__":
    audit_engine = build_audit_workflow()
    
    print("Initiating Deep Content Audit...")
    
    audit_results = audit_engine.invoke(
        {"content": sample_content},
        config={
            "run_name": "Space-Strategy-Audit-Session",
            "tags": ["Aerospace", "Strategic-Analysis"],
            "metadata": {"content_type": "Essay", "version": "1.2"}
        }
    )

    print("\n" + "="*40)
    print("       EXECUTIVE AUDIT REPORT")
    print("="*40)
    print(f"\nFinal Quality Score: {audit_results.get('final_score', 0.0):.2f}/10")
    print("\n--- Summary ---\n")
    print(audit_results.get("executive_summary", "No summary available."))
    print("\n" + "="*40)
