# GitHub Projects Setup Guide

This guide helps the team lead set up GitHub Projects for sprint planning and task management.

## Purpose
Track tasks, assignments, and progress across all three sprints using GitHub's built-in project management.

---

## Step 1: Create New Project

1. Go to your repository on GitHub
2. Click **"Projects"** tab
3. Click **"New project"**
4. Choose **"Board"** view
5. Name it: **"Bristol Food Network - Sprints"**
6. Click **"Create project"**

---

## Step 2: Configure Columns

**Default columns to create:**

1. **Backlog**
   - Description: "All identified tasks not yet in a sprint"
   
2. **Sprint 1** (15%)
   - Description: "Core architecture - Database, Auth, Containerisation"
   
3. **Sprint 2** (15%)
   - Description: "Extended features - Models, Views, APIs"
   
4. **Sprint 3** (50%)
   - Description: "Complete system - Test cases, Security, External services"
   
5. **In Progress**
   - Description: "Currently being worked on"
   
6. **Review**
   - Description: "PR created, awaiting code review"
   
7. **Done**
   - Description: "Merged to develop and tested"

---

## Step 3: Create Labels

Go to **Issues** → **Labels** → **New label**

### Service Labels (for tracking ownership)
- `frontend` - Green `#00FF00`
- `customer-api` - Blue `#0000FF`
- `platform-api` - Purple `#800080`
- `producer-api` - Orange `#FFA500`
- `payment-gateway` - Red `#FF0000`

### Type Labels
- `feature` - Light blue `#ADD8E6`
- `bug` - Red `#FF0000`
- `documentation` - Gray `#808080`
- `testing` - Yellow `#FFFF00`

### Sprint Labels
- `sprint-1` - Light green `#90EE90`
- `sprint-2` - Light orange `#FFDAB9`
- `sprint-3` - Light red `#FFB6C1`

### Priority Labels
- `high-priority` - Bright red `#FF0000`
- `medium-priority` - Orange `#FFA500`
- `low-priority` - Gray `#808080`

---

## Step 4: Create Initial Issues (Sprint 0)

### Example Issue Template:

**Title:** `[SERVICE] Brief task description`

**Description:**
```markdown
## Description
Detailed description of what needs to be done

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Related To
- Depends on: #issue-number
- Blocks: #issue-number

## Sprint
Sprint 1 / Sprint 2 / Sprint 3

## Estimated Effort
Small (< 4 hours) / Medium (4-8 hours) / Large (> 8 hours)
```

**Labels:** Add appropriate labels (service, type, sprint, priority)

**Assignees:** Assign to team member(s)

**Project:** Add to "Bristol Food Network - Sprints" project

---

## Step 5: Sample Sprint 1 Tasks

Create these issues to get started:

### Database & Infrastructure
1. **[PLATFORM] Create Product model**
   - Labels: `platform-api`, `feature`, `sprint-1`
   - Assignee: Person 3
   
2. **[PLATFORM] Create Customer model**
   - Labels: `platform-api`, `feature`, `sprint-1`
   - Assignee: Person 3
   
3. **[PLATFORM] Create Producer model**
   - Labels: `platform-api`, `feature`, `sprint-1`
   - Assignee: Person 3

### Authentication
4. **[CUSTOMER] Implement user registration**
   - Labels: `customer-api`, `feature`, `sprint-1`
   - Assignee: Person 2
   
5. **[CUSTOMER] Implement user login/logout**
   - Labels: `customer-api`, `feature`, `sprint-1`
   - Assignee: Person 2

### Frontend
6. **[FRONTEND] Create base template**
   - Labels: `frontend`, `feature`, `sprint-1`
   - Assignee: Person 1
   
7. **[FRONTEND] Create navigation menu**
   - Labels: `frontend`, `feature`, `sprint-1`
   - Assignee: Person 1

### Producer Features
8. **[PRODUCER] Create product listing form**
   - Labels: `producer-api`, `feature`, `sprint-1`
   - Assignee: Person 4

### Payment Gateway
9. **[PAYMENT] Create payment capture mock endpoint**
   - Labels: `payment-gateway`, `feature`, `sprint-1`
   - Assignee: Person 5

