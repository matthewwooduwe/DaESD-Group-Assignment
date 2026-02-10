# Team Lead Setup Guide
**For the person setting up the initial repository**

This guide walks you through setting up the entire project from scratch.

---

## Phase 1: GitHub Repository Setup (30 minutes)

### Step 1: Create Repository on GitHub

1. Go to GitHub and click **"New repository"**
2. Repository name: `bristol-food-network`
3. Description: `Bristol Regional Food Network - Distributed Software System`
4. Visibility: **Public** (required for submission)
5. ✅ Initialize with README (uncheck - we'll add our own)
6. Click **"Create repository"**

### Step 2: Initial Repository Setup

On your local machine:

```bash
# Clone the empty repository
git clone https://github.com/YOUR-USERNAME/bristol-food-network.git
cd bristol-food-network

# Copy all the setup files you received into this directory
# Then add and commit everything

git add .
git commit -m "Initial project setup with documentation and Docker configuration"
git push origin main
```

### Step 3: Protect Main Branch

1. Go to repository **Settings** → **Branches**
2. Click **"Add rule"**
3. Branch name pattern: `main`
4. Enable:
   - ✅ Require a pull request before merging
   - ✅ Require approvals (1)
   - ✅ Dismiss stale pull request approvals
5. Click **"Create"**

### Step 4: Create Develop Branch

```bash
git checkout -b develop
git push origin develop
```

This becomes your integration branch for all sprints.

### Step 5: Add Team Collaborators

1. Go to **Settings** → **Collaborators**
2. Click **"Add people"**
3. Add all 4 team members by their GitHub usernames
4. They should receive email invitations

---

## Phase 2: GitHub Projects Setup (20 minutes)

Follow the **GitHub_Projects_Setup.md** guide to:

1. Create new project board
2. Set up columns (Backlog, Sprint 1-3, In Progress, Review, Done)
3. Create labels for services, types, and priorities
4. Create initial Sprint 1 issues

---

## Phase 3: Team Onboarding (Week 1)

### Team Meeting Agenda:

**Before the meeting, send to everyone:**
- Repository link
- Link to this setup guide
- Link to CONTRIBUTING.md
- Request GitHub usernames

**During the meeting (1 hour):**

1. **Introductions & Roles (10 min)**
   - Assign service ownership to each person
   - Clarify team lead responsibilities
   - Set communication channels (Slack/Discord)

2. **Repository Walkthrough (15 min)**
   - Show repository structure
   - Explain branch strategy
   - Demo GitHub Projects board
   - Review CONTRIBUTING.md

3. **Technical Setup (20 min)**
   - Everyone clones repository
   - Everyone runs setup script
   - Verify Docker is working for everyone
   - Troubleshoot any issues

4. **Sprint 0 Planning (15 min)**
   - Review Sprint 0 tasks
   - Assign initial setup tasks
   - Set next meeting time
   - Agree on weekly meeting schedule

### Send After Meeting:

**Email template:**
```
Subject: Bristol Food Network - Next Steps

Hi team,

Great meeting today! Here's what you need to do:

1. Accept GitHub collaborator invitation
2. Clone the repository: git clone https://github.com/YOUR-USERNAME/bristol-food-network.git
3. Run setup script: bash setup.sh
4. Complete your assigned Sprint 0 tasks (see GitHub Projects)

Next meeting: [Date/Time]

Questions? Message in Slack!

[Your name]
Team Lead
```

---

## Phase 4: Sprint 0 Execution (Weeks 1-3)

### Week 1: Repository & Environment

**Your tasks as team lead:**
- [ ] Ensure all team members have access
- [ ] Monitor GitHub Projects board
- [ ] Help with setup issues
- [ ] Create Sprint 1 plan document

**Team tasks:**
- [ ] Everyone clones repository
- [ ] Everyone gets Docker running
- [ ] Each person creates their service Dockerfile
- [ ] Each person creates their requirements.txt
- [ ] First commits from all team members

### Week 2: Django Initialization

**Your tasks:**
- [ ] Review all PRs
- [ ] Ensure code quality
- [ ] Update documentation as needed
- [ ] Plan first standup

**Team tasks:**
- [ ] Initialize Django projects in each service
- [ ] Get all 6 containers running together
- [ ] Create basic database models
- [ ] Test inter-service connectivity

### Week 3: Sprint 1 Preparation

**Your tasks:**
- [ ] Finalize Sprint 1 task breakdown
- [ ] Assign Sprint 1 tasks
- [ ] Schedule Sprint 1 review demo
- [ ] Prepare standup tracking

**Team tasks:**
- [ ] Review BPMN diagrams
- [ ] Understand test cases (when provided)
- [ ] Plan their Sprint 1 work
- [ ] Complete Sprint 0 retrospective

---

## Phase 5: Weekly Routine (Ongoing)

### As Team Lead, You'll:

**Daily:**
- Check GitHub Projects board
- Review new commits/PRs
- Respond to team questions
- Unblock team members

**Weekly:**
- Facilitate standup meeting
- Record standup scores
- Review sprint progress
- Update sprint plan if needed

**End of Each Sprint:**
- Organize sprint review demo
- Coordinate who presents what
- Lead retrospective discussion
- Plan next sprint

---

## Managing Common Issues

### Team Member Not Responding

**Week 1-2:**
1. Send direct message
2. Try multiple channels (email, Slack, phone)
3. Give benefit of doubt (might be sick/busy)

**After Week 2:**
1. Document all communication attempts
2. Contact module leaders: Dr. Khoa Phung, Dilshan Jayatilake
3. Request workload adjustment
4. Update team on situation

**Document everything:**
```markdown
## Non-Responsive Team Member Log

### [Member Name]

**Week 1:**
- [Date]: Sent Slack message - no response
- [Date]: Sent email - no response
- [Date]: Called - no answer

**Week 2:**
- [Date]: Sent final warning
- [Date]: Contacted module leaders
- [Date]: Reassigned tasks to other team members
```

### Merge Conflicts

**Prevention:**
- Pull from develop before starting work
- Work on separate services = fewer conflicts
- Communicate before changing shared files

**Resolution:**
1. Help team member understand conflict
2. Use VS Code or PyCharm merge tools
3. Test thoroughly after resolving
4. Document what was changed

### Docker Issues

**Common problems:**

**"Port already in use":**
```bash
docker-compose down
# Kill process using port
lsof -ti:8000 | xargs kill -9
docker-compose up
```

**"Cannot connect to MySQL":**
```bash
# Wait for database to be ready
docker-compose down -v
docker-compose up --build
# Wait 30 seconds, then migrate
```

**"Permission denied":**
```bash
# On Linux/Mac
sudo chown -R $USER:$USER .
```

---

## Sprint Review Preparation

### 1 Week Before Review:

1. **Identify demo features:**
   - List what will be demonstrated
   - Assign who presents each feature
   - Create demo script

2. **Test everything:**
   - Full system walkthrough
   - Identify and fix critical bugs
   - Prepare for questions

3. **Prepare presentation:**
   - 10-minute time limit
   - Show working features only
   - Be ready for Q&A

### Demo Day:

**Format:**
1. Brief introduction (1 min)
2. Live demonstration (7 min)
3. Q&A (2 min)

**Tips:**
- Test one more time before demo
- Have backup plan if tech fails
- Share screen prepared and ready
- Everyone should speak

---

## Contributions Matrix Management

### Track From Sprint 1:

Create spreadsheet:

| Member | Commits | LOC | Features | Reviews | Docs | Standups | Total% |
|--------|---------|-----|----------|---------|------|----------|--------|
| Name 1 |         |     |          |         |      |          |        |
| Name 2 |         |     |          |         |      |          |        |

**Update weekly** to avoid last-minute disputes.

### GitHub Insights:

1. Go to **Insights** → **Contributors**
2. Export commit data
3. Screenshot contribution graphs
4. Save for contributions matrix

### End of Sprint 3:

1. Fill out contributions matrix template
2. Have team meeting to discuss
3. Reach agreement on percentages
4. Everyone signs
5. Submit with final code

---

## Final Submission Checklist (7th May 2026)

**Before 14:00:**

- [ ] GitHub repository link ready
- [ ] Repository is public
- [ ] All code pushed to main branch
- [ ] README.md is complete and accurate
- [ ] docker-compose up works without errors
- [ ] All migrations are included
- [ ] .env.example is up to date
- [ ] Contributions matrix completed and signed
- [ ] All team member signatures obtained
- [ ] Both documents submitted on Blackboard

---

## Resources for Team Lead

**Module Leaders:**
- Dr. Khoa Phung
- Dilshan Jayatilake

**Assessment Brief:**
- Review regularly for marking criteria
- Ensure work aligns with requirements

**Team Communication:**
- Set up Slack/Discord channel
- Weekly meeting schedule
- Emergency contact info

---

## Self-Care Tips

Being team lead is extra work:

✅ **DO:**
- Delegate tasks fairly
- Ask for help when stuck
- Use GitHub tools (don't track manually)
- Communicate issues early

❌ **DON'T:**
- Do everyone's work yourself
- Ignore non-contributing members
- Skip documentation
- Panic when things go wrong

**Remember:** Module leaders are there to help if team issues arise.

---

## Quick Reference Commands

```bash
# Daily workflow
git checkout develop
git pull origin develop
git checkout -b feature/my-feature
# ... work ...
git add .
git commit -m "feat: description"
git push origin feature/my-feature
# Create PR on GitHub

# Help teammate with Docker
docker-compose down
docker-compose build <service>
docker-compose up

# Check all services status
docker-compose ps

# View specific service logs
docker-compose logs -f <service>

# Run migrations
docker-compose exec platform-api python manage.py migrate

# Access database
docker-compose exec db mysql -u brfn_user -p brfn_db
```

---

**Good luck! You've got this! 🚀**

Remember: The team's success depends on good communication and documentation. Keep everyone informed and track everything!
