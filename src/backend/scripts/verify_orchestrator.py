import asyncio
import logging
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.orchestration.gemini_orchestrator import GeminiOrchestrator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def verify_routing():
    print("Initializing GeminiOrchestrator...")
    try:
        orchestrator = GeminiOrchestrator()
    except Exception as e:
        print(f"Failed to initialize orchestrator: {e}")
        return

    test_cases = [
        {
            "query": "I want to go diving in Bali next month.",
            "expected": "trip_planner"
        },
        {
            "query": "What is the maximum depth for Open Water divers?",
            "expected": "knowledge_base"
        },
        {
            "query": "Is it safe to fly after diving?",
            "expected": "knowledge_base"
        },
        {
            "query": "Can you recommend a dive shop in Tioman?",
            "expected": "trip_planner"
        }
    ]

    print("\nStarting Verification Tests...")
    print("-" * 50)
    
    passed = 0
    
    for test in test_cases:
        query = test["query"]
        expected = test["expected"]
        
        print(f"\nQuery: '{query}'")
        try:
            # Empty history for simplicity
            result = await orchestrator.route_request(query, history=[])
            target = result.get("target_agent")
            params = result.get("parameters")
            
            print(f"Result: {target}")
            print(f"Params: {params}")
            
            if target == expected:
                print("✅ PASS")
                passed += 1
            else:
                print(f"❌ FAIL (Expected {expected})")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")

    print("-" * 50)
    print(f"\nVerification Complete: {passed}/{len(test_cases)} Passed")

if __name__ == "__main__":
    asyncio.run(verify_routing())
