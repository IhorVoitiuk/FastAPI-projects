FROM python:3.11

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD alembic upgrade head && uvicorn --host 0.0.0.0 main:app --reload
