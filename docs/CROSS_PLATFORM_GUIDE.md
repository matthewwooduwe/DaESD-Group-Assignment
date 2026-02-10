# Cross-Platform Troubleshooting Guide

This guide helps resolve common issues across Windows, Mac, and Linux.

---

## 🖥️ Platform-Specific Setup

### Windows Users

**Setup Script:**
```cmd
setup.bat
```

**Docker Desktop:**
- Download from: https://www.docker.com/products/docker-desktop
- Enable WSL 2 backend (recommended)
- Ensure "Use Docker Compose V2" is enabled in settings

**Command Prompt vs PowerShell:**
- Both work for `docker-compose` commands
- Git Bash also works

**File Permissions:**
- Generally not an issue on Windows
- If problems occur, run CMD/PowerShell as Administrator

### Mac Users

**Setup Script:**
```bash
bash setup.sh
```

**Docker Desktop:**
- Download from: https://www.docker.com/products/docker-desktop
- May need to grant permissions in System Preferences

**Terminal:**
- Use built-in Terminal or iTerm2
- All bash commands work as documented

**File Permissions:**
- Usually not an issue
- If needed: `chmod +x setup.sh`

### Linux Users

**Setup Script:**
```bash
bash setup.sh
```

**Docker Installation:**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io docker-compose

# Add user to docker group (avoid sudo for every command)
sudo usermod -aG docker $USER
# Log out and log back in for this to take effect
```

**File Permissions:**
- May need: `sudo chown -R $USER:$USER .`
- Make setup executable: `chmod +x setup.sh`

---

## 🐳 Docker Issues

### Docker Won't Start

**Windows:**
```cmd
# Check Docker Desktop is running (system tray icon)
# Restart Docker Desktop from system tray

# If still not working:
wsl --shutdown
# Then restart Docker Desktop
```

**Mac:**
```bash
# Check Docker Desktop is running (menu bar icon)
# Restart Docker Desktop from menu bar

# If still not working, reset Docker:
# Docker Desktop → Troubleshoot → Reset to factory defaults
```

**Linux:**
```bash
# Check Docker daemon status
sudo systemctl status docker

# Start Docker if stopped
sudo systemctl start docker

# Enable Docker to start on boot
sudo systemctl enable docker
```

### Port Already in Use

**Windows:**
```cmd
# Find process using port
netstat -ano | findstr :8000

# Kill process (replace PID with actual process ID)
taskkill /PID <PID> /F

# Or change port in docker-compose.yml
```

**Mac/Linux:**
```bash
# Find and kill process using port
lsof -ti:8000 | xargs kill -9

# Or change port in docker-compose.yml
```

### Container Won't Start

**All Platforms:**
```bash
# Stop everything
docker-compose down

# Remove all volumes (WARNING: deletes database data)
docker-compose down -v

# Rebuild and start
docker-compose up --build
```

### Database Connection Errors

**All Platforms:**
```bash
# Wait for database to be ready
docker-compose down -v
docker-compose up -d db

# Wait 30 seconds
# Check database is healthy
docker-compose ps

# Then start other services
docker-compose up
```

---

## 📁 File Permission Issues

### Windows
Usually not an issue. If you encounter problems:
```cmd
# Run as Administrator
# Right-click CMD/PowerShell → "Run as administrator"
```

### Mac
```bash
# Fix ownership
sudo chown -R $(whoami) .

# Make setup script executable
chmod +x setup.sh
```

### Linux
```bash
# Fix ownership
sudo chown -R $USER:$USER .

# Make setup script executable
chmod +x setup.sh

# Fix Docker socket permissions
sudo chmod 666 /var/run/docker.sock
```

---

## 🔧 Git Issues

### Line Endings (Windows)

**Problem:** Git converts line endings causing issues with bash scripts

**Solution:**
```cmd
# Configure Git to not convert line endings for .sh files
git config --global core.autocrlf false

# If you already cloned, re-clone the repository
```

**In .gitattributes (already included in project):**
```
*.sh text eol=lf
```

### Permission Denied on setup.sh (Mac/Linux)

```bash
# Make executable
chmod +x setup.sh

# Then run
./setup.sh
```

---

## 🌐 Network Issues

### Cannot Access Localhost

**Windows with WSL 2:**
```cmd
# If using WSL 2 backend, use:
http://localhost:8000

# If that doesn't work, find WSL IP:
wsl hostname -I
# Use that IP: http://<WSL_IP>:8000
```

**All Platforms:**
- Try `http://127.0.0.1:8000` instead of `localhost`
- Check Windows Firewall / Mac Firewall
- Ensure Docker port mappings are correct in docker-compose.yml

### Inter-Service Communication

**Problem:** Services can't communicate with each other

**Solution:**
```yaml
# Ensure all services are on the same network in docker-compose.yml
networks:
  brfn-network:
    driver: bridge

# Each service should have:
networks:
  - brfn-network
```

---

## 💾 Disk Space Issues

### Docker Using Too Much Space

**All Platforms:**
```bash
# Check Docker disk usage
docker system df

# Clean up unused containers, images, volumes
docker system prune -a --volumes

# WARNING: This deletes everything not currently running!
```

### Windows: WSL 2 Disk Space

