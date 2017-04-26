截图及步骤请看
http://codingcrush.me/2017/04/16/weekly-report/

## 安装说明
+ 配置数据库
数据库没有限制，使用sqlite也可以，以周报的内容体量而言，并不会影响到性能。我这里用的是docker服务的postgres，cd到postgres目录下，pull镜像，启动container。只需要保证提供数据库名、用户名、密码、主机、端口号构造一个URI地址。
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

+ 配置config.py
复制config.py.sample重命名一份为config.py进行修改：
`SECRET_KEY`可以这样随机产生，也可以当做环境变量在初始化容器时注入
```python
In [1]: import os
In [2]: os.urandom(24)
Out[2]: b"W\x1a'\xfcM\xad\xf9?U8\x9c\xa7T\x7f\xae\x11a\xd9MKE}\x81\xed"

SECRET_KEY = "W\x1a'\xfcM\xad\xf9?U8\x9c\xa7T\x7f\xae\x11a\xd9MKE}\x81\xed"
```
`FLASK_ADMIN_EMAIL `:修改管理员邮箱，使用这个邮箱注册的用户自动成为管理员
`ProductionConfig:`此处需要根据不同的数据库构造SQLALCHEMY_DATABASE_URI
`DEPARTMENTS`与`PROJECTS:`这两个元组存储着部门、项目，可以通过`python manage.py deploy`初始化到数据库中，这样用户在注册时便可以选择部门。
`'default': ProductionConfig`修改为生产环境配置，也可以用FLASK_CONFIG着一环境变量指定当前选择的环境，通常是docker启动时使用生产环境，自己在容器外使用开发环境与SQLite进行修改调试

+ 制作镜像
在weeklyreport目录下，运行
```docker
docker build -t weeklyreport:yymmdd .
```
`yymmdd`是日期标签，自行修改。

+ 启动container
 <host>:<port>为监听的ip与端口号
 -w <N>为开启的gunicorn　worker进程数
```docker
 docker run \
            -d --restart=always \
            --name wr-server \
            --net='host' \
            -v /etc/localtime:/etc/localtime:ro \
            -v $PWD:/opt/weeklyreport \
            weeklyreport:yymmdd \
            gunicorn --bind <host>:<port> -w <N> wsgi:app --log-file logs/awsgi.log
```

+ 数据库初始化
进入container:
```bash
docker exec -it wr-server /bin/bash
```
进入manager shell 并创建数据库表,然后初始化角色与部门数据
```python
python3.6 manage.py shell
    db.create_all()
    Role.insert_roles()
    Department.insert_departments()
exit
```

```
配置完成，打开启动container指令里的host:port地址注册用户吧

## 后台管理
+ 首先使用`FLASK_ADMIN_EMAIL`邮箱注册管理员账户，可以登录后台。以后其他用户注册后，可以指定角色。默认用户角色为`EMPLOYEE`，仅具有读写自己的周报的权限，`MANAGER`可以读写周报，并查看本部门所有周报。而HR可以读写周报，并查看全部门所有周报。`ADMINISTRATOR`在HR基础上增加了进入后台的功能。`QUIT`用来标识离职后的员工，无法登录也不参与到每周统计中。
+ 项目Projects中选择is_closed后可以关闭项目，这样当写周报时便不能再绑定到该项目上，不影响HR查看历史周报
