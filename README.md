# DovvyBuddy 🤿

**Your AI companion for scuba diving certification and trip planning**

Making diving more accessible through intelligent, conversational guidance — because everyone deserves to explore the underwater world with confidence.

> 👨‍💻 **Developers:** See [README.DEV.md](./README.DEV.md) for technical documentation and setup instructions.

---

## 🌊 What is DovvyBuddy?

DovvyBuddy is an AI-powered diving assistant that helps both aspiring and experienced divers make informed decisions about their diving journey. Whether you're nervous about your first Open Water course or planning your next dive trip, DovvyBuddy provides friendly, accurate guidance powered by curated diving knowledge.

### What We Help With

🎓 **Certification Guidance**  
Navigate the world of diving certifications (PADI, SSI) with clarity. Understand which course is right for you, what to expect, and how to progress through different levels.

💙 **Fear Normalization**  
Nervous about diving? You're not alone. Get reassuring, educational support that acknowledges common fears while providing factual information to help you feel prepared.

🗺️ **Trip Planning**  
Discover dive sites that match your certification level and interests. From tropical reefs to dramatic wrecks, find your next underwater adventure.

🤝 **Professional Connections**  
When you're ready, we'll connect you with partner dive shops and certified instructors who can help turn your diving goals into reality.

### Our Guiding Principle

**Information, Not Instruction** — DovvyBuddy provides educational content and recommendations, but always redirects to certified professionals for training, medical advice, or safety-critical decisions. We're here to inform and inspire, not to replace proper instruction.

---

## ✨ Key Features

### Intelligent Conversation

Chat naturally about your diving questions and goals. DovvyBuddy understands context and provides personalized responses based on your certification level and experience.

### Curated Knowledge Base

Responses are grounded in carefully curated content about:

- Certification programs (PADI, SSI)
- Dive destinations worldwide
- Safety procedures and best practices
- Equipment and preparation guidance

### Multi-Agent Intelligence

Behind the scenes, specialized AI agents work together:

- **Certification Expert** — Knows the ins and outs of diving courses
- **Trip Advisor** — Matches you with suitable dive sites
- **Safety Guide** — Provides emergency contacts and safety protocols
- **Content Specialist** — Retrieves relevant information from our knowledge base

### Seamless Lead Capture

When you're ready to take action, we make it easy to connect with dive shops and instructors who can help you achieve your diving goals.

---

## 🚀 Current Status

**Development Stage:** Active Development (V0.5 → V1.0)

### ✅ What's Working

- Multi-agent RAG system with specialized diving knowledge
- Python FastAPI backend with async operations
- PostgreSQL database with vector embeddings
- Intelligent content retrieval and response generation
- Session management and conversation continuity

### 🚧 In Progress

- Web chat interface (React/Next.js)
- Lead capture and email delivery
- Landing page with feature showcase
- Production deployment and monitoring

### 🔮 Coming Soon

- Telegram bot interface
- User authentication and profiles
- Conversation history and bookmarking
- Enhanced trip planning tools

---

## 🎯 Use Cases

### For Aspiring Divers

_"I'm interested in learning to dive but I'm nervous about the water. What should I expect from an Open Water course?"_

Get honest, reassuring information about what training involves, common fears, and how instructors help students succeed.

### For Certification Progression

_"I'm PADI Open Water certified. What are my options for advancing my skills?"_

Explore Advanced Open Water, specialties, and other certifications. Understand prerequisites, costs, and what you'll learn.

### For Trip Planning

_"I'm Open Water certified and want to try my first dive trip. Where should I go in Southeast Asia?"_

Receive recommendations for beginner-friendly sites with calm conditions, good visibility, and professional dive operations.

### For Safety Questions

_"What should I do if I experience ear pain while descending?"_

Access proper equalization techniques, understand when to abort a dive, and learn when to consult a doctor — with clear boundaries about what requires professional medical advice.

---

## 🏗️ How It Works

### The Technology

DovvyBuddy combines several cutting-edge technologies to deliver intelligent responses:

**RAG (Retrieval-Augmented Generation)**  
Instead of making things up, the AI retrieves relevant information from our curated knowledge base before responding. This ensures accuracy and reduces hallucinations.

**Vector Embeddings**  
Diving content is converted into mathematical representations that capture semantic meaning. This allows the system to understand concepts, not just match keywords.

