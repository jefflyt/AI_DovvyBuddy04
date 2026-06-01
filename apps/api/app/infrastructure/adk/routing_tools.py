"""Shared routing tool definitions for ADK orchestrators."""

from typing import Any, Dict, Optional


def make_route_trip_specialist() -> callable:
    """Create a route_trip_specialist tool function for ADK function calling."""

    def route_trip_specialist(
        query: str,
        reason: str = "",
        location: Optional[str] = None,
    ) -> Dict[str, Any]:
        return {
            "route": "trip_specialist",
            "query": query,
            "reason": reason,
            "location": location,
        }

    return route_trip_specialist


def make_route_certification_specialist() -> callable:
    """Create a route_certification_specialist tool function."""

    def route_certification_specialist(
        query: str,
        reason: str = "",
    ) -> Dict[str, Any]:
        return {
            "route": "certification_specialist",
            "query": query,
            "reason": reason,
        }

    return route_certification_specialist


def make_route_general_retrieval_specialist() -> callable:
    """Create a route_general_retrieval_specialist tool function."""

    def route_general_retrieval_specialist(
        query: str,
        reason: str = "",
    ) -> Dict[str, Any]:
        return {
            "route": "general_retrieval_specialist",
            "query": query,
            "reason": reason,
        }

    return route_general_retrieval_specialist


def make_route_safety_specialist() -> callable:
    """Create a route_safety_specialist tool function."""

    def route_safety_specialist(
        query: str,
        reason: str = "",
    ) -> Dict[str, Any]:
        return {
            "route": "safety_specialist",
            "query": query,
            "reason": reason,
        }

    return route_safety_specialist


# Route tool name → specialist name mapping used by both orchestrators.
ROUTE_TOOL_TO_SPECIALIST = {
    "route_trip_specialist": "trip_specialist",
    "route_certification_specialist": "certification_specialist",
    "route_safety_specialist": "safety_specialist",
    "route_general_retrieval_specialist": "general_retrieval_specialist",
}
