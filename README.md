# Lab-Management-Portal
Portal for Lab managers and scientists to access mangement tools

AWS setup

Programs
attachment uploader (labguru)
Cherrypick
lentipool analysis tool
lentitools COA generator
manual mainetnance updater (labguru)
mRNA COA generator
Pluritest Form generator
scanned maintenance updater (labguru)
talon coa generator

Startup script for connecting to s3 bucket.  Can also be inputted into AWS coding block directly.
Bucket name: lsg-bid-services
Bucket policy: 

{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": "*",
            "Action": [
                "s3:GetObject",
                "s3:ListBucket",
                "s3:ListBucketVersions",
                "s3:ListBucketMultipartUploads"
            ],
            "Resource": [
                "arn:aws:s3:::lsg-bid-services",
                "arn:aws:s3:::lsg-bid-services/*"
            ]
        }
    ]
}

contains assemblies but otherwise can be discarded.

# .bashrc

# Source global definitions
if [ -f /etc/bashrc ]; then
        . /etc/bashrc
fi

export PATH=/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/home/ec2-user/.local/bin:/home/ec2-user/bin:/usr/lib64/libreoffice/program:/home/ec2-user/s3
export PYTHONPATH=/usr/lib64/python3.7/site-packages
export UNO_PATH=/usr/lib64/libreoffice/program
export JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.362.b08-1.amzn2.0.1.x86_64/jre/bin/java
# Uncomment the following line if you don't like systemctl's auto-paging feature:
# export SYSTEMD_PAGER=
/usr/bin/s3fs lsg-bid-services ~/s3 -o passwd_file=${HOME}/.bucket_password

# User specific aliases and functions



# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init'
export LD_PRELOAD=/usr/lib64/libstdc++.so.6

==================================================================

Will need to create NGINX server 
/etc/nginx/nginx.conf

user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log;
pid /run/nginx.pid;

# Load dynamic modules. See /usr/share/doc/nginx/README.dynamic.
include /usr/share/nginx/modules/*.conf;

events {
    worker_connections 1024;
}

http {
    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

    access_log  /var/log/nginx/access.log  main;

    map $http_upgrade $connection_upgrade {
        default upgrade;
        ''      close;
    }

    sendfile            on;
    tcp_nopush          on;
    tcp_nodelay         on;
    keepalive_timeout   65;
    types_hash_max_size 4096;

    include             /etc/nginx/mime.types;
    default_type        application/octet-stream;

    # Load modular configuration files from the /etc/nginx/conf.d directory.
    # See http://nginx.org/en/docs/ngx_core_module.html#include
    # for more information.
    include /etc/nginx/conf.d/*.conf;

    upstream channels-backend {
        server localhost:8001;
    }

    server {
        listen       10.243.116.77:80;
        server_name  10.243.116.77;
        root         /usr/share/nginx/html;

        # Load configuration files for the default server block.
        include /etc/nginx/default.d/*.conf;

        error_page 404 /404.html;
        location = /404.html {
        }

        error_page 500 502 503 504 /50x.html;
        location = /50x.html {
        }

        location / {
            proxy_pass http://127.0.0.1:5020;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /ws/ {
            proxy_pass http://127.0.0.1:8001;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_redirect off;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}

=========================================================================

Will have to use systemctl to create process for gunicorn WSGI HTTP server
Will also need to install uvicorn for http and websocket usage
Will need to create venv 

/etc/systemd/system/gunicorn.service
[Unit]
Description=Gunicorn instance to serve lab_management_portal
After=network.target

[Service]
User=ec2-user
Group=nginx
WorkingDirectory=/home/ec2-user/Lab-Management-Portal/lab_management_portal
ExecStart=/home/ec2-user/Lab-Management-Portal/venv/bin/gunicorn -w 3 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:5020 lab_management_portal.asgi:application

[Install]
WantedBy=multi-user.target
