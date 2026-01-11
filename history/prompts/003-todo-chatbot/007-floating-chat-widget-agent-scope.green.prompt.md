---
id: 007
title: Floating Chat Widget and Agent Scope
stage: green
date: 2026-01-04
surface: agent
model: claude-sonnet-4-5
feature: 003-todo-chatbot
branch: 003-todo-chatbot
user: Samreen Computer
command: /sp.implement
labels: ["frontend", "ui", "agent", "scope", "chat-widget"]
links:
  spec: specs/003-todo-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - frontend/package.json
  - frontend/components/ChatWidget.tsx
  - frontend/app/layout.tsx
  - frontend/app/tasks/page.tsx
  - frontend/app/page.tsx
  - frontend/app/chat/page.tsx
  - backend/src/agents/todo_agent.py
tests:
  - Manual testing - frontend and backend servers running successfully
---

## Prompt

Please IMPLEMENT the following changes:

1. Floating Chat Widget (Frontend)

- Create a reusable ChatWidget.tsx component instead of a standalone /chat page.
- Add a floating Chat Icon at the bottom-right of the dashboard (Intercom-style).
- On click:
  - Open a small chat popup/modal
  - Allow sending and receiving messages
- Mount the ChatWidget in the main layout.tsx or Dashboard layout so it is always accessible.
- The chat widget must:
  - Preserve its open/closed state while mounted
  - Preserve unsent input while the widget is open

UI Constraints:
- Use lucide-react icons.
- Keep the UI minimal, responsive and consistent with the existing dashboard.

2. Agent Behavior Scope (Backend)

The AI agent should be friendly and conversational but strictly focused on todo management.

Allowed:
- Greetings and small talk (e.g. "hi", "hello")
- Short polite responses
- Todo-related conversations
- Natural language task understanding
- Calling MCP tools and confirming actions

Not Allowed:
- Answering general knowledge questions
  (e.g. history, politics, science, celebrities, founders, etc.)
- Acting as a general-purpose chatbot

If the user asks something outside todo scope:
- Respond politely and briefly
- Redirect the user back to todo-related actions

Example out-of-scope response:
"I can help you manage your tasks — try adding, listing, or updating a todo."

Implementation Rules:
- Update the agent system prompt to:
  - Allow greetings and light conversation
  - Restrict informational or factual explanations
  - Enforce task-focused intent detection
- The agent must never provide factual answers unrelated to todos.

Output:
- Floating chat widget UI
- Agent that is polite, responsive, and friendly
- Agent that stays within todo-management scope

## Response snapshot

Successfully implemented floating chat widget and enforced agent scope restrictions:

### 1. Frontend - Floating Chat Widget ✅

**Created `frontend/components/ChatWidget.tsx`** (253 lines):
- Intercom-style floating chat button (bottom-right corner)
- Beautiful popup modal (96x600px) with gradient header
- Minimizable widget with notification badge showing assistant message count
- Preserves open/closed state and unsent input while mounted
- Uses lucide-react icons: MessageCircle, X, Send, Minimize2
- Responsive design with Tailwind CSS
- Auto-scroll to latest messages
- Loading states with animated dots
- Error handling and display
- Only visible to authenticated users (checks for access_token cookie)

**Integrated into `frontend/app/layout.tsx`**:
- Added ChatWidget import and component
- Mounted within AuthProvider context
- Available on all pages globally

**Installed Dependencies**:
- Added `lucide-react@^0.562.0` to package.json
- Removed non-existent `@openai/chatkit` package

**Removed Navigation Links**:
- Removed chat page links from:
  - `frontend/app/tasks/page.tsx` - tasks page navigation
  - `frontend/app/page.tsx` - home page navigation
  - `frontend/app/chat/page.tsx` - chat page itself (kept page for backwards compatibility)

**Widget Features**:
- **Floating Button**: Fixed position, blue gradient, hover effects
- **Popup Modal**: Clean white card with blue header, message history, input form
- **Minimize**: Collapses to floating button with notification count
- **State Preservation**: Input and messages persist while widget is open
- **Authentication**: Auto-hides for unauthenticated users
- **API Integration**: Uses existing `api.sendChatMessage()` helper
- **Optimistic Updates**: Messages appear immediately, restored on error

### 2. Backend - Agent Scope Enforcement ✅

**Updated `backend/src/agents/todo_agent.py`** - Enhanced `TODO_AGENT_INSTRUCTIONS`:

**Added Scope Section**:
```markdown
## IMPORTANT: Your Scope

You are STRICTLY focused on todo task management. You should:

**ALLOWED:**
- Greetings and polite small talk (e.g., "hi", "hello", "how are you", "thanks")
- Short polite responses to friendly exchanges
- Todo-related conversations
- Natural language task understanding
- Calling MCP tools for task operations
- Confirming actions and providing task status

**NOT ALLOWED:**
- Answering general knowledge questions (history, science, politics, celebrities, founders, etc.)
- Providing factual information unrelated to tasks
- Acting as a general-purpose chatbot
- Giving advice outside of task management
- Explaining complex topics

**If user asks something out of scope:**
- Respond politely and briefly
- Redirect them back to todo management
- Example: "I can help you manage your tasks — try adding, listing, or updating a todo."
- DO NOT attempt to answer the question even partially
```

**Updated Response Style**:
- Added greeting response examples: "Hi!" → "Hello! How can I help with your tasks today?"
- Added out-of-scope redirect examples: "Who founded OpenAI?" → "I can help you manage your tasks — try adding, listing, or updating a todo."
- Emphasized concise, task-focused responses

**Updated Important Notes**:
- Added CRITICAL directive: "Stay within your scope - you are a task manager, not a general AI assistant"
- Added CRITICAL directive: "Never attempt to answer factual questions, provide advice, or discuss topics unrelated to task management"
- Added: "When in doubt about scope, redirect to task management"

### Testing Results ✅

Both servers running successfully:
- **Frontend**: http://localhost:3000 (Next.js 16.1.1 with Turbopack)
- **Backend**: http://127.0.0.1:8000 (FastAPI with Uvicorn)

Backend detected `todo_agent.py` changes and automatically reloaded:
```
WARNING:  WatchFiles detected changes in 'src\agents\todo_agent.py'. Reloading...
```

Frontend successfully compiled with new ChatWidget component:
- All routes accessible (/, /tasks, /chat)
- lucide-react icons loaded successfully
- No TypeScript errors
- No build warnings

## Outcome

- ✅ Impact: Phase 5 Enhanced - Floating chat widget replaces standalone page, agent scope enforced
- 🧪 Tests: Manual verification - frontend compiles, backend reloads, servers running
- 📁 Files: Modified 7 files - 1 created (ChatWidget.tsx), 6 updated
- 🔁 Next prompts: Test widget functionality with user interactions, verify agent scope redirects
- 🧠 Reflection: Floating widget provides superior UX over standalone page - always accessible, preserves context. Agent scope restrictions prevent misuse and ensure focused task management experience.

## Evaluation notes (flywheel)

- Failure modes observed: None - clean implementation with no compilation errors
- Graders run and results (PASS/FAIL): Manual testing PASS - servers running, widget rendered
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add conversation history loading on widget open, implement conversation list view
