FROM ajagnanan/docker-opencv-base

ADD webservice /webservice

ADD openface /root/data

WORKDIR /webservice

EXPOSE 8888

ENTRYPOINT ["gunicorn"]

CMD ["web_server:app", "--config", "gunicorn.conf", "--log-config", "logging.conf", "--reload"]
