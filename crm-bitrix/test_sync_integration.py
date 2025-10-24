#!/usr/bin/env python3
"""
Bitrix ↔ Railway Integration Test Suite

Comprehensive testing for order status sync and product sync functionality.
Tests both direction of synchronization with error handling and performance monitoring.
"""

import os
import sys
import json
import time
import asyncio
import httpx
import argparse
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from enum import Enum


# Configuration
RAILWAY_API_URL = "https://figma-product-catalog-production.up.railway.app/api/v1"
BITRIX_URL = "https://cvety.kz"
WEBHOOK_SECRET = "cvety-webhook-2025-secure-key"
ADMIN_PHONE = "+77015211545"
ADMIN_PASSWORD = "1234"  # From project context


class TestStatus(str, Enum):
    """Test result status"""
    PASS = "PASS"
    FAIL = "FAIL"
    SKIP = "SKIP"
    PENDING = "PENDING"


@dataclass
class TestResult:
    """Single test result"""
    test_name: str
    status: TestStatus
    duration: float
    message: str = ""
    details: Dict[str, Any] = None
    timestamp: str = None

    def __post_init__(self):
        if self.details is None:
            self.details = {}
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self):
        return {
            "test_name": self.test_name,
            "status": self.status.value,
            "duration": round(self.duration, 3),
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp
        }


