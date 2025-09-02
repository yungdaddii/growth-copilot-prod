FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including Playwright dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    wget \
    gnupg \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libatspi2.0-0 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libxcb1 \
    libxkbcommon0 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt requirements.prod.txt ./

# Install Python dependencies
# Use prod requirements for Railway deployment
RUN if [ -f requirements.prod.txt ]; then \
        pip install --no-cache-dir -r requirements.prod.txt; \
    else \
        pip install --no-cache-dir -r requirements.txt; \
    fi

# Explicitly ensure google-ads is installed
RUN pip install --no-cache-dir google-ads==24.1.0

# Install Playwright and then browsers (as root before switching users)
RUN pip install playwright && playwright install chromium

# Copy application code
COPY . .

# Make startup script executable
RUN chmod +x scripts/startup.sh || true

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Use startup script that runs migrations first
CMD ["bash", "scripts/startup.sh"]