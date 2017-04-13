## STEPS:
1. Enter postgres directory and then Run Postgres Container or create role and database;

    1.docker pull daocloud.io/postgres:9.6
    2.docker run -d \
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
           
2. Build App image
    
    docker built -t weeklyreport:yymmdd .
   
3. Run the app container.

     docker run \
                -d --restart=always \
                --name wr-server \
                --net='host' \
                -v /etc/localtime:/etc/localtime:ro \
                -v $PWD:/opt/weeklyreport \
                weeklyreport:yymmdd \
                gunicorn --bind 0.0.0.0:8000 -w 2 wsgi:app --log-file logs/awsgi.log