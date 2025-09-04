# AI Content Activation Engine for Marketing Operations

**A functional prototype designed to demonstrate the skills required for the Contentful AI Engineer, Marketing Ops role.**

**Status:** `[Phase 1: MVP - In Progress]`

---

### Introduction: From Governance to a Self-Improving AI

I built this project to translate 20 years of enterprise content governance experience into a solution for modern AI-powered marketing operations. The core thesis is that trustworthy AI in the enterprise isn't just about better prompts; it's about creating auditable, repeatable, and *self-improving* workflows—principles learned from two decades of rolling out enterprise CMS platforms.

This tool is a functional prototype that demonstrates how to apply that governance mindset to increase marketing velocity and impact safely.

### The Problem: The Static AI Tool & The Manual Marketing Bottleneck

Marketing teams are often stuck with two bad options: time-consuming manual work or "black box" AI tools that don't learn and can't be trusted. As a Marketing Ops Manager, the pain is clear:

> "I want to have my content automatically tagged with relevant keywords and summarized for different channels, so that I can reduce the manual pre-launch checklist for every campaign and activate content faster. But I also need to see a complete audit trail for every piece of content an AI has touched, so that I can trust our systems and debug issues quickly."

### The Solution: An AI Activation Engine with a Learning Loop

This tool is a Contentful App that connects directly to a custom FastAPI backend. It allows a marketing manager to enrich and syndicate content to Marketo with a single click, automating the most repetitive parts of campaign preparation.

It has two functions:
1. **Immediate Value:** It enriches content with summaries and tags, pushing it to Marketo to accelerate campaigns.
2. **Long-Term Value:** It captures every interaction as structured data, creating the foundation for a learning loop that makes the AI smarter, cheaper, and more aligned with the company's voice over time.

**(This is where the live demo GIF will go. It will be the first thing a reviewer sees.)**

### The Governance Connection: The `ActivationLog` as a Dual-Use Asset

This system is designed for enterprise realities, where trust and auditability are non-negotiable. The `ActivationLog` is the key.

* **For Managers (The Audit Trail):** The log provides a clear, immutable record for governance. It's the modern equivalent of the audit-friendly publishing workflows I designed for enterprise CMS platforms, providing a clear answer to "What did the AI do and why?"

* **For Engineers (The Training Dataset):** Every log entry is a high-quality, Pydantic-validated piece of data formatted as a "prompt-response pair." This log is not just a record; it is the raw material (`JSONL`) for a future Supervised Fine-Tuning (SFT) pipeline that will continuously improve the model.

### Technical Architecture

The system uses a decoupled architecture to ensure scalability and maintainability. The Contentful App acts as the user interface, triggering a Python-based backend that orchestrates the AI and MarTech integrations.

~~~mermaid
graph TD
    subgraph "User's Browser"
        A[Marketing Manager] -- Clicks 'Activate' button in --> B(Contentful App UI);
    end

    subgraph "Contentful Cloud"
        B -- Sends webhook with Entry ID --> C{FastAPI Backend on Render};
    end

    subgraph "FastAPI Backend on Render"
        C -- 1. Receives Request --> D[Endpoint: /activate];
        D -- 2. Validates Input --> E[Pydantic Models];
        D -- 3. Enriches Content --> F(OpenAI API);
        D -- 4. Logs Evidence --> G[Contentful Management API];
        G -- Writes to --> H(ActivationLog Entry);
        D -- 5. Pushes to Campaign --> I[Marketo REST API];
    end

    subgraph "Marketo Cloud"
        I -- Updates --> J(Marketo List);
    end

    B -- Polls for status updates from --> H;
```

### The Living Roadmap: From Activation to True Learning

This project is built to evolve, just like a real-world enterprise system.

* **Phase 1 (This MVP):** The Activation Engine & Data Collection.
* **Phase 2 (Vision):** A Proactive Content Supply Chain (Webhook-driven, multi-variant generation).
* **Phase 3 (Vision):** The Fine-Tuning Pipeline (SFT) & Impact Dashboard.

### Setup & Installation

*(Instructions for cloning the repo, setting up the `.env` file, and running the services will go here.)*
