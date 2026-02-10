@echo off
REM Bristol Food Network - Initial Setup Script (Windows)
REM Run this after cloning the repository for the first time

echo ========================================
echo Bristol Food Network - Initial Setup
echo ========================================
echo.

REM Check if Docker is installed
echo Checking prerequisites...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] docker-compose is not installed. Please install docker-compose first.
    pause
    exit /b 1
)

echo [OK] Docker and docker-compose are installed
echo.

REM Create .env file from template
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
    echo [OK] .env file created ^(you can edit this file to customize settings^)
) else (
    echo [WARNING] .env file already exists, skipping
)
echo.

REM Create directory structure for services if they don't exist
echo Setting up service directories...
if not exist frontend-service mkdir frontend-service
if not exist customer-service mkdir customer-service
if not exist platform-service mkdir platform-service
if not exist producer-service mkdir producer-service
if not exist payment-gateway-service mkdir payment-gateway-service
if not exist docs\sprints mkdir docs\sprints
if not exist docs\standups mkdir docs\standups
if not exist test_cases mkdir test_cases
echo [OK] Service directories created
echo.

REM Copy Dockerfile template to each service
echo Setting up Dockerfiles...
for %%s in (frontend-service customer-service platform-service producer-service payment-gateway-service) do (
    if not exist %%s\Dockerfile (
        copy shared\Dockerfile.template %%s\Dockerfile
        echo   [OK] Created %%s\Dockerfile
    ) else (
        echo   [WARNING] %%s\Dockerfile already exists, skipping
    )
)
echo.

REM Copy requirements.txt template to each service
echo Setting up requirements.txt files...
for %%s in (frontend-service customer-service platform-service producer-service payment-gateway-service) do (
    if not exist %%s\requirements.txt (
        copy shared\requirements.txt.template %%s\requirements.txt
        echo   [OK] Created %%s\requirements.txt
    ) else (
        echo   [WARNING] %%s\requirements.txt already exists, skipping
    )
)
echo.

REM Initialize Django projects (optional - can be done later)
set /p INIT_DJANGO="Do you want to initialize Django projects now? (y/n): "
if /i "%INIT_DJANGO%"=="y" (
    echo Initializing Django projects...
    echo ^(This may take a few minutes...^)
    
    docker-compose run --rm frontend django-admin startproject frontend . 2>nul || echo   [WARNING] Frontend project might already exist
    docker-compose run --rm customer-api django-admin startproject customer_api . 2>nul || echo   [WARNING] Customer API project might already exist
    docker-compose run --rm platform-api django-admin startproject platform_api . 2>nul || echo   [WARNING] Platform API project might already exist
    docker-compose run --rm producer-api django-admin startproject producer_api . 2>nul || echo   [WARNING] Producer API project might already exist
    docker-compose run --rm payment-gateway django-admin startproject gateway_api . 2>nul || echo   [WARNING] Payment Gateway project might already exist
    
    echo [OK] Django projects initialized
) else (
    echo [SKIPPED] Skipping Django project initialization
    echo    You can initialize them later by running:
    echo    docker-compose run --rm ^<service-name^> django-admin startproject ^<project-name^> .
)
echo.

REM Build Docker containers
set /p BUILD_DOCKER="Do you want to build Docker containers now? (y/n): "
if /i "%BUILD_DOCKER%"=="y" (
    echo Building Docker containers...
    echo ^(This will take several minutes...^)
    docker-compose build
    echo [OK] Docker containers built
) else (
    echo [SKIPPED] Skipping Docker build
    echo    You can build later with: docker-compose build
)
echo.

echo ========================================
echo [OK] Setup complete!
echo.
echo Next steps:
echo 1. Review and customize your .env file
echo 2. Start the services with: docker-compose up
echo 3. Run migrations: docker-compose exec platform-api python manage.py migrate
echo 4. Create a superuser: docker-compose exec platform-api python manage.py createsuperuser
echo 5. Access the frontend at: http://localhost:8000
echo.
echo For more information, see README.md
echo ========================================
pause
