# Contributing Guidelines

## 🤝 Team Collaboration Rules

### 1. Communication
- **Daily:** Check Slack/Discord for updates
- **Weekly Standups:** Attend all 9 standups (best 6 count)
- **Sprint Reviews:** Attend all sprint review sessions
- **Response Time:** Respond to team messages within 24 hours

### 2. Code Quality Standards

**Before Committing:**
- [ ] Code runs without errors
- [ ] No syntax errors or warnings
- [ ] Tested locally with `docker-compose up`
- [ ] Follows Django best practices
- [ ] Added docstrings to new functions/classes

**Commit Message Format:**
```
type(scope): short description

Longer description if needed

Fixes #issue-number
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting, missing semicolons, etc.
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(customer-api): add shopping basket functionality

Implemented basket CRUD operations with session storage.
Users can now add, remove, and update basket items.

Fixes #23
```

```
fix(platform-api): resolve payment calculation error

Commission was being calculated incorrectly for multi-vendor orders.
Updated calculation logic to handle split payments.

Fixes #45
```

### 3. Branch Strategy

**Main Branches:**
- `main` - Protected, only for releases
- `develop` - Integration branch for each sprint

**Feature Branches:**
Format: `feature/service-component`

Examples:
- `feature/customer-api-basket`
- `feature/platform-catalog`
- `feature/producer-listings`
- `feature/payment-gateway-settlement`

**Creating a Feature Branch:**
```bash
# Always branch from develop
git checkout develop
git pull origin develop
git checkout -b feature/your-service-component

# Work on your feature...

# Push to remote
git push origin feature/your-service-component
```

### 4. Pull Request Process

**Before Creating PR:**
1. Pull latest changes from `develop`
2. Resolve any merge conflicts
3. Test everything works with `docker-compose up`
4. Write clear PR description

**PR Template:**
```markdown
## Description
Brief description of what this PR does

## Changes
- Added X functionality
- Updated Y model
- Fixed Z bug

## Testing
- [ ] Tested locally
- [ ] All containers start successfully
- [ ] No breaking changes to other services

## Screenshots (if UI changes)
[Add screenshots here]

## Related Issues
Closes #issue-number
```

**PR Review Rules:**
- **Required:** 1 team member approval
- **Merge:** Only to `develop` branch
- **Delete:** Delete feature branch after merge

### 5. Code Review Guidelines

**As a Reviewer:**
- [ ] Code follows project structure
- [ ] No hardcoded credentials or secrets
- [ ] Database queries are efficient
- [ ] Error handling is present
- [ ] Comments explain complex logic
- [ ] No unnecessary files committed

**Review Checklist:**
```markdown
- [ ] Code quality is good
- [ ] Tests pass (if applicable)
- [ ] Documentation updated
- [ ] No merge conflicts
- [ ] Follows Django conventions
```

### 6. Service Development Rules

**Database Models:**
- Define models in your service's `models.py`
- Run migrations in your service container
- Document any model relationships

**API Endpoints:**
- Follow REST conventions (GET, POST, PUT, DELETE)
- Use Django Rest Framework serializers
- Add authentication where needed
- Document endpoints in `docs/API.md`

**Inter-Service Communication:**
- Use HTTP requests to call other services
- Use environment variables for service URLs
- Handle connection errors gracefully
- Add retry logic for critical operations

### 7. File Organization

**Service Structure:**
```
service-name/
├── Dockerfile
├── requirements.txt
└── service_name/
    ├── manage.py
    ├── service_name/
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    ├── app_name/
    │   ├── models.py
    │   ├── views.py
    │   ├── serializers.py
    │   ├── urls.py
    │   └── tests.py
    └── templates/
```

**What NOT to Commit:**
- `.env` files (use `.env.example` instead)
- `__pycache__/` directories
- `.pyc` files
- `db.sqlite3` files
- IDE-specific files (`.idea/`, `.vscode/`)
- Log files

### 8. Testing Requirements

**Unit Tests:**
- Write tests for models, views, serializers
- Place in `tests.py` or `tests/` directory
- Run before pushing: `docker-compose exec <service> python manage.py test`

**Integration Tests:**
- Test API endpoints
- Test service-to-service communication
- Test with Docker containers running

### 9. Documentation Requirements

**Update When:**
- Adding new API endpoints → Update `docs/API.md`
- Changing architecture → Update `docs/ARCHITECTURE.md`
- Adding dependencies → Update `requirements.txt` AND `README.md`

**Standup Documentation:**
Create file: `docs/standups/week-X-yourname.md`
```markdown
# Week X Standup - Your Name

## Completed
- Implemented basket functionality
- Added product search API

## In Progress
- Working on checkout flow
- Fixing basket session storage bug

## Blockers
- Waiting for platform API authentication endpoint
- Need help with MySQL connection pooling

## Next Week
- Complete checkout integration
- Add unit tests for basket operations
```

### 10. Sprint-Specific Rules

**Sprint 1 (Core Architecture):**
- Focus on basic functionality
- Get all services running
- Implement core database models
- Basic authentication

**Sprint 2 (Features):**
- Extend functionality
- Inter-service APIs
- Business logic implementation
- Improved error handling

**Sprint 3 (Complete System):**
- Pass all test cases
- Security implementation
- External service integration
- Code cleanup and documentation

### 11. Conflict Resolution

**Merge Conflicts:**
1. Pull latest from `develop`
2. Resolve conflicts in your IDE
3. Test thoroughly
4. Commit resolved conflicts

**Code Disagreements:**
1. Discuss in team meeting
2. Refer to Django best practices
3. Vote if needed (majority wins)
4. Document decision in PR

**Team Issues:**
1. Try to resolve within team first
2. If member not responding for 2 weeks → Contact module leaders
3. Document all communication attempts
4. Update contributions matrix

### 12. GitHub Projects Usage

**Task Statuses:**
- **Backlog:** Planned but not started
- **To Do:** Ready for current sprint
- **In Progress:** Actively working
- **Review:** PR created, awaiting review
- **Done:** Merged and tested

**Creating Tasks:**
1. Click "New Issue"
2. Use template (Feature/Bug/Task)
3. Assign to yourself
4. Add to current sprint
5. Link to service label

**Updating Tasks:**
- Move cards as work progresses
- Comment on blockers
- Link related PRs
- Close when merged

### 13. Weekly Standup Attendance

**Required:**
- Attend all 9 standups
- Prepare 2-5 minute update
- Document in `docs/standups/`

**Standup Format:**
1. What you completed this week
2. What you're working on now
3. Any blockers or help needed

### 14. Contributions Matrix

**Track From Sprint 1:**
- Git commits (quantity and quality)
- Features implemented
- Code reviews performed
- Documentation contributions
- Sprint review participation

**Final Submission:**
- Complete by end of Sprint 3
- Must be signed by ALL members
- Reflects honest contribution percentages

### 15. Emergency Procedures

**Broken Main Branch:**
1. Don't panic
2. Revert the breaking commit
3. Fix in new branch
4. Test thoroughly before merging

**Merge Disasters:**
1. Create backup branch immediately
2. Use `git reflog` to find last good state
3. Reset to last working commit
4. Document what happened

**Service Won't Start:**
1. Check logs: `docker-compose logs <service>`
2. Rebuild: `docker-compose build <service>`
3. Check `.env` file is correct
4. Ask team for help in Slack

## Questions?

Ask in the team Slack channel or contact the team lead.

Remember: **Communication is key!** When in doubt, ask the team.
