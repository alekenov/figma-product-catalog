"""
AI Client Service - Simulates flower shop customer with persona.
Uses Claude 4.5 with memory and interleaved thinking for realistic behavior.
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from anthropic import Anthropic

import config
from logger_analyzer import TestLogger

logger = logging.getLogger(__name__)


class AIClient:
    """
    AI Client that simulates a customer with specific persona.
    Uses Claude 4.5 with memory for realistic multi-turn conversations.
    """

    def __init__(
        self,
        persona_name: str,
        test_logger: TestLogger,
        initial_goal: str
    ):
        """
        Initialize AI Client with persona.

        Args:
            persona_name: Name of persona JSON file (without .json)
            test_logger: TestLogger instance for logging
            initial_goal: Goal/scenario for this conversation
        """
        self.logger = test_logger
        self.persona_name = persona_name
        self.initial_goal = initial_goal

        # Load persona
        self.persona = self._load_persona(persona_name)

        # Initialize Claude client
        self.client = Anthropic(api_key=config.CLAUDE_API_KEY)
        self.model = config.CLAUDE_MODEL_CLIENT

        # Conversation history
        self.messages: List[Dict[str, Any]] = []

        # Track conversation state
        self.turn_count = 0
        self.goal_achieved = False

        # Memory directory for this client
        self.memory_dir = config.MEMORIES_DIR / "clients"
        self.memory_dir.mkdir(exist_ok=True)

        logger.info(f"👤 AI Client initialized: {self.persona.get('name', persona_name)}")
        logger.info(f"🎯 Goal: {initial_goal}")

    def _load_persona(self, persona_name: str) -> Dict[str, Any]:
        """Load persona from JSON file."""
        persona_path = config.PERSONAS_DIR / f"{persona_name}.json"

        if not persona_path.exists():
            raise FileNotFoundError(f"Persona not found: {persona_path}")

        with open(persona_path, 'r', encoding='utf-8') as f:
            persona = json.load(f)

        logger.info(f"📋 Loaded persona: {persona.get('name', persona_name)}")
        return persona

    def get_system_prompt(self) -> str:
        """Generate system prompt based on persona."""
        persona = self.persona

        # Extract persona characteristics
        name = persona.get('name', 'Клиент')
        persona_type = persona.get('type', 'customer')
        characteristics = persona.get('characteristics', {})
        preferences = persona.get('preferences', {})
        communication_style = persona.get('communication_style', {})
        order_history = persona.get('order_history', [])

        # Build prompt
        prompt = f"""Ты — клиент цветочного магазина. Твоя роль: {name}

**Твоя цель в этом диалоге:**
{self.initial_goal}

**Твоя персона:**
- Тип клиента: {persona_type}
- Уровень вежливости: {characteristics.get('politeness', 'medium')}
- Решительность: {characteristics.get('decisiveness', 'medium')}
- Чувствительность к бюджету: {characteristics.get('budget_sensitivity', 'medium')}
- Частота вопросов: {characteristics.get('question_frequency', 'medium')}

**Твои предпочтения:**
"""

        if preferences.get('colors'):
            prompt += f"- Любимые цвета: {', '.join(preferences['colors'])}\n"

        if preferences.get('price_range'):
            price_min, price_max = preferences['price_range']
            prompt += f"- Бюджет: {price_min:,} - {price_max:,} тенге\n"

        if preferences.get('delivery_time'):
            prompt += f"- Предпочитаемое время доставки: {preferences['delivery_time']}\n"

        if order_history:
            prompt += f"\n**Твоя история заказов:**\n"
            for order in order_history[:3]:  # Last 3 orders
                prompt += f"- {order.get('date')}: {order.get('product')} ({order.get('price'):,}тг, оценка: {order.get('rating')}/5)\n"

        prompt += f"""
**Стиль общения:**
- Приветствие: {communication_style.get('greeting', 'neutral')}
- Запросы: {communication_style.get('requests', 'polite')}
- Жалобы: {communication_style.get('complaints', 'rare')}

