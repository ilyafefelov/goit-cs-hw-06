# Use official Python image
FROM python:3.9-slim

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose ports
EXPOSE 3000 5000

# Remove the CMD from the Dockerfile
# CMD ["sh", "-c", "python socket_server.py & python main.py"]
