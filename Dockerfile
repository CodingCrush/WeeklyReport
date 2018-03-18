# image: weeklyreport:0.2
FROM centos:7
MAINTAINER CodingCrush
ENV LANG en_US.UTF-8
# TimeZone: Asia/Shanghai
RUN ln -s -f /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    curl -fsSL https://setup.ius.io/ | sh && \
    yum update -y && \
    yum install -y python36u python36u-devel python36u-pip && \
    mkdir ~/.pip && \
    echo -e "[global]\nindex-url=http://pypi.douban.com/simple/\ntrusted-host=pypi.douban.com">~/.pip/pip.conf && \
    yum clean all

RUN yum install -y supervisor

RUN mkdir -p /deploy
#VOLUME /deploy
WORKDIR /deploy
COPY requirements.txt /deploy/requirements.txt
RUN pip3.6 install -r requirements.txt --timeout=120

# Setup supervisord
RUN mkdir -p /var/log/supervisor
#COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
#COPY gunicorn.conf /etc/supervisor/conf.d/gunicorn.conf

# Start wp-server container

# docker run -d \
#            --restart=unless-stopped \
#            --name weeklyreport-server \
#            -p 8000:80 \
#            -v /etc/localtime:/etc/localtime:ro \
#            -v $PWD:/opt/weeklyreport \
#            weeklyreport:0.2 \
#            gunicorn wsgi:app --bind 0.0.0.0:5000 -w 2 --log-file logs/awsgi.log --log-level=DEBUG

# run sh. Start processes in docker-compose.yml


#deploy
COPY deploy /deploy
#wait pg connected
#RUN python3.6 checkdb.py
# db  init migrate
#RUN python3.6 wsgi.py deploy


RUN mkdir -p /scripts
COPY checkdb.py /scripts/checkdb.py
COPY entrypoint.sh /scripts/entrypoint.sh
#RUN chown -R /scripts
RUN chmod +x /scripts/entrypoint.sh

CMD ["/scripts/entrypoint.sh"]
#CMD ["/usr/bin/supervisord"]
#CMD ["/bin/bash"]
