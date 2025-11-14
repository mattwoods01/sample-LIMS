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

Directory setup
<lab_management_portal>
└── lab_management_portal
    ├── scan_maintenance_updater
    │   ├── scan_pdfs.py
    │   ├── migrations
    │   │   ├── __init__.py
    │   │   └── __pycache__
    │   │       └── __init__.cpython-310.pyc
    │   ├── models.py
    │   ├── maintenance.py
    │   ├── consumers.py
    │   ├── __init__.py
    │   ├── __pycache__
    │   │   ├── routing.cpython-310.pyc
    │   │   ├── views.cpython-310.pyc
    │   │   ├── return_maintenance.cpython-310.pyc
    │   │   ├── consumers.cpython-310.pyc
    │   │   ├── urls.cpython-310.pyc
    │   │   ├── maintenance.cpython-310.pyc
    │   │   ├── models.cpython-310.pyc
    │   │   ├── admin.cpython-310.pyc
    │   │   ├── upload_attachments.cpython-310.pyc
    │   │   ├── apps.cpython-310.pyc
    │   │   ├── scan_pdfs.cpython-310.pyc
    │   │   └── __init__.cpython-310.pyc
    │   ├── apps.py
    │   ├── READMEbm.md
    │   ├── admin.py
    │   ├── routing.py
    │   ├── return_maintenance.py
    │   ├── upload_attachments.py
    │   ├── templates
    │   │   └── scan_maintenance_updater.html
    │   ├── tests.py
    │   ├── urls.py
    │   └── views.py
    ├── Home
    │   ├── migrations
    │   │   ├── __init__.py
    │   │   └── __pycache__
    │   │       └── __init__.cpython-310.pyc
    │   ├── models.py
    │   ├── __init__.py
    │   ├── __pycache__
    │   │   ├── views.cpython-310.pyc
    │   │   ├── urls.cpython-310.pyc
    │   │   ├── models.cpython-310.pyc
    │   │   ├── admin.cpython-310.pyc
    │   │   ├── apps.cpython-310.pyc
    │   │   └── __init__.cpython-310.pyc
    │   ├── apps.py
    │   ├── admin.py
    │   ├── templates
    │   │   └── Home.html
    │   ├── tests.py
    │   ├── urls.py
    │   └── views.py
    ├── lentipool_analysis_tool
    │   ├── migrations
    │   │   └── __init__.py
    │   ├── models.py
    │   ├── consumers.py
    │   ├── __init__.py
    │   ├── __pycache__
    │   │   ├── routing.cpython-310.pyc
    │   │   ├── views.cpython-310.pyc
    │   │   ├── consumers.cpython-310.pyc
    │   │   ├── urls.cpython-310.pyc
    │   │   ├── models.cpython-310.pyc
    │   │   ├── admin.cpython-310.pyc
    │   │   ├── apps.cpython-310.pyc
    │   │   └── __init__.cpython-310.pyc
    │   ├── lentipool_headers.csv
    │   ├── apps.py
    │   ├── README.md
    │   ├── admin.py
    │   ├── sto_headers.csv
    │   ├── routing.py
    │   ├── templates
    │   │   └── lentipool_analysis_tool.html
    │   ├── tests.py
    │   ├── urls.py
    │   ├── views.py
    │   └── lentipool.py
    ├── .DS_Store
    ├── greenlab_signature
    │   └── Green-Circle.png
    ├── Overlays
    │   ├── overlay.pdf
    │   └── vertical_overlay.pdf
    ├── lenti_cherrypick
    │   ├── cherry_headers.csv
    │   ├── migrations
    │   │   └── __init__.py
    │   ├── sto.py
    │   ├── .DS_Store
    │   ├── config.py
    │   ├── models.py
    │   ├── overlays
    │   │   ├── sto_pool.pdf
    │   │   └── sto_single.pdf
    │   ├── signatures
    │   │   ├── .DS_Store
    │   │   └── Green-Circle.png
    │   ├── bio.py
    │   ├── consumers.py
    │   ├── __init__.py
    │   ├── cherry.py
    │   ├── __pycache__
    │   │   ├── routing.cpython-310.pyc
    │   │   ├── config.cpython-310.pyc
    │   │   ├── views.cpython-310.pyc
    │   │   ├── cherry.cpython-310.pyc
    │   │   ├── consumers.cpython-310.pyc
    │   │   ├── urls.cpython-310.pyc
    │   │   ├── bio.cpython-310.pyc
    │   │   ├── sto.cpython-310.pyc
    │   │   ├── models.cpython-310.pyc
    │   │   ├── admin.cpython-310.pyc
    │   │   ├── apps.cpython-310.pyc
    │   │   └── __init__.cpython-310.pyc
    │   ├── form_coordinates.csv
    │   ├── apps.py
    │   ├── bio_headers.csv
    │   ├── README.md
    │   ├── library_pref.csv
    │   ├── admin.py
    │   ├── sto_headers.csv
    │   ├── routing.py
    │   ├── templates
    │   │   ├── index.html
    │   │   └── catalogue.html
    │   ├── tests.py
    │   ├── urls.py
    │   └── views.py
    ├── man_maintenance_updater
    │   ├── migrations
    │   │   ├── __init__.py
    │   │   └── __pycache__
    │   │       └── __init__.cpython-310.pyc
    │   ├── models.py
    │   ├── maintenance.py
    │   ├── consumers.py
    │   ├── __init__.py
    │   ├── __pycache__
    │   │   ├── routing.cpython-310.pyc
    │   │   ├── views.cpython-310.pyc
    │   │   ├── return_maintenance.cpython-310.pyc
    │   │   ├── consumers.cpython-310.pyc
    │   │   ├── urls.cpython-310.pyc
    │   │   ├── maintenance.cpython-310.pyc
    │   │   ├── models.cpython-310.pyc
    │   │   ├── admin.cpython-310.pyc
    │   │   ├── apps.cpython-310.pyc
    │   │   └── __init__.cpython-310.pyc
    │   ├── apps.py
    │   ├── READMEbm.md
    │   ├── admin.py
    │   ├── routing.py
    │   ├── return_maintenance.py
    │   ├── templates
    │   │   └── man_maintenance_updater.html
    │   ├── tests.py
    │   ├── urls.py
    │   └── views.py
    ├── talon_coa_generator
    │   ├── migrations
    │   │   ├── __init__.py
    │   │   └── __pycache__
    │   │       └── __init__.cpython-310.pyc
    │   ├── .DS_Store
    │   ├── models.py
    │   ├── consumers.py
    │   ├── __init__.py
    │   ├── talon_seq_headers.csv
    │   ├── __pycache__
    │   │   ├── routing.cpython-310.pyc
    │   │   ├── views.cpython-310.pyc
    │   │   ├── consumers.cpython-310.pyc
    │   │   ├── talon.cpython-310.pyc
    │   │   ├── urls.cpython-310.pyc
    │   │   ├── models.cpython-310.pyc
    │   │   ├── admin.cpython-310.pyc
    │   │   ├── apps.cpython-310.pyc
    │   │   └── __init__.cpython-310.pyc
    │   ├── apps.py
    │   ├── talon.py
    │   ├── README.md
    │   ├── talon_form_headers.csv
    │   ├── admin.py
    │   ├── routing.py
    │   ├── templates
    │   │   └── talon_coa_generator.html
    │   ├── tests.py
    │   ├── urls.py
    │   └── views.py
    ├── lab_management_portal
    │   ├── asgi.py
    │   ├── __init__.py
    │   ├── __pycache__
    │   │   ├── asgi.cpython-310.pyc
    │   │   ├── settings.cpython-310.pyc
    │   │   ├── urls.cpython-310.pyc
    │   │   └── __init__.cpython-310.pyc
    │   ├── routing.py
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    ├── db.sqlite3
    ├── __pycache__
    │   └── helper.cpython-310.pyc
    ├── pluritest_form_generator
    │   ├── migrations
    │   │   ├── __init__.py
    │   │   └── __pycache__
    │   │       └── __init__.cpython-310.pyc
    │   ├── models.py
    │   ├── form_headers.csv
    │   ├── consumers.py
    │   ├── __init__.py
    │   ├── __pycache__
    │   │   ├── routing.cpython-310.pyc
    │   │   ├── views.cpython-310.pyc
    │   │   ├── consumers.cpython-310.pyc
    │   │   ├── urls.cpython-310.pyc
    │   │   ├── models.cpython-310.pyc
    │   │   ├── admin.cpython-310.pyc
    │   │   ├── apps.cpython-310.pyc
    │   │   ├── pluritest.cpython-310.pyc
    │   │   └── __init__.cpython-310.pyc
    │   ├── apps.py
    │   ├── README.md
    │   ├── admin.py
    │   ├── routing.py
    │   ├── pluritest_template.pptx
    │   ├── tests.py
    │   ├── urls.py
    │   ├── sample_headers.csv
    │   ├── pluritest.py
    │   └── views.py
    ├── attachment_uploader
    │   ├── migrations
    │   │   └── __init__.py
    │   ├── models.py
    │   ├── consumers.py
    │   ├── __init__.py
    │   ├── __pycache__
    │   │   ├── routing.cpython-310.pyc
    │   │   ├── scan.cpython-310.pyc
    │   │   ├── views.cpython-310.pyc
    │   │   ├── consumers.cpython-310.pyc
    │   │   ├── urls.cpython-310.pyc
    │   │   ├── models.cpython-310.pyc
    │   │   ├── admin.cpython-310.pyc
    │   │   ├── apps.cpython-310.pyc
    │   │   └── __init__.cpython-310.pyc
    │   ├── apps.py
    │   ├── admin.py
    │   ├── routing.py
    │   ├── upload_attachments.py
    │   ├── scan.py
    │   ├── templates
    │   │   └── attachment_uploader.html
    │   ├── tests.py
    │   ├── urls.py
    │   └── views.py
    ├── helper.py
    ├── templates
    │   ├── .DS_Store
    │   ├── pluritest_form_generator
    │   │   └── pluritest_form_generator.html
    │   ├── lentitools_coa_generator
    │   │   └── lentitools_coa_generator.html
    │   └── mrna_coa_generator
    │       └── mrna_coa_generator.html
    ├── manage.py
    ├── Fonts
    │   └── NotoSansCJK-VF.ttf.ttc
    ├── lentitools_coa_generator
    │   ├── migrations
    │   │   ├── __init__.py
    │   │   └── __pycache__
    │   │       └── __init__.cpython-310.pyc
    │   ├── models.py
    │   ├── consumers.py
    │   ├── __init__.py
    │   ├── lentitools_form_headers.csv
    │   ├── __pycache__
    │   │   ├── routing.cpython-310.pyc
    │   │   ├── generate_coa.cpython-310.pyc
    │   │   ├── views.cpython-310.pyc
    │   │   ├── consumers.cpython-310.pyc
    │   │   ├── urls.cpython-310.pyc
    │   │   ├── models.cpython-310.pyc
    │   │   ├── admin.cpython-310.pyc
    │   │   ├── apps.cpython-310.pyc
    │   │   └── __init__.cpython-310.pyc
    │   ├── apps.py
    │   ├── README.md
    │   ├── admin.py
    │   ├── routing.py
    │   ├── generate_coa.py
    │   ├── tests.py
    │   ├── urls.py
    │   ├── vertical_overlay.pdf
    │   └── views.py
    └── mrna_coa_generator
        ├── mRNA_form_headers.csv
        ├── mRNA_seq_headers.csv
        ├── migrations
        │   ├── __init__.py
        │   └── __pycache__
        │       └── __init__.cpython-310.pyc
        ├── .DS_Store
        ├── models.py
        ├── consumers.py
        ├── __init__.py
        ├── __pycache__
        │   ├── routing.cpython-310.pyc
        │   ├── views.cpython-310.pyc
        │   ├── consumers.cpython-310.pyc
        │   ├── urls.cpython-310.pyc
        │   ├── models.cpython-310.pyc
        │   ├── admin.cpython-310.pyc
        │   ├── mrna_coa_generator.cpython-310.pyc
        │   ├── apps.cpython-310.pyc
        │   └── __init__.cpython-310.pyc
        ├── apps.py
        ├── mrna_coa_generator.py
        ├── README.md
        ├── admin.py
        ├── routing.py
        ├── tests.py
        ├── urls.py
        └── views.py
</lab_management_portal>