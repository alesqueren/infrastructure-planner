FROM python

WORKDIR /app

ADD requirements.txt .
RUN pip install -r requirements.txt

ADD . .

CMD ./main.py
