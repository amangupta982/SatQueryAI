"""
LLM synthesis interface and grounded answer generation adapter.
Supports external LLM providers (OpenAI, Gemini) when configured,
and provides a resilient local synthesis fallback based on retrieved evidence.
"""

import os
import re
import logging
from abc import ABC, abstractmethod
from typing import List, Optional

from app.rag.schemas import RAGEvidence, RAGSource

logger = logging.getLogger(__name__)

NO_INFO_MESSAGE = "I could not find sufficient information in the knowledge base to answer this question."


class LLMAdapter(ABC):
    """Abstract interface for LLM synthesis."""

    @abstractmethod
    def synthesize_answer(self, query: str, evidence: List[RAGEvidence]) -> str:
        """Generate a grounded answer based strictly on retrieved evidence."""
        pass


class LocalGroundedSynthesizer(LLMAdapter):
    """
    Resilient offline grounded synthesizer.
    Extracts the most pertinent facts directly from the retrieved domain chunks
    without hallucination and without requiring external API keys.
    """

    def synthesize_answer(self, query: str, evidence: List[RAGEvidence]) -> str:
        if not evidence:
            return NO_INFO_MESSAGE

        # Clean query tokens for keyword relevance
        query_words = set(re.findall(r"\w+", query.lower())) - {
            "what", "is", "why", "how", "the", "a", "an", "and", "or", "in", "of", "to", "for", "do", "we", "explain"
        }

        # Select the most informative paragraphs from the top evidence chunks
        collected_sentences = []
        seen_sentences = set()

        for ev in evidence:
            text = ev.text.strip()
            # Split into individual sentences or bullet lines
            lines = text.split("\n")
            for line in lines:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                # If bullet point or heading text, keep clean
                clean_line = re.sub(r"^[-*•\d.]+\s*", "", line).strip()
                if len(clean_line) < 25:
                    continue

                line_words = set(re.findall(r"\w+", clean_line.lower()))
                overlap = len(query_words.intersection(line_words))

                # Deduplication key
                norm_key = clean_line[:40].lower()
                if norm_key not in seen_sentences:
                    seen_sentences.add(norm_key)
                    collected_sentences.append((overlap, clean_line))

        if not collected_sentences:
            # Fallback to the top chunk's first paragraphs directly
            top_text = evidence[0].text.strip()
            paragraphs = [p.strip() for p in top_text.split("\n\n") if p.strip() and not p.strip().startswith("#")]
            return "\n\n".join(paragraphs[:2]) if paragraphs else top_text[:500]

        # Sort by relevance to query keywords while preserving coherence
        collected_sentences.sort(key=lambda x: x[0], reverse=True)
        top_selected = [s[1] for s in collected_sentences[:4]]

        return "\n\n".join(top_selected)


class OpenAILLMAdapter(LLMAdapter):
    """OpenAI GPT synthesis adapter."""

    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model_name = model_name

    def synthesize_answer(self, query: str, evidence: List[RAGEvidence]) -> str:
        if not evidence:
            return NO_INFO_MESSAGE
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)

            context_str = "\n\n---\n\n".join(
                [f"Source: {ev.source} (Section: {ev.section})\n{ev.text}" for ev in evidence]
            )

            system_prompt = (
                "You are the SatQuery AI Remote Sensing Domain Knowledge assistant. "
                "Answer the user's question using ONLY the provided knowledge context. "
                "If the context does not contain enough information, reply with: "
                f"'{NO_INFO_MESSAGE}'. "
                "Do not hallucinate. Clearly distinguish knowledge evidence from satellite image analysis."
            )

            user_prompt = f"Context:\n{context_str}\n\nQuestion: {query}\n\nAnswer:"

            response = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.warning(f"[RAG LLM] OpenAI call failed ({e}). Falling back to local synthesizer.")
            return LocalGroundedSynthesizer().synthesize_answer(query, evidence)


def get_llm_adapter() -> LLMAdapter:
    """Factory function to instantiate the configured LLM adapter."""
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        model = os.getenv("LLM_MODEL", "gpt-4o-mini")
        logger.info(f"[RAG LLM] Initializing OpenAI adapter with model {model}")
        return OpenAILLMAdapter(api_key=openai_key, model_name=model)

    # Clean local grounded synthesizer when no external API key is configured
    return LocalGroundedSynthesizer()
