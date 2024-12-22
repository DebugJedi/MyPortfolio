FROM python:3.11

WORKDIR /.

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080


CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8080"]