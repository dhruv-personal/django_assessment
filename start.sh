#!/bin/bash

echo "Events Platform - Starting..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker first."
    exit 1
fi

echo "Starting services..."
docker-compose up -d --build

echo "Waiting for services to be ready..."
sleep 15

echo "Running migrations..."
docker-compose exec -T web python manage.py migrate --noinput

echo "Creating logs directory..."
docker-compose exec -T web mkdir -p logs
