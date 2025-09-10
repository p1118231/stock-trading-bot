# Use official Python runtime as base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Ensure static files and generate data
RUN apt-get update && apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p app/static data && \
    curl -o app/static/plotly.min.js https://cdnjs.cloudflare.com/ajax/libs/plotly.js/2.27.0/plotly.min.js && \
    chmod 644 app/static/plotly.min.js && \
    python src/fetch_data.py && \
    python src/ml_predict.py && \
    python src/analyze.py && \
    python src/check_signals.py

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "run.py"]