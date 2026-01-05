FROM python:3.14.2

WORKDIR /usr/src/app
COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY src .

CMD ["/bin/bash", "-c", "python main.py"]