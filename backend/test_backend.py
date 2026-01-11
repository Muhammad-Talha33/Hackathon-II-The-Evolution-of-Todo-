"""
Quick backend verification script for Phase III chatbot.

This script tests the backend implementation without requiring an OpenAI API key.
It verifies:
1. Database models are correct
2. MCP server can be initialized
3. Agent can be created
4. API endpoints are registered

Run: python test_backend.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all required modules can be imported."""
    print("=" * 60)
    print("TEST 1: Verifying Imports")
    print("=" * 60)

    try:
        from src.models.conversation import Conversation
        print("✅ Conversation model imported")
    except Exception as e:
        print(f"❌ Conversation model import failed: {e}")
        return False

    try:
        from src.models.message import Message, MessageRole
        print("✅ Message model imported")
    except Exception as e:
        print(f"❌ Message model import failed: {e}")
        return False

    try:
        from src.schemas.chat import ChatRequest, ChatResponse, ConversationSummary
        print("✅ Chat schemas imported")
    except Exception as e:
        print(f"❌ Chat schemas import failed: {e}")
        return False

    try:
        from src.agents.todo_agent import get_agent_with_tools, TODO_AGENT_INSTRUCTIONS
        print("✅ TodoAgent imported")
    except Exception as e:
        print(f"❌ TodoAgent import failed: {e}")
        return False

    try:
        from src.mcp_server.server import get_mcp_server
        print("✅ MCP server imported")
    except Exception as e:
        print(f"❌ MCP server import failed: {e}")
        return False

    try:
        from src.services.chat_service import process_chat_message
        print("✅ Chat service imported")
    except Exception as e:
        print(f"❌ Chat service import failed: {e}")
        return False

    try:
        from src.routers.chat import router as chat_router
        print("✅ Chat router imported")
    except Exception as e:
        print(f"❌ Chat router import failed: {e}")
        return False

    try:
        from src.routers.conversations import router as conversations_router
        print("✅ Conversations router imported")
    except Exception as e:
        print(f"❌ Conversations router import failed: {e}")
        return False

    print("\n✅ All imports successful!\n")
    return True


