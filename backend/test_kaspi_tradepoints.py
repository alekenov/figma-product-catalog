#!/usr/bin/env python3
"""
Kaspi Trade Points API Tester - r3 усиленная схема

Тестирует получение списка торговых точек через Kaspi QR API
с использованием mTLS (mutual TLS) аутентификации.

Использование:
    python test_kaspi_tradepoints.py [--bin BIN] [--env prod|test]
"""

import requests
import uuid
import sys
import argparse
from typing import Dict, Any, Optional


class KaspiTradePointsClient:
    """Клиент для работы с Kaspi Trade Points API"""

    # API endpoints
    ENDPOINTS = {
        "test": "https://mtokentest.kaspi.kz:8545",
        "prod": "https://mtoke.kaspi.kz:8545"
    }

    def __init__(
        self,
        cert_path: str,
        key_path: str,
        key_password: str,
        environment: str = "test"
    ):
        """
        Инициализация клиента

        Args:
            cert_path: Путь к клиентскому сертификату (.cer)
            key_path: Путь к приватному ключу (.key)
            key_password: Пароль для приватного ключа
            environment: Окружение - "test" или "prod"
        """
        self.cert_path = cert_path
        self.key_path = key_path
        self.key_password = key_password
        self.base_url = self.ENDPOINTS.get(environment, self.ENDPOINTS["test"])
        self.environment = environment

    def get_trade_points(self, organization_bin: str) -> Dict[str, Any]:
        """
        Получить список торговых точек для организации

        Args:
            organization_bin: БИН организации (12 цифр)

        Returns:
            Ответ от API с торговыми точками

        Example:
            >>> client.get_trade_points("991011000048")
            {
                "StatusCode": 0,
                "Message": "OK",
                "Data": [
                    {"TradePointId": 1, "TradePointName": "Магазин 1"},
                    {"TradePointId": 2, "TradePointName": "Магазин 2"}
                ]
            }
        """
        url = f"{self.base_url}/r3/v01/partner/tradepoints/{organization_bin}"

        headers = {
            "X-Request-ID": str(uuid.uuid4()),
            "Content-Type": "application/json"
        }

        print(f"\n{'='*60}")
        print(f"Запрос к Kaspi Trade Points API")
        print(f"{'='*60}")
        print(f"Environment: {self.environment}")
        print(f"URL: {url}")
        print(f"БИН: {organization_bin}")
        print(f"Сертификат: {self.cert_path}")
        print(f"Ключ: {self.key_path}")
        print(f"Request-ID: {headers['X-Request-ID']}")
        print(f"{'='*60}\n")

        try:
            # ВАЖНО: requests не поддерживает пароли для ключей напрямую
            # Ключ должен быть расшифрован заранее или использовать PEM без пароля
            # Для продакшн использовать openssl для декодирования ключа:
            # openssl rsa -in cvety-new.key -out cvety-new-decrypted.key -passin pass:PASSWORD

            response = requests.get(
                url,
                cert=(self.cert_path, self.key_path),
                headers=headers,
                verify=True,  # Проверять SSL сертификат сервера
                timeout=30
            )

            print(f"HTTP Status: {response.status_code}")
            print(f"Response Headers:")
            for key, value in response.headers.items():
                print(f"  {key}: {value}")
            print()

            # Попытка распарсить JSON
            try:
                data = response.json()
                print(f"Response Body (JSON):")
                import json
                print(json.dumps(data, indent=2, ensure_ascii=False))
                return data
            except ValueError:
                print(f"Response Body (Text):")
                print(response.text)
                return {"error": "Invalid JSON response", "text": response.text}

        except requests.exceptions.SSLError as e:
            print(f"❌ SSL/TLS ошибка: {e}")
            print("\nВозможные причины:")
            print("1. Неверный сертификат или ключ")
            print("2. Сертификат истек")
            print("3. IP адрес не в whitelist у Kaspi")
            print("4. Требуется расшифровать ключ (если защищен паролем)")
            return {"error": "SSL error", "details": str(e)}

        except requests.exceptions.ConnectionError as e:
            print(f"❌ Ошибка подключения: {e}")
            return {"error": "Connection error", "details": str(e)}

        except requests.exceptions.Timeout:
            print(f"❌ Timeout: запрос превысил 30 секунд")
            return {"error": "Timeout"}

        except Exception as e:
            print(f"❌ Неизвестная ошибка: {e}")
            return {"error": "Unknown error", "details": str(e)}

    def register_device(
        self,
        organization_bin: str,
        device_id: str,
        trade_point_id: int
    ) -> Dict[str, Any]:
        """
        Зарегистрировать устройство (кассу/терминал)

        Args:
            organization_bin: БИН организации
            device_id: Уникальный ID устройства (например, "cvety-kiosk-001")
            trade_point_id: ID торговой точки из get_trade_points()

        Returns:
            Ответ с DeviceToken для дальнейших операций
        """
        url = f"{self.base_url}/r3/v01/device/register"

        headers = {
            "X-Request-ID": str(uuid.uuid4()),
            "Content-Type": "application/json"
        }

        payload = {
            "OrganizationBin": organization_bin,
            "DeviceId": device_id,
            "TradePointId": trade_point_id
        }

        print(f"\n{'='*60}")
        print(f"Регистрация устройства")
        print(f"{'='*60}")
        print(f"URL: {url}")
        print(f"Payload:")
        import json
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        print(f"{'='*60}\n")

        try:
            response = requests.post(
                url,
                cert=(self.cert_path, self.key_path),
                headers=headers,
                json=payload,
                verify=True,
                timeout=30
            )

            print(f"HTTP Status: {response.status_code}")

            try:
                data = response.json()
                print(f"Response:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                return data
            except ValueError:
                print(f"Response (Text): {response.text}")
                return {"error": "Invalid JSON response", "text": response.text}

        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return {"error": str(e)}


def main():
    """Главная функция для запуска из командной строки"""
    parser = argparse.ArgumentParser(
        description="Kaspi Trade Points API Tester"
    )
    parser.add_argument(
        "--bin",
        default="991011000048",
        help="БИН организации (default: 991011000048)"
    )
    parser.add_argument(
        "--env",
        choices=["test", "prod"],
        default="test",
        help="Окружение: test или prod (default: test)"
    )
    parser.add_argument(
        "--cert",
        default="/home/bitrix/kaspi_certificates/prod/cvety.cer",
        help="Путь к сертификату"
    )
    parser.add_argument(
        "--key",
        default="/home/bitrix/kaspi_certificates/prod/cvety-new.key",
        help="Путь к ключу"
    )
    parser.add_argument(
        "--password",
        default="sy3t6G2HhuG1m4pEK8AJ2",
        help="Пароль для ключа"
    )
    parser.add_argument(
        "--register-device",
        action="store_true",
        help="Зарегистрировать устройство после получения торговых точек"
    )
    parser.add_argument(
        "--device-id",
        default="cvety-railway-test-001",
        help="ID устройства для регистрации"
    )

    args = parser.parse_args()

    # Создаем клиент
    client = KaspiTradePointsClient(
        cert_path=args.cert,
        key_path=args.key,
        key_password=args.password,
        environment=args.env
    )

    # Получаем торговые точки
    result = client.get_trade_points(args.bin)

    # Проверяем успех
    if result.get("StatusCode") == 0:
        print("\n✅ Успешно получены торговые точки!")
        trade_points = result.get("Data", [])
        print(f"\nНайдено торговых точек: {len(trade_points)}")

        for tp in trade_points:
            print(f"  - ID: {tp.get('TradePointId')}, Название: {tp.get('TradePointName')}")

        # Регистрация устройства (если запрошено)
        if args.register_device and trade_points:
            first_tp_id = trade_points[0].get("TradePointId")
            print(f"\n📝 Регистрируем устройство на торговой точке {first_tp_id}...")

            device_result = client.register_device(
                organization_bin=args.bin,
                device_id=args.device_id,
                trade_point_id=first_tp_id
            )

            if device_result.get("StatusCode") == 0:
                device_token = device_result.get("Data", {}).get("DeviceToken")
                print(f"\n✅ Устройство зарегистрировано!")
                print(f"DeviceToken: {device_token}")
                print(f"\n💡 Сохраните DeviceToken в таблице KaspiPayConfig:")
                print(f"  - organization_bin: {args.bin}")
                print(f"  - trade_point_id: {first_tp_id}")
                print(f"  - device_token: {device_token}")
            else:
                print(f"\n❌ Ошибка регистрации устройства")
                print(f"StatusCode: {device_result.get('StatusCode')}")
                print(f"Message: {device_result.get('Message')}")

    else:
        print("\n❌ Ошибка получения торговых точек")
        status_code = result.get("StatusCode", "unknown")
        message = result.get("Message", result.get("error", "Unknown error"))

        print(f"StatusCode: {status_code}")
        print(f"Message: {message}")

        # Подсказки по кодам ошибок
        error_hints = {
            -10000: "Ошибка авторизации - проверьте сертификат и IP whitelist",
            -999: "Техническая ошибка Kaspi API",
            -14000002: "Торговые точки не найдены для данного БИНа"
        }

        if status_code in error_hints:
            print(f"\n💡 {error_hints[status_code]}")


if __name__ == "__main__":
    main()
