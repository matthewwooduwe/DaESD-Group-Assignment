# Sprint 0 Planning Document
**Duration:** Weeks 1-3 of Term 2  
**Status:** In Progress  
**Goal:** Team formation, technical setup, and project preparation

## Sprint 0 Objectives
This sprint is **non-assessed** but crucial for project success. Focus on:
1. Forming the team (4-5 members)
2. Setting up technical infrastructure
3. Understanding requirements
4. Planning Sprints 1-3

## Team Formation

| Role | Name | Service Ownership | GitHub Username |
|------|------|-------------------|-----------------|
| Team Lead | [Name] | Frontend Service | @username |
| Developer | [Name] | Customer API | @username |
| Developer | [Name] | Platform API | @username |
| Developer | [Name] | Producer API | @username |
| Developer | [Name] | Payment Gateway | @username |

**Team Lead Responsibilities:**
- Coordinate weekly standups
- Manage GitHub Projects
- Lead sprint reviews
- Final submission coordination

## Sprint 0 Checklist

### Week 1: Team & Repository Setup
- [ ] Team formed (4-5 members confirmed)
- [ ] Communication channels established (Slack/Discord)
- [ ] GitHub repository created
- [ ] All team members added as collaborators
- [ ] Everyone cloned repository locally
- [ ] Docker Desktop installed on all machines
- [ ] Initial README created
- [ ] .gitignore configured
- [ ] .env.example created

### Week 2: Technical Foundation
- [ ] docker-compose.yml created with all services
- [ ] MySQL database container working
- [ ] Each service has basic Django project initialized
- [ ] All containers can start successfully
- [ ] Database connections verified
- [ ] GitHub Projects board created
- [ ] Branch protection rules set on `main`
- [ ] CONTRIBUTING.md guidelines documented

### Week 3: Planning & Analysis
- [ ] BPMN diagrams analyzed
- [ ] Test cases reviewed (when provided)
- [ ] Sprint 1 tasks identified and created in GitHub Projects
- [ ] Sprint 1 goals defined
- [ ] Each developer knows their Sprint 1 tasks
- [ ] Architecture documented
- [ ] API endpoints planned
- [ ] Sprint 0 retrospective completed

## Sprint 0 Deliverables

### 1. Working Docker Environment
All team members should be able to run:
```bash
docker-compose up --build
```
And see all 6 containers running successfully.

### 2. GitHub Repository Structure
```
bristol-food-network/
├── .gitignore
├── .env.example
├── docker-compose.yml
├── README.md
├── docs/
│   ├── CONTRIBUTING.md
│   ├── ARCHITECTURE.md
│   └── sprints/
│       └── sprint-1-plan.md
├── frontend-service/
├── customer-service/
├── platform-service/
├── producer-service/
└── payment-gateway-service/
```

### 3. Initial Django Projects
Each service should have:
- `Dockerfile`
- `requirements.txt`
- Basic Django project created with `django-admin startproject`
- Can run migrations successfully

### 4. Sprint 1 Planning
Document in `docs/sprints/sprint-1-plan.md`:
- Sprint 1 goals (aligned with marking criteria)
- Task breakdown
- Assignments
- Definition of Done

## Technical Setup Tasks

### Person 1: Frontend Service
```bash
cd frontend-service
# Create Dockerfile
# Create requirements.txt
# Initialize Django project
docker-compose run --rm frontend django-admin startproject frontend .
```

### Person 2: Customer Service
```bash
cd customer-service
# Create Dockerfile
# Create requirements.txt
# Initialize Django project
docker-compose run --rm customer-api django-admin startproject customer_api .
```

### Person 3: Platform Service
```bash
cd platform-service
# Create Dockerfile
# Create requirements.txt
# Initialize Django project
docker-compose run --rm platform-api django-admin startproject platform_api .
```

### Person 4: Producer Service
```bash
cd producer-service
# Create Dockerfile
# Create requirements.txt
# Initialize Django project
docker-compose run --rm producer-api django-admin startproject producer_api .
```

### Person 5: Payment Gateway
```bash
cd payment-gateway-service
# Create Dockerfile
# Create requirements.txt
# Initialize Django project
docker-compose run --rm payment-gateway django-admin startproject gateway_api .
```

## GitHub Projects Setup

### Board Columns:
1. **Backlog** - All planned tasks
2. **Sprint 1** - Tasks for Sprint 1
3. **Sprint 2** - Tasks for Sprint 2
4. **Sprint 3** - Tasks for Sprint 3
5. **In Progress** - Currently being worked on
6. **Review** - PR created, awaiting review
7. **Done** - Merged and tested

### Labels:
- `frontend`
- `customer-api`
- `platform-api`
- `producer-api`
- `payment-gateway`
- `bug`
- `feature`
- `documentation`
- `sprint-1`
- `sprint-2`
- `sprint-3`
- `high-priority`

## Understanding Requirements

### Sprint 1 Focus (15% of Group Mark)
**Marking Criteria:**
- Project Management & Planning (50%)
- Technical Development & Implementation (50%)

**Deliverables:**
- Database connection with Models
- User authentication
- Basic containerisation
- Sprint review demo (10 minutes)

### Sprint 2 Focus (15% of Group Mark)
**Marking Criteria:**
- Project Management & Planning (50%)
- Technical Development & Implementation (50%)

**Deliverables:**
- Extended models, views, templates
- Backend/frontend components
- Inter-service communication started
- Sprint review demo (10 minutes)

### Sprint 3 Focus (50% of Group Mark)
**Marking Criteria:**
- Test Cases & Technical Understanding (50%)
- Database & Containerisation (20%)
- Authentication & Authorization (20%)
- External Services (10%)

**Deliverables:**
- Pass 70%+ test cases (for 1st class)
- Complete system functionality
- Security implementation
- Final presentation & Q&A

## Weekly Meeting Schedule

**Team Meetings:**
- Day: [Choose day]
- Time: [Choose time]
- Duration: 1 hour
- Location: [In-person/Online]

**Standup Schedule:**
- Frequency: Weekly (9 total across sprints)
- Best 6 scores count (20% of individual mark)
- Each person: 2-5 minutes

## Sprint 0 Success Criteria

By end of Sprint 0, the team should:
1. ✅ Have all 6 Docker containers running
2. ✅ All team members can access and run the project locally
3. ✅ GitHub Projects board populated with Sprint 1 tasks
4. ✅ Clear understanding of BPMN processes
5. ✅ Sprint 1 goals and assignments documented
6. ✅ Communication channels working
7. ✅ Everyone committed at least once to the repository

## Notes
- No marks for Sprint 0 - focus on preparation
- Sprint 1 starts Week 4 (16th February 2026)
- Groups cannot change after Sprint 1 starts
- If team member becomes unresponsive in first 2 weeks, contact module leaders

## Next Steps
After Sprint 0 completion:
1. Team lead creates Sprint 1 plan document
2. Each developer picks their first tasks
3. Start Sprint 1 development
4. Begin weekly standups
