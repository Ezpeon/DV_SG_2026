FROM python:3.11-slim

WORKDIR /app

COPY app_requirements.txt .
RUN pip install --no-cache-dir -r app_requirements.txt

COPY webapp/ .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
