## DEPLOYMENT

    1. docker pull mongo:3.4.3
    2. docker run -d \
           --restart=always \
           --name wr-mongo \
           -v $PWD/mongo_data:/data/db \
           --net='host' \
           mongo:3.4.3
    3. docker exec -it wr-mongo mongo admin
    4. use wr 
    5. db.createUser({user: 'wr_usr',
                      pwd: 'wr_pwd',
                      roles: ["readWrite"]});
