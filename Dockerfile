FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc libpq-dev bash

COPY requirements/ requirements/
RUN pip install --upgrade pip \
  && pip install -r requirements/dev.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
