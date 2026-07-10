# RAG Tutorial — Linux x86_64 image
# Runs the modern ML stack (torch, onnxruntime, langchain) in Linux,
# where all wheels exist. This sidesteps the Intel-Mac wheel problem:
# Docker builds/runs this as linux/amd64, which is NATIVE on your Intel Mac
# (no slow emulation).

FROM python:3.12-slim

# System libraries some wheels need at runtime (pymupdf, numpy, git installs)
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        git \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv (same tool you use locally)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install dependencies first (cached layer — only re-runs when requirements change)
COPY requirements.txt ./
RUN uv pip install --system --no-cache -r requirements.txt \
    && uv pip install --system --no-cache jupyterlab

# Project files are bind-mounted at runtime via docker-compose,
# so edits on your Mac show up instantly inside the container.

EXPOSE 8888

# Start Jupyter Lab, reachable from your Mac's browser.
# Token disabled for local convenience — do not expose this port publicly.
CMD ["jupyter", "lab", \
     "--ip=0.0.0.0", \
     "--port=8888", \
     "--no-browser", \
     "--allow-root", \
     "--ServerApp.token=", \
     "--ServerApp.password=", \
     "--ServerApp.root_dir=/app"]
