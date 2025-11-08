from prometheus_client import Counter, start_http_server
import random, time

# Define your custom metric
openai_api_calls_total = Counter(
    'openai_api_calls_total', 
    'Total OpenAI API calls',
    ['model', 'status']
)

# Start an HTTP server for Prometheus to scrape
start_http_server(8000)
print("✅ Metrics endpoint available at http://localhost:8000/metrics")

# Simulate data being generated
models = ["gpt-4", "gpt-3.5-turbo"]
statuses = ["success", "error"]

while True:
    model = random.choice(models)
    status = random.choice(statuses)
    openai_api_calls_total.labels(model=model, status=status).inc()
    time.sleep(2)
