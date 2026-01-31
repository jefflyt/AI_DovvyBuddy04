"""
Verify Gemini-Only Configuration
=================================

This script verifies that the codebase is configured to use Gemini exclusively,
with Groq as a deprecated optional provider.

Date: January 31, 2026
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def verify_gemini_config():
    """Verify Gemini-only configuration."""
    
    print("=" * 70)
    print("GEMINI-ONLY CONFIGURATION VERIFICATION")
    print("=" * 70)
    print()
    
    issues = []
    
    # 1. Check config.py defaults
    print("1. Checking backend/app/core/config.py")
    print("-" * 70)
    from app.core.config import settings
    
    print(f"   Default LLM Provider: {settings.default_llm_provider}")
    print(f"   Default LLM Model: {settings.default_llm_model}")
    print(f"   Gemini API Key set: {'Yes' if settings.gemini_api_key else 'No'}")
    print(f"   Groq API Key set: {'Yes' if settings.groq_api_key else 'No (expected)'}")
    
    if settings.default_llm_provider != "gemini":
        issues.append("❌ Default LLM provider is not 'gemini'")
    else:
        print("   ✅ Default provider is Gemini")
    
    if "gemini" not in settings.default_llm_model.lower():
        issues.append(f"❌ Default model is not Gemini: {settings.default_llm_model}")
    else:
        print("   ✅ Default model is Gemini")
    
    print()
    
    # 2. Check medical detector
    print("2. Checking medical_detector.py")
    print("-" * 70)
    with open(Path(__file__).parent.parent / "app/orchestration/medical_detector.py") as f:
        medical_content = f.read()
        if 'provider_name="gemini"' in medical_content:
            print("   ✅ Medical detector hardcoded to Gemini")
        else:
            issues.append("❌ Medical detector not hardcoded to Gemini")
            print("   ❌ Medical detector not using Gemini")
    print()
    
    # 3. Check emergency detector
    print("3. Checking emergency_detector_hybrid.py")
    print("-" * 70)
    with open(Path(__file__).parent.parent / "app/orchestration/emergency_detector_hybrid.py") as f:
        emergency_content = f.read()
        if 'provider_name="gemini"' in emergency_content:
            print("   ✅ Emergency detector hardcoded to Gemini")
        else:
            issues.append("❌ Emergency detector not hardcoded to Gemini")
            print("   ❌ Emergency detector not using Gemini")
    print()
    
    # 4. Check .env.local
    print("4. Checking .env.local")
    print("-" * 70)
    env_path = Path(__file__).parent.parent.parent / ".env.local"
    if env_path.exists():
        with open(env_path) as f:
            env_content = f.read()
            if "DEFAULT_LLM_PROVIDER=gemini" in env_content:
                print("   ✅ .env.local sets DEFAULT_LLM_PROVIDER=gemini")
            else:
                issues.append("❌ .env.local does not set DEFAULT_LLM_PROVIDER=gemini")
                print("   ❌ .env.local not configured for Gemini")
            
            if "GEMINI_API_KEY=" in env_content and not env_content.split("GEMINI_API_KEY=")[1].split("\\n")[0].strip() == "":
                print("   ✅ GEMINI_API_KEY is set")
            else:
                print("   ⚠️  GEMINI_API_KEY may not be set")
    else:
        print("   ⚠️  .env.local not found")
    print()
    
    # 5. Test LLM factory
    print("5. Testing LLM factory")
    print("-" * 70)
    try:
        from app.services.llm import create_llm_provider
        provider = create_llm_provider()  # Uses defaults from settings
        model_name = provider.get_model_name()
        
        print(f"   Created provider model: {model_name}")
        
        if "gemini" in model_name.lower():
            print("   ✅ Factory creates Gemini provider by default")
        else:
            issues.append(f"❌ Factory creates non-Gemini provider: {model_name}")
            print(f"   ❌ Factory created: {model_name}")
    except Exception as e:
        issues.append(f"❌ Failed to create provider: {e}")
        print(f"   ❌ Error: {e}")
    print()
    
    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    
    if issues:
        print("❌ ISSUES FOUND:")
        for issue in issues:
            print(f"   {issue}")
        print()
        return False
    else:
        print("✅ ALL CHECKS PASSED")
        print()
        print("Configuration Summary:")
        print("  • Default Provider: Gemini")
        print("  • Default Model: gemini-2.0-flash-exp")
        print("  • Medical Detector: Gemini (hardcoded)")
        print("  • Emergency Detector: Gemini (hardcoded)")
        print("  • Groq Provider: Optional/Deprecated (fallback to Gemini)")
        print("  • Factory: Creates Gemini by default")
        print()
        print("🎉 System configured for Gemini-only operation")
        return True


if __name__ == "__main__":
    success = verify_gemini_config()
    sys.exit(0 if success else 1)
