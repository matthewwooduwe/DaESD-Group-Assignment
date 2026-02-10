# Quick Start - Set Up in 10 Minutes

**For the person setting up the repository right now**

---

## ⚡ Super Quick Setup

### 1. Create GitHub Repository (2 minutes)

```bash
# On GitHub.com:
# 1. New repository → "bristol-food-network"
# 2. Public visibility
# 3. Create repository

# On your computer:
git clone https://github.com/YOUR-USERNAME/bristol-food-network.git
cd bristol-food-network
```

### 2. Add All Setup Files (3 minutes)

Copy all the files you received into the repository:

```
bristol-food-network/
├── .gitignore
├── .env.example
├── docker-compose.yml
├── README.md
├── setup.sh
├── docs/
│   ├── CONTRIBUTING.md
│   ├── TEAM_LEAD_GUIDE.md
│   ├── GitHub_Projects_Setup.md
│   ├── Contributions_Matrix_Template.md
│   ├── sprints/
│   │   └── sprint-0-plan.md
│   └── standups/
│       └── standup-template.md
└── shared/
    ├── Dockerfile.template
    └── requirements.txt.template
```

### 3. Initial Commit (1 minute)

```bash
git add .
git commit -m "Initial project setup"
git push origin main
```

### 4. Add Team Members (2 minutes)

1. Go to Settings → Collaborators
2. Add your 4 teammates
3. Send them the repository link

### 5. Create GitHub Project (2 minutes)

1. Go to Projects tab → New Project
2. Name: "Bristol Food Network - Sprints"
3. Template: Board
4. Create it

**Done!** Repository is ready for your team.

---

## 📧 Email to Send Team

```
Subject: Bristol Food Network Project - Let's Get Started!

Hi team,

I've set up our GitHub repository for the Bristol Regional Food Network project!

🔗 Repository: https://github.com/YOUR-USERNAME/bristol-food-network

📝 Next Steps:
1. Accept the GitHub collaborator invitation (check your email)
2. Clone the repo: git clone [repo-url]
3. Read the README.md for setup instructions
4. Install Docker Desktop if you haven't already

📅 First Team Meeting:
[Propose date/time]

We'll go through the setup together and assign roles.

See you then!
[Your name]
```

---

## 👥 First Team Meeting Agenda (1 hour)

### 1. Introductions (5 min)
- Names, experience levels
- Availability and time zones

### 2. Assign Service Ownership (10 min)

| Person | Service | Port |
|--------|---------|------|
| Person 1 (You?) | Frontend | 8000 |
| Person 2 | Customer API | 8001 |
| Person 3 | Platform API | 8002 |
| Person 4 | Producer API | 8003 |
| Person 5 | Payment Gateway | 8004 |

### 3. Setup Together (30 min)
Everyone runs:
```bash
git clone [repo-url]
cd bristol-food-network
cp .env.example .env
bash setup.sh
docker-compose up --build
```

### 4. Sprint 0 Planning (15 min)
- Review docs/sprints/sprint-0-plan.md
- Assign first tasks
- Set weekly meeting time
- Create Slack/Discord channel

---

## 🎯 Week 1 Tasks (Sprint 0)

**Everyone:**
- [ ] Get Docker running locally
- [ ] Make first commit to your service
- [ ] Join team communication channel

**Team Lead (You):**
- [ ] Set up GitHub Projects board
- [ ] Create initial issues for Sprint 1
- [ ] Schedule weekly standups

**Each Developer:**
- [ ] Create your service's Dockerfile
- [ ] Create your service's requirements.txt
- [ ] Initialize Django project in your service
- [ ] Test your service container starts

---

## 🚀 Once Everyone is Set Up

### Test Everything Works:

```bash
# Everyone should be able to run this:
docker-compose up

# Should see all 6 containers start:
# ✅ brfn_db (MySQL)
# ✅ brfn_frontend
# ✅ brfn_customer_api
# ✅ brfn_platform_api
# ✅ brfn_producer_api
# ✅ brfn_payment_gateway
```

### Access Points:
- Frontend: http://localhost:8000
- Customer API: http://localhost:8001
- Platform API: http://localhost:8002
- Producer API: http://localhost:8003
- Payment Gateway: http://localhost:8004

---

## 📚 Key Documents to Read

**Everyone should read:**
1. README.md - Overall project guide
2. docs/CONTRIBUTING.md - How to collaborate
3. docs/sprints/sprint-0-plan.md - This sprint's goals

**You (Team Lead) should read:**
1. docs/TEAM_LEAD_GUIDE.md - Your responsibilities
2. docs/GitHub_Projects_Setup.md - Project management
3. Assessment brief (check against our architecture)

---

## ⚠️ Common First-Week Issues

**Docker won't start:**
- Check Docker Desktop is running
- Try: `docker-compose down -v` then `docker-compose up --build`

**Port conflicts:**
- Change ports in docker-compose.yml
- Or kill processes: `lsof -ti:8000 | xargs kill -9`

**Permission errors:**
- Linux/Mac: `sudo chown -R $USER:$USER .`
- Windows: Run as administrator

**Team member stuck:**
- Schedule 1-on-1 screen share
- Help them debug together
- Update docs with solution

---

## 📊 Success Metrics - End of Week 1

✅ All 5 team members have:
- Cloned repository
- Docker running
- Made at least 1 commit
- Can see all 6 containers start

✅ Team has:
- Communication channel active
- Weekly meeting scheduled
- GitHub Projects board set up
- Sprint 0 tasks assigned

---

## 🎓 Remember

**This is Sprint 0 - NOT assessed!**

Focus on:
- Getting comfortable with tools
- Understanding the architecture
- Building team dynamics
- Planning Sprint 1

Don't stress about perfect code yet. Sprint 1 is when the real work begins.

---

## 🆘 Need Help?

**Module Leaders:**
- Dr. Khoa Phung
- Dilshan Jayatilake

**In docs/:**
- TEAM_LEAD_GUIDE.md - Detailed leadership guide
- CONTRIBUTING.md - Collaboration guidelines
- GitHub_Projects_Setup.md - Project management

**Good luck! You've got great documentation and a solid foundation. The team will do great! 🚀**
