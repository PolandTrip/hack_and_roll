# Use the official Python base image
FROM python:3.9-slim as base

# Install ffmpeg and other dependencies
RUN apt-get update && apt-get install -y ffmpeg && apt-get clean

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . /app/

# Expose the port FastAPI is running on
EXPOSE 8000

# Run the FastAPI server with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


