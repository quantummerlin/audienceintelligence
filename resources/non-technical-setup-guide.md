# OpenClaw for Non-Technical Users
## The Complete Setup Guide for Founders, Marketers, and Operations Teams

---

## Introduction

You've heard about autonomous AI agents. You want to automate your work. But every guide you find assumes you're a developer.

**This guide is different.**

I'll walk you through setting up OpenClaw step-by-step, with copy-paste commands and zero assumptions about your technical background.

---

## Part 1: What You'll Need

### Before You Start

**Required:**
- A computer (Mac, Windows, or Linux)
- 30-60 minutes
- $20-50 to spend on API credits initially
- An OpenAI or Anthropic API key

**Not Required:**
- Programming knowledge
- Computer science degree
- Command line experience (I'll teach you)

### Understanding the Costs

| What | Cost | Notes |
|------|------|-------|
| OpenClaw software | Free | Open source |
| API credits | $20-100/month | Depends on usage |
| Server (optional) | $5-20/month | If running 24/7 |

**⚠️ Warning:** Without proper configuration, agents can burn $200+ in a single night. We'll prevent this.

---

## Part 2: Installation (Mac Users)

### Step 1: Open Terminal

1. Press `Cmd + Space`
2. Type "Terminal"
3. Press Enter

You'll see a window with a cursor. This is where we'll type commands.

### Step 2: Install Homebrew

Homebrew is like an app store for your terminal. Copy and paste this:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Press Enter. Type your computer password when asked (you won't see it typed). Press Enter again.

**Wait 5-10 minutes** for installation to complete.

### Step 3: Install Docker

Docker runs OpenClaw in an isolated container (like a mini-computer inside your computer).

```bash
brew install --cask docker
```

After installation:
1. Open Docker from your Applications folder
2. Click "Accept" on any prompts
3. Wait for Docker to start (whale icon in menu bar should be steady)

### Step 4: Install Git

Git downloads the OpenClaw code:

```bash
brew install git
```

### Step 5: Download OpenClaw

```bash
cd ~
git clone https://github.com/your-openclaw-repo/openclaw.git
cd openclaw
```

**What this does:**
- `cd ~` - Go to your home folder
- `git clone` - Download OpenClaw
- `cd openclaw` - Enter the OpenClaw folder

---

## Part 2: Installation (Windows Users)

### Step 1: Install WSL

WSL lets Windows run Linux tools:

1. Right-click the Start button
2. Select "Windows Terminal (Admin)" or "PowerShell (Admin)"
3. Type this command and press Enter:

```powershell
wsl --install
```

4. Restart your computer
5. After restart, a Linux window will open
6. Create a username and password when prompted

### Step 2: Install Docker Desktop

1. Download Docker Desktop from: https://www.docker.com/products/docker-desktop
2. Run the installer
3. Restart your computer
4. Open Docker Desktop and complete setup

### Step 3: Run Commands in WSL

Open "Ubuntu" from your Start menu. All commands below should be typed here.

```bash
# Update package list
sudo apt update

# Install Git
sudo apt install git -y

# Download OpenClaw
cd ~
git clone https://github.com/your-openclaw-repo/openclaw.git
cd openclaw
```

---

## Part 3: Get Your API Key

### Option A: OpenAI (GPT-4, GPT-3.5)

1. Go to https://platform.openai.com/api-keys
2. Sign up or log in
3. Click "Create new secret key"
4. **Copy the key immediately** - you can't see it again
5. Save it somewhere safe (password manager)

**Pricing:** GPT-4 costs ~$0.03 per 1K tokens, GPT-3.5 costs ~$0.001 per 1K tokens

### Option B: Anthropic (Claude)

1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Navigate to API Keys
4. Create a new key
5. Copy and save it

**Pricing:** Claude Sonnet costs ~$0.003 per 1K tokens, Claude Opus costs ~$0.015 per 1K tokens

### ⚠️ Important Security Notes

- **Never share your API key** - it's like a credit card number
- **Never commit it to GitHub** - bots will find and use it
- **Set a spending limit** in your API provider dashboard
- **Use a separate key for each project** - easier to revoke if compromised

---

## Part 4: Configuration

### Step 1: Create Your Config File

In your terminal (in the openclaw folder):

```bash
cp config/example.yaml config/my-agent.yaml
```

### Step 2: Edit the Config File

**Mac:**
```bash
open -a "TextEdit" config/my-agent.yaml
```

**Windows/WSL:**
```bash
notepad.exe config/my-agent.yaml
```

### Step 3: Essential Configuration

Replace the contents with this starter template:

```yaml
# BASIC SETTINGS
name: "My First Agent"

# API KEYS - Replace with your actual key
api:
  provider: "openai"  # or "anthropic"
  key: "sk-your-actual-key-here"  # REPLACE THIS
  model: "gpt-4o-mini"  # Cheaper than GPT-4

# COST CONTROL - Prevent runaway bills
budget:
  daily_limit: 5.00  # $5 max per day
  monthly_limit: 50.00  # $50 max per month
  alert_threshold: 0.8  # Alert at 80% of limit

# MEMORY - Prevent forgetting
memory:
  type: "simple"
  max_history: 20  # Remember last 20 messages

# SAFETY - Prevent disasters
safety:
  require_confirmation: true  # Ask before important actions
  allowed_directories:
    - "/workspace"  # Only access this folder
  blocked_commands:
    - "rm -rf"
    - "sudo"
    - "chmod"

# OUTPUT - Keep it concise
output:
  verbosity: "normal"  # "quiet", "normal", or "verbose"
```

**⚠️ Change These Values:**
1. Replace `sk-your-actual-key-here` with your real API key
2. Adjust budget limits to your comfort level
3. Choose your model based on the table below

### Model Selection Guide

| Model | Best For | Cost Level |
|-------|----------|------------|
| `gpt-4o-mini` | Most tasks, balanced | 💰 Cheap |
| `gpt-4o` | Complex reasoning | 💰💰 Moderate |
| `claude-3-5-sonnet` | Coding, analysis | 💰💰 Moderate |
| `claude-3-opus` | Advanced reasoning | 💰💰💰 Expensive |

**Recommendation:** Start with `gpt-4o-mini` or `claude-3-5-sonnet`.

---

## Part 5: Running Your Agent

### Step 1: Start Docker

Make sure Docker is running (check the whale icon in your menu bar/system tray).

### Step 2: Build and Start

```bash
# Build the agent (first time only, takes 5-10 minutes)
docker-compose build

# Start the agent
docker-compose up -d

# Check it's running
docker-compose ps
```

You should see something like:
```
NAME         STATUS    PORTS
openclaw     running   0.0.0.0:8080->8080/tcp
```

### Step 3: Access the Web Interface

Open your browser and go to:
```
http://localhost:8080
```

You should see the OpenClaw dashboard!

### Step 4: Test Your Agent

Try these test prompts to verify everything works:

1. **Simple test:**
   > "What is 25 multiplied by 47?"

2. **File test:**
   > "Create a file called test.txt with 'Hello World' inside"

3. **Web test:**
   > "Search for the current weather in San Francisco"

If all three work, your agent is ready!

---

## Part 6: Common Tasks

### How to Stop the Agent

```bash
docker-compose down
```

### How to Restart the Agent

```bash
docker-compose restart
```

### How to Update OpenClaw

```bash
docker-compose down
git pull origin main
docker-compose build
docker-compose up -d
```

### How to Check Logs

```bash
# See recent logs
docker-compose logs --tail=50

# Follow logs in real-time
docker-compose logs -f
```

### How to Check API Usage

**OpenAI:**
- Go to https://platform.openai.com/usage

**Anthropic:**
- Go to https://console.anthropic.com/settings/usage

---

## Part 7: Pre-Built Configurations

### Marketing Agent

```yaml
name: "Marketing Assistant"

api:
  provider: "anthropic"
  key: "${ANTHROPIC_API_KEY}"
  model: "claude-3-5-sonnet"

capabilities:
  - web_search
  - content_writing
  - social_media

instructions: |
  You are a marketing assistant. Help with:
  - Writing blog posts, tweets, LinkedIn posts
  - Researching competitors and trends
  - Creating content calendars
  
  Always maintain the brand voice provided by the user.

budget:
  daily_limit: 10.00

safety:
  require_confirmation: false  # Auto-execute for speed
```

### Research Agent

```yaml
name: "Research Assistant"

api:
  provider: "openai"
  key: "${OPENAI_API_KEY}"
  model: "gpt-4o-mini"  # Cheap for research

capabilities:
  - web_search
  - summarization
  - data_extraction

instructions: |
  You are a research assistant. Your job is to:
  - Search for information on any topic
  - Summarize findings in bullet points
  - Cite sources with URLs
  - Flag conflicting information

budget:
  daily_limit: 5.00

output:
  verbosity: "quiet"  # Less chatty, more focused
```

### Personal Assistant

```yaml
name: "Personal Assistant"

api:
  provider: "openai"
  key: "${OPENAI_API_KEY}"
  model: "gpt-4o-mini"

capabilities:
  - email_drafting
  - calendar
  - task_management
  - reminders

instructions: |
  You are a personal assistant. Help with:
  - Drafting emails (professional but friendly tone)
  - Organizing tasks by priority
  - Setting reminders
  - Summarizing information
  
  Always ask for clarification if a request is ambiguous.

budget:
  daily_limit: 3.00

safety:
  require_confirmation: true  # Confirm before sending emails
```

---

## Part 8: Troubleshooting

### "Docker is not running"

**Solution:**
1. Open Docker Desktop
2. Wait for it to start (whale icon should be steady)
3. Try again

### "Permission denied"

**Solution:**
```bash
# Mac/Linux
sudo chmod -R 755 ~/openclaw

# Or run with sudo
sudo docker-compose up
```

### "API key invalid"

**Solution:**
1. Go to your API provider's website
2. Generate a new key
3. Update your config file
4. Restart: `docker-compose restart`

### "Agent is stuck in a loop"

**Solution:**
1. Stop immediately: `docker-compose down`
2. Check your budget limits are set
3. Add loop detection to your config:

```yaml
execution:
  max_iterations: 50  # Stop after 50 steps
  timeout: 600  # Stop after 10 minutes
```

### "Agent forgot what we discussed"

**Solution:**
Increase memory history:

```yaml
memory:
  type: "simple"
  max_history: 50  # Increase from default
```

### "Running out of tokens too fast"

**Solution:**
1. Switch to a cheaper model
2. Enable caching:

```yaml
cache:
  enabled: true
  ttl: 3600  # Cache for 1 hour
```

3. Reduce verbosity:

```yaml
output:
  verbosity: "quiet"
```

### "Can't connect to localhost:8080"

**Solution:**
1. Check if container is running: `docker-compose ps`
2. Check port conflicts:
```bash
# Mac/Linux
lsof -i :8080

# Change port if needed
# In docker-compose.yml, change:
# ports:
#   - "8081:8080"  # Use 8081 instead
```

---

## Part 9: Going Further

### Running 24/7 on a Server

If you want your agent running continuously:

**Option 1: Cloud VPS ($5-20/month)**
- DigitalOcean Droplet
- Linode
- AWS EC2 (t3.micro)
- Google Cloud (e2-micro)

**Option 2: Raspberry Pi at Home**
- Requires ARM-compatible image
- Limited performance but free

**Setup steps:**
1. Rent a VPS
2. SSH into server: `ssh root@your-server-ip`
3. Install Docker and Git (see Part 2)
4. Clone OpenClaw
5. Configure and run

### Adding Skills

Skills extend your agent's capabilities:

```bash
# List available skills
cd ~/openclaw/skills
ls

# Install a skill (example: web scraping)
git clone https://github.com/skill-author/web-scraper-skill.git

# Restart to load
docker-compose restart
```

### Connecting to Other Tools

**Zapier Integration:**
1. Create a Zapier webhook trigger
2. Configure OpenClaw to send events to webhook URL

**Slack Integration:**
```yaml
integrations:
  slack:
    enabled: true
    webhook_url: "${SLACK_WEBHOOK_URL}"
    channel: "#agents"
```

**Email Integration:**
```yaml
integrations:
  email:
    enabled: true
    smtp_host: "smtp.gmail.com"
    smtp_port: 587
    username: "${EMAIL_ADDRESS}"
    password: "${EMAIL_APP_PASSWORD}"
```

---

## Part 10: Cost Management Cheat Sheet

### Daily Habits
- [ ] Check API usage dashboard once per day
- [ ] Review logs for unexpected patterns
- [ ] Monitor budget alerts

### Weekly Habits
- [ ] Review total spend vs. tasks completed
- [ ] Identify tasks that could use cheaper models
- [ ] Clean up old conversation histories

### Monthly Habits
- [ ] Rotate API keys
- [ ] Update OpenClaw version
- [ ] Review and update safety rules

### Emergency Response
If you see unexpected charges:
1. **Immediately:** Revoke API key at provider
2. **Within 5 min:** Stop Docker containers
3. **Within 30 min:** Check logs for cause
4. **Next day:** Generate new key, add better limits

---

## Glossary

| Term | Meaning |
|------|---------|
| API | Application Programming Interface - how software talks to other software |
| API Key | Like a password that lets your code access a service |
| Container | A self-contained package of software |
| Docker | Software that runs containers |
| Terminal | Text-based interface for your computer |
| Token | A chunk of text that AI processes (~4 characters) |
| YAML | A human-readable format for configuration files |
| CVE | Common Vulnerability and Exposure - a known security hole |

---

## Getting Help

### Free Resources
- OpenClaw Discord: https://discord.gg/openclaw
- GitHub Issues: https://github.com/your-openclaw-repo/openclaw/issues
- Community Forums: AI discussions and support

### When Asking for Help
Include:
1. Your operating system (Mac/Windows/Linux)
2. What you were trying to do
3. The exact error message
4. Your config file (with API key removed!)

---

## Checklist: You're Ready When...

- [ ] Docker is installed and running
- [ ] OpenClaw is downloaded and built
- [ ] API key is obtained and added to config
- [ ] Budget limits are configured
- [ ] Agent responds to test prompts
- [ ] You know how to stop the agent
- [ ] You know where to check usage

**Congratulations!** You have a working AI agent.

---

*Last updated: 2024. OpenClaw is rapidly evolving - some commands may change. Check the official documentation for updates.*