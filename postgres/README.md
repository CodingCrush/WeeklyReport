## DEPLOYMENT

    1. docker pull postgres:9.6.5
    2. docker run -d \
           --restart=unless-stopped \
           --name wr-postgres \
           -p 5432:5432 \
           -v /etc/localtime:/etc/localtime:ro \
           -e "LANG=en_US.UTF-8" \
           -v $PWD/pg96_data:/var/lib/postgresql/data \
           -e POSTGRES_DB=wr_prd \
           -e POSTGRES_USER=postgres \
           -e POSTGRES_PASSWORD=postgres \
           postgres:9.6.5
