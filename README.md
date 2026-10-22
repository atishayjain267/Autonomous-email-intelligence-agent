# Autonomous Email Intelligence Agent

An AI-powered autonomous email triage system built with Python, LangGraph, Google Gemini, and the Gmail API, featuring state persistence and Pydantic structured outputs.

## 🚀 Architecture & Tech Stack

1. **Orchestration**: Built using **LangGraph** to manage stateful, multi-step agent workflows.
2. **Intelligence**: Powered by **Google Gemini API** with strict **Pydantic-structured outputs** for accurate email classification (Urgent, Meetings, Newsletters, Spam).
3. **Integration**: Secure **Gmail API (OAuth 2.0)** integration to fetch unread messages and execute real-time inbox modifications (archiving, updating labels, or marking as read).
4. **Persistence**: Utilizes **SQLite** (`agent_state.db`) via `SqliteSaver` to maintain workflow state and execution logs securely.

---

## 📂 Project Structure

```text
Autonomous-email-intelligence-agent/
│
├── agent.py          # Core LangGraph workflow and agent logic
├── auth.py           # Gmail OAuth 2.0 authentication handling
├── agent_state.db    # SQLite state persistence checkpointing (git-ignored)
├── credentials.json  # Google Cloud OAuth credentials (git-ignored)
├── token.json        # User access/refresh tokens (git-ignored)
├── .gitignore        # Security configuration for sensitive files
└── README.md         # Project documentation
```
