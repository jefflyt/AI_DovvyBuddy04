"""Typed contracts for ADK-native orchestration."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional


RouteName = Literal[
    "trip_specialist",
    "certification_specialist",
    "general_retrieval_specialist",
    "safety_specialist",
]

SafetyLabel = Literal["emergency", "medical", "non_medical"]


@dataclass
class RouteDecision:
    """Coordinator route decision for a single turn."""

    route: RouteName
    reason: str = ""
    confidence: float = 0.8
    parameters: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "route": self.route,
            "reason": self.reason,
            "confidence": self.confidence,
            "parameters": self.parameters,
        }


@dataclass
class RagSearchResult:
    """RAG tool result contract."""

    chunks: List[str] = field(default_factory=list)
    citations: List[str] = field(default_factory=list)
    has_data: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunks": self.chunks,
            "citations": self.citations,
            "has_data": self.has_data,
        }


@dataclass
class SafetyClassification:
    """Safety classifier output contract."""

    classification: SafetyLabel = "non_medical"
    is_emergency: bool = False
    is_medical: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "classification": self.classification,
            "is_emergency": self.is_emergency,
            "is_medical": self.is_medical,
        }


@dataclass
class PolicyValidationResult:
    """Response policy validation contract."""

    is_allowed: bool = True
    policy_enforced: bool = False
    reason: str = ""
    should_append_uncertainty: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_allowed": self.is_allowed,
            "policy_enforced": self.policy_enforced,
            "reason": self.reason,
            "should_append_uncertainty": self.should_append_uncertainty,
        }


@dataclass
class AgentTurnTrace:
    """Structured per-turn execution trace."""

    tools_called: List[str] = field(default_factory=list)
    citations_count: int = 0
    safety_label: SafetyLabel = "non_medical"
    route: Optional[RouteName] = None
    latency_ms: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tools_called": self.tools_called,
            "citations_count": self.citations_count,
            "safety_label": self.safety_label,
            "route": self.route,
            "latency_ms": self.latency_ms,
        }


@dataclass
class NativeTurnResult:
    """Full turn output for ADK-native graph orchestration."""

    message: str
    route_decision: RouteDecision
    citations: List[str] = field(default_factory=list)
    safety_classification: SafetyClassification = field(
        default_factory=SafetyClassification
    )
    policy_validation: PolicyValidationResult = field(
        default_factory=PolicyValidationResult
    )
    state_updates: Dict[str, Any] = field(default_factory=dict)
    trace: AgentTurnTrace = field(default_factory=AgentTurnTrace)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "message": self.message,
            "route_decision": self.route_decision.to_dict(),
            "citations": self.citations,
            "safety_classification": self.safety_classification.to_dict(),
            "policy_validation": self.policy_validation.to_dict(),
            "state_updates": self.state_updates,
            "trace": self.trace.to_dict(),
        }
