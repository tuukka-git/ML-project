#!/bin/bash

# Exit on error
set -e

echo "Installing dependencies..."
apt install pip
pip install -r requirements.txt

echo "Setting up NGINX..."
sudo cp nginx.conf /etc/nginx/sites-available/flask_service
sudo ln -s /etc/nginx/sites-available/flask_service /etc/nginx/sites-enabled/
sudo systemctl restart nginx

echo "Generating SSL certificates..."
sudo mkdir -p /etc/nginx/ssl
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/nginx/ssl/selfsigned.key -out /etc/nginx/ssl/selfsigned.crt -subj "/CN=localhost"

echo "Starting Flask application..."
bash start_service.sh

echo "Deployment completed successfully."