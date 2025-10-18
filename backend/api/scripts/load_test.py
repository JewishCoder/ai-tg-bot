"""Нагрузочное тестирование API endpoint."""

import asyncio
import logging
import statistics
import time
from datetime import UTC, datetime
from typing import Any

import httpx

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class LoadTester:
    """Класс для нагрузочного тестирования API."""

    def __init__(self, base_url: str = "http://localhost:8000") -> None:
        """
        Инициализация LoadTester.

        Args:
            base_url: Базовый URL API сервера
        """
        self.base_url = base_url
        self.results: list[float] = []

    async def make_request(self, period: str) -> tuple[int, float]:
        """
        Выполнить один запрос к API.

        Args:
            period: Период для статистики ('day', 'week', 'month')

        Returns:
            Tuple (status_code, response_time_seconds)
        """
        start = time.time()

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/api/v1/stats",
                    params={"period": period},
                    timeout=30.0,
                )
                elapsed = time.time() - start
                return response.status_code, elapsed
            except Exception as e:
                elapsed = time.time() - start
                logger.error(f"Request failed: {e}")
                return 0, elapsed

    async def run_concurrent_requests(
        self, period: str, num_requests: int
    ) -> list[tuple[int, float]]:
        """
        Запустить несколько параллельных запросов.

        Args:
            period: Период для статистики
            num_requests: Количество параллельных запросов

        Returns:
            Список (status_code, response_time) для каждого запроса
        """
        tasks = [self.make_request(period) for _ in range(num_requests)]
        return await asyncio.gather(*tasks)

    async def run_load_test(
        self,
        period: str = "week",
        total_requests: int = 100,
        concurrent_users: int = 10,
    ) -> dict[str, Any]:
        """
        Запустить полное нагрузочное тестирование.

        Args:
            period: Период для статистики
            total_requests: Общее количество запросов
            concurrent_users: Количество параллельных пользователей

        Returns:
            Словарь с результатами тестирования
        """
        logger.info(f"\n{'=' * 70}")
        logger.info(f"Starting load test: {total_requests} requests, {concurrent_users} concurrent")
        logger.info(f"Period: {period}")
        logger.info(f"Target: {self.base_url}/api/v1/stats")
        logger.info(f"{'=' * 70}\n")

        all_results: list[tuple[int, float]] = []
        batches = total_requests // concurrent_users

        test_start = time.time()

        for batch in range(batches):
            logger.info(f"Batch {batch + 1}/{batches} - {concurrent_users} concurrent requests")

            batch_results = await self.run_concurrent_requests(period, concurrent_users)
            all_results.extend(batch_results)

            # Показываем прогресс
            successful = sum(1 for status, _ in batch_results if status == 200)
            avg_time = statistics.mean([t for _, t in batch_results])
            logger.info(
                f"  ✅ {successful}/{concurrent_users} success, "
                f"avg time: {avg_time * 1000:.2f}ms"
            )

            # Небольшая пауза между батчами
            await asyncio.sleep(0.1)

        test_duration = time.time() - test_start

        # Анализ результатов
        response_times = [t for _, t in all_results]
        successful_requests = sum(1 for status, _ in all_results if status == 200)
        failed_requests = len(all_results) - successful_requests

        return {
            "test_date": datetime.now(UTC).isoformat(),
            "period": period,
            "total_requests": len(all_results),
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "success_rate": (successful_requests / len(all_results)) * 100,
            "test_duration_seconds": test_duration,
            "requests_per_second": len(all_results) / test_duration,
            "response_times": {
                "min_ms": min(response_times) * 1000,
                "max_ms": max(response_times) * 1000,
                "mean_ms": statistics.mean(response_times) * 1000,
                "median_ms": statistics.median(response_times) * 1000,
                "p95_ms": self._percentile(response_times, 95) * 1000,
                "p99_ms": self._percentile(response_times, 99) * 1000,
            },
        }

    def _percentile(self, data: list[float], percentile: int) -> float:
        """
        Вычислить перцентиль.

        Args:
            data: Список значений
            percentile: Перцентиль (0-100)

        Returns:
            Значение перцентиля
        """
        sorted_data = sorted(data)
        index = int(len(sorted_data) * (percentile / 100))
        return sorted_data[min(index, len(sorted_data) - 1)]

    def print_results(self, results: dict[str, Any]) -> None:
        """
        Красиво вывести результаты тестирования.

        Args:
            results: Словарь с результатами
        """
        logger.info(f"\n{'=' * 70}")
        logger.info("LOAD TEST RESULTS")
        logger.info(f"{'=' * 70}\n")

        logger.info(f"Test Date: {results['test_date']}")
        logger.info(f"Period: {results['period']}")
        logger.info(f"Duration: {results['test_duration_seconds']:.2f}s")
        logger.info("")

        logger.info("REQUEST SUMMARY:")
        logger.info(f"  Total Requests: {results['total_requests']}")
        logger.info(f"  Successful: {results['successful_requests']} ✅")
        logger.info(f"  Failed: {results['failed_requests']} ❌")
        logger.info(f"  Success Rate: {results['success_rate']:.2f}%")
        logger.info(f"  Throughput: {results['requests_per_second']:.2f} req/s")
        logger.info("")

        rt = results["response_times"]
        logger.info("RESPONSE TIMES:")
        logger.info(f"  Min: {rt['min_ms']:.2f}ms")
        logger.info(f"  Max: {rt['max_ms']:.2f}ms")
        logger.info(f"  Mean: {rt['mean_ms']:.2f}ms")
        logger.info(f"  Median: {rt['median_ms']:.2f}ms")
        logger.info(f"  P95: {rt['p95_ms']:.2f}ms")
        logger.info(f"  P99: {rt['p99_ms']:.2f}ms")
        logger.info("")

        # Performance оценка
        logger.info("PERFORMANCE ASSESSMENT:")
        if rt["p95_ms"] < 100:
            logger.info("  🌟 EXCELLENT - P95 < 100ms")
        elif rt["p95_ms"] < 500:
            logger.info("  ✅ GOOD - P95 < 500ms")
        elif rt["p95_ms"] < 1000:
            logger.info("  ⚠️  ACCEPTABLE - P95 < 1s")
        else:
            logger.info("  ❌ POOR - P95 > 1s")

        if results["success_rate"] >= 99:
            logger.info("  🌟 EXCELLENT - Success rate >= 99%")
        elif results["success_rate"] >= 95:
            logger.info("  ✅ GOOD - Success rate >= 95%")
        else:
            logger.info("  ❌ POOR - Success rate < 95%")

        logger.info(f"\n{'=' * 70}\n")


async def main() -> None:
    """Главная функция для запуска нагрузочного тестирования."""
    import argparse

    parser = argparse.ArgumentParser(description="Load testing для Stats API")
    parser.add_argument(
        "--url",
        type=str,
        default="http://localhost:8000",
        help="Base URL API сервера (default: http://localhost:8000)",
    )
    parser.add_argument(
        "--period",
        type=str,
        default="week",
        choices=["day", "week", "month"],
        help="Период для статистики (default: week)",
    )
    parser.add_argument(
        "--requests",
        type=int,
        default=100,
        help="Общее количество запросов (default: 100)",
    )
    parser.add_argument(
        "--concurrent",
        type=int,
        default=10,
        help="Количество параллельных пользователей (default: 10)",
    )

    args = parser.parse_args()

    tester = LoadTester(base_url=args.url)

    # Прогрев (warmup)
    logger.info("Warming up API...")
    await tester.make_request(args.period)
    await asyncio.sleep(1)

    # Основной тест
    results = await tester.run_load_test(
        period=args.period,
        total_requests=args.requests,
        concurrent_users=args.concurrent,
    )

    tester.print_results(results)


if __name__ == "__main__":
    asyncio.run(main())
