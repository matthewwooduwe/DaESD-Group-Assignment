# Team Meeting Agenda

## First Meeting - 03/02/2026
### 1. Introductions
- Names, experience levels
- Availability and agreed team cooperation strategy

### 2. Assign Service Ownership

| Person | Service | Port |
|--------|---------|------|
| Person 1 | Frontend | 8000 |
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

## Week 1 Tasks (Sprint 0)

**Everyone:**
- [x] Get Docker running locally
- [x] Join team communication channel
- [x] Set up GitHub Projects board together

**Team Lead:**

- [ ] Create initial issues for Sprint 1
- [x] Schedule weekly standups

**Other Members:**
- [x] Create your service's Dockerfile
- [x] Create your service's requirements.txt
- [x] Initialize Django project in your service


---

### Test Everything Works:

```bash
docker-compose up

# Should see all 6 containers start:
# brfn_db (MySQL)
# brfn_frontend
# brfn_customer_api
# brfn_platform_api
# brfn_producer_api
# brfn_payment_gateway
```

---
## Second Meeting - 10/02/2026
### 1. 


### 2. 


### 3. 

---

## Week 2 Tasks (Sprint 0)

**Everyone:**
- [x] Set up GitHub Projects board together
- [ ] Test your service container starts

**Team Lead:**



**Other Members:**


---
