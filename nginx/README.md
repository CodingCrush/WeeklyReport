## DEPLOYMENT

    1. docker pull nginx:1.13
    2. docker run -d \
           --restart=always \
           --name wr-nginx \
           --net='host' \
           -v /etc/localtime:/etc/localtime:ro \
           -e "LANG=en_US.UTF-8" \
           -v $(dirname "$PWD"):/opt/weeklyreport \
           -v $PWD/nginx.conf:/etc/nginx/conf.d/default.conf \
           -v $PWD/nginx:/var/log/nginx \
           nginx:1.13
