# Multi-stage build for Railway deployment
FROM python:3.11-slim as backend-builder

WORKDIR /app/backend

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Frontend build stage
FROM node:20-alpine as frontend-builder

WORKDIR /app/frontend

# Copy package files and install dependencies
COPY frontend/package*.json ./
RUN npm ci || npm install

# Copy frontend source and build
COPY frontend/ .
RUN npm run build

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies for Playwright
RUN apt-get update && apt-get install -y \
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
    libglib2.0-0 \
    postgresql-client \
    nginx \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=backend-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin

# Copy backend application
COPY backend/ backend/

# Copy frontend build
COPY --from=frontend-builder /app/frontend/.next frontend/.next
COPY --from=frontend-builder /app/frontend/public frontend/public
COPY --from=frontend-builder /app/frontend/package*.json frontend/
COPY --from=frontend-builder /app/frontend/node_modules frontend/node_modules

# Install Playwright browsers
RUN playwright install chromium --with-deps

# Copy nginx configuration
COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY nginx/conf.d/keelo.conf /etc/nginx/conf.d/default.conf

# Create supervisor config
RUN mkdir -p /etc/supervisor/conf.d
RUN echo "[supervisord]\n\
nodaemon=true\n\
logfile=/dev/stdout\n\
logfile_maxbytes=0\n\
pidfile=/tmp/supervisord.pid\n\
\n\
[program:backend]\n\
command=sh -c 'cd /app/backend && alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000'\n\
autostart=true\n\
autorestart=true\n\
stderr_logfile=/dev/stderr\n\
stderr_logfile_maxbytes=0\n\
stdout_logfile=/dev/stdout\n\
stdout_logfile_maxbytes=0\n\
\n\
[program:frontend]\n\
command=sh -c 'cd /app/frontend && npm start'\n\
autostart=true\n\
autorestart=true\n\
stderr_logfile=/dev/stderr\n\
stderr_logfile_maxbytes=0\n\
stdout_logfile=/dev/stdout\n\
stdout_logfile_maxbytes=0\n\
\n\
[program:nginx]\n\
command=nginx -g 'daemon off;'\n\
autostart=true\n\
autorestart=true\n\
stderr_logfile=/dev/stderr\n\
stderr_logfile_maxbytes=0\n\
stdout_logfile=/dev/stdout\n\
stdout_logfile_maxbytes=0" > /etc/supervisor/supervisord.conf

# Set environment variable for Railway
ENV NODE_ENV=production
ENV PYTHONUNBUFFERED=1

# Expose the port Railway expects
EXPOSE ${PORT:-8080}

# Start supervisor
CMD ["supervisord", "-c", "/etc/supervisor/supervisord.conf"]