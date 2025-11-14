# Lab Management Portal

A comprehensive web-based platform designed for laboratory managers and research scientists to streamline workflows, automate certificate generation, analyze CRISPR libraries, handle maintenance records, and integrate with Labguru and AWS S3. The portal unifies multiple internal tools into a scalable Django application with real-time WebSocket capabilities, PDF/PPTX generation, high-throughput parsing, and automated data pipelines.

---

## Table of Contents
1. Overview
2. Features
3. System Architecture
4. AWS Configuration
5. Environment Setup
6. NGINX Configuration
7. Gunicorn + Uvicorn Service
8. Project Structure
9. Available Tools
10. Future Improvements
11. License

---

## Overview

The Lab Management Portal consolidates a suite of laboratory automation and data management tools into a single application. This system is ideal for labs that handle large-scale CRISPR workflows, routine equipment maintenance, certificate generation, and internal data processing. It integrates seamlessly with AWS services and existing lab software such as Labguru.

Technologies used:
- Django (ASGI)
- Django Channels (WebSockets)
- Uvicorn + Gunicorn
- NGINX reverse proxy
- AWS S3 + S3FS mount

---

## Features

### General Features
- Unified interface for numerous lab automation tools
- Real-time WebSocket-powered dashboards
- Automated PDF, CSV, and PPTX generation
- High-throughput ETL capabilities
- Labguru integration for uploading attachments and maintenance logs

### COA & Document Generators
- mRNA COA generator
- Talon sequencing COA generator
- Lentitools COA generator
- Pluritest PPTX form generator

### CRISPR/Lentiviral Tools
- Lentipool analysis tool
- Cherrypick mapping and plate generation
- sgRNA distribution and library QC workflows

### Lab Maintenance Tools
- Manual maintenance updater
- Scanned maintenance updater
- Attachment uploader (Labguru)

---

## System Architecture

Client → NGINX → Gunicorn + Uvicorn → Django ASGI → App Modules  
                         ↓  
                       S3FS  
                         ↓  
                        AWS S3

---

## AWS Configuration

S3 Bucket: lsg-bid-services

Bucket Policy:
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

---

## Environment Setup

### .bashrc Configuration

# Source global definitions
if [ -f /etc/bashrc ]; then
        . /etc/bashrc
fi

export PATH=/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/home/ec2-user/.local/bin:/home/ec2-user/bin:/usr/lib64/libreoffice/program:/home/ec2-user/s3
export PYTHONPATH=/usr/lib64/python3.7/site-packages
export UNO_PATH=/usr/lib64/libreoffice/program
export JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk/jre/bin/java

# Mount S3 bucket
/usr/bin/s3fs lsg-bid-services ~/s3 -o passwd_file=${HOME}/.bucket_password

# Conda initialization
export LD_PRELOAD=/usr/lib64/libstdc++.so.6

---

## NGINX Configuration

File: /etc/nginx/nginx.conf

user nginx;
worker_processes auto;

include /usr/share/nginx/modules/*.conf;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;

    upstream channels-backend {
        server localhost:8001;
    }

    server {
        listen 80;
        server_name _;

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
        }
    }
}

---

## Gunicorn + Uvicorn Service

File: /etc/systemd/system/gunicorn.service

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

---

## Project Structure

lab_management_portal/
├── attachment_uploader/
├── lenti_cherrypick/
├── lentipool_analysis_tool/
├── lentitools_coa_generator/
├── man_maintenance_updater/
├── mrna_coa_generator/
├── pluritest_form_generator/
├── scan_maintenance_updater/
├── talon_coa_generator/
├── lab_management_portal/
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
├── templates/
├── Fonts/
├── db.sqlite3
├── manage.py
└── helper.py

Each module contains independent URLs, views, WebSocket consumers, templates, CSV headers, PDF overlays, and logic.

---

## Available Tools

### Lentipool Analysis Tool
- CSV parsing
- sgRNA distribution analysis
- Coverage validation
- Live WebSocket progress updates

### Cherrypick Tool
- Plate assembly
- Barcode/library mapping
- Signature & overlay PDF generation

### COA Generators
- mRNA PDF generator
- Talon sequencing COA generator
- Lentitools COA generator
- Pluritest PPTX generator

### Maintenance Tools
- Upload attachments to Labguru
- Manual and scanned maintenance logs
- Automatic PDF parsing and record updates

### WebSocket-Powered Features
- Real-time progress bars
- Status push updates
- Asynchronous file processing

---

## Future Improvements
- Docker and containerized deployments
- GitHub Actions CI/CD automation
- Replace S3FS with boto3 streaming
- Broader dashboard visibility and analytics
- ECS/Fargate deployment option
- Enhanced unit/integration test suite

---

## License
Internal / proprietary. Modify based on deployment environment.
