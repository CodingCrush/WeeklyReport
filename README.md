个人网站的服务链接： http://106.14.125.116:10000/

截图及步骤请看
http://codingcrush.me/2017/04/16/weekly-report/

## 安装说明
+ 配置数据库
数据库没有限制，可选择使用sqlite，跳过数据库安装，方便快捷。
```
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(os.getcwd(), 'wr_prd.sqlite')
```

项目中集成了是docker化的postgres，cd到postgres目录下，pull镜像，启动container。
数据库URI地址由数据库名、用户名、密码、主机、端口号构造。
```
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@localhost/wr_prd'
```

```docker
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
```

+  配置nginx
   必要性不大，可略过
   
+  配置config.py

重命名config.py.sample为config.py并进行配置：

`SECRET_KEY`随机产生，可以当做环境变量在初始化容器时注入

`FLASK_ADMIN_EMAIL `:修改管理员邮箱，使用这个邮箱注册的用户自动成为管理员

`ProductionConfig:`此处需要根据不同的数据库构造SQLALCHEMY_DATABASE_URI

`DEPARTMENTS`:`这个元组存储着部门列表，根据初始化到数据库中，用户在注册时便可以选择部门。

`default: ProductionConfig`修改为生产环境配置，也可以用FLASK_CONFIG这个环境变量指定当前选择的环境，通常是docker启动时使用生产环境，自己在本地使用开发环境与SQLite进行修改调试

`MAIL_USERNAME` : 用来发送邮件通知的邮箱账号

`MAIL_PASSWORD` : 密码

+ 制作镜像

在weeklyreport目录下，运行
```docker
docker build -t weeklyreport:20170609 .
```
`yymmdd`是日期标签，自行修改。

+ 启动container

 `<host>:<port>`为监听的ip与端口号
 
 `-w <N>`为开启的gunicorn　worker进程数

```docker
 docker run \
            -d --restart=always \
            --name wr-server \
            --net='host' \
            -v /etc/localtime:/etc/localtime:ro \
            -v $PWD:/opt/weeklyreport \
            weeklyreport:20170609 \
            gunicorn wsgi:app --bind localhost:8000 -w 4 --log-file logs/awsgi.log --log-level=DEBUG

```

+ 数据库初始化

这时打开localhost:8000会出现错误，因为还未初始化数据库，在bash中执行初始化deploy命令
```bash
docker exec weeklyreport-server bash -c 'python3.6 manage.py deploy'
```

配置完成，注册用户吧

## 后台管理

首先使用`FLASK_ADMIN_EMAIL`邮箱注册管理员账户，可以登录后台。

以后其他用户注册后，可以指定角色。

默认用户角色为`EMPLOYEE`，仅具有读写自己的周报的权限，

`MANAGER`可以读写周报，并查看本部门所有周报。而HR可以读写周报，并查看全部门所有周报。

`ADMINISTRATOR`在HR基础上增加了进入后台的功能。

`QUIT`用来标识离职后的员工，禁止其登录。
