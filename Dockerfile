FROM ajagnanan/docker-ai-base

# cache mxnet models
RUN mkdir /webservice \
 && cd /webservice \
 && curl -O http://data.mxnet.io/models/imagenet/squeezenet/squeezenet_v1.1-0000.params \
 && curl -O http://data.mxnet.io/models/imagenet/squeezenet/squeezenet_v1.1-symbol.json \
 && curl -O http://data.mxnet.io/models/imagenet/vgg/vgg19-0000.params \
 && curl -O http://data.mxnet.io/models/imagenet/vgg/vgg19-symbol.json \
 && curl -O http://data.mxnet.io/models/imagenet/synset.txt

ADD openface /root/data

ADD webservice /webservice

WORKDIR /webservice

EXPOSE 8888

ENTRYPOINT ["gunicorn"]

CMD ["web_server:app", "--config", "gunicorn.conf", "--log-config", "logging.conf", "--reload"]
