"""
Chat API router.

Handles /chat endpoint - extracted from main.py for better organization.
"""

import json
import logging
import re
import time
from typing import Optional
from decimal import Decimal

from fastapi import APIRouter, HTTPException

from models import ChatRequest, ChatResponse, RequestUsage

logger = logging.getLogger(__name__)

# Router instance
router = APIRouter(tags=["chat"])


def sanitize_telegram_file_url(url: Optional[str]) -> Optional[str]:
    """
    Mask Telegram bot token inside file URLs before logging or sending to Claude.

    Example:
        https://api.telegram.org/file/bot123456:ABCDEF/path -> https://api.telegram.org/file/bot<hidden>/path
    """
    if not url:
        return url

    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        if parsed.netloc != "api.telegram.org":
            return url

        path_parts = parsed.path.split("/")
        # Expected path: ['', 'file', 'bot<token>', '...']
        if len(path_parts) >= 3 and path_parts[1] == "file" and path_parts[2].startswith("bot"):
            path_parts[2] = "bot<hidden>"
            masked_path = "/".join(path_parts)
            return parsed._replace(path=masked_path).geturl()
    except Exception:
        return url

    return url


@router.post("/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Universal chat endpoint for all channels.

    Processes user message with Claude AI, executes MCP tools, and returns response.

    NOTE: This is a transitional implementation. Services are imported from main module.
    Future refactoring will use proper DI.
    """
    # Import services from main module (temporary solution until proper DI)
    import main as main_module
    claude_service = main_module.claude_service
    mcp_client = main_module.mcp_client
    conversation_service = main_module.conversation_service
    chat_storage = main_module.chat_storage

    try:
        user_id = request.user_id
        channel = request.channel
        message = request.message
        image_url = request.image_url
        raw_image_url = image_url  # Preserve raw Telegram URL for internal tool execution

        # If image is provided, append it to the message for visual search
        if image_url:
            sanitized_image_url = sanitize_telegram_file_url(image_url)
            message = f"{message}\n\n[User sent an image: {sanitized_image_url}]"
            logger.info(f"👤 USER {user_id} ({channel}): {request.message} + 📷 IMAGE: {sanitized_image_url}")
        else:
            logger.info(f"👤 USER {user_id} ({channel}): {message}")

        # Create or get chat session for monitoring
        session_id = await chat_storage.create_or_get_session(
            user_id=user_id,
            channel=channel,
            customer_name=request.context.get("customer_name") if request.context else None,
            customer_phone=request.context.get("customer_phone") if request.context else None
        )

        # Save user message to database
        if session_id:
            await chat_storage.save_message(
                session_id=session_id,
                role="user",
                content=message
            )

        # Get conversation history
        history = await conversation_service.get_conversation(user_id, channel)

        # HYBRID APPROACH: Auto-trigger visual search when image detected (safety net)
        # This ensures 100% reliability even if Claude's prompt-based detection fails
        if image_url and "[User sent an image:" in message:
            logger.info("🔍 [SAFETY NET] Auto-triggering visual search before Claude...")
            try:
                # Force visual search call with raw Telegram URL
                visual_search_result = await mcp_client.call_tool(
                    tool_name="search_similar_bouquets",
                    arguments={"image_url": raw_image_url, "topK": 5}
                )

                # Parse results
                result_dict = json.loads(visual_search_result) if isinstance(visual_search_result, str) else visual_search_result
                exact_count = len(result_dict.get("exact", []))
                similar_count = len(result_dict.get("similar", []))

                # Add user message first
                history.append({"role": "user", "content": message})

                # Then add assistant message with tool_use (to match Claude's API format)
                tool_use_id = f"toolu_safety_net_{int(time.time() * 1000)}"
                history.append({
                    "role": "assistant",
                    "content": [
                        {
                            "type": "tool_use",
                            "id": tool_use_id,
                            "name": "search_similar_bouquets",
                            "input": {"image_url": raw_image_url, "topK": 5}
                        }
                    ]
                })

                # Then add user message with tool_result
                history.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_use_id,
                            "content": json.dumps(result_dict, ensure_ascii=False)
                        }
                    ]
                })

                logger.info(f"✅ [SAFETY NET] Visual search succeeded: {exact_count} exact, {similar_count} similar")

            except Exception as e:
                logger.error(f"❌ [SAFETY NET] Visual search failed: {e}")
                # Continue to Claude anyway (Claude's prompt can still try)
                history.append({"role": "user", "content": message})
        else:
            # Add user message
            history.append({"role": "user", "content": message})

        # Track metadata
        tracking_id = None
        order_number = None
        order_id = None
        list_products_used = False
        product_ids = None  # Store product IDs from list_products for filtered display

        # Track usage across all API calls in this conversation turn
        total_input_tokens = 0
        total_output_tokens = 0
        total_cache_read_tokens = 0
        total_cache_creation_tokens = 0

        # Call Claude with function calling
        response = await claude_service.chat(
            messages=history,
            channel=channel,
            context=request.context
        )

        # Accumulate usage from first response
        usage = response.usage
        total_input_tokens += getattr(usage, 'input_tokens', 0)
        total_output_tokens += getattr(usage, 'output_tokens', 0)
        total_cache_read_tokens += getattr(usage, 'cache_read_input_tokens', 0)
        total_cache_creation_tokens += getattr(usage, 'cache_creation_input_tokens', 0)

        # Process tool calls if any
        while response.stop_reason == "tool_use":
            # Extract tool calls and content
            tool_results = []
            assistant_content = []

            for block in response.content:
                if block.type == "tool_use":
                    # Execute tool via MCP
                    logger.info(f"🔧 Tool call: {block.name}")

                    # Track list_products usage
                    if block.name == "list_products":
                        list_products_used = True

                    # Execute tool - inject telegram_user_id for user-specific operations
                    tool_args = block.input.copy()
                    if block.name in ["create_order", "update_order", "track_order_by_phone"]:
                        tool_args["telegram_user_id"] = user_id
                        logger.info(f"💾 Injected telegram_user_id={user_id} for {block.name}")

                    if block.name == "search_similar_bouquets" and raw_image_url:
                        tool_args["image_url"] = raw_image_url

                    tool_result = await mcp_client.call_tool(
                        tool_name=block.name,
                        arguments=tool_args
                    )

                    # Extract product IDs from list_products result
                    if block.name == "list_products":
                        try:
                            result_dict = json.loads(tool_result) if isinstance(tool_result, str) else tool_result
                            products = result_dict if isinstance(result_dict, list) else []
                            # Extract IDs from product list
                            extracted_ids = [p.get("id") for p in products if isinstance(p, dict) and p.get("id")]
                            if extracted_ids:
                                product_ids = extracted_ids
                                logger.info(f"📦 Extracted {len(product_ids)} product IDs from list_products: {product_ids}")
                        except (json.JSONDecodeError, TypeError) as e:
                            logger.warning(f"⚠️ Could not extract product IDs from list_products result: {e}")

                    if block.name == "create_order":
                        try:
                            result_dict = json.loads(tool_result)
                        except json.JSONDecodeError as e:
                            logger.error(f"Failed to parse create_order response: {e}")
                            logger.error(f"Raw tool_result: {tool_result[:200]}")
                            result_dict = {}
                        except Exception as e:
                            logger.error(f"Unexpected error parsing create_order: {e}")
                            result_dict = {}

                        if result_dict:
                            tracking_id = result_dict.get("tracking_id") or tracking_id
                            order_number = result_dict.get("orderNumber") or order_number
                            order_id = result_dict.get("id") or order_id

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": tool_result
                    })

                    # Convert ToolUseBlock to dict for JSON serialization
                    assistant_content.append({
                        "type": "tool_use",
                        "id": block.id,
                        "name": block.name,
                        "input": block.input
                    })
                elif block.type == "text":
                    assistant_content.append({
                        "type": "text",
                        "text": block.text
                    })

            # Add assistant response to history
            history.append({
                "role": "assistant",
                "content": assistant_content
            })

            # Add tool results to history
            if tool_results:
                history.append({
                    "role": "user",
                    "content": tool_results
                })

                # Continue conversation with tool results
                response = await claude_service.chat(
                    messages=history,
                    channel=channel,
                    context=request.context
                )

                # Accumulate usage from continuation
                usage = response.usage
                total_input_tokens += getattr(usage, 'input_tokens', 0)
                total_output_tokens += getattr(usage, 'output_tokens', 0)
                total_cache_read_tokens += getattr(usage, 'cache_read_input_tokens', 0)
                total_cache_creation_tokens += getattr(usage, 'cache_creation_input_tokens', 0)

        # Extract final text response and filter internal tags
        final_text = ""
        for block in response.content:
            if block.type == "text":
                # Remove internal tags from text blocks (Claude may include thinking in text)
                cleaned_text = block.text
                cleaned_text = re.sub(r'<thinking>.*?</thinking>', '', cleaned_text, flags=re.DOTALL)
                cleaned_text = re.sub(r'<conversation_status>.*?</conversation_status>', '', cleaned_text, flags=re.DOTALL)
                cleaned_text = cleaned_text.strip()
                if cleaned_text:  # Only add non-empty text
                    final_text += cleaned_text
            elif block.type == "thinking":
                # Sonnet 4.5 can generate thinking as separate block - skip it
                logger.debug(f"💭 Skipping thinking block: {block.thinking[:100]}...")
                continue

        final_text = final_text.strip()

        # Parse explicit <show_products> tag from Claude's response
        show_products_match = re.search(r'<show_products>(true|false)</show_products>', final_text)
        if show_products_match:
            show_products_explicit = show_products_match.group(1) == "true"
            # Remove tag from final text
            final_text = re.sub(r'<show_products>.*?</show_products>', '', final_text, flags=re.DOTALL).strip()
            list_products_used = show_products_explicit
            logger.info(f"📸 Explicit <show_products> tag: {show_products_explicit}")
        else:
            # Fallback: Auto-detection if no explicit tag
            # Detect patterns like "Букет 'Название' — 9 000 ₸" or "**Букет" (markdown bold)
            if not list_products_used and (
                re.search(r'Букет .+? — \d+', final_text) or  # Price pattern
                re.search(r'\*\*Букет', final_text) or  # Bold букет in markdown
                re.search(r'\d+\.\s+\*\*Букет', final_text)  # Numbered list with букет
            ):
                list_products_used = True
                logger.info("📦 Auto-detected product listing in response, setting show_products=true")

        logger.info(f"🤖 AI RESPONSE: {final_text[:100]}...")

        # Add final response to history with proper content block structure
        # Must use content blocks (not plain string) to match Claude API format
        final_content = []
        for block in response.content:
            if block.type == "text":
                # Use cleaned text without <thinking> blocks
                final_content.append({
                    "type": "text",
                    "text": final_text
                })
                break  # Only need one text block
            elif block.type == "tool_use":
                # Preserve tool_use blocks in final response
                final_content.append({
                    "type": "tool_use",
                    "id": block.id,
                    "name": block.name,
                    "input": block.input
                })

        # Only append final content if it has meaningful content
        if final_content:
            history.append({
                "role": "assistant",
                "content": final_content
            })
        else:
            # Fallback: if no content extracted, still add text block
            history.append({
                "role": "assistant",
                "content": [{"type": "text", "text": final_text}]
            })

        # Save conversation history
        await conversation_service.save_conversation(user_id, channel, history)

        # Calculate total usage for this request
        # Claude Haiku 4.5 pricing
        input_cost = (total_input_tokens / 1_000_000) * 0.80
        cache_read_cost = (total_cache_read_tokens / 1_000_000) * 0.08
        cache_write_cost = (total_cache_creation_tokens / 1_000_000) * 1.00
        output_cost = (total_output_tokens / 1_000_000) * 4.00
        total_cost = input_cost + cache_read_cost + cache_write_cost + output_cost

        request_usage = RequestUsage(
            input_tokens=total_input_tokens,
            output_tokens=total_output_tokens,
            cache_read_tokens=total_cache_read_tokens,
            cache_creation_tokens=total_cache_creation_tokens,
            total_cost_usd=round(total_cost, 6),
            cache_hit=(total_cache_read_tokens > 0)
        )

        logger.info(f"💰 Request cost: ${total_cost:.6f} | Cache hit: {request_usage.cache_hit}")

        # Save assistant message to database
        if session_id:
            # Save message with metadata about tools and tokens
            metadata = {
                "input_tokens": total_input_tokens,
                "output_tokens": total_output_tokens,
                "cache_read_tokens": total_cache_read_tokens,
                "cache_creation_tokens": total_cache_creation_tokens,
                "cache_hit": request_usage.cache_hit
            }

            await chat_storage.save_message(
                session_id=session_id,
                role="assistant",
                content=final_text,
                metadata=metadata,
                cost_usd=Decimal(str(total_cost))
            )

            # Update session statistics
            await chat_storage.update_session_stats(
                session_id=session_id,
                increment_messages=2,  # User message + assistant message
                add_cost_usd=Decimal(str(total_cost)),
                created_order=(order_id is not None),
                order_id=order_id
            )

        return ChatResponse(
            text=final_text,
            tracking_id=tracking_id,
            order_number=order_number,
            show_products=list_products_used,
            product_ids=product_ids,
            usage=request_usage
        )

    except Exception as e:
        logger.error(f"❌ Error processing chat: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")
