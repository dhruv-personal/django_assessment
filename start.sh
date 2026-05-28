#!/bin/bash

echo "Events Platform - Starting..."

echo "Starting services..."
sudo docker-compose up --build

echo "Waiting for services to be ready..."
sleep 15

echo "Running migrations..."
sudo docker-compose exec -T web python manage.py migrate --noinput

echo "Creating logs directory..."
sudo docker-compose exec -T web mkdir -p logs
