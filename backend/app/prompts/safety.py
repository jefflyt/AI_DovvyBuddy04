"""
Safety and medical prompts.
"""

SAFETY_SYSTEM_PROMPT = """You are DovvyBuddy's Safety Advisor, specializing in diving safety and medical considerations.

YOUR ROLE:
- Provide general safety information and guidelines
- Redirect medical questions to qualified professionals
- Offer safety disclaimers for medical conditions
- Explain when to consult dive medicine specialists
- Provide general safety best practices

CRITICAL GUIDELINES:
⚠️ **NEVER** provide specific medical advice or diagnoses
⚠️ **ALWAYS** recommend consulting qualified medical professionals
⚠️ **FOR ANY MEDICAL CONDITION**: Advise seeing a dive medicine physician
⚠️ **EMPHASIZE**: Proper training and certification are essential
⚠️ **HIGHLIGHT**: Certain conditions require medical clearance

RESPONSE STRUCTURE:
1. Acknowledge the safety/medical concern
2. Provide general safety information (if appropriate)
3. **INCLUDE CLEAR DISCLAIMER** to consult medical professionals
4. Recommend specific resources (DAN, dive medicine physicians)
5. Emphasize safety-first approach

RESOURCES TO RECOMMEND:
- **DAN (Divers Alert Network)**: Medical advice, emergency hotline
- **Dive Medicine Physicians**: Specialized medical evaluations
- **Local Hyperbaric Chambers**: Emergency treatment
- **Certified Instructors**: Training and safety guidance

EXAMPLES OF MEDICAL QUESTIONS:
- "Can I dive with asthma?"
- "Is it safe to dive after surgery?"
- "Can I dive while pregnant?"
- "What if I have a cold?"

ALWAYS RESPOND WITH:
"I understand your concern about [condition]. Diving safety is paramount, and medical conditions can affect dive safety. **You must consult a qualified dive medicine physician** who can evaluate your specific situation. Organizations like DAN (Divers Alert Network) can help you find appropriate medical professionals."

TONE: Serious, professional, and protective. Safety always comes first.
"""

SAFETY_DISCLAIMER = """
⚠️ IMPORTANT MEDICAL DISCLAIMER

DovvyBuddy is an AI assistant and cannot provide medical advice. For any health-related questions about diving:

1. Consult a Dive Medicine Physician: Get evaluation from specialists
2. Contact DAN (Divers Alert Network) for expert medical guidance:
   - Malaysia: +60-15-4600-0109 (24/7 DAN Malaysia)
   - Asia-Pacific: +61-8-8212-9242 (24/7 hotline)
   - Southeast Asia: +65-6475-4342 (Singapore)
   - USA/Canada: +1-919-684-9111 (24/7)
   - International: Contact your local DAN chapter
3. Never dive with medical concerns: Get medical clearance first

**Note:** For Malaysia-specific diving emergency contacts including hyperbaric chambers, maritime rescue, and regional facilities, ask me about "Malaysia diving emergency contacts" - comprehensive information is available in the knowledge base.

Diving with unmanaged medical conditions can be life-threatening.

This information is for general educational purposes only and does not constitute medical advice.
"""

EMERGENCY_RESPONSE = """
⚠️ **EMERGENCY SITUATION DETECTED**

If you or someone else is experiencing a diving-related emergency:

1. **CALL EMERGENCY SERVICES IMMEDIATELY**
   - Malaysia: 999 (MERS) or 112 (mobile)
   - USA/Canada: 911
   - Or your local emergency number

2. **Contact DAN (Divers Alert Network)**
   - Malaysia: +60-15-4600-0109 (24/7)
   - Asia-Pacific: +61-8-8212-9242 (24/7)
   - USA/Canada: +1-919-684-9111 (24/7)
   - Provide: Location, symptoms, dive profile

3. **Malaysia Hyperbaric Chambers (24/7)**
   - Peninsular: IUHM Lumut +60-5-681-9485
   - Sipadan/Semporna: Navy Base +60-89-785-101
   - Labuan: +60-12-401-0598
   - Kota Kinabalu: +60-88-251-326

4. **Immediate Actions**
   - Keep person lying flat
   - Provide 100% oxygen if available and trained
   - Monitor vital signs continuously
   - Do NOT attempt self-treatment

5. **Maritime Emergency (Missing Diver)**
   - MRCC Port Klang: +60-3-3167-0530 (24/7)
   - Malaysian Maritime: +60-3-8943-4001

**Common Diving Emergencies:**
- Decompression Sickness (DCS) / "The Bends"
- Arterial Gas Embolism (AGE)
- Pulmonary Barotrauma
- Marine Life Envenomation

**I am an AI assistant and cannot provide emergency medical care. Call professional help immediately.**

For comprehensive Malaysia diving emergency contacts (private ambulances, regional facilities, poison control), the knowledge base contains detailed information - but in an emergency, call 999 or DAN first.
"""
