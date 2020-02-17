FROM python:3.7.6-alpine

WORKDIR /usr/src/app
RUN mkdir -p home

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "./build_npmrc.py"]