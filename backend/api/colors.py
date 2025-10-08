"""
API эндпоинты для работы с цветами букетов
"""
from typing import Optional
from fastapi import APIRouter

router = APIRouter(prefix="/colors", tags=["colors"])

# Синхронизировано с /shared/constants/colors.js
BOUQUET_COLORS = [
    {
        "id": "red",
        "name": "Красный",
        "hex": "#FF4444",
        "description": "Красные розы, гвоздики"
    },
    {
        "id": "pink",
        "name": "Розовый",
        "hex": "#FFB6C1",
        "description": "Розовые розы, пионы"
    },
    {
        "id": "white",
        "name": "Белый",
        "hex": "#FFFFFF",
        "border": True,
        "description": "Белые розы, лилии, хризантемы"
    },
    {
        "id": "mixed",
        "name": "Микс",
        "hex": "linear-gradient(90deg, #FF4444 0%, #FFB6C1 50%, #FFD700 100%)",
        "description": "Разноцветный букет"
    },
    {
        "id": "purple",
        "name": "Фиолетовый",
        "hex": "#9B59B6",
        "description": "Фиолетовые тюльпаны, ирисы"
    },
    {
        "id": "cream",
        "name": "Кремовый",
        "hex": "#F5E6D3",
        "border": True,
        "description": "Кремовые розы, эустома"
    },
    {
        "id": "yellow",
        "name": "Желтый",
        "hex": "#FFD700",
        "description": "Желтые розы, подсолнухи"
    },
    {
        "id": "blue",
        "name": "Синий",
        "hex": "#4A90E2",
        "description": "Синие гортензии, дельфиниумы"
    }
]

@router.get("")
async def get_colors():
    """
    Получить список всех доступных цветов букетов

    Возвращает полную информацию о каждом цвете:
    - name: Русское название (сохраняется в БД)
    - hex: Hex код или CSS gradient
    - description: Примеры цветов
    - border: Нужна ли граница (для светлых цветов)
    """
    return {"colors": BOUQUET_COLORS}


def get_color_details(color_name: str) -> Optional[dict]:
    """
    Получить детали цвета по его названию

    Args:
        color_name: Русское название цвета (например, "Красный")

    Returns:
        Словарь с деталями цвета или None если не найден
    """
    for color in BOUQUET_COLORS:
        if color["name"] == color_name:
            return color
    return None
