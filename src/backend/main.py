# @Study:ST-008 @Study:ST-012 @Study:ST-009 @Study:ST-010
#!/usr/bin/env python3
"""
Modamoda Invisible Mannequin - FastAPI Backend
Main application entry point with OpenTelemetry monitoring
"""

import os
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import time
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource

# Configure OpenTelemetry
resource = Resource.create({
    "service.name": "modamoda-backend",
    "service.version": "0.1.0",
    "service.instance.id": os.getenv("HOSTNAME", "localhost")
})

trace.set_tracer_provider(TracerProvider(resource=resource))

# Configure OTLP exporter for Jaeger/OTel collector
otel_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4317")
otlp_exporter = OTLPSpanExporter(endpoint=otel_endpoint, insecure=True)
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Create tracer
tracer = trace.get_tracer(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
)

IMAGE_ACCURACY_GAUGE = Gauge(
    'image_accuracy_score',
    'Current image accuracy score for virtual try-on'
)

ERROR_RATE_GAUGE = Gauge(
    'error_rate_percentage',
    'Current error rate percentage'
)

ACTIVE_CONNECTIONS = Gauge(
    'active_connections',
    'Number of active connections'
)

# Create FastAPI application
app = FastAPI(
    title="Modamoda Invisible Mannequin API",
    description="AI-powered fashion virtual try-on platform with SLO monitoring",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware for metrics collection
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Middleware to collect HTTP metrics"""
    start_time = time.time()
    method = request.method
    path = request.url.path

    # Track active connections
    ACTIVE_CONNECTIONS.inc()

    try:
        response = await call_next(request)
        status_code = response.status_code

        # Record metrics
        REQUEST_COUNT.labels(method=method, endpoint=path, status_code=status_code).inc()
        REQUEST_LATENCY.labels(method=method, endpoint=path).observe(time.time() - start_time)

        return response
    except Exception as e:
        # Record error metrics
        REQUEST_COUNT.labels(method=method, endpoint=path, status_code=500).inc()
        REQUEST_LATENCY.labels(method=method, endpoint=path).observe(time.time() - start_time)
        raise e
    finally:
        ACTIVE_CONNECTIONS.dec()

# Prometheus metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Modamoda Invisible Mannequin API", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/api/v1/try-on")
async def virtual_try_on():
    """Virtual try-on endpoint - simulates AI processing"""
    with tracer.start_as_current_span("virtual_try_on_processing") as span:
        span.set_attribute("operation", "image_processing")
        span.set_attribute("model_version", "v1.0")

        # Simulate processing time and accuracy
        import random
        processing_time = random.uniform(0.5, 2.0)  # Simulate 0.5-2 second processing
        accuracy = random.uniform(0.95, 0.99)  # Simulate high accuracy

        # Update metrics
        IMAGE_ACCURACY_GAUGE.set(accuracy * 100)

        # Simulate occasional errors (2% error rate)
        if random.random() < 0.02:
            ERROR_RATE_GAUGE.set(2.0)
            span.set_status(trace.Status(trace.StatusCode.ERROR, "Processing failed"))
            raise Exception("AI processing failed")

        ERROR_RATE_GAUGE.set(0.5)  # Low error rate

        span.set_attribute("processing_time", processing_time)
        span.set_attribute("accuracy_score", accuracy)

        return {
            "result": "success",
            "processing_time": processing_time,
            "accuracy": accuracy,
            "image_url": "https://example.com/generated-image.jpg"
        }

# Instrument FastAPI with OpenTelemetry
FastAPIInstrumentor.instrument_app(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
