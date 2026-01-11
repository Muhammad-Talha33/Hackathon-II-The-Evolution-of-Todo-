"""Quick backend verification - Windows compatible."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    print("=" * 60)
    print("TEST 1: Verifying Imports")
    print("=" * 60)

    try:
        from src.models.conversation import Conversation
        from src.models.message import Message, MessageRole
        from src.schemas.chat import ChatRequest, ChatResponse
        from src.agents.todo_agent import get_agent_with_tools
        from src.mcp_server.server import get_mcp_server
        from src.services.chat_service import process_chat_message
        from src.routers.chat import router as chat_router
        from src.routers.conversations import router as conversations_router

        print("[OK] All imports successful!")
        return True
    except Exception as e:
        print(f"[FAIL] Import failed: {e}")
        return False

def test_mcp_server():
    print("\n" + "=" * 60)
    print("TEST 2: Verifying MCP Server")
    print("=" * 60)

    try:
        # Check that MCP server module can be imported
        from src.mcp_server import server as mcp_module

        # Check that tools are defined as functions
        tools = ['mcp_add_task', 'mcp_list_tasks', 'mcp_complete_task',
                 'mcp_delete_task', 'mcp_update_task']

        for tool_name in tools:
            if hasattr(mcp_module, tool_name):
                print(f"[OK] Tool '{tool_name}' defined")
            else:
                print(f"[FAIL] Tool '{tool_name}' NOT found")
                return False

        print("[OK] MCP server initialized with all 5 tools!")
        return True
    except Exception as e:
        print(f"[FAIL] MCP server failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_routes():
    print("\n" + "=" * 60)
    print("TEST 3: Verifying API Routes")
    print("=" * 60)

    try:
        from src.main import app
        routes = {route.path: route.methods for route in app.routes}

        if "/api/chat" in routes:
            print(f"[OK] POST /api/chat registered")
        else:
            print("[FAIL] POST /api/chat NOT registered")
            return False

        if "/api/conversations" in routes:
            print(f"[OK] GET /api/conversations registered")
        else:
            print("[FAIL] GET /api/conversations NOT registered")
            return False

        print("[OK] All API routes registered!")
        return True
    except Exception as e:
        print(f"[FAIL] API route verification failed: {e}")
        return False

def test_env_config():
    print("\n" + "=" * 60)
    print("TEST 4: Verifying Environment")
    print("=" * 60)

    try:
        from src.config import settings

        if settings.DATABASE_URL:
            print("[OK] DATABASE_URL configured")
        else:
            print("[FAIL] DATABASE_URL not set")
            return False

        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "your-openai-api-key-here":
            print(f"[OK] OPENAI_API_KEY configured")
        else:
            print("[WARNING] OPENAI_API_KEY not configured (placeholder)")
            print("          Get one from: https://platform.openai.com/api-keys")

        print(f"[OK] ENVIRONMENT: {settings.ENVIRONMENT}")
        return True
    except Exception as e:
        print(f"[FAIL] Environment config failed: {e}")
        return False

def main():
    print("\n" + "=" * 60)
    print("PHASE III BACKEND VERIFICATION")
    print("=" * 60 + "\n")

    tests = [
        ("Imports", test_imports),
        ("MCP Server", test_mcp_server),
        ("API Routes", test_api_routes),
        ("Environment", test_env_config),
    ]

    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"[FAIL] {name} test crashed: {e}")
            results[name] = False

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED!")
        print("=" * 60)
        print("\nBackend structure is correct!")
        print("\nNext steps:")
        print("1. Add your OpenAI API key to backend/.env")
        print("2. Start server: python -m uvicorn src.main:app --reload")
        print("3. Run manual API tests from TESTING_GUIDE.md")
        print("4. Proceed to Phase 5 (Frontend) once tests pass")
        return 0
    else:
        print("\n" + "=" * 60)
        print("SOME TESTS FAILED")
        print("=" * 60)
        print("\nPlease fix the failing tests before proceeding.")
        return 1

if __name__ == "__main__":
    exit(main())
