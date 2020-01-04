FROM python:2.7-slim
WORKDIR /app
RUN pip install flask
COPY . .
EXPOSE 5000
CMD ["python", "server.py"]