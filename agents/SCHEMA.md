# Aether Intel Agent Schema (v1)

Every Aether Intel agent ships as **two files**:

- `/agents/{slug}.json` — primary downloadable config. Hyperagent-compatible, also readable by any platform that handles JSON.
- `/agents/{slug}.md` — companion Markdown with just the system prompt, for users on Claude Projects, Custom GPTs, or any platform without JSON import.

A landing page at `/agents/{slug}.html` and a hero image at `/images/agents/{slug}-hero.webp` accompany every agent.

---

## JSON file shape

```json
{
  "schema_version": 1,
  "agent_id": "claude-business-strategist",
  "name": "Claude Business Strategist",
  "version": "1.0.0",
  "description": "Senior strategy advisor that runs a structured three-pass analysis on go/no-go decisions.",
  "category": "business",
  "category_label": "Business",
  "tags": ["strategy", "decisions", "analysis"],
  "model_hint": "sonnet",
  "temperature": 0.7,
  "system_prompt": "You are...",
  "recommended_tools": ["WebSearch", "WebFetch"],
  "starter_message": "What strategic decision are you working through?",
  "use_cases": [
    "Go/no-go on a new product line",
    "Pricing changes",
    "Hiring decisions"
  ],
  "example_interactions": [
    {
      "user": "Should I raise prices on my flagship product by 20%?",
      "agent": "Before we model that — what's your current win rate on this product..."
    }
  ],
  "platforms": {
    "hyperagent": "direct_import",
    "claude_projects": "system_prompt_copy",
    "custom_gpt": "instructions_copy",
    "openrouter": "system_prompt_copy",
    "claude_code": "system_prompt_copy"
  },
  "author": "Quantum Merlin",
  "license": "MIT",
  "created": "2026-05-20",
  "updated": "2026-05-20",
  "url": "/agents/claude-business-strategist.html",
  "hero": "/images/agents/claude-business-strategist-hero.webp",
  "badge": "badge-business"
}
```

---

## Field reference

| Field | Required | Type | Notes |
|---|---|---|---|
| `schema_version` | yes | int | Always `1` for now. Bump when shape changes. |
| `agent_id` | yes | string | kebab-case slug matching the filename. Stable identity across versions. |
| `name` | yes | string | Display name. Title case. |
| `version` | yes | string | semver. Bump on prompt updates. |
| `description` | yes | string | One-sentence summary. Card teaser. |
| `category` | yes | string | One of: `business`, `dev`, `agents`, `ethics`, `research`, `creative`. |
| `category_label` | yes | string | Human label shown in badge. |
| `tags` | yes | string[] | Free-form tags for search/filter. |
| `model_hint` | yes | string | `haiku` \| `sonnet` \| `opus` \| `gpt-4o` \| `gpt-5` \| `gemini-pro`. Recommended baseline. |
| `temperature` | no | float | Default `0.7`. Set lower (0.2-0.4) for deterministic agents. |
| `system_prompt` | yes | string | The actual prompt. The heart of the agent. |
| `recommended_tools` | no | string[] | Names of tools the agent works best with (WebSearch, WebFetch, Bash, etc.). |
| `starter_message` | no | string | Suggested opening prompt the user can paste to kick off a session. |
| `use_cases` | no | string[] | 2-5 concrete scenarios this agent excels at. |
| `example_interactions` | no | object[] | Sample user/agent exchanges. Renders on the landing page. |
| `platforms` | no | object | Compatibility map. Values: `direct_import` \| `system_prompt_copy` \| `instructions_copy` \| `not_supported`. |
| `author` | yes | string | Default `"Quantum Merlin"`. |
| `license` | yes | string | Default `"MIT"`. |
| `created` | yes | string | ISO date. |
| `updated` | yes | string | ISO date. |
| `url` | yes | string | Landing page path. |
| `hero` | yes | string | Hero image path. WebP only. |
| `badge` | yes | string | CSS class: `badge-business` \| `badge-dev` \| `badge-agents` \| `badge-ethics` \| `badge-secondary`. |

---

## Markdown companion file shape

```markdown
# {name}

> {description}

**Recommended model:** {model_hint}
**Temperature:** {temperature}
**Category:** {category_label}

## System Prompt

{system_prompt}

## Recommended Tools

- {tool 1}
- {tool 2}

## Use Cases

- {use case 1}
- {use case 2}

---

Built by {author}. License: {license}. Version {version}. From [Aether Intel](https://ai.quantummerlin.com/agents/{slug}.html).
```

---

## Platform compatibility values

| Value | Meaning |
|---|---|
| `direct_import` | The JSON file imports as-is. Currently only Hyperagent. |
| `system_prompt_copy` | Copy the `system_prompt` field into the platform's system prompt slot. |
| `instructions_copy` | Same as above but the platform calls it "instructions" (Custom GPTs, etc.). |
| `not_supported` | Platform can't run this agent in any usable form. |

---

## How to use these files

**On Hyperagent:** Download the JSON, open it in any agent's settings, paste into the system prompt field. Future versions will support direct import.

**On Claude Projects:** Download the JSON, open it, copy the `system_prompt` value into your Project's instructions. Or download the `.md` and copy from there.

**On Custom GPTs:** Same as Claude Projects but paste into the Instructions field.

**On OpenRouter / API direct:** Use the `system_prompt` as your system message, set `temperature` and pick a model matching `model_hint`.

**On Claude Code / agents anywhere:** The system prompt is the agent. Drop it in.

---

## Versioning policy

- `1.x.x` — schema_version 1 (current).
- Prompt revisions bump the minor version (1.0.0 → 1.1.0).
- Structural changes to the agent (new use cases, tool changes) bump the patch (1.0.0 → 1.0.1).
- Major version (1.0.0 → 2.0.0) only for prompt rewrites that change the agent's behaviour materially.
