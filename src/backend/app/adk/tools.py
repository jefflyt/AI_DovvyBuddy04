"""Shared tool contracts for ADK-native orchestration."""

import logging
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from app.orchestration.emergency_detector_hybrid import EmergencyDetector
from app.orchestration.medical_detector import MedicalQueryDetector
from app.services.rag.pipeline import RAGPipeline

from .types import PolicyValidationResult, RagSearchResult, SafetyClassification

logger = logging.getLogger(__name__)


@dataclass
class _TurnContext:
    """In-memory per-turn context shared by tools."""

    session_id: str = ""
    message: str = ""
    history: List[Dict[str, str]] = None
    session_state: Dict[str, Any] = None
    diver_profile: Dict[str, Any] = None

    def __post_init__(self):
        if self.history is None:
            self.history = []
        if self.session_state is None:
            self.session_state = {}
        if self.diver_profile is None:
            self.diver_profile = {}


class ADKToolbox:
    """Single source of truth for ADK tool behaviors and contracts."""

    def __init__(
        self,
        rag_pipeline: Optional[RAGPipeline] = None,
        emergency_detector: Optional[EmergencyDetector] = None,
        medical_detector: Optional[MedicalQueryDetector] = None,
    ):
        self.rag_pipeline = rag_pipeline or RAGPipeline()
        self.emergency_detector = emergency_detector or EmergencyDetector()
        self.medical_detector = medical_detector or MedicalQueryDetector()

        self.turn_context = _TurnContext()
        self.last_rag_result = RagSearchResult()
        self.last_safety_classification = SafetyClassification()
        self.last_policy_validation = PolicyValidationResult()

    def reset_turn_state(self) -> None:
        """Reset mutable per-turn snapshots."""
        self.last_rag_result = RagSearchResult()
        self.last_safety_classification = SafetyClassification()
        self.last_policy_validation = PolicyValidationResult()

    def set_turn_context(
        self,
        *,
        session_id: str,
        message: str,
        history: Optional[List[Dict[str, str]]] = None,
        session_state: Optional[Dict[str, Any]] = None,
        diver_profile: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Set current turn context consumed by tools."""
        self.turn_context = _TurnContext(
            session_id=session_id,
            message=message,
            history=history or [],
            session_state=session_state or {},
            diver_profile=diver_profile or {},
        )
        self.reset_turn_state()

    async def rag_search_tool(
        self, query: str, filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Retrieve grounded context from the RAG pipeline."""
        try:
            context = await self.rag_pipeline.retrieve_context(
                query=query,
                filters=filters or {},
            )
            chunks = [result.text for result in context.results]
            citations = context.citations

            self.last_rag_result = RagSearchResult(
                chunks=chunks,
                citations=citations,
                has_data=context.has_data,
            )
            return self.last_rag_result.to_dict()
        except Exception as exc:
            logger.error("rag_search_tool failed: %s", exc, exc_info=True)
            self.last_rag_result = RagSearchResult(chunks=[], citations=[], has_data=False)
            return self.last_rag_result.to_dict()

    def session_context_tool(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Return normalized turn/session context for specialists."""
        requested_session = session_id or self.turn_context.session_id
        return {
            "session_id": requested_session,
            "history": self.turn_context.history[-10:],
            "session_state": self.turn_context.session_state,
            "diver_profile": self.turn_context.diver_profile,
        }

    async def safety_classification_tool(
        self,
        message: str,
        history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """Classify a turn as emergency, medical, or non-medical."""
        conversation_history = history if history is not None else self.turn_context.history

        try:
            is_emergency, _ = await self.emergency_detector.detect_emergency(
                message, conversation_history=conversation_history
            )
            if is_emergency:
                self.last_safety_classification = SafetyClassification(
                    classification="emergency",
                    is_emergency=True,
                    is_medical=True,
                )
                return self.last_safety_classification.to_dict()

            is_medical = await self.medical_detector.is_medical_query(message)
            self.last_safety_classification = SafetyClassification(
                classification="medical" if is_medical else "non_medical",
                is_emergency=False,
                is_medical=is_medical,
            )
            return self.last_safety_classification.to_dict()
        except Exception as exc:
            logger.error("safety_classification_tool failed: %s", exc, exc_info=True)
            self.last_safety_classification = SafetyClassification(
                classification="medical",
                is_emergency=False,
                is_medical=True,
            )
            return self.last_safety_classification.to_dict()

    def response_policy_tool(
        self,
        answer: str,
        citations: Optional[List[str]] = None,
        safety_flags: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Validate and enforce grounding/safety policy.

        Policy:
        - Factual-looking statements should include citations.
        - Medical/emergency statements are allowed but should be concise and cautious.
        """
        citations = citations or []
        safety_flags = safety_flags or self.last_safety_classification.to_dict()

        answer_text = (answer or "").strip()
        lower = answer_text.lower()
        factual_cue_terms = (
            "depth",
            "meter",
            "meters",
            "certification",
            "required",
            "recommended",
            "minimum",
            "hours",
            "days",
            "temperature",
        )
        has_numeric_claim = bool(re.search(r"\b\d+(\.\d+)?\b", lower))
        is_question = "?" in answer_text
        appears_factual = (
            len(answer_text) > 40
            and any(term in lower for term in factual_cue_terms)
            and has_numeric_claim
            and not is_question
        )
        has_citations = len(citations) > 0

        should_enforce_citation = appears_factual and not has_citations
        policy_enforced = should_enforce_citation

        result = PolicyValidationResult(
            is_allowed=True,
            policy_enforced=policy_enforced,
            reason=(
                "missing_citations_for_factual_claim"
                if should_enforce_citation
                else "policy_pass"
            ),
            should_append_uncertainty=should_enforce_citation,
        )

        # Safety mode keeps response allowed; emergency behavior is intercepted earlier.
        if safety_flags.get("is_emergency"):
            result.policy_enforced = True
            result.reason = "emergency_path"
            result.should_append_uncertainty = False

        self.last_policy_validation = result
        return result.to_dict()
