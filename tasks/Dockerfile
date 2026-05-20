FROM python:3.11-slim
WORKDIR /task
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
ENTRYPOINT ["python"]
CMD ["app.py"]