### Documentation
10. **[DOCS] Write API documentation for Sprint 1 endpoints**
    - Labels: `documentation`, `sprint-1`
    - Assignee: Team Lead

---

## Step 6: Daily Workflow

### For Developers:
1. Go to GitHub Projects board
2. Move your task from "Sprint X" to "In Progress"
3. Work on the task
4. Create Pull Request
5. Move task to "Review"
6. After PR merged, move to "Done"

### For Team Lead:
1. Monitor board daily
2. Update sprint progress
3. Identify blockers
4. Assign new tasks as needed
5. Prepare sprint review demos

---

## Step 7: Sprint Planning Meetings

**At start of each sprint:**
1. Review backlog
2. Identify sprint goals (from marking criteria)
3. Break goals into tasks
4. Create issues for each task
5. Assign to team members
6. Move to appropriate sprint column

**During sprint:**
- Daily: Check board, update task statuses
- Weekly: Standup meeting reviewing progress

**End of sprint:**
- Sprint review demo (10 minutes)
- Move incomplete tasks to next sprint or backlog
- Sprint retrospective (what went well, what to improve)

---

## Step 8: Using Milestones (Optional)

Create milestones for each sprint:

1. Go to **Issues** → **Milestones** → **New milestone**
2. Create:
   - **Sprint 1** - Due: [Week 6 date]
   - **Sprint 2** - Due: [Week 9 date]
   - **Sprint 3** - Due: 7th May 2026

3. Assign issues to milestones
4. Track progress with milestone completion %

---

## Step 9: Automation (Optional but Recommended)

Set up GitHub Actions for automated workflows:

**Auto-move PR to Review:**
When PR is created, move linked issue to "Review" column

**Auto-close Issue:**
When PR is merged, move issue to "Done"

---

## Best Practices

### Creating Issues:
**DO:**
- Write clear, specific titles
- Include acceptance criteria
- Link related issues
- Add appropriate labels
- Assign to someone
- Set realistic estimates

**DON'T:**
- Create vague issues like "Fix bugs"
- Leave issues unassigned
- Forget to add sprint labels
- Create duplicate issues

### Managing Board:
**DO:**
- Update daily
- Close completed issues promptly
- Comment on blockers
- Link PRs to issues

**DON'T:**
- Let issues pile up in "In Progress"
- Forget to move cards
- Work on unassigned tasks
- Start new work while others are blocked

### Sprint Reviews:
- Demo only completed work
- Show what's in "Done" column
- Explain any "In Progress" tasks
- Discuss blockers and solutions

---

## Tracking Contributions

GitHub Projects automatically tracks:
- Who worked on what (via assignments)
- Task completion rates
- Sprint velocity
- Individual contributions

**For Contributions Matrix:**
1. Go to **Insights** → **Contributors**
2. Screenshot commit graphs
3. Count issues completed per person
4. Document in contributions matrix

---

## Example Sprint Burndown

**Sprint 1 Example:**
- Total tasks: 15
- Week 1: 15 remaining (just started)
- Week 2: 8 remaining (good progress)
- Week 3: 2 remaining (mostly done)
- Sprint Review: Demo 13 completed features

**Velocity:** 13 tasks completed in 3 weeks ≈ 4.3 tasks/week

Use this to plan Sprint 2 workload.

---

## Troubleshooting

**Issue not showing on board?**
- Check if it's added to the project
- Ensure it has correct labels

**Can't move cards?**
- Check project permissions
- Ensure you're a collaborator

**Too many tasks in "In Progress"?**
- Limit work-in-progress (max 2-3 per person)
- Finish before starting new tasks

**Unbalanced workload?**
- Reassign tasks during standups
- Break large tasks into smaller ones
- Communicate with team

---

## Resources

- [GitHub Projects Documentation](https://docs.github.com/en/issues/planning-and-tracking-with-projects)
- [Creating Issues](https://docs.github.com/en/issues/tracking-your-work-with-issues/creating-an-issue)
- [Labels Guide](https://docs.github.com/en/issues/using-labels-and-milestones-to-track-work/managing-labels)

---

**Remember:** The project board is your team's single source of truth for what's being worked on. Keep it updated!
