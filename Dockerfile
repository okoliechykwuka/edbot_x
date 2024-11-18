# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y git curl build-essential

# Install Rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Clean up to reduce image size and free up memory
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Ensure Python output is sent to the container log
ENV PYTHONUNBUFFERED=1

# Copy only the requirements file first
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

RUN pip cache purge

# Copy the rest of the application code
COPY . .

# Create log directory and set permissions
RUN mkdir -p /app/logs && \
    touch /app/logs/app.log && \
    chmod 777 /app/logs/app.log

# Create and set permissions for the database directory
RUN mkdir -p /app/db && \
    chmod 777 /app/db

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run the application with Gunicorn
CMD ["sh", "-c", "python clean.py && gunicorn main:app --bind 0.0.0.0:8000"]