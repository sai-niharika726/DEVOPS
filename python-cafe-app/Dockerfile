FROM python:3.11-slim
WORKDIR /cafe
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
VOLUME /cafe /data
EXPOSE 5000
ENTRYPOINT ["python"]
CMD ["app.py"]
