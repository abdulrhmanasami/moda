# @Study:ST-008 @Study:ST-012 @Study:ST-009 @Study:ST-010
#!/usr/bin/env python3
"""
Modamoda Invisible Mannequin - FastAPI Backend
Main application entry point with OpenTelemetry monitoring
"""

import os
import time
from typing import Callable
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, CollectorRegistry, CONTENT_TYPE_LATEST, generate_latest
from starlette.responses import Response as StarletteResponse

# -------- Observability (Prometheus) --------
OBS_ENABLE_METRICS = os.getenv("OBS_ENABLE_METRICS", "false").lower() in {"1","true","yes"}
_registry = CollectorRegistry() if OBS_ENABLE_METRICS else None

if OBS_ENABLE_METRICS:
    REQUEST_COUNT = Counter(
        'http_requests_total',
        'Total number of HTTP requests',
        ['method', 'endpoint', 'status_code'],
        registry=_registry
    )

    REQUEST_LATENCY = Histogram(
        'http_request_duration_seconds',
        'HTTP request latency in seconds',
        ['method', 'endpoint'],
        registry=_registry,
        buckets=(0.05,0.1,0.25,0.5,0.75,1.0,1.5,2.0,3.0,5.0,10.0)
    )

    IMAGE_ACCURACY_GAUGE = Gauge(
        'image_accuracy_score',
        'Current image accuracy score for virtual try-on',
        registry=_registry
    )

    ERROR_RATE_GAUGE = Gauge(
        'error_rate_percentage',
        'Current error rate percentage',
        registry=_registry
    )

    ACTIVE_CONNECTIONS = Gauge(
        'active_connections',
        'Number of active connections',
        registry=_registry
    )

# -------- OpenTelemetry (optional) --------
if os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"):
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.instrumentation.logging import LoggingInstrumentation
        from opentelemetry.instrumentation.requests import RequestsInstrumentor

        res = Resource.create({
            "service.name": os.getenv("OTEL_SERVICE_NAME","modamoda-api"),
            "service.namespace": os.getenv("OTEL_SERVICE_NAMESPACE","modamoda"),
            "service.version": os.getenv("OTEL_SERVICE_VERSION","1.0.0-rc1"),
        })
        provider = TracerProvider(resource=res)
        provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
        trace.set_tracer_provider(provider)

        # Create tracer
        tracer = trace.get_tracer(__name__)

        FastAPIInstrumentor.instrument_app(app)
        LoggingInstrumentation().instrument(set_logging_format=True)
        RequestsInstrumentor().instrument()
    except Exception as _e:
        # Do not fail app if OTel optional deps mismatch
        tracer = None
        pass
else:
    tracer = None

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

# -------- Prometheus Middleware --------
if OBS_ENABLE_METRICS:
    @app.middleware("http")
    async def prometheus_middleware(request: Request, call_next: Callable):
        start = time.perf_counter()
        method = request.method
        # Normalize path (optional): collapse ids → :id
        path = request.scope.get("route").path if request.scope.get("route") else request.url.path

        # Track active connections
        ACTIVE_CONNECTIONS.inc()

        try:
            response = await call_next(request)
            dur = max(0.0, time.perf_counter() - start)
            status_code = response.status_code

            # Record metrics
            REQUEST_COUNT.labels(method=method, endpoint=path, status_code=status_code).inc()
            REQUEST_LATENCY.labels(method=method, endpoint=path).observe(dur)

            return response
        except Exception as e:
            # Record error metrics
            dur = max(0.0, time.perf_counter() - start)
            REQUEST_COUNT.labels(method=method, endpoint=path, status_code=500).inc()
            REQUEST_LATENCY.labels(method=method, endpoint=path).observe(dur)
            raise e
        finally:
            ACTIVE_CONNECTIONS.dec()

    @app.get("/metrics")
    async def metrics():
        data = generate_latest(_registry)
        return StarletteResponse(content=data, media_type=CONTENT_TYPE_LATEST)

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
    if tracer:
        with tracer.start_as_current_span("virtual_try_on_processing") as span:
            span.set_attribute("operation", "image_processing")
            span.set_attribute("model_version", "v1.0")

            # Simulate processing time and accuracy
            import random
            processing_time = random.uniform(0.5, 2.0)  # Simulate 0.5-2 second processing
            accuracy = random.uniform(0.95, 0.99)  # Simulate high accuracy

            if OBS_ENABLE_METRICS:
                # Update metrics
                IMAGE_ACCURACY_GAUGE.set(accuracy * 100)

            # Simulate occasional errors (2% error rate)
            if random.random() < 0.02:
                if OBS_ENABLE_METRICS:
                    ERROR_RATE_GAUGE.set(2.0)
                span.set_status(trace.Status(trace.StatusCode.ERROR, "Processing failed"))
                raise Exception("AI processing failed")

            if OBS_ENABLE_METRICS:
                ERROR_RATE_GAUGE.set(0.5)  # Low error rate

            span.set_attribute("processing_time", processing_time)
            span.set_attribute("accuracy_score", accuracy)

            return {
                "result": "success",
                "processing_time": processing_time,
                "accuracy": accuracy,
                "image_url": "https://example.com/generated-image.jpg"
            }
    else:
        # Fallback without tracing
        import random
        processing_time = random.uniform(0.5, 2.0)
        accuracy = random.uniform(0.95, 0.99)

        if OBS_ENABLE_METRICS:
            IMAGE_ACCURACY_GAUGE.set(accuracy * 100)
            if random.random() < 0.02:
                ERROR_RATE_GAUGE.set(2.0)
                raise Exception("AI processing failed")
            ERROR_RATE_GAUGE.set(0.5)

        return {
            "result": "success",
            "processing_time": processing_time,
            "accuracy": accuracy,
            "image_url": "https://example.com/generated-image.jpg"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
