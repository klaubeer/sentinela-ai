FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir streamlit>=1.35 httpx>=0.27 pandas>=2.0 plotly>=5.0

COPY . .

EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
