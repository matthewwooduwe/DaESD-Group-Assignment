# Bristol Regional Food Network - Complete Setup Package

## 📦 What You've Received

This package contains everything you need to set up and manage your 5-person group project for the Bristol Regional Food Network using Django, MySQL, and Docker.

---

## 🎯 Project Overview

**Architecture:** 6 Docker containers (5 microservices + 1 database)
- Frontend Service (Port 8000)
- Customer API (Port 8001)
- Platform API (Port 8002) - Contains 4 internal apps
- Producer API (Port 8003)
- Payment Gateway (Port 8004) - External mock service
- MySQL Database (Port 3306)

**Team:** 5 people, each owning one service
**Duration:** 12 weeks (Sprint 0 + 3 assessed sprints)
**Assessment:** 60% of module mark

---

## 📂 Package Contents

```
bristol-food-network/
├── QUICK_START.md                    ⭐ START HERE
├── README.md                          📖 Main documentation
├── .gitignore                         🚫 Git ignore rules
├── .env.example                       🔧 Environment template
├── docker-compose.yml                 🐳 All 6 containers
├── setup.sh                           🚀 Automated setup script
│
├── docs/
│   ├── TEAM_LEAD_GUIDE.md            👑 For team lead (you?)
│   ├── CONTRIBUTING.md               🤝 Team collaboration rules
│   ├── GitHub_Projects_Setup.md      📊 Project management guide
│   ├── Contributions_Matrix_Template.md 📝 Track individual work
│   ├── sprints/
│   │   └── sprint-0-plan.md          📅 First 3 weeks plan
│   └── standups/
│       └── standup-template.md       📢 Weekly report template
│
├── shared/
│   ├── Dockerfile.template           🐳 Docker template
│   └── requirements.txt.template     📦 Python dependencies
│
└── [service-directories]/
    ├── frontend-service/
    ├── customer-service/
    ├── platform-service/
    ├── producer-service/
    └── payment-gateway-service/
```

---

## 🚀 Getting Started (3 Steps)

### Step 1: Read QUICK_START.md
This tells you exactly what to do in the next 10 minutes.

### Step 2: Create GitHub Repository
Follow instructions in QUICK_START.md to:
- Create public GitHub repository
- Add these files
- Invite team members

### Step 3: First Team Meeting
Use the agenda in QUICK_START.md to:
- Assign service ownership
- Get everyone set up with Docker
- Plan Sprint 0

---

## 📚 Document Guide

### For EVERYONE:
1. **README.md** - Start here for technical setup and daily commands
2. **CONTRIBUTING.md** - How to collaborate, branch, commit, and PR
3. **docs/sprints/sprint-0-plan.md** - This sprint's goals and tasks

### For TEAM LEAD:
1. **QUICK_START.md** - Immediate next steps
2. **docs/TEAM_LEAD_GUIDE.md** - Your complete responsibilities guide
3. **docs/GitHub_Projects_Setup.md** - How to manage sprints

### For END OF PROJECT:
1. **docs/Contributions_Matrix_Template.md** - Track who did what

---

## ✅ Architecture Alignment with Assessment

### Sprint 1 (15% - Weeks 4-6)
**Required:**
- ✅ Database connection with Models
- ✅ User authentication
- ✅ Basic containerisation
- ✅ Project management evidence

**Your Setup Provides:**
- MySQL container with all services connected
- Authentication planned across services
- 6 containers = "optimal containerisation"
- GitHub Projects for management

### Sprint 2 (15% - Weeks 7-9)
**Required:**
- ✅ Extended models, views, templates
- ✅ Backend/frontend separation
- ✅ Further containerised architecture

**Your Setup Provides:**
- Separate frontend and API services
- Service-to-service REST APIs
- Clear architecture for expansion

### Sprint 3 (50% - Weeks 10-12)
**Required:**
- ✅ Pass 70%+ test cases (for 1st class)
- ✅ Database & Containerisation (20%)
- ✅ Authentication & Authorization (20%)
- ✅ External Services (10%)

**Your Setup Provides:**
- 6 containers = maximum containerisation marks
- Payment Gateway = external service integration
- JWT authentication framework included
- Structure supports test case implementation

---

## 🎯 Service Ownership Recommendation

| Person | Service | Why This Makes Sense |
|--------|---------|---------------------|
| Person 1 | Frontend | User interface, templates, UX |
| Person 2 | Customer API | Browse, basket, checkout logic |
| Person 3 | Platform API | Largest service - 4 internal apps |
| Person 4 | Producer API | Product listings, fulfillment |
| Person 5 | Payment Gateway | External service mock |

