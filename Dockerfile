FROM python:3.14.2
WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY src .
CMD ["python", "-m", "elkollege_schedule_bot"]
