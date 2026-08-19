FROM python:3.12-slim

WORKDIR /opt/pyhole

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY . /opt/pyhole
RUN pip install --no-cache-dir .

ENV PYHOLE_HOME=/data
VOLUME ["/data"]

EXPOSE 5000

CMD ["pyhole"]