**Note:** Platform API is the biggest - assign to most experienced developer

---

## 🔄 Workflow Summary

### Daily:
```bash
git pull origin develop
git checkout -b feature/your-feature
# ... work ...
git commit -m "feat: description"
git push origin feature/your-feature
# Create PR on GitHub
```

### Weekly:
- Attend standup (best 6/9 count for 20% of grade)
- Update GitHub Projects board
- Document progress in docs/standups/

### End of Each Sprint:
- 10-minute live demo
- Sprint retrospective
- Plan next sprint

---

## 🎓 Grading Breakdown

**Group Mark (80% of individual):**
- Sprint 1: 15%
- Sprint 2: 15%
- Sprint 3: 50%

**Individual Mark:**
```
Individual Mark = (Group Mark × Contribution %) + (Standup Mark × 20%)
```

**Example:**
If Group gets 70% and you contribute 40% (highest in group):
- Project Mark: 70 × (40/40) = 70
- Standup Mark: 25 (average 4.17/5 on best 6 standups)
- Final: (70 × 0.8) + (25 × 0.2) = 56 + 5 = 61%

---

## ⚠️ Critical Success Factors

### From Assessment Brief:

1. **Test Cases:** System must pass 70%+ for 1st class (50% minimum to pass)
2. **Containerisation:** Your 6-container setup = optimal marks ✓
3. **Authentication:** Must implement across services
4. **External Services:** Payment Gateway = this requirement ✓
5. **Contributions Matrix:** Must be signed by ALL members
6. **Weekly Standups:** Attendance affects individual marks

### From Experience:

1. **Communication:** Set up Slack/Discord ASAP
2. **Regular Commits:** Daily small commits > big monthly commits
3. **Document Everything:** Helps with contributions matrix
4. **Ask for Help Early:** Module leaders are there to help
5. **Handle Non-Contributors:** Document attempts, escalate by week 3

---

## 🆘 Common Issues & Solutions

### "Docker won't start"
```bash
docker-compose down -v
docker-compose up --build
```

### "Port already in use"
```bash
lsof -ti:8000 | xargs kill -9
docker-compose up
```

### "Team member not responding"
1. Week 1-2: Give benefit of doubt
2. Week 3: Document attempts, contact module leaders
3. Adjust workload with team

### "Merge conflicts"
```bash
git pull origin develop
# Resolve in IDE
git add .
git commit -m "fix: resolved merge conflicts"
```

---

## 📅 Timeline

**Week 1-3 (Sprint 0):** Setup, not assessed
**Week 4-6 (Sprint 1):** Core architecture - 15%
**Week 7-9 (Sprint 2):** Extended features - 15%
**Week 10-12 (Sprint 3):** Complete system - 50%
**May 7th, 2026:** Final submission deadline (before 14:00)

---

## 🎯 Your Immediate Next Steps

1. ✅ Read QUICK_START.md (10 minutes)
2. ✅ Create GitHub repository (2 minutes)
3. ✅ Upload all these files (5 minutes)
4. ✅ Invite team members (2 minutes)
5. ✅ Send email to team (template in QUICK_START.md)
6. ✅ Schedule first team meeting
7. ✅ Read docs/TEAM_LEAD_GUIDE.md before meeting

---

## 📞 Support

**Module Leaders:**
- Dr. Khoa Phung
- Dilshan Jayatilake

**In This Package:**
- QUICK_START.md - Immediate setup
- README.md - Technical reference
- TEAM_LEAD_GUIDE.md - Leadership guide
- CONTRIBUTING.md - Collaboration rules

---

## ✨ What Makes This Setup Great

✅ **Perfectly aligned** with marking criteria
✅ **5 services** for 5 people = clear ownership
✅ **6 containers** = maximum containerisation marks
✅ **External service** included for those marks
✅ **Complete documentation** for team collaboration
✅ **GitHub Projects** workflow ready to use
✅ **Sprint plans** aligned with assessment timeline
✅ **Contributions tracking** from day 1

---

## 🎊 You're Ready!

You have everything you need to:
- Set up the repository (today)
- Onboard your team (week 1)
- Complete Sprint 0 (weeks 1-3)
- Excel in Sprints 1-3 (weeks 4-12)
- Achieve a 1st class result!

**The foundation is solid. Focus on:**
1. Clear communication with team
2. Regular small progress
3. Following the documentation
4. Asking for help when stuck

**Good luck! You've got this! 🚀**

---

*Package created to support UWE Bristol UFCFTR-30-3 Assessment Task 2*
*Based on Bristol Regional Food Network case study and BPMN diagrams*