**Важные правила:**
1. Веди себя естественно, как реальный клиент
2. Задавай вопросы согласно твоей персоне
3. Не торопись - реальные клиенты думают и сомневаются
4. Используй свои предпочтения (цвета, бюджет) в разговоре
5. Если ты постоянный клиент - упоминай прошлые заказы
6. Отвечай на русском языке
7. Пиши кратко и естественно (1-3 предложения за раз)

**Критерии успеха:**
- Диалог должен привести к достижению твоей цели
- Менеджер должен помочь тебе с выбором
- В конце ты либо оформишь заказ, либо останешься довольным информацией

Начни диалог сейчас!
"""

        return prompt

    async def generate_initial_message(self) -> str:
        """
        Generate the first message to start conversation.

        Returns:
            Initial greeting/request
        """
        # Add initial context
        self.messages.append({
            "role": "user",
            "content": "Начни диалог с менеджером магазина. Представься и скажи что тебе нужно."
        })

        # Call Claude
        response = self.client.messages.create(
            model=self.model,
            max_tokens=config.MAX_TOKENS,
            system=self.get_system_prompt(),
            messages=self.messages,
            extra_headers=config.CLAUDE_EXTRA_HEADERS  # Enable memory and interleaved thinking
        )

        # Extract response
        message_text = ""
        for block in response.content:
            if block.type == "thinking":
                # Log thinking block
                self.logger.log_message(
                    sender="client",
                    message_type="thinking",
                    content=block.thinking
                )
            elif block.type == "text":
                message_text += block.text

        # Add to history
        self.messages.append({
            "role": "assistant",
            "content": message_text
        })

        self.turn_count += 1

        return message_text

    async def process_manager_response(
        self,
        manager_message: str
    ) -> Optional[str]:
        """
        Process manager's response and generate next client message.

        Args:
            manager_message: Message from manager

        Returns:
            Client's next message, or None if conversation should end
        """
        # Check if client wants to end conversation
        ending_phrases = [
            "спасибо, это все",
            "благодарю, до свидания",
            "спасибо за помощь",
            "понятно, спасибо"
        ]

        if any(phrase in manager_message.lower() for phrase in ending_phrases):
            self.goal_achieved = True

        # Add manager's message to history
        self.messages.append({
            "role": "user",
            "content": f"Менеджер ответил: {manager_message}\n\nТеперь твой ответ. Если твоя цель достигнута или менеджер полностью ответил на твои вопросы, вежливо закончи диалог словами 'Спасибо за помощь!'. Иначе продолжай диалог."
        })

        # Call Claude
        response = self.client.messages.create(
            model=self.model,
            max_tokens=config.MAX_TOKENS,
            system=self.get_system_prompt(),
            messages=self.messages,
            extra_headers=config.CLAUDE_EXTRA_HEADERS
        )

        # Extract response
        client_message = ""
        for block in response.content:
            if block.type == "thinking":
                # Log thinking block (shows decision-making)
                self.logger.log_message(
                    sender="client",
                    message_type="thinking",
                    content=block.thinking
                )
            elif block.type == "text":
                client_message += block.text

        # Add to history
        self.messages.append({
            "role": "assistant",
            "content": client_message
        })

        self.turn_count += 1

        # Check if client wants to end
        if any(phrase in client_message.lower() for phrase in ending_phrases):
            self.goal_achieved = True
            return None

        # Limit conversation history
        if len(self.messages) > 30:
            self.messages = self.messages[:2] + self.messages[-28:]

        return client_message

    def should_continue(self, max_turns: int) -> bool:
        """
        Check if conversation should continue.

        Args:
            max_turns: Maximum allowed turns

        Returns:
            True if should continue, False otherwise
        """
        # Stop if goal achieved
        if self.goal_achieved:
            return False

        # Stop if max turns reached
        if self.turn_count >= max_turns:
            return False

        return True

    def get_conversation_analysis(self) -> Dict[str, Any]:
        """
        Analyze conversation from client's perspective.

        Returns:
            Analysis data
        """
        return {
            "persona": self.persona.get('name'),
            "persona_type": self.persona.get('type'),
            "goal": self.initial_goal,
            "goal_achieved": self.goal_achieved,
            "turn_count": self.turn_count,
            "conversation_length": len(self.messages)
        }