def test_mcp_server():
    """Test MCP server initialization."""
    print("=" * 60)
    print("TEST 2: Verifying MCP Server")
    print("=" * 60)

    try:
        from src.mcp_server.server import get_mcp_server
        mcp = get_mcp_server()

        # Check that tools exist
        tools = [
            'mcp_add_task',
            'mcp_list_tasks',
            'mcp_complete_task',
            'mcp_delete_task',
            'mcp_update_task'
        ]

        for tool_name in tools:
            if hasattr(mcp, tool_name):
                print(f"✅ Tool '{tool_name}' registered")
            else:
                print(f"❌ Tool '{tool_name}' NOT found")
                return False

        print("\n✅ MCP server initialized with all 5 tools!\n")
        return True

    except Exception as e:
        print(f"❌ MCP server initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_agent_creation():
    """Test that agent can be created with MCP tools."""
    print("=" * 60)
    print("TEST 3: Verifying Agent Creation")
    print("=" * 60)

    try:
        from src.mcp_server.server import get_mcp_server
        from src.agents.todo_agent import get_agent_with_tools, TODO_AGENT_INSTRUCTIONS

        mcp = get_mcp_server()
        tools = [
            mcp.mcp_add_task,
            mcp.mcp_list_tasks,
            mcp.mcp_complete_task,
            mcp.mcp_delete_task,
            mcp.mcp_update_task
        ]

        agent = get_agent_with_tools(tools)
        print(f"✅ Agent created: {agent.name}")
        print(f"✅ Agent has {len(tools)} tools")

        # Check instructions
        if "friendly and helpful Todo Task Manager" in TODO_AGENT_INSTRUCTIONS:
            print("✅ Agent instructions loaded correctly")
        else:
            print("❌ Agent instructions may be incorrect")
            return False

        print("\n✅ Agent creation successful!\n")
        return True

    except Exception as e:
        print(f"❌ Agent creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_routes():
    """Test that API routes are registered."""
    print("=" * 60)
    print("TEST 4: Verifying API Routes")
    print("=" * 60)

    try:
        from src.main import app

        routes = {route.path: route.methods for route in app.routes}

        # Check chat endpoint
        if "/api/chat" in routes:
            print(f"✅ POST /api/chat registered: {routes['/api/chat']}")
        else:
            print("❌ POST /api/chat NOT registered")
            return False

        # Check conversations endpoints
        if "/api/conversations" in routes:
            print(f"✅ GET /api/conversations registered: {routes['/api/conversations']}")
        else:
            print("❌ GET /api/conversations NOT registered")
            return False

        # Check conversation messages endpoint
        conv_msg_route = None
        for path in routes:
            if "conversations" in path and "messages" in path:
                conv_msg_route = path
                break

        if conv_msg_route:
            print(f"✅ GET /api/conversations/{{id}}/messages registered")
        else:
            print("❌ GET /api/conversations/{id}/messages NOT registered")
            return False

        print("\n✅ All API routes registered!\n")
        return True

    except Exception as e:
        print(f"❌ API route verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_database_models():
    """Test database model definitions."""
    print("=" * 60)
    print("TEST 5: Verifying Database Models")
    print("=" * 60)

    try:
        from src.models.conversation import Conversation
        from src.models.message import Message, MessageRole

        # Check Conversation model fields
        conv_fields = ['id', 'user_id', 'created_at', 'updated_at']
        for field in conv_fields:
            if hasattr(Conversation, field):
                print(f"✅ Conversation.{field} exists")
            else:
                print(f"❌ Conversation.{field} NOT found")
                return False

        # Check Message model fields
        msg_fields = ['id', 'conversation_id', 'role', 'content', 'created_at']
        for field in msg_fields:
            if hasattr(Message, field):
                print(f"✅ Message.{field} exists")
            else:
                print(f"❌ Message.{field} NOT found")
                return False

        # Check MessageRole enum
        if hasattr(MessageRole, 'USER') and hasattr(MessageRole, 'ASSISTANT'):
            print("✅ MessageRole enum has USER and ASSISTANT")
        else:
            print("❌ MessageRole enum incomplete")
            return False

        print("\n✅ Database models correctly defined!\n")
        return True

    except Exception as e:
        print(f"❌ Database model verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_environment_config():
    """Test environment configuration."""
    print("=" * 60)
    print("TEST 6: Verifying Environment Configuration")
    print("=" * 60)

    try:
        from src.config import settings

        # Check DATABASE_URL
        if settings.DATABASE_URL:
            db_preview = settings.DATABASE_URL.split('@')[1][:30] if '@' in settings.DATABASE_URL else 'configured'
            print(f"✅ DATABASE_URL: ...{db_preview}...")
        else:
            print("❌ DATABASE_URL not set")
            return False

        # Check OPENAI_API_KEY
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "your-openai-api-key-here":
            print(f"✅ OPENAI_API_KEY: {settings.OPENAI_API_KEY[:10]}... (configured)")
        else:
            print("⚠️  OPENAI_API_KEY: Not configured (placeholder)")
            print("    ℹ️  You need to add your OpenAI API key to backend/.env")
            print("    ℹ️  Get one from: https://platform.openai.com/api-keys")

        # Check other settings
        print(f"✅ SECRET_KEY: {settings.SECRET_KEY[:10]}... (configured)")
        print(f"✅ ENVIRONMENT: {settings.ENVIRONMENT}")
        print(f"✅ CORS_ORIGINS: {settings.cors_origins_list}")

        print("\n✅ Environment configuration loaded!\n")
        return True

    except Exception as e:
        print(f"❌ Environment configuration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("PHASE III BACKEND VERIFICATION")
    print("=" * 60 + "\n")

    tests = [
        ("Imports", test_imports),
        ("MCP Server", test_mcp_server),
        ("Agent Creation", test_agent_creation),
        ("API Routes", test_api_routes),
        ("Database Models", test_database_models),
        ("Environment Config", test_environment_config),
    ]

    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"❌ {name} test crashed: {e}")
            results[name] = False

    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 60)
        print("\n✅ Backend structure is correct!")
        print("\nNext steps:")
        print("1. Add your OpenAI API key to backend/.env")
        print("2. Start backend server: python -m uvicorn src.main:app --reload")
        print("3. Run manual API tests from TESTING_GUIDE.md")
        print("4. Proceed to Phase 5 (Frontend) once API tests pass")
        return 0
    else:
        print("\n" + "=" * 60)
        print("❌ SOME TESTS FAILED")
        print("=" * 60)
        print("\nPlease fix the failing tests before proceeding.")
        return 1


if __name__ == "__main__":
    exit(main())
