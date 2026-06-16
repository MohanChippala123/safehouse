# Build stage
FROM python:3.12-slim as builder

WORKDIR /build
RUN apt-get update && apt-get install -y --no-install-recommends \
    libimage-exiftool-perl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Runtime stage
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libimage-exiftool-perl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

COPY . .

# Create non-root user
RUN useradd -m -u 1000 safehouse && \
    chown -R safehouse:safehouse /app

USER safehouse

EXPOSE 5000

# Default to production settings
ENV FLASK_ENV=production
ENV FLASK_DEBUG=0

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-"]
