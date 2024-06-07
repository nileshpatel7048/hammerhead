import asyncio
import logging
import time

from aiohttp import ClientSession, ClientTimeout
from statistics import mean, stdev

class LoadTester:
    def __init__(self, url, qps, max_timeout, method="GET", headers=None, payload=None):
        self.url = url
        self.qps = qps
        self.method = method
        self.headers = headers or {}
        self.payload = payload
        self.latencies = []
        self.errors = 0
        self.max_timeout = max_timeout / 1000  # Convert milliseconds to seconds
        logging.info("Initialized LoadTester with URL: %s, QPS: %d, Method: %s", self.url, self.qps, self.method)

    async def send_request(self, session):
        start_time = time.time()
        try:
            async with session.request(self.method, self.url, headers=self.headers, data=self.payload, timeout=ClientTimeout(total=self.max_timeout)) as response:
                latency = time.time() - start_time
                self.latencies.append(latency)
                logging.info("Request successful, latency: %f seconds", latency)
        except Exception as e:
            self.errors += 1
            logging.error("Request failed: %s", e)

    async def run_test(self, duration):
        async with ClientSession() as session:
            start_time = time.time()
            end_time = start_time + duration
            tasks = []

            def schedule_request():
                if time.time() < end_time:
                    tasks.append(asyncio.create_task(self.send_request(session)))
                    asyncio.get_event_loop().call_later(1, schedule_request)

            # Start the first batch of requests
            for _ in range(self.qps):
                schedule_request()

            # Wait for the duration of the test
            await asyncio.sleep(duration)

            # Wait for all tasks to complete
            await asyncio.gather(*tasks, return_exceptions=True)

        self.report_results()
        return self.calculate_total_requests()

    def calculate_total_requests(self):
        if self.latencies:
            return len(self.latencies) + self.errors
        else:
            return self.errors

    def report_results(self):
        total_requests = self.calculate_total_requests()
        if total_requests > 0:
            min_latency = min(self.latencies) if self.latencies else 0
            max_latency = max(self.latencies) if self.latencies else 0
            avg_latency = mean(self.latencies) if self.latencies else 0
            stddev_latency = stdev(self.latencies) if self.latencies else 0
            p95_latency = self.calculate_percentile(95) if self.latencies else 0
            p99_latency = self.calculate_percentile(99) if self.latencies else 0
            error_rate = self.errors / total_requests
        else:
            min_latency = max_latency = avg_latency = stddev_latency = p95_latency = p99_latency = error_rate = 0

        # Log test results
        logging.info("Min Latency: %f seconds", min_latency)
        logging.info("Max Latency: %f seconds", max_latency)
        logging.info("Average Latency: %f seconds", avg_latency)
        logging.info("Latency Stddev: %f seconds", stddev_latency)
        logging.info("95th Percentile Latency: %f seconds", p95_latency)
        logging.info("99th Percentile Latency: %f seconds", p99_latency)
        logging.info("Error Rate: %f%%", error_rate * 100)
        logging.info("Total Requests: %d", total_requests)

    def calculate_percentile(self, percentile):
        if not self.latencies:
            return None  # Return None if latencies list is empty

        size = len(self.latencies)
        if percentile < 0 or percentile > 100:
            return None  # Return None if percentile is out of range

        index = int(size * percentile / 100) - 1
        index = max(0, min(index, size - 1))  # Ensure index is within bounds
        return sorted(self.latencies)[index]
