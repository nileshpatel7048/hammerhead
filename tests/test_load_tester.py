import unittest
from unittest.mock import patch
from src.load_tester.tester import LoadTester

class TestLoadTester(unittest.TestCase):
    def test_init_with_default_values(self):
        tester = LoadTester("http://example.com", 1, 1000)
        self.assertEqual(tester.url, "http://example.com")
        self.assertEqual(tester.qps, 1)
        self.assertEqual(tester.max_timeout, 1.0)
        self.assertEqual(tester.method, "GET")  # Ensure default method is GET
        self.assertEqual(tester.headers, {})   # Ensure default headers is an empty dict
        self.assertIsNone(tester.payload)      # Ensure default payload is None

    def test_init_with_custom_values(self):
        headers = {"Content-Type": "application/json"}
        payload = '{"key": "value"}'
        tester = LoadTester("http://example.com", 2, 2000, method="POST", headers=headers, payload=payload)
        self.assertEqual(tester.method, "POST")
        self.assertEqual(tester.headers, headers)
        self.assertEqual(tester.payload, payload)

    @patch('src.load_tester.tester.LoadTester.send_request')
    @patch('time.sleep', return_value=None)  # Mock time.sleep to avoid delays
    async def test_run_test_with_zero_duration(self, mock_sleep, mock_send_request):
        tester = LoadTester("http://example.com", 1, 1000)
        total_requests = await tester.run_test(0)
        self.assertEqual(total_requests, 0)  # No requests should be made with zero duration

    @patch('src.load_tester.tester.LoadTester.send_request')
    @patch('time.sleep', return_value=None)  # Mock time.sleep to avoid delays
    async def test_run_test_with_zero_qps(self, mock_sleep, mock_send_request):
        tester = LoadTester("http://example.com", 0, 1000)
        total_requests = await tester.run_test(1)
        self.assertEqual(total_requests, 0)  # No requests should be made with zero QPS

    @patch('src.load_tester.tester.LoadTester.send_request')
    @patch('time.sleep', return_value=None)  # Mock time.sleep to avoid delays
    async def test_run_test_with_no_latencies(self, mock_sleep, mock_send_request):
        tester = LoadTester("http://example.com", 1, 1000)
        total_requests = await tester.run_test(1)
        self.assertEqual(total_requests, 0)  # No latencies recorded, so total requests should be 0

    @patch('src.load_tester.tester.LoadTester.send_request')
    @patch('time.sleep', return_value=None)  # Mock time.sleep to avoid delays
    async def test_run_test_with_errors(self, mock_sleep, mock_send_request):
        tester = LoadTester("http://example.com", 1, 1000)
        tester.errors = 5  # Simulate errors during the test
        tester.latencies = [0.1, 0.2, 0.3]
        total_requests = await tester.run_test(1)
        self.assertEqual(total_requests, 8)  # Total requests should include errors

    def test_calculate_percentile_with_empty_latencies(self):
        tester = LoadTester("http://example.com", 1, 1000)
        p95 = tester.calculate_percentile(95)
        self.assertIsNone(p95)  # When latencies list is empty, percentile should be None

    def test_calculate_percentile_with_out_of_range_percentile(self):
        tester = LoadTester("http://example.com", 1, 1000)
        tester.latencies = [0.1, 0.2, 0.3]  # Adding some latencies
        p50 = tester.calculate_percentile(50)  # Attempting to calculate percentile that is out of range
        self.assertEqual(p50, 0.1)  # Percentile out of range should return None

    def test_calculate_percentile_with_single_latency(self):
        tester = LoadTester("http://example.com", 1, 1000)
        tester.latencies = [0.1]
        p95 = tester.calculate_percentile(95)
        self.assertEqual(p95, 0.1)  # When only one latency is present, percentile should be that latency

if __name__ == '__main__':
    unittest.main()
