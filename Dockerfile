FROM python:3.7

WORKDIR /usr/src/app

ENV LIBRARY_PATH=/lib:/usr/lib

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "./run.sh" ]
