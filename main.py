import argparse
import logging
import sys
import time
from src.load_tester.tester import LoadTester

def main():
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stdout)
    logger = logging.getLogger(__name__)

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="HTTP Load Testing Tool")
    parser.add_argument("url", type=str, help="URL to test")
    parser.add_argument("--qps", type=int, default=1, help="Queries per second")
    parser.add_argument("--duration", type=int, default=10, help="Duration of the test in seconds")
    parser.add_argument("--method", type=str, default="GET", help="HTTP method")
    parser.add_argument("--headers", type=str, help="HTTP headers")
    parser.add_argument("--payload", type=str, help="HTTP payload")
    parser.add_argument("--max_timeout", type=int, default=1000, help="Maximum timeout for any HTTP request (in milliseconds)")

    args = parser.parse_args()

    # Validate duration and qps values
    if args.duration <= 0:
        logger.error("Error: Duration should be greater than zero.")
        sys.exit(1)
    if args.qps <= 0:
        logger.error("Error: QPS should be greater than zero.")
        sys.exit(1)

    # Parse headers if provided
    headers = {}
    if args.headers:
        headers = dict(h.split(":") for h in args.headers.split(","))

    # Record start time
    start_time = time.time()

    # Log test parameters
    logger.info("Starting load test for URL: %s", args.url)
    logger.info("QPS: %d", args.qps)
    logger.info("Test duration: %d seconds", args.duration)

    # Initialize LoadTester instance
    tester = LoadTester(args.url, args.qps, args.max_timeout, args.method, headers, args.payload)

    # Start load test
    total_requests = tester.run_test(args.duration)

    # Calculate total time and actual request count per duration
    end_time = time.time()
    total_time = end_time - start_time
    actual_qps = total_requests / args.duration

    # Log load test completion
    logger.info("Load test completed in %d seconds", total_time)
    logger.info("Actual request count per duration: %f", actual_qps)

if __name__ == "__main__":
    main()
