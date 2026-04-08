# OpenClaw Cost Optimization Guide
## Stop Burning Money on API Calls

---

## The Problem: Your Agent is a Money Furnace

If you're reading this, you've probably experienced one of these scenarios:

- **$200 surprise bill** from an agent that looped overnight
- **$300/day costs** trying to run 24/7 operations
- **Model confusion** burning 10-15x more tokens than necessary
- **Token bloat** from inefficient memory management

This guide will show you exactly how to cut your OpenClaw API costs by 50-80% without sacrificing agent capability.

---

## Part 1: Understanding the Cost Drivers

### 1.1 Model Selection: The 15x Multiplier

The single biggest cost factor is model selection. Here's the reality:

| Model | Relative Cost | Best For |
|-------|--------------|----------|
| **Claude Opus** | 15x (most expensive) | Complex reasoning, multi-step planning, creative tasks |
| **Claude Sonnet** | 1x (baseline) | Most agentic tasks, coding, analysis |
| **Claude Haiku** | 0.1x (cheapest) | Simple queries, formatting, quick responses |
| **GPT-4** | 10x | General reasoning, knowledge tasks |
| **GPT-4 Turbo** | 5x | Faster GPT-4 alternative |
| **GPT-3.5** | 0.5x | Simple tasks, classification |

**The Rule:** Use the cheapest model that can handle the task. Most agents spend 80% of their time on tasks that don't require Opus.

### 1.2 Token Bloat: The Hidden Tax

OpenClaw's default memory management is inefficient:

- **Redundant context** sent with every API call
- **Full conversation history** instead of summaries
- **Verbose system prompts** repeated unnecessarily
- **No compression** of previous exchanges

**Typical waste:** 40-60% of tokens are unnecessary.

### 1.3 Runaway Agents: The $200 Nightmare

Agents can enter infinite loops where they:
- Repeatedly "research" the same thing
- Get stuck in decision cycles
- Make the same API call 50+ times
- Run for hours without progress

Without circuit breakers, one loop can cost $200+ in a single night.

---

## Part 2: Model Selection Matrix

### Decision Framework

Use this decision tree for each task type:

```
Is the task complex reasoning? (planning, strategy, creative)
├── YES → Use Opus
└── NO ↓

Is the task coding/analysis/execution?
├── YES → Use Sonnet (DEFAULT for most agent work)
└── NO ↓

Is the task simple/formatting/quick?
├── YES → Use Haiku or GPT-3.5
└── NO → Re-evaluate task description
```

### Task-by-Task Model Recommendations

| Task Type | Recommended Model | Why |
|-----------|------------------|-----|
| **Planning complex workflows** | Opus | Requires multi-step reasoning |
| **Writing code** | Sonnet | Best cost/performance for coding |
| **Debugging** | Sonnet | Good enough for most issues |
| **Code review** | Sonnet | Doesn't need Opus-level reasoning |
| **File operations** | Haiku | Simple read/write/format |
| **Web scraping** | Sonnet | Needs parsing logic |
| **Data analysis** | Sonnet | Good balance of capability |
| **Simple classification** | Haiku | Binary or multi-class sorting |
| **Creative writing** | Opus | Quality matters more than cost |
| **Summarization** | Haiku/Sonnet | Depends on length/complexity |
| **Translation** | Haiku | Straightforward task |
| **Research/synthesis** | Opus | Needs deep reasoning |

### The 80/20 Rule for Agents

- **80% of tasks** → Sonnet or cheaper
- **20% of tasks** → Opus (complex reasoning only)

**Typical savings:** Switching from "always Opus" to smart routing saves 60-70% on API costs.

---

## Part 3: Memory Optimization

### 3.1 Configure Memory Compression

OpenClaw's default memory sends full conversation history. Fix this:

**Step 1:** Enable conversation summarization

Add to your agent configuration:
```yaml
memory:
  type: "compressed"
  max_history: 10
  summarization: true
  summary_trigger: 5  # Summarize after 5 exchanges
```

**Step 2:** Use semantic memory instead of chat history

```yaml
memory:
  type: "semantic"
  embedding_model: "text-embedding-3-small"
  retrieval_limit: 5
```

This stores facts, not conversation logs. Reduces token usage by 50-70%.

### 3.2 Trim System Prompts

Default system prompts are often 500-1000 tokens. Trim to essentials:

**Before (847 tokens):**
```
You are an AI assistant designed to help users with various tasks. You should always be helpful, harmless, and honest. When approaching problems, think step by step and explain your reasoning. If you're unsure about something, ask for clarification. Always verify your work before presenting results. Remember that accuracy is more important than speed...
```

**After (124 tokens):**
```
You are an autonomous agent. Execute tasks efficiently.
Rules:
- Verify before acting
- Ask if unclear
- Report progress concisely
```

**Savings:** 723 tokens × every API call = significant reduction over time.

### 3.3 Implement Context Checkpoints

For long-running tasks, save progress checkpoints:

```yaml
checkpoints:
  enabled: true
  interval: 10  # Save every 10 steps
  storage: "local"  # or "s3", "redis"
```

This prevents catastrophic context loss and reduces re-explanation tokens.

---

## Part 4: Circuit Breakers & Budget Controls

### 4.1 Implement Hard Budget Caps

**Critical:** Add these safeguards to prevent runaway costs.

**Method 1: Environment Variable Cap**

Create a monitoring script:
```python
import os
import sys
from openai import OpenAI

client = OpenAI()
MAX_DAILY_SPEND = float(os.getenv("MAX_DAILY_SPEND", 10.00))  # $10 default

def check_budget():
    # Get today's usage from your API provider
    usage = client.usage.get(date="today")
    if usage.total_cost >= MAX_DAILY_SPEND:
        print("BUDGET EXCEEDED - STOPPING AGENT")
        sys.exit(1)

# Call before each agent action
check_budget()
```

