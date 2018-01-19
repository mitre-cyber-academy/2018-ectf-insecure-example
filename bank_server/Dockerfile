FROM python:2.7-alpine

# Include following if proxies are needed:
#ENV http_proxy 'http://url'
#ENV https_proxy 'https://url'
#ENV HTTP_PROXY 'http://url'
#ENV HTTPS_PROXY 'https://url'


RUN apk update \
    && apk add sqlite
    
EXPOSE 1337
EXPOSE 1338

WORKDIR /bank
ADD bank_server ./bank_server
RUN mkdir /bank/bank_server/logs
RUN cat /bank/bank_server/tests/test_db.sql | sqlite3 /bank/bank_server/tests/test.db
RUN cat /bank/bank_server/ectf_db.sql | sqlite3 /bank/bank_server/ectf.db
ADD setup.py ./setup.py
ADD README.md ./README.md

RUN python -m pip install pyyaml nose
RUN python setup.py install

CMD python -m bank_server.__main__
