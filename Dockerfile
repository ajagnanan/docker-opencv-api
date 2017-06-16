FROM bamos/openface

RUN apt-get -y update && \
    apt-get -y install libzbar0 libzbar-dev libopencv-dev libtesseract-dev git cmake build-essential libleptonica-dev liblog4cplus-dev libcurl3-dev beanstalkd && \
    pip install gunicorn bottle zbar numpy Pillow

RUN chmod 777 -R /root

ADD openalpr /storage/projects/alpr

RUN cd /storage/projects/alpr/src && \
      mkdir build && \
      cd build && \
      cmake -DCMAKE_INSTALL_PREFIX:PATH=/usr -DCMAKE_INSTALL_SYSCONFDIR:PATH=/etc .. && \
      make -j2 && \
      make install

RUN cd /storage/projects/alpr/src/bindings/python && \
      python setup.py install 
      #./make.sh

ADD webservice /webservice

ADD openface /root/data

WORKDIR /webservice

ENTRYPOINT ["gunicorn"]

CMD ["web_server:app", "--workers", "8", "--bind=0.0.0.0:8888", "--log-config", "logging.conf", "--access-logfile", "-", "--reload"]
