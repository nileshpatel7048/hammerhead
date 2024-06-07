# Hammerhead : HTTP Load Testing Tool

This is a command-line tool for performing HTTP load testing, designed to evaluate the performance of web services by simulating a specified number of requests per second (QPS) over a set duration.

## Features

- Supports all HTTP Methods(GET, POST, PUT , PATCH and DELETE) requests.
- Allows specifying custom headers and payloads.
- Calculates various performance metrics such as average latency, standard deviation, and error rate.
- Configurable request timeout.

## Requirements

- Docker

## Build the Docker Image

First, build the Docker image:

```sh
docker build -t hammerhead .
```
## Usage

To run the load testing tool, use the following command:

```sh
docker run -it --rm hammerhead <url> [options]
```
## Command-Line Arguments
- url (required): The URL to test.
- --qps (optional): Queries per second. Default is 1.
- --duration (optional): Duration of the test in seconds. Default is 10.
- --method (optional): HTTP method (GET or POST). Default is GET.
- --headers (optional): HTTP headers in the format "Header1:Value1,Header2:Value2".
- --payload (optional): HTTP payload as a string.
- --max_timeout (optional): Maximum timeout for any HTTP request in milliseconds. Default is 10,000.

## Example Commands
### Basic GET Request
```sh
docker run -it --rm hammerhead http://www.example.com --duration=10 --qps=2
```
### POST Request with Headers and Payload
```sh
docker run -it --rm hammerhead http://www.example.com --duration=10 --qps=2 --method=POST --headers="Content-Type:application/json,Authorization:Bearer mytoken" --payload='{"key1":"value1","key2":"value2"}'
```

## Output
The tool logs the following information:

- Start and completion of the load test.
- Latency of each successful request.
- Summary statistics after the test, including:
  - Minimum, maximum, and average latency.
  - Standard deviation of latency.
  - 95th and 99th percentile latency.
  - Error rate.
  - Total number of requests.

# Future Enhancements
- Allow user to define maximum concurrent threads for load testing.
- Generate a detailed report (in formats such as CSV or JSON) that can be analyzed later.
- Using a configuration file (YAML/JSON) for load test parameters
- Allow specifying headers and payload as JSON data


# TODOs
- Add More Unit test cases to cover all corner cases
- Explore using a thread pool for worker thread management 
- Implement different logging levels and potentially separate log files
- Implement more sophisticated error handling and retry mechanisms.
 
