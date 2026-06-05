# Multi-stage build for PhishNet Backend
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user first
RUN groupadd -g 1000 phishnet && \
    useradd -r -u 1000 -g phishnet phishnet && \
    chown -R phishnet:phishnet /app

# Copy installed packages from builder to accessible location
COPY --from=builder /root/.local /home/phishnet/.local

# Set ownership of Python packages
RUN chown -R phishnet:phishnet /home/phishnet/.local

# Copy application code
COPY --chown=phishnet:phishnet . .

# Switch to non-root user
USER phishnet

# Make sure the PATH includes local packages
ENV PATH=/home/phishnet/.local/bin:$PATH

# Expose port
EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:5000/api/health || exit 1

# Run with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "wsgi:app"]
