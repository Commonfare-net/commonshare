FROM python:2-slim

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY python/ ./

ENV TASK=parse
ENV GEXF_INPUT=/usr/src/app/data/input/latest.gexf
ENV PAGERANK_FILE=/usr/src/app/data/output/recommenderdata.gexf

COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT [ "/entrypoint.sh" ]