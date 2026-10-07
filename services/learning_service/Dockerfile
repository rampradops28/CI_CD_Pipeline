# 1. Base Image: Use an official lightweight Python image
FROM python:3.11-slim

# 2. Environment variables: Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 3. Set working directory inside the container
WORKDIR /app

# 4. Copy dependency specification and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the application source code
COPY app/ ./app/

# 6. Expose the port the app runs on
EXPOSE 8000

# 7. Start the FastAPI server using Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
