# ----------------------------------------------------------------
# 1. Use Python 3.11 slim (Debian Buster) for broad wheel support
# ----------------------------------------------------------------
FROM python:3.11-slim-buster

WORKDIR /app

# ----------------------------------------------------------------
# 2. Install Python dependencies with extended pip timeouts/retries
# ----------------------------------------------------------------
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir \
      --timeout=1000 \
      --retries=10 \
      -r requirements.txt

# ----------------------------------------------------------------
# 3. Install headless Chromium & WebDriver (multi-arch)
# ----------------------------------------------------------------
RUN apt-get update -qq && \
    apt-get install -yqq --no-install-recommends \
      chromium \
      chromium-driver \
      wget \
      ca-certificates \
      unzip && \
    rm -rf /var/lib/apt/lists/*

# ----------------------------------------------------------------
# 4. Copy application code and expose port
# ----------------------------------------------------------------
COPY . .

EXPOSE 8080

# ----------------------------------------------------------------
# 5. Launch FastAPI via Uvicorn
# ----------------------------------------------------------------
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
