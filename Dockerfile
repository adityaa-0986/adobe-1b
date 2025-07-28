# Dockerfile for Adobe Hackathon Round 1B

FROM python:3.9-slim as builder

WORKDIR /app


RUN pip install sentence-transformers


COPY download_model.py .


RUN python download_model.py



FROM --platform=linux/amd64 python:3.9-slim

WORKDIR /app


COPY requirements.txt .


RUN pip install --no-cache-dir -r requirements.txt


COPY --from=builder /app/model/ ./model/


COPY . .


CMD ["python", "main.py"]