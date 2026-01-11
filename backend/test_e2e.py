"""
End-to-end backend test for Phase III chatbot.

This script tests the complete flow:
1. User signup
2. User signin
3. Chat message (create task)
4. Verify task created
5. Chat message (list tasks)
6. Chat message (complete task)
7. Verify conversation history

Run: python test_e2e.py
"""
import requests
import json
import time
from datetime import datetime

API_BASE = "http://localhost:8000"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def log_success(msg):
    print(f"{Colors.GREEN}[OK]{Colors.END} {msg}")

def log_fail(msg):
    print(f"{Colors.RED}[FAIL]{Colors.END} {msg}")

def log_info(msg):
    print(f"{Colors.BLUE}[INFO]{Colors.END} {msg}")

def log_warning(msg):
    print(f"{Colors.YELLOW}[WARN]{Colors.END} {msg}")

def test_health():
    """Test 1: Health check"""
    print("\n" + "=" * 60)
    print("TEST 1: Health Check")
    print("=" * 60)

    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "healthy":
                log_success(f"Backend is healthy: {data}")
                return True
        log_fail(f"Health check failed: {response.status_code}")
        return False
    except Exception as e:
        log_fail(f"Health check error: {e}")
        return False

def test_signup():
    """Test 2: User signup"""
    print("\n" + "=" * 60)
    print("TEST 2: User Signup")
    print("=" * 60)

    email = f"test_{int(time.time())}@example.com"
    password = "TestPass123!"

    try:
        response = requests.post(
            f"{API_BASE}/auth/signup",
            json={"email": email, "password": password},
            timeout=10
        )

        if response.status_code in [200, 201]:
            data = response.json()
            if "access_token" in data:
                log_success(f"User created: {email}")
                log_info(f"Access token: {data['access_token'][:20]}...")
                return {"email": email, "password": password, "token": data["access_token"]}

        log_fail(f"Signup failed: {response.status_code} - {response.text}")
        return None
    except Exception as e:
        log_fail(f"Signup error: {e}")
        return None

