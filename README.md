# Bristol Regional Food Network

Distributed software system for connecting local food producers with customers.

## Architecture

**Microservices:**
- **Frontend Service** (Port 8000): Web UI and templates
- **Customer API** (Port 8001): Customer browsing, ordering, basket management
- **Platform API** (Port 8002): Catalog, Orders, Payments, Notifications
- **Producer API** (Port 8003): Product listing, order fulfillment, surplus management
- **Payment Gateway** (Port 8004): External payment processing (mock)
- **MySQL Database** (Port 3306): Shared database

## Team Members & Service Ownership

| Team Member | Service Ownership | Primary Responsibilities | Assigned To |
|-------------|-------------------|-------------------------|-------------|
| Person 1 | Frontend Service | Web UI, templates, user experience |
| Person 2 | Customer API | Browse, search, basket, checkout |
| Person 3 | Platform API | Catalog, orders, payments, notifications (4 apps) |
| Person 4 | Producer API | Listings, fulfillment, surplus alerts |
| Person 5 | Payment Gateway | External payment mock, settlements |

## Quick Start

### Prerequisites
- Docker Desktop installed
- Git installed
- GitHub account with repo access

### First Time Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-org/bristol-food-network.git
   cd bristol-food-network
   ```

2. **Create your environment file:**
   ```bash
   cp .env.example .env
   # Edit .env if needed (optional for development)
   ```

3. **Build and start all services:**
   ```bash
   docker-compose up --build
   ```

4. **In a new terminal, run migrations:**
   ```bash
   docker-compose exec platform-api python manage.py migrate
   ```

5. **Create a superuser (optional):**
   ```bash
   docker-compose exec platform-api python manage.py createsuperuser
   ```

6. **Access the services:**
   - Frontend: http://localhost:8000
   - Customer API: http://localhost:8001
   - Platform API: http://localhost:8002/admin
   - Producer API: http://localhost:8003
   - Payment Gateway: http://localhost:8004

## Daily Development Workflow

### Starting Work
```bash
# 1. Pull latest changes
git pull origin main

# 2. Create/checkout your feature branch
git checkout -b feature/your-service-name

# 3. Start containers
docker-compose up
```

### During Development
```bash
# Run migrations (when models change)
docker-compose exec <service-name> python manage.py makemigrations
docker-compose exec <service-name> python manage.py migrate

# Create a new Django app
docker-compose exec platform-api python manage.py startapp catalog

# Access Django shell
docker-compose exec platform-api python manage.py shell

# View logs
docker-compose logs -f <service-name>
```

### Finishing Work
```bash
# 1. Stop containers
docker-compose down

# 2. Stage and commit changes
git add .
git commit -m "feat(customer-api): add basket functionality"

# 3. Push to your branch
git push origin feature/your-service-name

# 4. Create Pull Request on GitHub
```

## Useful Commands

### Docker Commands
```bash
# Rebuild a specific service
docker-compose build <service-name>

# Restart a service
docker-compose restart <service-name>

# Access database directly
docker-compose exec db mysql -u brfn_user -p brfn_db

# Clean everything (WARNING: deletes all data)
docker-compose down -v
```

### Django Commands
```bash
# Create superuser
docker-compose exec <service> python manage.py createsuperuser

# Run tests
docker-compose exec <service> python manage.py test

# Collect static files
docker-compose exec <service> python manage.py collectstatic
```

## Branch Strategy

- `main` - Production-ready code (protected)
- `develop` - Integration branch for each sprint
- `feature/service-name` - Individual feature branches
- `hotfix/issue-description` - Urgent fixes

**Naming Convention:**
- `feature/customer-api-basket`
- `feature/platform-orders`
- `fix/producer-api-auth`

## Sprint Workflow

### Sprint 0 (Setup - Weeks 1-3)
- Repository setup
- Docker configuration
- Team roles assigned
- Initial architecture

### Sprint 1 (Core - Weeks 4-6)
- Basic database models
- User authentication
- Core CRUD operations
- Sprint Review: 10-min demo

### Sprint 2 (Features - Weeks 7-9)
- Extended features
- Inter-service APIs
- Business logic
- Sprint Review: 10-min demo

### Sprint 3 (Complete - Weeks 10-12)
- Full implementation
- Test case coverage
- Security & external services
- **Final Presentation & Demo**

## Project Management

We use **GitHub Projects's Kanban Board** for sprint planning:
- Sprint backlog
- Task assignments
- Progress tracking
- Burndown charts

See: https://github.com/users/matthewwooduwe/projects/1

## Testing

```bash
# Run all tests for a service
docker-compose exec <service> python manage.py test

# Run specific test
docker-compose exec <service> python manage.py test app_name.tests.TestClassName

# Run with coverage
docker-compose exec <service> coverage run --source='.' manage.py test
docker-compose exec <service> coverage report
```

## Contributing

1. Read [CONTRIBUTING.md](docs/CONTRIBUTING.md)
2. Pick a task from GitHub Projects
3. Create feature branch
4. Develop and test locally
5. Create Pull Request
6. Get 1 team member to review PR
7. Merge to develop

## Weekly Standups

Standups are documented in `docs/standups/week-X-your-name.md`:
- What you completed
- What you're working on
- Any blockers

## Documentation

- [Architecture Overview](docs/ARCHITECTURE.md)
- [API Documentation](docs/API.md)
- [Sprint Plans](docs/sprints/)
- [Standup Reports](docs/standups/)

## Troubleshooting

**Port already in use:**
```bash
docker-compose down
# Change port in docker-compose.yml
```

**Database connection errors:**
```bash
docker-compose down -v
docker-compose up --build
```

**Permission errors:**
```bash
sudo chown -R $USER:$USER .
```

## Assessment Info

- **Group Mark:** Sprint 1 (15%) + Sprint 2 (15%) + Sprint 3 (50%)
- **Individual Mark:** Group Mark × Contribution % + Standup Score (20%)
- **Test Cases:** Must pass 70%+ for 1st class marks
- **Submission:** GitHub link + Signed contributions matrix by 7th May 2026

## Support

- Module Leaders: Dr. Khoa Phung, Dilshan Jayatilake
- Team Lead: Matt Wood
- Teams Channel: bristol-food-network