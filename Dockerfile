FROM python:3.10-slim

WORKDIR /backend

COPY . /backend/

RUN pip install --no-cache-dir -r requirements.txt

ENV GOOGLE_APPLICATION_CREDENTIALS=/backend/google_key.json
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
