FROM python:3.11-alpine
WORKDIR /
COPY . .
RUN pip install -r requirements.txt
EXPOSE 3000
CMD ["python", "main.py"]