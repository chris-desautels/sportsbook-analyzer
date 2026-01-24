# =============================================================================
# Dockerfile - A recipe for building a container image of your app
# =============================================================================
# Think of this like a requirements.txt but for your ENTIRE environment,
# not just Python packages. It ensures your app runs identically everywhere.
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Start with a base image (like choosing an OS + Python pre-installed)
# -----------------------------------------------------------------------------
# python:3.11-slim is a lightweight Linux image with Python 3.11 already set up
# "slim" means it doesn't include extra stuff we don't need (smaller = faster)
FROM python:3.11-slim

# -----------------------------------------------------------------------------
# Set environment variables
# -----------------------------------------------------------------------------
# PYTHONDONTWRITEBYTECODE: Don't create .pyc files (cleaner container)
# PYTHONUNBUFFERED: Print output immediately (better for logs)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# -----------------------------------------------------------------------------
# Set the working directory inside the container
# -----------------------------------------------------------------------------
# All following commands will run from /app (like doing `cd /app`)
WORKDIR /app

# -----------------------------------------------------------------------------
# Install system dependencies (if needed)
# -----------------------------------------------------------------------------
# Some Python packages need system libraries to compile
# We clean up after to keep the image small
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------------------------------------------------------
# Copy and install Python dependencies FIRST
# -----------------------------------------------------------------------------
# Why copy requirements.txt separately? Docker caches each step.
# If your code changes but requirements.txt doesn't, Docker reuses
# the cached pip install (much faster rebuilds!)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# -----------------------------------------------------------------------------
# Copy the rest of your application code
# -----------------------------------------------------------------------------
COPY . .

# -----------------------------------------------------------------------------
# Expose the port your app runs on
# -----------------------------------------------------------------------------
# This is documentation - it tells users "this container listens on port 5000"
EXPOSE 5000

# -----------------------------------------------------------------------------
# Define the command to run your app
# -----------------------------------------------------------------------------
# When the container starts, run this command
# Using gunicorn (production WSGI server) instead of Flask's dev server
# --bind 0.0.0.0:5000 means "listen on all network interfaces, port 5000"
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]
