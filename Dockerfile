FROM python:3.9-slim

# Install system dependencies needed for dlib and face_recognition
RUN apt-get update && apt-get install -y \
    build-essential cmake \
    libopenblas-dev liblapack-dev \
    libx11-dev libgtk-3-dev \
    libboost-python-dev libboost-system-dev \
    libboost-thread-dev libboost-chrono-dev \
    libboost-test-dev libboost-atomic-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# Copy rest of your app code
COPY . .

# Expose port 5000 for Flask
EXPOSE 5000

# Run the app with Gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