class SyncTester:
    """Integration tester for Bitrix ↔ Railway sync"""

    def __init__(self):
        self.results: List[TestResult] = []
        self.jwt_token: Optional[str] = None
        self.test_order_id: int = 123456  # Test order ID
        self.test_product_id: int = 668826  # Test product ID

    async def setup(self):
        """Setup test environment - get JWT token"""
        print("🔧 Setting up test environment...")
        try:
            async with httpx.AsyncClient() as client:
                # Login to get JWT token
                response = await client.post(
                    f"{RAILWAY_API_URL}/auth/login",
                    json={"phone": ADMIN_PHONE, "password": ADMIN_PASSWORD},
                    timeout=10.0
                )
                if response.status_code == 200:
                    data = response.json()
                    self.jwt_token = data.get("access_token")
                    print(f"✅ JWT Token obtained for {ADMIN_PHONE}")
                else:
                    print(f"❌ Failed to get JWT token: {response.status_code}")
                    print(response.text)
                    return False
        except Exception as e:
            print(f"❌ Setup failed: {e}")
            return False
        return True

    def record_result(
        self,
        test_name: str,
        status: TestStatus,
        duration: float,
        message: str = "",
        details: Optional[Dict[str, Any]] = None
    ):
        """Record test result"""
        result = TestResult(
            test_name=test_name,
            status=status,
            duration=duration,
            message=message,
            details=details or {}
        )
        self.results.append(result)
        status_emoji = "✅" if status == TestStatus.PASS else "❌" if status == TestStatus.FAIL else "⏭️"
        print(f"{status_emoji} {test_name}: {status.value} ({duration:.3f}s)")
        if message:
            print(f"   {message}")

    # =====================================================================
    # PHASE 2: Functional Tests
    # =====================================================================

    async def test_webhook_auth_invalid_secret(self):
        """Test 2.1.1: Webhook rejects invalid secret"""
        print("\n📋 Test 2.1.1: Webhook Authentication - Invalid Secret")
        start_time = time.time()

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{RAILWAY_API_URL}/webhooks/order-status-sync",
                    headers={"X-Webhook-Secret": "wrong-secret"},
                    json={"order_id": 99999, "status": "AP"},
                    timeout=10.0
                )

                duration = time.time() - start_time

                if response.status_code == 401:
                    self.record_result(
                        "webhook_auth_invalid_secret",
                        TestStatus.PASS,
                        duration,
                        "Correctly returned 401 Unauthorized",
                        {"http_status": 401}
                    )
                else:
                    self.record_result(
                        "webhook_auth_invalid_secret",
                        TestStatus.FAIL,
                        duration,
                        f"Expected 401, got {response.status_code}",
                        {"http_status": response.status_code, "response": response.text}
                    )
        except Exception as e:
            duration = time.time() - start_time
            self.record_result(
                "webhook_auth_invalid_secret",
                TestStatus.FAIL,
                duration,
                str(e)
            )

    async def test_webhook_auth_missing_secret(self):
        """Test 2.1.2: Webhook rejects missing secret header"""
        print("📋 Test 2.1.2: Webhook Authentication - Missing Secret Header")
        start_time = time.time()

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{RAILWAY_API_URL}/webhooks/order-status-sync",
                    json={"order_id": 99999, "status": "AP"},
                    timeout=10.0
                )

                duration = time.time() - start_time

                if response.status_code == 401:
                    self.record_result(
                        "webhook_auth_missing_secret",
                        TestStatus.PASS,
                        duration,
                        "Correctly returned 401 when secret header missing",
                        {"http_status": 401}
                    )
                else:
                    self.record_result(
                        "webhook_auth_missing_secret",
                        TestStatus.FAIL,
                        duration,
                        f"Expected 401, got {response.status_code}",
                        {"http_status": response.status_code}
                    )
        except Exception as e:
            duration = time.time() - start_time
            self.record_result(
                "webhook_auth_missing_secret",
                TestStatus.FAIL,
                duration,
                str(e)
            )

    async def test_webhook_auth_valid_secret(self):
        """Test 2.1.3: Webhook accepts valid secret"""
        print("📋 Test 2.1.3: Webhook Authentication - Valid Secret")
        start_time = time.time()

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{RAILWAY_API_URL}/webhooks/order-status-sync",
                    headers={"X-Webhook-Secret": WEBHOOK_SECRET},
                    json={"order_id": 99999, "status": "AP", "changed_by_id": 1},
                    timeout=10.0
                )

                duration = time.time() - start_time

                if response.status_code == 200:
                    data = response.json()
                    self.record_result(
                        "webhook_auth_valid_secret",
                        TestStatus.PASS,
                        duration,
                        "Correctly returned 200 with valid secret",
                        {"http_status": 200, "response": data}
                    )
                else:
                    self.record_result(
                        "webhook_auth_valid_secret",
                        TestStatus.FAIL,
                        duration,
                        f"Expected 200, got {response.status_code}",
                        {"http_status": response.status_code, "response": response.text}
                    )
        except Exception as e:
            duration = time.time() - start_time
            self.record_result(
                "webhook_auth_valid_secret",
                TestStatus.FAIL,
                duration,
                str(e)
            )

    async def test_invalid_order_not_found(self):
        """Test 2.3: Webhook handles non-existent order gracefully"""
        print("📋 Test 2.3: Non-existent Order Handling")
        start_time = time.time()

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{RAILWAY_API_URL}/webhooks/order-status-sync",
                    headers={"X-Webhook-Secret": WEBHOOK_SECRET},
                    json={"order_id": 999999999, "status": "AP"},
                    timeout=10.0
                )

                duration = time.time() - start_time
                data = response.json()

                if response.status_code == 200 and data.get("status") == "skipped":
                    self.record_result(
                        "invalid_order_not_found",
                        TestStatus.PASS,
                        duration,
                        "Correctly skipped non-existent order",
                        {"response": data}
                    )
                else:
                    self.record_result(
                        "invalid_order_not_found",
                        TestStatus.FAIL,
                        duration,
                        f"Expected skipped status, got {data.get('status')}",
                        {"response": data}
                    )
        except Exception as e:
            duration = time.time() - start_time
            self.record_result(
                "invalid_order_not_found",
                TestStatus.FAIL,
                duration,
                str(e)
            )

    async def test_unknown_status_code(self):
        """Test 2.3.2: Webhook handles unknown status codes"""
        print("📋 Test 2.3.2: Unknown Status Code Handling")
        start_time = time.time()

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{RAILWAY_API_URL}/webhooks/order-status-sync",
                    headers={"X-Webhook-Secret": WEBHOOK_SECRET},
                    json={"order_id": 123456, "status": "UNKNOWN_STATUS"},
                    timeout=10.0
                )

                duration = time.time() - start_time
                data = response.json()

                if response.status_code == 200 and data.get("status") == "skipped":
                    self.record_result(
                        "unknown_status_code",
                        TestStatus.PASS,
                        duration,
                        "Correctly skipped unknown status",
                        {"response": data}
                    )
                else:
                    self.record_result(
                        "unknown_status_code",
                        TestStatus.FAIL,
                        duration,
                        f"Expected skipped status, got {data}",
                        {"response": data}
                    )
        except Exception as e:
            duration = time.time() - start_time
            self.record_result(
                "unknown_status_code",
                TestStatus.FAIL,
                duration,
                str(e)
            )

    # =====================================================================
    # PHASE 4: Performance Tests
    # =====================================================================

    async def test_webhook_response_time(self):
        """Test 4.1: Measure webhook endpoint response time"""
        print("\n⚡ Test 4.1: Webhook Response Time (50 concurrent requests)")
        start_time = time.time()
        response_times = []

        try:
            async with httpx.AsyncClient() as client:
                for i in range(50):
                    req_start = time.time()
                    response = await client.post(
                        f"{RAILWAY_API_URL}/webhooks/order-status-sync",
                        headers={"X-Webhook-Secret": WEBHOOK_SECRET},
                        json={"order_id": 123456 + i, "status": "AP"},
                        timeout=10.0
                    )
                    req_duration = time.time() - req_start
                    response_times.append(req_duration)

                    if response.status_code not in [200, 422]:
                        print(f"  ⚠️ Request {i+1}: HTTP {response.status_code}")

            duration = time.time() - start_time
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            min_time = min(response_times)

            if avg_time < 0.5:  # < 500ms
                self.record_result(
                    "webhook_performance",
                    TestStatus.PASS,
                    duration,
                    f"Average response time: {avg_time*1000:.1f}ms (target < 500ms)",
                    {
                        "avg_time_ms": round(avg_time * 1000, 2),
                        "max_time_ms": round(max_time * 1000, 2),
                        "min_time_ms": round(min_time * 1000, 2),
                        "requests": 50
                    }
                )
            else:
                self.record_result(
                    "webhook_performance",
                    TestStatus.FAIL,
                    duration,
                    f"Average response time too high: {avg_time*1000:.1f}ms",
                    {
                        "avg_time_ms": round(avg_time * 1000, 2),
                        "max_time_ms": round(max_time * 1000, 2)
                    }
                )
        except Exception as e:
            duration = time.time() - start_time
            self.record_result(
                "webhook_performance",
                TestStatus.FAIL,
                duration,
                str(e)
            )

    async def test_health_check(self):
        """Test: Backend health endpoint"""
        print("\n🏥 Test: Backend Health Check")
        start_time = time.time()

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{RAILWAY_API_URL.replace('/api/v1', '')}/health",
                    timeout=10.0
                )

                duration = time.time() - start_time
                data = response.json() if response.status_code == 200 else {}

                if response.status_code == 200 and data.get("status") == "healthy":
                    self.record_result(
                        "health_check",
                        TestStatus.PASS,
                        duration,
                        "Backend is healthy",
                        {"status": data.get("status"), "database": data.get("checks", {}).get("database", {})}
                    )
                else:
                    self.record_result(
                        "health_check",
                        TestStatus.FAIL,
                        duration,
                        f"Health check failed: {response.status_code}",
                        {"response": data}
                    )
        except Exception as e:
            duration = time.time() - start_time
            self.record_result(
                "health_check",
                TestStatus.FAIL,
                duration,
                str(e)
            )

    # =====================================================================
    # Test Execution
    # =====================================================================

    async def run_phase2_functional_tests(self):
        """Run all Phase 2 functional tests"""
        print("\n" + "="*70)
        print("PHASE 2: FUNCTIONAL TESTS")
        print("="*70)

        await self.test_webhook_auth_invalid_secret()
        await self.test_webhook_auth_missing_secret()
        await self.test_webhook_auth_valid_secret()
        await self.test_invalid_order_not_found()
        await self.test_unknown_status_code()

    async def run_phase4_performance_tests(self):
        """Run all Phase 4 performance tests"""
        print("\n" + "="*70)
        print("PHASE 4: PERFORMANCE TESTS")
        print("="*70)

        await self.test_webhook_response_time()

    async def run_all_tests(self):
        """Run all test phases"""
        await self.test_health_check()
        await self.run_phase2_functional_tests()
        await self.run_phase4_performance_tests()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)

        total = len(self.results)
        passed = sum(1 for r in self.results if r.status == TestStatus.PASS)
        failed = sum(1 for r in self.results if r.status == TestStatus.FAIL)
        skipped = sum(1 for r in self.results if r.status == TestStatus.SKIP)

        print(f"Total: {total} | Passed: {passed} | Failed: {failed} | Skipped: {skipped}")
        print(f"Success Rate: {(passed/total*100):.1f}%")

        if failed > 0:
            print("\n❌ Failed Tests:")
            for result in self.results:
                if result.status == TestStatus.FAIL:
                    print(f"  - {result.test_name}: {result.message}")

        print("\n" + "="*70)

    def export_results(self, filename: str = "test_results.json"):
        """Export test results to JSON"""
        output = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(self.results),
            "passed": sum(1 for r in self.results if r.status == TestStatus.PASS),
            "failed": sum(1 for r in self.results if r.status == TestStatus.FAIL),
            "skipped": sum(1 for r in self.results if r.status == TestStatus.SKIP),
            "results": [r.to_dict() for r in self.results]
        }

        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)

        print(f"\n📊 Results exported to {filename}")


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Bitrix ↔ Railway Integration Test Suite"
    )
    parser.add_argument(
        "phase",
        choices=["health", "phase2", "phase4", "all"],
        nargs="?",
        default="all",
        help="Which test phase to run"
    )
    parser.add_argument(
        "--export",
        action="store_true",
        help="Export results to JSON"
    )

    args = parser.parse_args()

    tester = SyncTester()

    if not await tester.setup():
        print("❌ Setup failed, exiting")
        sys.exit(1)

    if args.phase == "health":
        await tester.test_health_check()
    elif args.phase == "phase2":
        await tester.run_phase2_functional_tests()
    elif args.phase == "phase4":
        await tester.run_phase4_performance_tests()
    elif args.phase == "all":
        await tester.run_all_tests()

    tester.print_summary()

    if args.export:
        tester.export_results()


if __name__ == "__main__":
    asyncio.run(main())
