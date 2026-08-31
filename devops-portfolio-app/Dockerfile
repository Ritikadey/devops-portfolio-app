# ---- Build stage: install deps into a virtualenv ----
FROM python:3.12-slim AS builder

WORKDIR /build

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY app/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ---- Runtime stage: copy only what's needed to run ----
FROM python:3.12-slim AS runtime

# Metadata — useful when inspecting images pulled from ECR
LABEL org.opencontainers.image.source="https://github.com/<your-username>/devops-portfolio-app"
LABEL org.opencontainers.image.description="Minimal Flask app for a DevOps CI/CD/Docker/AWS portfolio"

# Run as a non-root user
RUN addgroup --system app && adduser --system --ingroup app app

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY app/ .

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PORT=8080

USER app
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

# gunicorn, not the Flask dev server, is the real entrypoint
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "main:app"]
