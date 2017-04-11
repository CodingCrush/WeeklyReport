# image: wp-server:yymmdd
FROM daocloud.io/centos:7
MAINTAINER CJ
ENV LANG en_US.UTF-8
RUN ln -s -f /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
COPY ./requirements.txt /opt/
RUN curl -fsSL https://setup.ius.io/ | sh && \
    yum update -y && yum install -y net-tools ntp &&\
    yum install -y gcc gcc-c++ automake autoconf libtool make yasm && \
    yum install -y python35u python35u-devel python35u-pip && \
    yum install -y freetype freetype-devel libpng libpng-devel libjpeg libjpeg-devel openssl-devel &&\
    pip3.5 install -r opt/requirements.txt && \
    yum clean all
ADD . .
WORKDIR /opt/


# Start wp-server container
# docker run \
#            -d --restart=always \
#            --name wp-server \
#            --net='host' \
#            -v /etc/localtime:/etc/localtime:ro \
#            -e "LANG=en_US.UTF-8" \
#            -v $PWD:/opt/ \
#            wp-server:20170411 \
#            python3.5 WeeklyReport/manage runserver(host="0.0.0.0", port=10080)
#            gunicorn --bind 0.0.0.0:10080 wsgi
