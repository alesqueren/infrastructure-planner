FROM python

WORKDIR /app

ADD requirements.txt .
RUN pip install -r requirements.txt

ADD . .

ENTRYPOINT ["/app/main.py"]
