FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

WORKDIR /app

# System deps kept minimal; build tools only if wheels need them later.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Non-root user
RUN useradd --create-home --uid 10001 --shell /usr/sbin/nologin labuser

# Copy project metadata first for better layer caching
COPY pyproject.toml README.md ./
COPY src ./src
COPY app.py ./
COPY pages ./pages
COPY docs ./docs
COPY scripts ./scripts
COPY artifacts ./artifacts
COPY data ./data

RUN pip install --upgrade pip \
    && pip install . \
    && chown -R labuser:labuser /app

USER labuser

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import vietlott_quant_lab" || exit 1

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