**Multi-Agent Architecture**  
Specialized AI agents handle different types of questions (certifications, trips, safety), each with domain-specific knowledge and guardrails.

**Conversation Memory**  
Sessions persist across messages, allowing for natural, context-aware conversations that build on previous exchanges.

### The Stack (For the Curious)

- **Frontend:** Next.js (React) for the web interface
- **Backend:** Python FastAPI for high-performance async operations
- **Database:** PostgreSQL with pgvector for storing content embeddings
- **LLM:** Google Gemini for cost-effective, high-quality responses
- **Hosting:** Vercel (frontend) + Google Cloud Run (backend)

Want technical details? Check out [README.DEV.md](./README.DEV.md).

---

## 🗺️ Project Roadmap

### Phase 1: Foundation (✅ Complete)

- Multi-agent RAG system
- Python backend with FastAPI
- Content ingestion pipeline
- Vector similarity search
- Session management

### Phase 2: Web Application (🚧 In Progress)

- Chat interface with React
- Lead capture forms
- Landing page with feature showcase
- Production deployment
- Error monitoring and analytics

### Phase 3: Telegram Bot (🔮 Planned)

- Telegram adapter for mobile-first experience
- Cross-channel session continuity
- Simplified lead capture for messaging

### Phase 4: User Accounts (🔮 Future)

- Authentication and profiles
- Conversation history
- Bookmarked dive sites
- Personalized recommendations

---

## 💡 Design Philosophy

### User-First

Every feature starts with a real diver's need. No complexity for complexity's sake.

### Safety-Conscious

Clear boundaries about what AI can and cannot advise on. Medical and training decisions always redirect to professionals.

### Transparency

Users understand they're talking to AI, not a human instructor. No deception, ever.

### Continuous Learning

The knowledge base grows with feedback. Inaccuracies are corrected, gaps are filled, and content quality improves over time.

### Privacy-Aware

Conversations are stored to improve the experience, but personal data is protected. Users control their information.

---

## 📚 Documentation

| For...                        | Read...                                                 |
| ----------------------------- | ------------------------------------------------------- |
| **Understanding the project** | This README (you're here!)                              |
| **Setting up development**    | [README.DEV.md](./README.DEV.md)                        |
| **Product vision**            | [Product Spec (PSD)](./docs/psd/DovvyBuddy-PSD-V6.2.md) |
| **Technical architecture**    | [Technical Spec](./docs/technical/specification.md)     |
| **Development roadmap**       | [Master Plan](./docs/plans/MASTER_PLAN.md)              |
| **Design decisions**          | [Architecture Decision Records](./docs/decisions/)      |

---

## 🤝 About This Project

### Motivation

As a diver and technologist, I saw an opportunity to make diving more accessible through AI. Too many people are intimidated by the certification process or overwhelmed by trip planning options. DovvyBuddy aims to be the friendly, knowledgeable companion that helps people take that first step into the underwater world.

### Current Status

DovvyBuddy is a solo founder project in active development. The core RAG system and multi-agent backend are operational, and the web interface is being built out for public launch.

### Contributing

This is currently a closed-source project. However, feedback and suggestions are always welcome! Feel free to open an issue if you have ideas or spot problems.

---

## 🙏 Acknowledgments

This project wouldn't be possible without:

- **PADI & SSI** — Setting global standards for diver education
- **The diving community** — Sharing knowledge and helping newcomers feel welcome
- **Open source tools** — FastAPI, Next.js, PostgreSQL, and countless libraries
- **AI providers** — Google (Gemini) for accessible, powerful language models

---

## 📧 Contact

**Creator:** Jeff Lee  
**Repository:** [github.com/jefflyt/AI_DovvyBuddy04](https://github.com/jefflyt/AI_DovvyBuddy04)  
**Purpose:** Making diving accessible through intelligent conversation

---

**Ready to dive deeper?** 🤿

- **Developers:** Start with [README.DEV.md](./README.DEV.md)
- **Product Vision:** Read the [Product Specification](./docs/psd/DovvyBuddy-PSD-V6.2.md)
- **Technical Deep-Dive:** Check the [Technical Specification](./docs/technical/specification.md)

_Built with curiosity, powered by AI, inspired by the ocean._