```cmd
# WSL 2 can consume lots of disk space
# Compact the virtual disk:
wsl --shutdown
diskpart
# In diskpart:
select vdisk file="C:\Users\YourUsername\AppData\Local\Docker\wsl\data\ext4.vhdx"
compact vdisk
```

---

## 🔍 IDE-Specific Issues

### PyCharm (All Platforms)

**Docker Compose Interpreter:**
- File → Settings → Project → Python Interpreter
- Add Interpreter → On Docker Compose
- Select docker-compose.yml
- Select service (e.g., platform-api)

**Windows Path Issues:**
- Ensure PyCharm uses WSL 2 if Docker Desktop uses WSL 2
- Settings → Tools → WSL → WSL executable path

### VS Code (All Platforms)

**Recommended Extensions:**
- Docker
- Remote - Containers
- Python

**Windows:**
- Install "Remote - WSL" extension if using WSL 2
- Open project in WSL: `code .` from WSL terminal

---

## 🚨 Common Error Messages

### "bind: address already in use"

**Solution:** Port conflict - see "Port Already in Use" section above

### "Cannot connect to the Docker daemon"

**Windows:**
- Ensure Docker Desktop is running
- Check WSL 2 integration is enabled

**Mac/Linux:**
```bash
# Check Docker is running
docker ps

# Start Docker daemon
sudo systemctl start docker  # Linux
# or restart Docker Desktop  # Mac
```

### "no such file or directory: /code/manage.py"

**Solution:** Django project not initialized yet
```bash
# Initialize the project first
docker-compose run --rm <service> django-admin startproject <project_name> .
```

### "Couldn't connect to Docker daemon"

**Linux:**
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Log out and back in, then test
docker ps
```

### "The process cannot access the file because it is being used by another process" (Windows)

**Solutions:**
```cmd
# Stop all containers
docker-compose down

# If that doesn't work, restart Docker Desktop

# Or reboot Windows
```

---

## 🔄 Environment-Specific Workflows

### Windows-Specific

**Using WSL 2 (Recommended):**
```bash
# Open WSL terminal
wsl

# Navigate to project
cd /mnt/c/Users/YourName/Projects/bristol-food-network

# Run Docker commands normally
docker-compose up
```

**Using Windows CMD/PowerShell:**
```cmd
# All docker-compose commands work the same
cd C:\Users\YourName\Projects\bristol-food-network
docker-compose up
```

### Mac-Specific

**M1/M2 (Apple Silicon):**
```bash
# Add platform to docker-compose.yml if needed
platform: linux/amd64

# Or use ARM-compatible images (Python 3.11 is compatible)
```

### Linux-Specific

**Running without sudo:**
```bash
# Add user to docker group (one time)
sudo usermod -aG docker $USER

# Log out and back in

# Now docker commands work without sudo
docker-compose up
```

---

## 📝 Testing Your Setup

### Verify Docker Installation

**All Platforms:**
```bash
# Check Docker version
docker --version

# Check docker-compose version
docker-compose --version

# Test Docker works
docker run hello-world
```

### Verify Project Setup

**All Platforms:**
```bash
# Clone and setup
git clone <repo-url>
cd bristol-food-network

# Windows:
setup.bat

# Mac/Linux:
bash setup.sh

# Test all containers start
docker-compose up

# Should see all 6 services starting:
# ✅ brfn_db
# ✅ brfn_frontend
# ✅ brfn_customer_api
# ✅ brfn_platform_api
# ✅ brfn_producer_api
# ✅ brfn_payment_gateway
```

---

## 🆘 Getting Help

### Team Help
1. Check this troubleshooting guide first
2. Ask in team Slack/Discord
3. Schedule screen-share debugging session

### Module Leaders
If stuck after trying everything:
- Dr. Khoa Phung
- Dilshan Jayatilake

### Docker Help
- Docker Desktop documentation
- Docker Community Forums
- Stack Overflow (search error messages)

---

## ✅ Quick Reference: Platform Commands

| Task | Windows (CMD) | Windows (PowerShell) | Mac/Linux |
|------|---------------|---------------------|-----------|
| Run setup | `setup.bat` | `.\setup.bat` | `bash setup.sh` |
| List files | `dir` | `Get-ChildItem` | `ls` |
| Change directory | `cd path` | `cd path` | `cd path` |
| View file | `type file.txt` | `Get-Content file.txt` | `cat file.txt` |
| Find process | `netstat -ano \| findstr :8000` | `Get-NetTCPConnection -LocalPort 8000` | `lsof -i:8000` |
| Kill process | `taskkill /PID 1234 /F` | `Stop-Process -Id 1234` | `kill -9 1234` |

**Note:** All `docker-compose` commands work identically across all platforms!

---

## 🎯 Pro Tips for Cross-Platform Teams

1. **Normalize Line Endings:** Already handled in `.gitattributes`
2. **Use Relative Paths:** Docker Compose handles this automatically
3. **Consistent Commands:** Stick to `docker-compose` commands (work everywhere)
4. **Document OS:** When reporting issues, mention your OS
5. **Share Screenshots:** Helps teammates help you
6. **Test on Multiple OS:** If possible, verify changes work everywhere

---

**Remember:** Docker is designed to work consistently across platforms. Most commands are identical regardless of OS!
