# image: weeklyreport:yymmdd
FROM daocloud.io/centos:7
MAINTAINER CodingCrush
ENV LANG en_US.UTF-8
ADD . .
RUN ln -s -f /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    curl -fsSL https://setup.ius.io/ | sh && \
    yum update -y && yum install -y net-tools ntp &&\
    yum install -y gcc gcc-c++ automake autoconf libtool make yasm && \
    yum install -y python36u python36u-devel python36u-pip && \
    yum install -y freetype freetype-devel libpng libpng-devel libjpeg libjpeg-devel openssl-devel &&\
    pip3.6 install -r requirements.txt && \
    yum clean all
WORKDIR /opt/weeklyreport


# Start wp-server container
# docker run \
#            -d --restart=always \
#            --name wr-server \
#            --net='host' \
#            -v /etc/localtime:/etc/localtime:ro \
#            -v $PWD:/opt/weeklyreport \
#            weeklyreport:yymmdd \
#            gunicorn wsgi:app \
#            --bind <host>:<port> \
#            -w <N> \
#            --log-file logs/awsgi.log
