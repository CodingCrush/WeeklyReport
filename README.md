demo: https://wr.mcloud.fun:81

#加入docker-compose

可以在新机器上, 直接一键启动了:
docker-compose up

加入entrypoint.sh脚本:
1 启动时先等待pg启动
2 判断pg里是否已经有表
3 如果没有表, 初始化表
4 用gunicorn 启动 app

## 快速运行
`-w <N>`为开启的gunicorn　worker进程数
`-p 8000:80` 主机通过8000端口访问

```bash
git clone https://github.com/CodingCrush/WeeklyReport && \

cd WeeklyReport && \

docker build -t weeklyreport:0.2 . && \

docker run -d \
        --restart=unless-stopped \
        --name weeklyreport-server \
        -p 8000:80 \
        -v /etc/localtime:/etc/localtime:ro \
        -v $PWD:/opt/weeklyreport \
        weeklyreport:0.2 \
        gunicorn wsgi:app --bind 0.0.0.0:80 -w 2 --log-file logs/awsgi.log --log-level=DEBUG
```

## 更新说明
V0.2: 简化了部署步骤

## 配置说明

+ 配置数据库
数据库默认使用sqlite，也可以使用postgres container，cd到postgres目录下，pull镜像，启动。
数据库URI地址由数据库名、用户名、密码、主机、端口号组成。
```
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@localhost/wr_prd'
```
步骤见postgres目录下的readme.md

+  配置config.py

`DEPARTMENTS`: 这个元组为部门列表，第一次打开时自动初始化到数据库中，用户在注册时可以选择部门。

`MAIL_USERNAME` : 用来发送邮件通知的邮箱账号

`MAIL_PASSWORD` : 用来发送邮件通知的邮箱密码


## 后台管理

第一次注册的用户为超级管理员，永远有登录后台的权限。
管理员可以修改其他角色

默认用户角色为`EMPLOYEE`，仅具有读写自己的周报的权限，

`MANAGER`可以读写周报，并查看本部门所有周报。而HR可以读写周报，并查看全部门所有周报。

`ADMINISTRATOR`在HR基础上增加了进入后台的功能。

`QUIT`用来标识离职后的员工，禁止其登录。
