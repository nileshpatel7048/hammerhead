import logging
import requests
import time
import threading
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
        self.lock = threading.Lock()  # Lock for thread safety
        self.stop_test = False
        self.max_timeout = max_timeout / 1000  # Convert milliseconds to seconds
        logging.info("Initialized LoadTester with URL: %s, QPS: %d, Method: %s", self.url, self.qps, self.method)

    def send_request(self):
        while not self.stop_test:
            start_time = time.time()
            try:
                response = requests.request(self.method, self.url, headers=self.headers, data=self.payload, timeout=self.max_timeout)
                response.raise_for_status()
                latency = time.time() - start_time
                with self.lock:
                    self.latencies.append(latency)
                logging.info("Request successful, latency: %f seconds", latency)
            except requests.RequestException as e:
                with self.lock:
                    self.errors += 1
                logging.error("Request failed: %s", e)

            # Adjust sleep duration dynamically to achieve desired QPS
            time_taken = time.time() - start_time
            sleep_time = max(0, 1 - time_taken)
            time.sleep(sleep_time)

    def run_test(self, duration):
        threads = []
        for _ in range(self.qps):
            thread = threading.Thread(target=self.send_request)
            thread.start()
            threads.append(thread)

        logging.info("Starting load test for %d seconds", duration)
        time.sleep(duration)
        self.stop_test = True

        for thread in threads:
            thread.join()

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
        size = len(self.latencies)
        return sorted(self.latencies)[int(size * percentile / 100) - 1]
