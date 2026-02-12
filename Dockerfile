# Dockerfile.dev
FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV UV_PYTHON=3.14
ENV PORT=8000

# 1) system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    build-essential \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# 2) install uv (official install script)
RUN curl -Ls https://astral.sh/uv/install.sh | sh

# 3) make uv available
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app

# 4) copy dependency manifests first (for layer caching)
COPY pyproject.toml uv.lock requirements.txt* ./

# 5) install Python + deps using uv
# - uv sync → pyproject.toml / uv.lock
# - uv pip install → requirements.txt
RUN uv sync --python ${UV_PYTHON}

# 6) copy application code
COPY . .

EXPOSE ${PORT}

# 7) run FastAPI (reload for dev)
CMD ["uv", "run", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