**Method 2: Token Counter Middleware**

```python
class TokenCounter:
    def __init__(self, max_tokens=100000):
        self.max_tokens = max_tokens
        self.used = 0
    
    def count_and_check(self, tokens_used):
        self.used += tokens_used
        if self.used >= self.max_tokens:
            raise Exception(f"Token limit reached: {self.used}/{self.max_tokens}")
        return True
```

### 4.2 Kill Switch for Infinite Loops

Detect and stop looping behavior:

```python
import time
from collections import defaultdict

class LoopDetector:
    def __init__(self, max_repeats=3, window_seconds=60):
        self.max_repeats = max_repeats
        self.window = window_seconds
        self.actions = defaultdict(list)
    
    def check_action(self, action_type, action_detail):
        """Returns True if this action appears to be looping."""
        now = time.time()
        key = f"{action_type}:{action_detail[:50]}"  # Truncate for comparison
        
        # Clean old entries
        self.actions[key] = [t for t in self.actions[key] if now - t < self.window]
        self.actions[key].append(now)
        
        if len(self.actions[key]) >= self.max_repeats:
            print(f"LOOP DETECTED: {action_type} repeated {len(self.actions[key])} times")
            return True
        return False

# Usage
detector = LoopDetector(max_repeats=3, window_seconds=60)

# Before each agent action:
if detector.check_action("api_call", "search_web"):
    # Stop the agent or force a different approach
    agent.interrupt()
```

### 4.3 Time-Based Limits

Prevent agents from running indefinitely:

```bash
# Run agent with 30-minute timeout
timeout 1800 python -m openclaw run --config agent.yaml

# Or in your agent config:
execution:
  max_runtime_minutes: 30
  on_timeout: "save_state"  # Don't lose progress
```

---

## Part 5: Token Efficiency Checklist

Run through this checklist weekly:

### Pre-Deployment
- [ ] Selected appropriate model (not defaulting to most expensive)
- [ ] Configured memory compression
- [ ] Trimmed system prompts to essentials
- [ ] Set daily/hourly budget caps
- [ ] Implemented loop detection
- [ ] Added timeout limits

### Daily Monitoring
- [ ] Check API dashboard for anomalies
- [ ] Review token usage by agent/task
- [ ] Identify top token-consuming operations
- [ ] Look for repeated identical calls

### Weekly Optimization
- [ ] Analyze cost-per-task metrics
- [ ] Identify tasks that could use cheaper models
- [ ] Review and update summarization triggers
- [ ] Clean up unused context in long-running agents

---

## Part 6: Cost Calculation Formulas

### Estimating Daily Costs

```
Daily Cost = (Avg tokens per call × Calls per day × Price per 1K tokens) / 1000

Example for Sonnet:
- 2000 tokens avg per call
- 500 calls per day
- $0.003 per 1K tokens (input)

Daily Cost = (2000 × 500 × 0.003) / 1000 = $3.00/day
```

### Cost Comparison Calculator

| Scenario | Opus | Sonnet | Savings |
|----------|------|--------|---------|
| 1000 calls, 2K tokens each | $90 | $6 | $84 (93%) |
| 500 calls, 5K tokens each | $112 | $7.50 | $104.50 (93%) |
| 24/7 agent, 100 calls/hr | $648/day | $43/day | $605/day |

### Break-Even Analysis

When does it make sense to pay for optimization tools?

```
If you spend $500/month on API calls:
- A $29/month tool that saves 20% = $100 savings - $29 cost = $71 net savings
- A $99/month tool that saves 50% = $250 savings - $99 cost = $151 net savings
```

---

## Part 7: Quick Wins (Implement Today)

### 1. Switch Default Model to Sonnet
**Time:** 5 minutes
**Savings:** 90%+ if you were using Opus by default

```yaml
model:
  default: "claude-sonnet-4-20250514"
```

### 2. Add a $50 Daily Cap
**Time:** 10 minutes
**Savings:** Prevents catastrophic overruns

```python
MAX_DAILY_SPEND=50  # Set in environment
```

### 3. Enable Response Caching
**Time:** 5 minutes
**Savings:** 10-30% by reusing identical responses

```yaml
cache:
  enabled: true
  ttl: 3600  # 1 hour
```

### 4. Reduce Max Tokens Per Response
**Time:** 2 minutes
**Savings:** Prevents runaway responses

```yaml
model:
  max_tokens: 2000  # Adjust based on needs
```

### 5. Add 30-Minute Timeout
**Time:** 2 minutes
**Savings:** Stops infinite loops

```yaml
execution:
  timeout: 1800  # seconds
```

---

## Appendix: Model Pricing Reference (2024)

### Anthropic Claude
| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|-------|----------------------|------------------------|
| Opus 4 | $15.00 | $75.00 |
| Sonnet 4 | $3.00 | $15.00 |
| Haiku 3.5 | $0.80 | $4.00 |

### OpenAI GPT
| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|-------|----------------------|------------------------|
| GPT-4 | $30.00 | $60.00 |
| GPT-4 Turbo | $10.00 | $30.00 |
| GPT-3.5 Turbo | $0.50 | $1.50 |

---

## Conclusion

You don't need to accept runaway API costs as the price of autonomous agents. By implementing:

1. **Smart model selection** (biggest impact)
2. **Memory compression** (token reduction)
3. **Budget circuit breakers** (safety net)
4. **Loop detection** (prevent runaway)

You can reduce your OpenClaw API costs by 50-80% while maintaining agent capability.

**Start today:** Pick one quick win from Part 7 and implement it now.

---

*Last updated: 2024. Prices subject to change. Verify current pricing with your API provider.*