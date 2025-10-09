"""MCP Tools schema for Claude function calling."""

from typing import List, Dict, Any


def get_tools_schema() -> List[Dict[str, Any]]:
    """
    Get MCP tools schema for Claude function calling.

    Returns list of tools that Claude can call to interact with backend.
    """
    return [
        {
            "name": "list_products",
            "description": "Получить список цветов и букетов с фильтрацией по названию, типу, цене",
            "input_schema": {
                "type": "object",
                "properties": {
                    "search": {
                        "type": "string",
                        "description": "Поиск по названию продукта"
                    },
                    "product_type": {
                        "type": "string",
                        "enum": ["ready", "custom", "subscription"],
                        "description": "Тип товара: ready (готовый букет), custom (на заказ), subscription (подписка)"
                    },
                    "min_price": {
                        "type": "integer",
                        "description": "Минимальная цена в тиынах (1 тенге = 100 тиынов)"
                    },
                    "max_price": {
                        "type": "integer",
                        "description": "Максимальная цена в тиынах"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Количество результатов (по умолчанию 20)",
                        "default": 20
                    }
                },
                "required": []
            }
        },
        {
            "name": "get_product",
            "description": "Получить подробную информацию о конкретном товаре по ID",
            "input_schema": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "integer",
                        "description": "ID товара"
                    }
                },
                "required": ["product_id"]
            }
        },
        {
            "name": "create_order",
            "description": "Создать новый заказ на доставку цветов. Возвращает объект с полями: orderNumber, tracking_id. ОБЯЗАТЕЛЬНО используй tracking_id для ссылки отслеживания.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "customer_name": {
                        "type": "string",
                        "description": "Полное имя клиента (заказчика)"
                    },
                    "customer_phone": {
                        "type": "string",
                        "description": "Номер телефона клиента"
                    },
                    "delivery_address": {
                        "type": "string",
                        "description": "Адрес доставки. Можно передать 'Адрес уточнит менеджер' если клиент просит уточнить у получателя."
                    },
                    "delivery_date": {
                        "type": "string",
                        "description": "Передавай естественную фразу: 'сегодня', 'завтра', 'послезавтра', 'через 2 дня'"
                    },
                    "delivery_time": {
                        "type": "string",
                        "description": "Передавай естественную фразу: 'утром', 'днем', 'вечером', 'как можно скорее', '18:00'"
                    },
                    "delivery_type": {
                        "type": "string",
                        "enum": ["delivery", "pickup"],
                        "description": "Тип: delivery (доставка) или pickup (самовывоз)"
                    },
                    "items": {
                        "type": "array",
                        "description": "Список товаров в заказе",
                        "items": {
                            "type": "object",
                            "properties": {
                                "product_id": {"type": "integer"},
                                "quantity": {"type": "integer"}
                            },
                            "required": ["product_id", "quantity"]
                        }
                    },
                    "total_price": {
                        "type": "integer",
                        "description": "Общая сумма в тиынах (цена в тенге * 100)"
                    },
                    "recipient_name": {
                        "type": "string",
                        "description": "Имя получателя (если заказ для другого человека)"
                    },
                    "recipient_phone": {
                        "type": "string",
                        "description": "Телефон получателя (если заказ для другого человека)"
                    },
                    "notes": {
                        "type": "string",
                        "description": "Дополнительные пожелания к заказу"
                    }
                },
                "required": [
                    "customer_name",
                    "customer_phone",
                    "delivery_address",
                    "delivery_date",
                    "delivery_time",
                    "items",
                    "total_price"
                ]
            }
        },
        {
            "name": "track_order_by_phone",
            "description": "Отследить заказы клиента по номеру телефона",
            "input_schema": {
                "type": "object",
                "properties": {
                    "customer_phone": {
                        "type": "string",
                        "description": "Номер телефона клиента"
                    }
                },
                "required": ["customer_phone"]
            }
        },
        {
            "name": "update_order",
            "description": "Изменить данные заказа (адрес, дата, время, и т.д.) по tracking_id",
            "input_schema": {
                "type": "object",
                "properties": {
                    "tracking_id": {
                        "type": "string",
                        "description": "9-значный tracking ID заказа"
                    },
                    "delivery_address": {
                        "type": "string",
                        "description": "Новый адрес доставки"
                    },
                    "delivery_date": {
                        "type": "string",
                        "description": "Новая дата доставки ('сегодня', 'завтра', '2025-10-15')"
                    },
                    "delivery_time": {
                        "type": "string",
                        "description": "Новое время доставки ('утром', '18:00', и т.д.)"
                    },
                    "recipient_name": {
                        "type": "string",
                        "description": "Новое имя получателя"
                    },
                    "notes": {
                        "type": "string",
                        "description": "Дополнительные заметки"
                    }
                },
                "required": ["tracking_id"]
            }
        },
        {
            "name": "get_working_hours",
            "description": "Получить расписание работы магазина на неделю",
            "input_schema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "get_shop_settings",
            "description": "Получить настройки и информацию о магазине",
            "input_schema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    ]
