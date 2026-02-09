---
id: 011
title: Configure OpenAI API Key for Chatbot
stage: green
date: 2026-02-09
surface: agent
model: claude-opus-4-6
feature: 005-phase5-partc-cloud-production
branch: 001-phase2-full-stack-web
user: Muhammad-Talha33
command: /sp.implement
labels: ["openai", "chatbot", "kubernetes", "secrets", "deployment"]
links:
  spec: specs/005-phase5-partc-cloud-production/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - Kubernetes secret app-secrets updated (OPENAI_API_KEY added)
tests:
  - POST /api/api/chat with auth token - PASS (returns chatbot response)
  - GET /api/health - PASS
  - Backend pod 2/2 Running with Dapr sidecar - PASS
---

## Prompt

User reported chatbot error: "Incorrect API key provided: your-ope************here" - the backend was using the placeholder default value from config.py. User provided their OpenAI API key (credentials not recorded per user request).

## Response snapshot

Fixed the chatbot by adding the real OpenAI API key to the Kubernetes `app-secrets` secret:

1. **Diagnosed**: Backend deployment already had `OPENAI_API_KEY` env var configured to read from `app-secrets` K8s secret, but the secret only contained `JWT_SECRET`
2. **Patched secret**: Added `OPENAI_API_KEY` to the existing `app-secrets` secret
3. **Restarted backend**: Rolled out new backend pod to pick up the updated secret
4. **Verified**: Chat endpoint returned successful response: "Hello! How can I help with your tasks today?"

## Outcome

- ✅ Impact: AI chatbot fully functional - users can interact with the todo assistant via natural language
- 🧪 Tests: Chat endpoint returns valid response with conversation_id and AI message
- 📁 Files: Kubernetes app-secrets secret updated with OPENAI_API_KEY
- 🔁 Next prompts: End-to-end test of chatbot task management features, add TLS/domain configuration
- 🧠 Reflection: The backend deployment was already pre-configured to read OPENAI_API_KEY from secrets - just needed the actual key value added

## Evaluation notes (flywheel)

- Failure modes observed: Placeholder API key in config.py default used when secret key not present
- Graders run and results (PASS/FAIL): Chat endpoint integration test PASS
- Prompt variant (if applicable): N/A
- Next experiment: Test chatbot with task creation commands to verify full agent functionality
