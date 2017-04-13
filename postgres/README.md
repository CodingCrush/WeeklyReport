## DEPLOYMENT

    1. docker pull daocloud.io/postgres:9.6
    2. docker run -d \
           --restart=always \
           --name wr-postgres \
           --net='host' \
           -v /etc/localtime:/etc/localtime:ro \
           -e "LANG=en_US.UTF-8" \
           -v $PWD/pg96_data:/var/lib/postgresql/data \
           -e POSTGRES_DB=wr_prd \
           -e POSTGRES_USER=postgres \
           -e POSTGRES_PASSWORD=postgres \
           daocloud.io/postgres:9.6
