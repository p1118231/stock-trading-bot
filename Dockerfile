FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN apt-get update && apt-get install -y curl && \
    mkdir -p app/static && \
    curl -o app/static/plotly.min.js https://cdnjs.cloudflare.com/ajax/libs/plotly.js/2.27.0/plotly.min.js && \
    chmod 644 app/static/plotly.min.js
EXPOSE 5000
CMD ["python", "run.py"]