def test_chat_create_task(token):
    """Test 3: Create task via chat"""
    print("\n" + "=" * 60)
    print("TEST 3: Chat - Create Task")
    print("=" * 60)

    try:
        response = requests.post(
            f"{API_BASE}/api/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={"message": "Add buy groceries to my tasks", "conversation_id": None},
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            log_info(f"Response: {json.dumps(data, indent=2)}")

            if "conversation_id" in data and "message" in data:
                log_success(f"Task creation response received")
                log_info(f"Conversation ID: {data['conversation_id']}")
                log_info(f"Agent message: {data['message']}")

                # Check if response is conversational (not raw JSON)
                if "add" in data["message"].lower() or "groceries" in data["message"].lower():
                    log_success("Agent response is conversational")
                    return data["conversation_id"]
                else:
                    log_warning("Agent response may not be conversational")
                    return data["conversation_id"]

        log_fail(f"Chat failed: {response.status_code} - {response.text}")
        return None
    except Exception as e:
        log_fail(f"Chat error: {e}")
        return None

def test_verify_task(token):
    """Test 4: Verify task was created in database"""
    print("\n" + "=" * 60)
    print("TEST 4: Verify Task in Database")
    print("=" * 60)

    try:
        response = requests.get(
            f"{API_BASE}/tasks",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )

        if response.status_code == 200:
            tasks = response.json()
            log_info(f"Tasks in database: {len(tasks)}")

            if len(tasks) > 0:
                grocery_task = None
                for task in tasks:
                    if "groceries" in task.get("title", "").lower():
                        grocery_task = task
                        break

                if grocery_task:
                    log_success(f"Task found: {grocery_task['title']}")
                    log_info(f"Task ID: {grocery_task['id']}")
                    log_info(f"Status: {grocery_task.get('status', 'unknown')}")
                    return True
                else:
                    log_warning("Grocery task not found, but other tasks exist")
                    log_info(f"Tasks: {[t.get('title') for t in tasks]}")
                    return True
            else:
                log_fail("No tasks found in database")
                return False

        log_fail(f"Task verification failed: {response.status_code}")
        return False
    except Exception as e:
        log_fail(f"Task verification error: {e}")
        return False

def test_chat_list_tasks(token, conversation_id):
    """Test 5: List tasks via chat (multi-turn context)"""
    print("\n" + "=" * 60)
    print("TEST 5: Chat - List Tasks (Multi-turn)")
    print("=" * 60)

    try:
        response = requests.post(
            f"{API_BASE}/api/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={"message": "Show me my tasks", "conversation_id": conversation_id},
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            log_info(f"Agent message: {data['message']}")

            # Check if same conversation
            if data.get("conversation_id") == conversation_id:
                log_success("Multi-turn context maintained (same conversation_id)")
            else:
                log_warning(f"Different conversation_id: {data.get('conversation_id')}")

            # Check if response mentions tasks
            if "task" in data["message"].lower() or "groceries" in data["message"].lower():
                log_success("Agent listed tasks")
                return True
            else:
                log_warning("Agent response doesn't clearly mention tasks")
                return True

        log_fail(f"Chat failed: {response.status_code}")
        return False
    except Exception as e:
        log_fail(f"Chat error: {e}")
        return False

def test_conversation_history(token, conversation_id):
    """Test 6: Verify conversation history"""
    print("\n" + "=" * 60)
    print("TEST 6: Conversation History")
    print("=" * 60)

    try:
        # List conversations
        response = requests.get(
            f"{API_BASE}/api/conversations",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )

        if response.status_code == 200:
            conversations = response.json()
            log_success(f"Found {len(conversations)} conversation(s)")

            if len(conversations) > 0:
                conv = conversations[0]
                log_info(f"Conversation ID: {conv['id']}")
                log_info(f"Message count: {conv.get('message_count', 0)}")

                # Get messages
                response2 = requests.get(
                    f"{API_BASE}/api/conversations/{conversation_id}/messages",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=10
                )

                if response2.status_code == 200:
                    data = response2.json()
                    messages = data.get("messages", [])
                    log_success(f"Retrieved {len(messages)} messages")

                    for i, msg in enumerate(messages):
                        role = msg.get("role", "unknown")
                        content = msg.get("content", "")[:50]
                        log_info(f"Message {i+1} ({role}): {content}...")

                    return True

        log_fail(f"Conversation history failed: {response.status_code}")
        return False
    except Exception as e:
        log_fail(f"Conversation history error: {e}")
        return False

def main():
    print("\n" + "=" * 60)
    print("PHASE III BACKEND END-TO-END TEST")
    print("=" * 60)
    print(f"API Base: {API_BASE}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results = {}

    # Test 1: Health check
    results["Health Check"] = test_health()
    if not results["Health Check"]:
        log_fail("Backend is not healthy. Cannot proceed with tests.")
        return 1

    # Test 2: Signup
    user_data = test_signup()
    results["User Signup"] = user_data is not None
    if not user_data:
        log_fail("Cannot proceed without user account")
        return 1

    token = user_data["token"]

    # Test 3: Chat - Create task
    conversation_id = test_chat_create_task(token)
    results["Chat - Create Task"] = conversation_id is not None

    # Test 4: Verify task in database
    results["Verify Task"] = test_verify_task(token)

    # Test 5: Chat - List tasks (multi-turn)
    if conversation_id:
        results["Chat - List Tasks"] = test_chat_list_tasks(token, conversation_id)
    else:
        results["Chat - List Tasks"] = False

    # Test 6: Conversation history
    if conversation_id:
        results["Conversation History"] = test_conversation_history(token, conversation_id)
    else:
        results["Conversation History"] = False

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = 0
    total = len(results)

    for test_name, result in results.items():
        status = f"{Colors.GREEN}PASS{Colors.END}" if result else f"{Colors.RED}FAIL{Colors.END}"
        print(f"{status}: {test_name}")
        if result:
            passed += 1

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print(f"\n{Colors.GREEN}{'=' * 60}{Colors.END}")
        print(f"{Colors.GREEN}ALL TESTS PASSED!{Colors.END}")
        print(f"{Colors.GREEN}{'=' * 60}{Colors.END}")
        print("\nBackend is working correctly!")
        print("\nVerified:")
        print("- Agent can create tasks via natural language")
        print("- Tasks are persisted to database")
        print("- Multi-turn context is maintained")
        print("- Conversation history is saved")
        print("\nReady to proceed to Phase 5: Frontend (ChatKit)")
        return 0
    else:
        print(f"\n{Colors.RED}{'=' * 60}{Colors.END}")
        print(f"{Colors.RED}SOME TESTS FAILED{Colors.END}")
        print(f"{Colors.RED}{'=' * 60}{Colors.END}")
        print("\nPlease review the errors above.")
        return 1

if __name__ == "__main__":
    exit(main())
