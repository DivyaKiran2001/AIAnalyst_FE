FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY . /app/Backend

# Expose Cloud Run port
EXPOSE 8080
ENV PORT=8080

# Run the FastAPI + Socket.IO app
# CMD uvicorn Backend.agents.final_agent:sio_app --host 0.0.0.0 --port 8000 --reload
CMD exec uvicorn Backend.agents.final_agent:sio_app --host 0.0.0.0 --port ${PORT}


