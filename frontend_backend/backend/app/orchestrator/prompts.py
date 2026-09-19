"""
Prompts and grounded answer synthesis templates for the SatQuery Orchestrator.

Ensures that the final answer is:
- Grounded strictly in the outputs returned by the executed agents.
- Clear and professional in tone.
- Separates image evidence from knowledge base evidence.
- Explains any discrepancies between multiple agents if detected.
"""

from typing import List, Dict, Any, Optional

CLARIFICATION_AMBIGUOUS_QUERY = """What would you like to analyze in your satellite imagery?

You can ask SatQuery AI for:
• **Visual Question Answering**: "What is present in this image?", "Describe this landscape."
• **Object Grounding & Counting**: "Find all buildings", "Locate the runways", "How many structures are visible?"
• **Temporal Change Detection**: "What changed between 2022 and 2026?", "Show new construction."
• **Optical-SAR Multimodal Fusion**: "What does SAR show that optical does not?", "Analyze flood extent under cloud cover."
• **Area & Land-Cover Measurement**: "What percentage of the area is water?", "Calculate the urban coverage area."
• **Remote Sensing Domain Knowledge**: "What is Sentinel-1?", "Explain the difference between optical and SAR."
"""

MISSING_TEMPORAL_IMAGES_MESSAGE = (
    "Change detection requires two spatially corresponding satellite images from different dates "
    "(e.g., baseline T1 and follow-up T2). Please select or upload both temporal scenes."
)

MISSING_IMAGE_MESSAGE = (
    "The requested analysis requires at least one satellite image. "
    "Please upload an image or choose one of the preset constellation scenes above."
)

MISSING_SAR_MESSAGE = (
    "Joint Optical-SAR analysis benefits from both optical reflectance and microwave SAR backscatter. "
    "Analyzing using the available scene mode."
)


def build_synthesis_prompt(
    query: str,
    intent: str,
    agent_results: List[Dict[str, Any]]
) -> str:
    """Builds a structured prompt for LLM synthesis when an LLM adapter is used."""
    findings_str = ""
    for r in agent_results:
        agent_name = r.get("agent_name", "Unknown Agent")
        status = r.get("status", "unknown")
        answer = r.get("answer", "No answer provided")
        confidence = r.get("confidence")
        conf_str = f" (Confidence: {int(confidence * 100)}%)" if confidence else ""
        findings_str += f"\n- [{agent_name}] Status: {status}{conf_str}\n  Finding: {answer}\n"
        if r.get("measurements"):
            findings_str += f"  Measurements: {r['measurements']}\n"

    prompt = (
        f"You are the SatQuery AI Central Orchestrator.\n"
        f"User Query: \"{query}\"\n"
        f"Detected Intent: {intent}\n\n"
        f"Agent Findings:\n{findings_str}\n\n"
        f"Instructions:\n"
        f"1. Generate a coherent, grounded final answer directly answering the user's query.\n"
        f"2. DO NOT invent, hallucinate, or extrapolate numbers not present in the agent findings.\n"
        f"3. Explicitly cite which agent(s) provided the observations.\n"
        f"4. Clearly distinguish physical imagery findings from domain knowledge facts.\n"
        f"5. If an agent reported failure or partial results, state that transparently.\n"
    )
    return prompt
