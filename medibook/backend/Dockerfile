FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN apt update && apt install curl -y
EXPOSE 5000
ENTRYPOINT ["python"]
CMD ["app.py"]

