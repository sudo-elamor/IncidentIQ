from prometheus_client import Counter

llm_api_requests_total = Counter(
    "llm_api_requests_total",
    "Total LLM API requests received"
)

llm_api_success_total = Counter(
    "llm_api_success_total",
    "Total successful LLM API responses"
)

llm_api_failure_total = Counter(
    "llm_api_failure_total",
    "Total failed LLM API responses"
)

llm_api_parse_failure_total = Counter(
    "llm_api_parse_failure_total",
    "Total failures due to invalid LLM JSON output"
)

llm_api_llm_error_total = Counter(
    "llm_api_llm_error_total",
    "Total failures due to LLM invocation errors"
)
