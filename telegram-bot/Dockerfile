FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot code
COPY . .

# Create non-root user
RUN adduser --disabled-password --gecos '' botuser && chown -R botuser /app
USER botuser

# Environment variables
ENV PYTHONUNBUFFERED=1

# Command
CMD ["python", "bot.py"]