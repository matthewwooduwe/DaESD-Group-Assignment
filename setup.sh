#!/bin/bash

# Bristol Food Network - Initial Setup Script
# Run this after cloning the repository for the first time

echo "🚀 Bristol Food Network - Initial Setup"
echo "========================================"
echo ""

# Check if Docker is installed
echo "Checking prerequisites..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker Desktop first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install docker-compose first."
    exit 1
fi

echo "✅ Docker and docker-compose are installed"
echo ""

# Create .env file from template
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created (you can edit this file to customize settings)"
else
    echo "⚠️  .env file already exists, skipping"
fi
echo ""

# Create directory structure for services if they don't exist
echo "Setting up service directories..."
mkdir -p frontend-service customer-service platform-service producer-service payment-gateway-service
mkdir -p docs/sprints docs/standups test_cases
echo "✅ Service directories created"
echo ""

# Copy Dockerfile template to each service
echo "Setting up Dockerfiles..."
for service in frontend-service customer-service platform-service producer-service payment-gateway-service; do
    if [ ! -f "$service/Dockerfile" ]; then
        cp shared/Dockerfile.template "$service/Dockerfile"
        echo "  ✅ Created $service/Dockerfile"
    else
        echo "  ⚠️  $service/Dockerfile already exists, skipping"
    fi
done
echo ""

# Copy requirements.txt template to each service
echo "Setting up requirements.txt files..."
for service in frontend-service customer-service platform-service producer-service payment-gateway-service; do
    if [ ! -f "$service/requirements.txt" ]; then
        cp shared/requirements.txt.template "$service/requirements.txt"
        echo "  ✅ Created $service/requirements.txt"
    else
        echo "  ⚠️  $service/requirements.txt already exists, skipping"
    fi
done
echo ""

# Initialize Django projects (optional - can be done later)
read -p "Do you want to initialize Django projects now? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Initializing Django projects..."
    echo "(This may take a few minutes...)"
    
    docker-compose run --rm frontend django-admin startproject frontend . 2>/dev/null || echo "  ⚠️  Frontend project might already exist"
    docker-compose run --rm customer-api django-admin startproject customer_api . 2>/dev/null || echo "  ⚠️  Customer API project might already exist"
    docker-compose run --rm platform-api django-admin startproject platform_api . 2>/dev/null || echo "  ⚠️  Platform API project might already exist"
    docker-compose run --rm producer-api django-admin startproject producer_api . 2>/dev/null || echo "  ⚠️  Producer API project might already exist"
    docker-compose run --rm payment-gateway django-admin startproject gateway_api . 2>/dev/null || echo "  ⚠️  Payment Gateway project might already exist"
    
    echo "✅ Django projects initialized"
else
    echo "⏭️  Skipping Django project initialization"
    echo "   You can initialize them later by running:"
    echo "   docker-compose run --rm <service-name> django-admin startproject <project-name> ."
fi
echo ""

# Build Docker containers
read -p "Do you want to build Docker containers now? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Building Docker containers..."
    echo "(This will take several minutes...)"
    docker-compose build
    echo "✅ Docker containers built"
else
    echo "⏭️  Skipping Docker build"
    echo "   You can build later with: docker-compose build"
fi
echo ""

echo "=========================================="
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Review and customize your .env file"
echo "2. Start the services with: docker-compose up"
echo "3. Run migrations: docker-compose exec platform-api python manage.py migrate"
echo "4. Create a superuser: docker-compose exec platform-api python manage.py createsuperuser"
echo "5. Access the frontend at: http://localhost:8000"
echo ""
echo "For more information, see README.md"
echo "=========================================="
