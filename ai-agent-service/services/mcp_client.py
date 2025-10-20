"""HTTP client for calling backend API directly (bypassing MCP for now)."""

import base64
import logging
from typing import Dict, Any, Optional
import httpx
import json
from datetime import datetime, timedelta
import re
import copy
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class MCPClient:
    """HTTP client for calling backend API directly."""

    def __init__(self, backend_api_url: str, shop_id: int):
        """
        Initialize MCP client.

        Args:
            backend_api_url: Base URL of backend API (e.g. http://localhost:8014/api/v1)
            shop_id: Default shop ID for all requests
        """
        self.backend_url = backend_api_url.rstrip('/')
        self.shop_id = shop_id
        self.client = httpx.AsyncClient(timeout=30.0)

    def _parse_natural_date(self, date_str: str) -> str:
        """
        Parse natural language date to ISO format.

        Args:
            date_str: Natural language date like "сегодня", "завтра", "послезавтра"

        Returns:
            ISO date string like "2025-10-08"
        """
        date_lower = date_str.lower().strip()
        today = datetime.now().date()

        # Russian natural language dates
        if date_lower in ["сегодня", "today"]:
            return today.isoformat()
        elif date_lower in ["завтра", "tomorrow"]:
            return (today + timedelta(days=1)).isoformat()
        elif date_lower in ["послезавтра", "day after tomorrow"]:
            return (today + timedelta(days=2)).isoformat()

        # "через N дня/дней" pattern
        match = re.search(r'через\s+(\d+)\s+(день|дня|дней)', date_lower)
        if match:
            days = int(match.group(1))
            return (today + timedelta(days=days)).isoformat()

        # Already ISO format or specific date - return as is
        return date_str

    def _parse_natural_time(self, time_str: str) -> str:
        """
        Parse natural language time to HH:MM format.

        Args:
            time_str: Natural language time like "утром", "днем", "вечером"

        Returns:
            Time string like "09:00", "14:00", "18:00"
        """
        time_lower = time_str.lower().strip()

        # Russian natural language times
        if time_lower in ["утром", "morning"]:
            return "09:00"
        elif time_lower in ["днем", "afternoon", "день"]:
            return "14:00"
        elif time_lower in ["вечером", "evening", "вечер"]:
            return "18:00"
        elif time_lower in ["как можно скорее", "asap", "срочно"]:
            return "09:00"  # Earliest available slot
        elif time_lower in ["уточнит менеджер", "manager will clarify", "уточнить"]:
            return "12:00"  # Default midday time

        # Already HH:MM format - return as is
        # Check if it looks like time (HH:MM or H:MM)
        if re.match(r'^\d{1,2}:\d{2}$', time_str):
            return time_str

        # Default fallback
        return "12:00"

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """
        Execute a tool by calling backend API directly.

        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments (will NOT be mutated)

        Returns:
            String representation of tool result
        """
        payload = copy.deepcopy(arguments)
        payload.setdefault("shop_id", self.shop_id)
        logger.info(f"🔧 TOOL CALL: {tool_name} with args: {self._mask_sensitive_data(payload)}")

        try:
            if tool_name == "list_products":
                result = await self._list_products(payload)
            elif tool_name == "get_product":
                result = await self._get_product(payload)
            elif tool_name == "get_working_hours":
                result = await self._get_working_hours(payload)
            elif tool_name == "create_order":
                result = await self._create_order(payload)
            elif tool_name == "track_order_by_phone":
                result = await self._track_order_by_phone(payload)
            elif tool_name == "get_shop_settings":
                result = await self._get_shop_settings(payload)
            elif tool_name == "update_order":
                result = await self._update_order(payload)
            elif tool_name == "kaspi_create_payment":
                result = await self._kaspi_create_payment(payload)
            elif tool_name == "kaspi_check_payment_status":
                result = await self._kaspi_check_payment_status(payload)
            elif tool_name == "kaspi_get_payment_details":
                result = await self._kaspi_get_payment_details(payload)
            elif tool_name == "kaspi_refund_payment":
                result = await self._kaspi_refund_payment(payload)
            elif tool_name == "get_client_profile":
                result = await self._get_client_profile(payload)
            elif tool_name == "update_profile_privacy":
                result = await self._update_profile_privacy(payload)
            elif tool_name == "search_similar_bouquets":
                result = await self._search_similar_bouquets(payload)
            else:
                result = {"error": f"Unknown tool: {tool_name}"}

            logger.info(f"✅ TOOL RESULT: {str(result)[:200]}...")
            return json.dumps(result, ensure_ascii=False)

        except Exception as e:
            logger.error(f"❌ TOOL ERROR: {str(e)}")
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    async def _list_products(self, args: Dict[str, Any]) -> Dict:
        """List products from backend."""
        params = {
            "shop_id": args["shop_id"],
            "enabled_only": args.get("enabled_only", True)
        }

        if "product_type" in args:
            params["product_type"] = args["product_type"]
        if "min_price" in args:
            params["min_price"] = args["min_price"]
        if "max_price" in args:
            params["max_price"] = args["max_price"]
        if "limit" in args:
            params["limit"] = args["limit"]

        response = await self.client.get(f"{self.backend_url}/products/", params=params)
        response.raise_for_status()
        return response.json()

    async def _get_product(self, args: Dict[str, Any]) -> Dict:
        """
        Get detailed product information by ID.

        FIX BUG 1: Implement get_product tool for Claude.
        """
        product_id = args.get("product_id")
        if not product_id:
            return {"error": "product_id is required"}

        try:
            response = await self.client.get(
                f"{self.backend_url}/products/{product_id}",
                params={"shop_id": args.get("shop_id", self.shop_id)}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return {"error": f"Product {product_id} not found"}
            return {"error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            return {"error": str(e)}

    async def _get_working_hours(self, args: Dict[str, Any]) -> Dict:
        """
        Get shop working hours and availability.

        FIX BUG 1: Implement get_working_hours tool for Claude.
        """
        try:
            shop_id = args.get("shop_id", self.shop_id)
            response = await self.client.get(
                f"{self.backend_url}/shop/settings/public",
                params={"shop_id": shop_id}
            )
            response.raise_for_status()
            settings = response.json()

            # Extract working hours info for AI
            hours_info = {
                "shop_name": settings.get("shop_name"),
                "weekday_hours": settings.get("weekday_hours"),
                "weekend_hours": settings.get("weekend_hours"),
                "weekday_closed": settings.get("weekday_closed"),
                "weekend_closed": settings.get("weekend_closed"),
                "phone": settings.get("phone"),
                "address": settings.get("address"),
                "city": settings.get("city")
            }

            return hours_info
        except Exception as e:
            return {"error": str(e)}

    async def _create_order(self, args: Dict[str, Any]) -> Dict:
        """
        Create order via backend.

        Parses natural language dates/times and transforms fields to backend format.
        """
        # Extract shop_id for query params (safe to modify now - we operate on a copy)
        shop_id = args.pop("shop_id", self.shop_id)

        # Parse delivery_date and delivery_time if present
        if "delivery_date" in args and args["delivery_date"]:
            date_iso = self._parse_natural_date(args["delivery_date"])
            time_str = self._parse_natural_time(args.get("delivery_time", "12:00"))

            # Combine date and time into ISO datetime
            args["delivery_date"] = f"{date_iso}T{time_str}:00"

            # Remove delivery_time as it's now part of delivery_date
            if "delivery_time" in args:
                del args["delivery_time"]

            logger.info(f"📅 Parsed datetime: {args['delivery_date']}")

        # Transform field names from AI format to backend format
        # AI uses: customer_name, customer_phone
        # Backend expects: customerName, phone
        if "customer_name" in args:
            args["customerName"] = args["customer_name"]
            del args["customer_name"]
        if "customer_phone" in args:
            args["phone"] = args["customer_phone"]
            del args["customer_phone"]

        response = await self.client.post(
            f"{self.backend_url}/orders/public/create",
            params={"shop_id": shop_id},  # shop_id goes in query params
            json=args
        )
        response.raise_for_status()
        return response.json()

    async def _track_order_by_phone(self, args: Dict[str, Any]) -> Dict:
        """Track order by phone."""
        phone = args["customer_phone"]
        shop_id = args["shop_id"]

        response = await self.client.get(
            f"{self.backend_url}/orders/public/track/phone/{phone}",
            params={"shop_id": shop_id}
        )
        response.raise_for_status()
        return response.json()

    async def _get_shop_settings(self, args: Dict[str, Any]) -> Dict:
        """Get shop settings."""
        response = await self.client.get(
            f"{self.backend_url}/shop/settings",
            params={"shop_id": args["shop_id"]}
        )
        response.raise_for_status()
        return response.json()

    async def _update_order(self, args: Dict[str, Any]) -> Dict:
        """
        Update order.

        Parses natural language dates/times before sending to backend.
        """
        tracking_id = args.pop("tracking_id")
        shop_id = args.pop("shop_id", None)  # Remove shop_id if present

        # Parse delivery_date and delivery_time if present
        if "delivery_date" in args and args["delivery_date"]:
            date_iso = self._parse_natural_date(args["delivery_date"])
            time_str = self._parse_natural_time(args.get("delivery_time", "12:00"))

            # Combine date and time into ISO datetime
            args["delivery_date"] = f"{date_iso}T{time_str}:00"

            # Remove delivery_time as it's now part of delivery_date
            args.pop("delivery_time", None)

            logger.info(f"📅 Parsed datetime for update: {args['delivery_date']}")

        response = await self.client.put(
            f"{self.backend_url}/orders/by-tracking/{tracking_id}",
            params={"changed_by": "customer"},  # Track who made the change
            json=args
        )
        response.raise_for_status()
        return response.json()

    async def _kaspi_create_payment(self, args: Dict[str, Any]) -> Dict:
        """
        Create Kaspi Pay payment.

        Args:
            args: {phone: str, amount: float, message: str}

        Returns:
            Dict with external_id and status
        """
        try:
            response = await self.client.post(
                f"{self.backend_url}/kaspi/create",
                json={
                    "phone": args["phone"],
                    "amount": args["amount"],
                    "message": args["message"]
                }
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Kaspi create payment error: {e.response.status_code} - {e.response.text}")
            return {"error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            logger.error(f"Kaspi create payment error: {str(e)}")
            return {"error": str(e)}

    async def _kaspi_check_payment_status(self, args: Dict[str, Any]) -> Dict:
        """
        Check Kaspi Pay payment status.

        Args:
            args: {external_id: str}

        Returns:
            Dict with status (Wait/Processed/Error)
        """
        external_id = args.get("external_id")
        if not external_id:
            return {"error": "external_id is required"}

        try:
            response = await self.client.get(
                f"{self.backend_url}/kaspi/status/{external_id}"
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Kaspi check status error: {e.response.status_code} - {e.response.text}")
            return {"error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            logger.error(f"Kaspi check status error: {str(e)}")
            return {"error": str(e)}

    async def _kaspi_get_payment_details(self, args: Dict[str, Any]) -> Dict:
        """
        Get Kaspi Pay payment details including available refund amount.

        Args:
            args: {external_id: str}

        Returns:
            Dict with total_amount, available_return_amount, etc.
        """
        external_id = args.get("external_id")
        if not external_id:
            return {"error": "external_id is required"}

        try:
            response = await self.client.get(
                f"{self.backend_url}/kaspi/details/{external_id}"
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"Kaspi details endpoint not available on this backend")
                return {"error": "Details endpoint not available on this backend (404)"}
            logger.error(f"Kaspi get details error: {e.response.status_code} - {e.response.text}")
            return {"error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            logger.error(f"Kaspi get details error: {str(e)}")
            return {"error": str(e)}

    async def _kaspi_refund_payment(self, args: Dict[str, Any]) -> Dict:
        """
        Refund Kaspi Pay payment (full or partial).

        Args:
            args: {external_id: str, amount: float}

        Returns:
            Dict with success status
        """
        external_id = args.get("external_id")
        amount = args.get("amount")

        if not external_id:
            return {"error": "external_id is required"}
        if not amount:
            return {"error": "amount is required"}

        try:
            response = await self.client.post(
                f"{self.backend_url}/kaspi/refund",
                json={
                    "external_id": external_id,
                    "amount": amount
                }
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Kaspi refund error: {e.response.status_code} - {e.response.text}")
            if e.response.status_code == 400:
                # Insufficient funds error
                return {"error": f"Insufficient funds: {e.response.text}"}
            return {"error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            logger.error(f"Kaspi refund error: {str(e)}")
            return {"error": str(e)}

    async def _get_client_profile(self, args: Dict[str, Any]) -> Dict:
        """
        Get client profile for AI personalization.

        Args:
            args: {customer_phone: str}

        Returns:
            Dict with budget preferences, frequent recipients, last order date
        """
        customer_phone = args.get("customer_phone")
        if not customer_phone:
            return {"error": "customer_phone is required"}

        try:
            # TODO: Replace with actual auth token once we have user authentication in MCP
            # For now, use shop_id from constructor
            response = await self.client.get(
                f"{self.backend_url}/client_profile",
                params={"phone": customer_phone},
                headers={"shop_id": str(self.shop_id)}  # Temporary: will use JWT token later
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return {"error": f"Client profile not found for phone {customer_phone}"}
            logger.error(f"Get client profile error: {e.response.status_code} - {e.response.text}")
            return {"error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            logger.error(f"Get client profile error: {str(e)}")
            return {"error": str(e)}

    async def _update_profile_privacy(self, args: Dict[str, Any]) -> Dict:
        """
        Update client profile privacy settings (GDPR).

        Args:
            args: {customer_phone: str, action: str}
            action: "enable_personalization", "disable_personalization", or "delete_profile_data"

        Returns:
            Dict with success status and message
        """
        customer_phone = args.get("customer_phone")
        action = args.get("action")

        if not customer_phone:
            return {"error": "customer_phone is required"}
        if not action:
            return {"error": "action is required"}

        valid_actions = ["enable_personalization", "disable_personalization", "delete_profile_data"]
        if action not in valid_actions:
            return {"error": f"Invalid action. Must be one of: {', '.join(valid_actions)}"}

        try:
            # TODO: Replace with actual auth token once we have user authentication in MCP
            response = await self.client.patch(
                f"{self.backend_url}/client_profile/privacy",
                params={"phone": customer_phone, "action": action},
                headers={"shop_id": str(self.shop_id)}  # Temporary: will use JWT token later
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return {"error": f"Client not found for phone {customer_phone}"}
            logger.error(f"Update profile privacy error: {e.response.status_code} - {e.response.text}")
            return {"error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            logger.error(f"Update profile privacy error: {str(e)}")
            return {"error": str(e)}

    def _mask_sensitive_data(self, data: Any) -> Any:
        """
        Recursively mask sensitive values (like Telegram bot tokens) for logging.
        """
        if isinstance(data, dict):
            return {key: self._mask_sensitive_data(value) for key, value in data.items()}
        if isinstance(data, list):
            return [self._mask_sensitive_data(item) for item in data]
        if isinstance(data, str) and self._is_telegram_file_url(data):
            return self._sanitize_telegram_url(data)
        return data

    @staticmethod
    def _sanitize_telegram_url(url: str) -> str:
        """
        Mask Telegram bot token in file URLs.
        """
        try:
            parsed = urlparse(url)
            path_parts = parsed.path.split("/")
            if len(path_parts) >= 3 and path_parts[1] == "file" and path_parts[2].startswith("bot"):
                path_parts[2] = "bot<hidden>"
                return parsed._replace(path="/".join(path_parts)).geturl()
        except Exception:
            return url
        return url

    @staticmethod
    def _is_telegram_file_url(url: Optional[str]) -> bool:
        if not url:
            return False
        try:
            parsed = urlparse(url)
            return parsed.netloc == "api.telegram.org" and parsed.path.startswith("/file/bot")
        except Exception:
            return False

    async def _download_telegram_image(self, url: str) -> tuple[bytes, Optional[str]]:
        """
        Download image bytes from Telegram CDN. Returns (bytes, content_type).
        """
        response = await self.client.get(url)
        response.raise_for_status()
        content_type = response.headers.get("content-type", "image/jpeg")
        return await response.aread(), content_type

    @staticmethod
    def _encode_image_to_data_uri(image_bytes: bytes, content_type: Optional[str]) -> str:
        """
        Encode raw image bytes into data URI expected by visual search worker.
        Visual Search Worker only accepts: png, jpeg, jpg, webp
        """
        mime = content_type or "image/jpeg"

        # Normalize MIME type to match Visual Search Worker validation
        # Worker accepts: data:image/(png|jpeg|jpg|webp);base64,
        mime_lower = mime.lower()
        if "jpeg" in mime_lower or "jpg" in mime_lower:
            mime = "image/jpeg"
        elif "png" in mime_lower:
            mime = "image/png"
        elif "webp" in mime_lower:
            mime = "image/webp"
        else:
            # Default to jpeg for unknown types
            mime = "image/jpeg"

        encoded = base64.b64encode(image_bytes).decode("ascii")
        return f"data:{mime};base64,{encoded}"

    async def _search_similar_bouquets(self, args: Dict[str, Any]) -> Dict:
        """
        Search for similar bouquets using AI visual search.

        Args:
            args: {image_url: str, topK: int (optional, default 5)}

        Returns:
            Dict with exact matches (85%+) and similar matches (70-85%)
        """
        image_url = args.get("image_url")
        image_base64 = args.get("image_base64")
        if not image_url and not image_base64:
            return {"error": "image_url or image_base64 is required"}

        topK = args.get("topK", 5)

        try:
            # Call Cloudflare Visual Search Worker
            payload = {"topK": topK}

            if image_base64:
                payload["image_base64"] = image_base64
            elif image_url and self._is_telegram_file_url(image_url):
                image_bytes, content_type = await self._download_telegram_image(image_url)
                encoded_uri = self._encode_image_to_data_uri(image_bytes, content_type)
                payload["image_base64"] = encoded_uri
                # Debug logging
                logger.info(f"Visual search - Downloaded {len(image_bytes)} bytes, content_type: {content_type}")
                logger.info(f"Visual search - Data URI prefix: {encoded_uri[:100]}...")
                logger.info(f"Visual search - Data URI length: {len(encoded_uri)}")
            else:
                payload["image_url"] = image_url

            logger.info(f"Visual search - Sending payload with keys: {list(payload.keys())}")

            response = await self.client.post(
                "https://visual-search.alekenov.workers.dev/search",
                json=payload,
                timeout=30.0  # Visual search can take a while
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Visual search error: {e.response.status_code} - {e.response.text}")
            return {"error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            logger.error(f"Visual search error: {str(e)}")
            return {"error": str(e)}

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
