#!/usr/bin/env python3
"""List available models in google-genai SDK"""
import asyncio
from google import genai

async def list_models():
    client = genai.Client(api_key="AIzaSyDhifgi1xT4BFLtT_Ko_ITWCS4PoRy7Pxg")
    
    print("Listing all available models...")
    models = await client.aio.models.list()
    
    print("\nAll models:")
    for model in models:
        print(f"  - {model.name}")
        if hasattr(model, 'supported_generation_methods'):
            print(f"    Methods: {model.supported_generation_methods}")
        print()
    
    print("\nEmbedding-capable models:")
    found_any = False
    for model in models:
        # Check if it supports embedContent
        if hasattr(model, 'supported_generation_methods') and 'embedContent' in model.supported_generation_methods:
            found_any = True
            print(f"  - {model.name}")
            print(f"    Display Name: {model.display_name if hasattr(model, 'display_name') else 'N/A'}")
            print(f"    Methods: {model.supported_generation_methods}")
            print()
    
    if not found_any:
        print("  None found! The v1beta API may not support embedding models.")

if __name__ == "__main__":
    asyncio.run(list_models())
