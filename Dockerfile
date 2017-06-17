FROM ajagnanan/docker-opencv-base

ADD webservice /webservice

ADD openface /root/data

WORKDIR /webservice

EXPOSE 8888

ENTRYPOINT ["gunicorn"]

CMD ["web_server:app", "--workers", "3", "--bind=0.0.0.0:8888", "--log-config", "logging.conf", "--access-logfile", "-", "--reload"]
