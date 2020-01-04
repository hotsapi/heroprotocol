FROM python:2.7-slim
WORKDIR /app
RUN pip install flask
COPY . .
CMD ["python", "server.py"]