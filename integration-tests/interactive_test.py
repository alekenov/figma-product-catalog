#!/usr/bin/env python3
"""
Interactive AI Agent Testing Script

Usage:
    python3 interactive_test.py

Features:
- Chat with AI Agent in terminal
- See full JSON responses
- Maintains conversation context
- Easy testing of multi-turn conversations
"""

import asyncio
import httpx
import uuid
import json
from datetime import datetime
from config import config


class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'


async def chat_with_agent():
    """Interactive chat session with AI Agent."""

    ai_agent_url = config.AI_AGENT_URL
    user_id = f"interactive_{uuid.uuid4().hex[:8]}"

    print(f"\n{Colors.BOLD}{Colors.BLUE}🤖 AI Agent Interactive Testing{Colors.END}")
    print(f"{Colors.CYAN}{'=' * 60}{Colors.END}")
    print(f"{Colors.YELLOW}User ID: {user_id}{Colors.END}")
    print(f"{Colors.YELLOW}AI Agent: {ai_agent_url}{Colors.END}")
    print(f"{Colors.CYAN}{'=' * 60}{Colors.END}\n")

    # Check health
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            health_response = await client.get(f"{ai_agent_url}/health")
            if health_response.status_code == 200:
                print(f"{Colors.GREEN}✅ AI Agent is healthy{Colors.END}\n")
            else:
                print(f"{Colors.YELLOW}⚠️  AI Agent health check returned {health_response.status_code}{Colors.END}\n")
        except Exception as e:
            print(f"{Colors.RED}❌ Cannot connect to AI Agent: {e}{Colors.END}\n")
            return

    print(f"{Colors.MAGENTA}Commands:{Colors.END}")
    print(f"  {Colors.CYAN}/quit{Colors.END} - Exit chat")
    print(f"  {Colors.CYAN}/new{Colors.END} - Start new conversation (new user_id)")
    print(f"  {Colors.CYAN}/json{Colors.END} - Toggle JSON response display")
    print(f"  {Colors.CYAN}/clear{Colors.END} - Clear screen\n")

    show_json = False
    conversation_count = 0

    async with httpx.AsyncClient(timeout=60.0) as client:
        while True:
            try:
                # Get user input
                print(f"{Colors.BOLD}{Colors.GREEN}You:{Colors.END} ", end='')
                message = input().strip()

                if not message:
                    continue

                # Handle commands
                if message == '/quit':
                    print(f"\n{Colors.YELLOW}👋 Goodbye!{Colors.END}\n")
                    break

                if message == '/new':
                    user_id = f"interactive_{uuid.uuid4().hex[:8]}"
                    conversation_count = 0
                    print(f"{Colors.YELLOW}🔄 New conversation started (user_id: {user_id}){Colors.END}\n")
                    continue

                if message == '/json':
                    show_json = not show_json
                    status = "enabled" if show_json else "disabled"
                    print(f"{Colors.YELLOW}JSON display {status}{Colors.END}\n")
                    continue

                if message == '/clear':
                    print("\033[H\033[J")  # Clear screen
                    continue

                # Send message to AI Agent
                conversation_count += 1
                request_id = f"{user_id}_msg{conversation_count}"

                payload = {
                    "message": message,
                    "user_id": user_id,
                    "request_id": request_id
                }

                print(f"{Colors.CYAN}⏳ Thinking...{Colors.END}", end='\r')

                start_time = datetime.now()
                response = await client.post(
                    f"{ai_agent_url}/chat",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                elapsed = (datetime.now() - start_time).total_seconds()

                print(" " * 50, end='\r')  # Clear "Thinking..." line

                if response.status_code == 200:
                    data = response.json()
                    ai_text = data.get("text", "")

                    # Display AI response
                    print(f"{Colors.BOLD}{Colors.BLUE}AI:{Colors.END} {ai_text}\n")

                    # Show metadata
                    metadata_parts = []
                    if data.get("tracking_id"):
                        metadata_parts.append(f"tracking_id={data['tracking_id']}")
                    if data.get("show_products"):
                        metadata_parts.append("show_products=True")

                    if metadata_parts or show_json:
                        print(f"{Colors.CYAN}{'─' * 60}{Colors.END}")

                    if metadata_parts:
                        print(f"{Colors.MAGENTA}Metadata: {', '.join(metadata_parts)}{Colors.END}")

                    # Show full JSON if enabled
                    if show_json:
                        print(f"{Colors.YELLOW}Full JSON Response:{Colors.END}")
                        print(json.dumps(data, indent=2, ensure_ascii=False))

                    print(f"{Colors.CYAN}Response time: {elapsed:.2f}s{Colors.END}")
                    print(f"{Colors.CYAN}{'─' * 60}{Colors.END}\n")

                else:
                    print(f"{Colors.RED}❌ Error {response.status_code}: {response.text}{Colors.END}\n")

            except KeyboardInterrupt:
                print(f"\n\n{Colors.YELLOW}👋 Interrupted. Goodbye!{Colors.END}\n")
                break

            except Exception as e:
                print(f"{Colors.RED}❌ Error: {e}{Colors.END}\n")


async def quick_test_suite():
    """Run a quick automated test suite."""

    print(f"\n{Colors.BOLD}{Colors.BLUE}🧪 Quick AI Agent Test Suite{Colors.END}")
    print(f"{Colors.CYAN}{'=' * 60}{Colors.END}\n")

    ai_agent_url = config.AI_AGENT_URL
    test_user_id = f"quick_test_{uuid.uuid4().hex[:8]}"

    test_cases = [
        {
            "name": "Product Search by Price",
            "message": "Покажи мне цветы до 15000 тенге",
            "expected_keywords": ["тенге", "₸", "букет"]
        },
        {
            "name": "Multi-turn Context",
            "messages": [
                "Какие у вас есть розы?",
                "А сколько стоит самый дорогой?"
            ],
            "expected_keywords": ["роз", "тенге", "₸"]
        },
        {
            "name": "Error Handling",
            "message": "Проверь заказ 000000000",
            "expected_keywords": ["не найден", "не могу найти", "не существует", "tracking", "проверьте"]
        }
    ]

    async with httpx.AsyncClient(timeout=60.0) as client:
        for i, test in enumerate(test_cases, 1):
            print(f"{Colors.YELLOW}Test {i}: {test['name']}{Colors.END}")

            messages = test.get("messages", [test["message"]])

            for msg in messages:
                print(f"  {Colors.GREEN}→{Colors.END} {msg}")

                payload = {
                    "message": msg,
                    "user_id": test_user_id,
                    "request_id": f"quick_test_{i}_{uuid.uuid4().hex[:4]}"
                }

                try:
                    response = await client.post(
                        f"{ai_agent_url}/chat",
                        json=payload,
                        headers={"Content-Type": "application/json"}
                    )

                    if response.status_code == 200:
                        data = response.json()
                        ai_text = data.get("text", "")
                        print(f"  {Colors.BLUE}←{Colors.END} {ai_text[:150]}...")

                        # Check if expected keywords present
                        found_keywords = [
                            kw for kw in test.get("expected_keywords", [])
                            if kw.lower() in ai_text.lower()
                        ]

                        if found_keywords:
                            print(f"  {Colors.GREEN}✅ PASS{Colors.END} (found: {', '.join(found_keywords)})\n")
                        else:
                            print(f"  {Colors.YELLOW}⚠️  PARTIAL{Colors.END} (no expected keywords, but responded)\n")
                    else:
                        print(f"  {Colors.RED}❌ FAIL{Colors.END} (HTTP {response.status_code})\n")

                except Exception as e:
                    print(f"  {Colors.RED}❌ ERROR{Colors.END}: {e}\n")

            print(f"{Colors.CYAN}{'─' * 60}{Colors.END}\n")


async def main():
    """Main entry point."""

    print(f"\n{Colors.BOLD}Select testing mode:{Colors.END}")
    print(f"  {Colors.GREEN}1{Colors.END} - Interactive chat (recommended)")
    print(f"  {Colors.GREEN}2{Colors.END} - Quick automated test suite")
    print(f"  {Colors.GREEN}q{Colors.END} - Quit\n")

    choice = input(f"{Colors.YELLOW}Choice [1/2/q]:{Colors.END} ").strip().lower()

    if choice == '1':
        await chat_with_agent()
    elif choice == '2':
        await quick_test_suite()
    elif choice == 'q':
        print(f"\n{Colors.YELLOW}👋 Goodbye!{Colors.END}\n")
    else:
        print(f"\n{Colors.RED}Invalid choice{Colors.END}\n")


if __name__ == "__main__":
    asyncio.run(main())
