FROM python:3.9-slim-bullseye


WORKDIR /bot

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

RUN mkdir -p configs

COPY . .

CMD ["python3", "main.py"]