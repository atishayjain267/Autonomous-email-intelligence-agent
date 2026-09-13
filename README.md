# Autonomous Email Intelligence Agent

An AI-powered autonomous agent built with Python, LangGraph, Google Gemini, and the Gmail API to intelligently triage, classify, and execute live actions on unread inbox messages.

## Architecture & Tech Stack

- **Orchestration**: LangGraph (StateGraph architecture with SQLite state persistence via `SqliteSaver`)
- **LLM & Structuring**: Google Gemini (`gemini-1.5-flash`) with Pydantic for strict structured classification outputs
- **API Integration**: Gmail API (OAuth 2.0 authentication)

## Workflow Nodes

1. **Fetch**: Connects securely via OAuth 2.0 to fetch unread messages from the inbox.
2. **Classify**: Passes message snippets to Gemini to categorize them into structured buckets (e.g., Urgent, Meeting, Newsletter, Spam) with a one-sentence summary.
3. **Execute**: Performs live modifications (such as archiving or updating labels) back in Gmail based on classification logic.
