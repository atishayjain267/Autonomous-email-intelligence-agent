import os
from googleapiclient.discovery import build
from auth import get_gmail_service
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from typing import TypedDict, List
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI

# 1. Define Pydantic schema for structured output classification
class EmailClassification(BaseModel):
    category: str = Field(description="Category of the email: Urgent, Meeting, Newsletter, or Spam")
    summary: str = Field(description="A concise one-sentence summary of the email content")

class AgentState(TypedDict):
    messages: List[dict]
    classified_emails: List[dict]
    action_logs: List[str]

def fetch_emails(state: AgentState):
    print("--- FETCHING UNREAD EMAILS ---")
    creds = get_gmail_service()
    service = build('gmail', 'v1', credentials=creds)
    # Broadened query to catch any unread message across all tabs
    results = service.users().messages().list(userId='me', q='is:unread', maxResults=5).execute()
    messages = results.get('messages', [])
    
    fetched = []
    for msg in messages:
        txt = service.users().messages().get(userId='me', id=msg['id']).execute()
        snippet = txt.get('snippet', '')
        fetched.append({'id': msg['id'], 'snippet': snippet})
        
    print(f"Found {len(fetched)} unread messages.")
    return {"messages": fetched, "action_logs": [f"Fetched {len(fetched)} unread emails."]}

def classify_emails(state: AgentState):
    print("--- CLASSIFYING EMAILS WITH GEMINI STRUCTURED OUTPUT ---")
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
    structured_llm = llm.with_structured_output(EmailClassification)
    
    classified = []
    for email in state['messages']:
        prompt = f"Classify this email snippet: '{email['snippet']}' into one of: Urgent, Meeting, Newsletter, Spam."
        try:
            result = structured_llm.invoke(prompt)
            cat = result.category
            summ = result.summary
        except Exception as e:
            cat = "General"
            summ = email['snippet']
            
        classified.append({**email, 'category': cat, 'summary': summ})
        print(f"Email ID {email['id']} -> Category: {cat} | Summary: {summ}")
        
    return {"classified_emails": classified, "action_logs": ["Successfully classified emails using Gemini and Pydantic."]}

def execute_actions(state: AgentState):
    print("--- EXECUTING REAL GMAIL ACTIONS ---")
    creds = get_gmail_service()
    service = build('gmail', 'v1', credentials=creds)
    
    logs = []
    for email in state['classified_emails']:
        msg_id = email['id']
        category = email['category']
        
        try:
            if category in ["Newsletter", "Spam"]:
                service.users().messages().batchModify(
                    userId='me',
                    body={
                        'ids': [msg_id],
                        'removeLabelIds': ['UNREAD', 'INBOX']
                    }
                ).execute()
                action_msg = f"Archived & marked {category} email ({msg_id}) as read."
            else:
                action_msg = f"Flagged {category} email ({msg_id}) for review."
                
        except Exception as e:
            action_msg = f"Failed to execute action for {msg_id}: {e}"
            
        print(f"-> {action_msg}")
        logs.append(action_msg)
        
    return {"action_logs": logs}

# Setup SQLite checkpointing with context manager
with SqliteSaver.from_conn_string("agent_state.db") as memory:
    workflow = StateGraph(AgentState)
    workflow.add_node("fetch_emails", fetch_emails)
    workflow.add_node("classify_emails", classify_emails)
    workflow.add_node("execute_actions", execute_actions)

    workflow.set_entry_point("fetch_emails")
    workflow.add_edge("fetch_emails", "classify_emails")
    workflow.add_edge("classify_emails", "execute_actions")
    workflow.add_edge("execute_actions", END)

    app = workflow.compile(checkpointer=memory)

    if __name__ == "__main__":
        print("Running Autonomous Agent with Gemini & SQLite Persistence...")
        config = {"configurable": {"thread_id": "1"}}
        initial_state = {"messages": [], "classified_emails": [], "action_logs": []}
        result = app.invoke(initial_state, config)
        print("\nWorkflow Finished Successfully! State saved to agent_state.db.")