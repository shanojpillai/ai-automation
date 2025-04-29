FROM python:3.10-slim

WORKDIR /app

# We'll copy requirements.txt at build time
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create directories for scripts and data
RUN mkdir -p /app/scripts /app/data

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Default command
CMD ["tail", "-f", "/dev/null"]
