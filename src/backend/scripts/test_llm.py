"""
Manual test script for LLM generation.

Usage:
    python -m scripts.test_llm "Explain buoyancy control"
    python -m scripts.test_llm --provider groq "Explain buoyancy control"
    python -m scripts.test_llm --provider gemini "Explain buoyancy control"
"""

import asyncio
import sys
import os
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.llm import create_llm_provider, LLMMessage


async def main():
    """Test LLM generation."""
    parser = argparse.ArgumentParser(description="Test LLM generation")
    parser.add_argument("prompt", help="The prompt to send to the LLM")
    parser.add_argument(
        "--provider",
        choices=["groq", "gemini"],
        default=None,
        help="LLM provider (default: from config)",
    )
    parser.add_argument(
        "--temperature", type=float, default=0.7, help="Temperature (default: 0.7)"
    )
    parser.add_argument(
        "--max-tokens", type=int, default=500, help="Max tokens (default: 500)"
    )

    args = parser.parse_args()

    print(f"\n=== Testing LLM Generation ===")
    print(f"Prompt: {args.prompt}")
    print(f"Provider: {args.provider or '(from config)'}")
    print(f"Temperature: {args.temperature}")
    print(f"Max tokens: {args.max_tokens}\n")

    # Create provider
    try:
        provider = create_llm_provider(provider_name=args.provider)
        print(f"Provider: {provider.__class__.__name__}")
        print(f"Model: {provider.get_model_name()}\n")
    except Exception as e:
        print(f"Error creating provider: {e}")
        print("\nMake sure API keys are set in your environment:")
        print("  - GROQ_API_KEY (for Groq)")
        print("  - GEMINI_API_KEY (for Gemini)")
        sys.exit(1)

    # Create messages
    messages = [
        LLMMessage(role="system", content="You are a helpful diving assistant."),
        LLMMessage(role="user", content=args.prompt),
    ]

    # Generate response
    try:
        print("Generating response...\n")
        response = await provider.generate(
            messages, temperature=args.temperature, max_tokens=args.max_tokens
        )

        print("=== Response ===")
        print(response.content)
        print("\n=== Metadata ===")
        print(f"Model: {response.model}")
        print(f"Tokens used: {response.tokens_used}")
        print(f"Finish reason: {response.finish_reason}")

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
