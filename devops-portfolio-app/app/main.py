"""
Minimal Flask app for a DevOps portfolio project.

Kept intentionally simple: the point of this repo is the CI/CD pipeline,
Docker image, and AWS deployment around it — not the app logic.
"""
import os
import socket
from datetime import datetime, timezone

from flask import Flask, jsonify, render_template

app = Flask(__name__)

APP_VERSION = os.getenv("APP_VERSION", "dev")
APP_ENV = os.getenv("APP_ENV", "development")


@app.route("/")
def index():
    """Simple homepage showing build/runtime metadata."""
    return render_template(
        "index.html",
        version=APP_VERSION,
        environment=APP_ENV,
        hostname=socket.gethostname(),
    )


@app.route("/health")
def health():
    """Liveness/readiness probe used by Docker HEALTHCHECK, ALB/App Runner,
    and the CI pipeline's smoke test."""
    return jsonify(status="healthy", timestamp=datetime.now(timezone.utc).isoformat())


@app.route("/api/info")
def info():
    """Exposes build metadata — handy for confirming a deploy actually
    shipped the version you think it did."""
    return jsonify(
        version=APP_VERSION,
        environment=APP_ENV,
        hostname=socket.gethostname(),
    )


if __name__ == "__main__":
    # Only used for local `python main.py` runs; gunicorn is the real
    # entrypoint in Docker (see Dockerfile CMD).
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
