"""
Lab detail page templater.

Reads:
  - labs.json (canonical data: name, founded, hq, country, color_accent, models)
  - LAB_CONTENT (this file): editorial intro, use/skip lists, articles, status, next-lab pointer

Emits:
  - {slug}.html for each of the 11 labs (OpenAI is hand-tuned; this script
    generates Anthropic through Nous Research)
"""
import json, os, html as html_lib

# ── Per-lab editorial content (everything not in labs.json) ─────────────────
LAB_CONTENT = {
    "anthropic": {
        "next_lab": "google-deepmind",
        "next_lab_name": "Google DeepMind",
        "status": "Frontier",
        "intro": [
            "Founded in 2021 by Dario and Daniela Amodei (former OpenAI VP of Research and policy chief, respectively) along with several other ex-OpenAI researchers, Anthropic positioned itself from day one as the safety-conscious frontier lab. Constitutional AI is the methodology, training models against a written set of principles rather than purely through human-rating reinforcement. The Responsible Scaling Policy is the public commitment to pause new training tiers until safety evidence catches up.",
            "The 2026 strategy is to ship the model developers actually want. Claude Sonnet 4.6 became the daily driver for most production agentic workflows. Claude Code became the IDE companion that pulled enterprises off Cursor and Copilot. The latest raise puts the company near <strong>$900B valuation</strong>, ARR up <em>80x year over year</em>, and the $200B Google compute deal locks in years of training capacity.",
            "The catch is the one that haunts every safety-first lab. When the bar is high, products feel hedged. Claude refuses requests other models execute, asks clarifying questions other models guess at. The pitch is that developers want a thoughtful collaborator more than an obedient one. That bet is working at the high end. It leaves room for rivals at the low end where users want speed without friction.",
        ],
        "articles": [
            ("/articles/61-anthropic-200b-google-compute-deal.html", "Business",  "Anthropic's $200B Google Bet: Why the AI Lab Is Hoovering Up Every Chip"),
            ("/articles/33-claude-code-80x-anthropic-infrastructure.html", "Business", "Claude Code Up 80x. Anthropic Accidentally Became the Infrastructure Company."),
            ("/articles/31-anthropic-reads-claudes-mind.html", "Agents", "Anthropic Can Read Claude's Mind. And It Knows When It's Being Tested."),
            ("/articles/57-anthropic-cfo-ai-arms-race-economics.html", "Business", "Anthropic's CFO Just Revealed the Real Economics of the AI Arms Race"),
        ],
        "use_for": [
            "Long-context document analysis where Claude's stable comprehension at 500K+ tokens matters",
            "Production agentic workflows where Sonnet's reliability beats faster rivals",
            "Coding agents — Claude Code is the gold standard with deep IDE integration",
            "Use cases that benefit from a model that refuses-when-uncertain rather than hallucinates",
            "Enterprise rollouts where Constitutional AI alignment is a procurement requirement",
        ],
        "skip_for": [
            'Real-time current events — <a href="/labs/xai.html" style="color:#1da1f2;">xAI Grok</a> has live X integration',
            'Self-hosted or air-gapped — open weights from <a href="/labs/meta-ai.html" style="color:#1877f2;">Meta</a> or <a href="/labs/deepseek.html" style="color:#5b8def;">DeepSeek</a>',
            'Video generation or video-in — <a href="/labs/google-deepmind.html" style="color:#4285f4;">Google Gemini 3.5 Pro</a>',
            'Bottom-of-the-budget batch processing — DeepSeek and Qwen are dramatically cheaper',
            'Image generation where text must render — <a href="/labs/openai.html" style="color:#10a37f;">OpenAI GPT-Image-2</a>',
        ],
    },

    "google-deepmind": {
        "next_lab": "meta-ai",
        "next_lab_name": "Meta AI",
        "status": "Frontier",
        "intro": [
            "DeepMind began as a London research lab in 2010, founded by Demis Hassabis, Shane Legg, and Mustafa Suleyman, and was acquired by Google in 2014. In 2023 it merged with Google Brain to form the unified Google DeepMind, the AI arm of Alphabet. The lab brings 25 years of accumulated research depth: AlphaGo, AlphaFold, AlphaProof, Gemma open models, and now the Gemini frontier family.",
            "The 2026 strategy is leverage the distribution moat. Gemini powers Search AI Overviews, Workspace, Android, the standalone Gemini app, and a growing portfolio of agentic products through Gemini Spark. Pricing is aggressive — <em>Flash undercuts every frontier model on cost</em>. Pro is the only model at <strong>2M token context</strong>. Multimodality (image, audio, video in and out) is native, not bolted on like rivals.",
            "The catch is execution. Google has the research depth, the distribution, the chip supply through TPU, and the multimodal lead. What it has historically lacked is the consumer product chops to make AI feel exciting rather than utilitarian. The Gemini app has been catching up. ChatGPT still owns the cultural conversation. When research labs become product companies, the things that matter change.",
        ],
        "articles": [
            ("/articles/google-antigravity-deleted-hard-drive.html", "AI Safety", "The AI Wiped His Drive. Then It Blamed the System."),
            ("/articles/40-ai-search-kills-google-seo.html", "Business", "Your #1 Google Rank Means Nothing to ChatGPT"),
            ("/articles/61-anthropic-200b-google-compute-deal.html", "Business", "Anthropic's $200B Google Bet: Hoovering Up Every Chip"),
            ("/articles/59-ai-electric-grid-bottleneck.html", "Business", "The AI Wall Is the Electric Grid, Not the Algorithm"),
        ],
        "use_for": [
            "Long-context multimodal work — 2M tokens of video, audio, code, documents in one prompt",
            "Workspace and search-native applications via the native Google ecosystem",
            "Cost-sensitive workloads where Gemini Flash undercuts other frontier models",
            "Spark for autonomous agent and computer-use trajectories",
            "Video-in and audio-in workloads where Gemini's native multimodality wins",
        ],
        "skip_for": [
            'Refusal-aware production agents — <a href="/labs/anthropic.html" style="color:#d4a574;">Anthropic Claude</a> is the gold standard',
            'Self-hosted air-gapped — open weights from <a href="/labs/meta-ai.html" style="color:#1877f2;">Meta</a> or <a href="/labs/deepseek.html" style="color:#5b8def;">DeepSeek</a>',
            'Image generation with text — <a href="/labs/openai.html" style="color:#10a37f;">OpenAI GPT-Image-2</a> wins',
            'European data residency — <a href="/labs/mistral.html" style="color:#ff7000;">Mistral</a>',
            'Hardcore reasoning math at the top — OpenAI GPT-5.4 Think still leads',
        ],
    },

    "meta-ai": {
        "next_lab": "xai",
        "next_lab_name": "xAI",
        "status": "Open Weights",
        "intro": [
            "The lab traces back to FAIR (Facebook AI Research), founded in 2013 under Yann LeCun. After a decade of mostly academic output, Meta pivoted to open-weights AI in 2023 with the original Llama release. Llama 4 in 2026 is the open-weights frontier — weights downloadable, license commercially permissive, available on every cloud, every laptop, every phone with enough RAM.",
            "The unusual strategy: Mark Zuckerberg's bet is that <em>open models commoditise the layer above the chip</em>. If anyone can run a frontier-class model, the value moves to apps, distribution, and hardware — three layers Meta already dominates. The <strong>Reality Labs hardware roadmap</strong> (smart glasses, AR/VR) needs a model running locally; making that model open accelerates the ecosystem Meta wants to capture.",
            "The catch is twofold. First, open weights are easy to weaponise — every release sparks a fresh debate about misuse and a fresh round of regulatory attention. Second, \"open\" doesn't mean open development. Meta picks the training data and the alignment, releases finished weights, but the lab itself is closed. You can run Llama. You can't really see how it was built.",
        ],
        "articles": [
            ("/articles/75-personal-ai-agent-stack-under-50.html", "Agents", "Build Your Personal AI Agent Stack for Under $50 a Month"),
            ("/articles/39-model-routing-cost-collapse.html", "Dev", "The $8 Agent vs. the $400 Agent"),
            ("/articles/44-openclaw-multi-model-unlock.html", "Dev", "Your AI Agent Is Locked to One Model. That's a Liability."),
            ("/articles/64-ai-jobs-80-million-lost-170-million-created.html", "Business", "80 Million Jobs Will Be Lost. 170 Million Will Be Created."),
        ],
        "use_for": [
            "Self-hosting where weights and licensing matter (commercially permissive)",
            "Fine-tuning on your own data without sending it to a vendor",
            "Air-gapped deployments in regulated environments",
            "Edge inference with Llama 4 Scout on a single H100 or quantised consumer hardware",
            "Real-time voice and video apps via Llama 4 Omni",
        ],
        "skip_for": [
            'Out-of-the-box production reliability — <a href="/labs/anthropic.html" style="color:#d4a574;">Anthropic Claude</a>',
            'Frontier reasoning math — <a href="/labs/openai.html" style="color:#10a37f;">OpenAI GPT-5.4 Think</a>',
            'Search-grounded answers with citations — <a href="/labs/perplexity.html" style="color:#1fb8cd;">Perplexity Sonar</a>',
            'Refusal-aware enterprise risk profiles — Anthropic Claude',
            'Image generation with baked-in text — OpenAI GPT-Image-2',
        ],
    },

    "xai": {
        "next_lab": "mistral",
        "next_lab_name": "Mistral AI",
        "status": "Frontier",
        "intro": [
            "Founded in 2023 by Elon Musk after his departure from the OpenAI board, xAI was positioned as the <em>maximally curious</em> alternative to mainstream AI labs — explicitly rejecting what Musk characterised as overcautious tuning at OpenAI and Anthropic. The implicit edge is real-time access to X (formerly Twitter), the world's largest live conversation feed, which xAI uses as a training and grounding signal.",
            "Four major Grok versions have shipped in under two years, an aggressive cadence even for AI labs. Grok 4 is the flagship reasoning model. Grok Build 0.1 is the agentic coding wager going head to head with Claude Code and Cursor — aggressive pricing, fast iteration, the bet that quality follows distribution. Grok Vision handles document and chart understanding for OCR-heavy workflows.",
            "The catch is the brand and the methodology. xAI's deliberate posture of \"fewer guardrails\" is the explicit product pitch, which means the models will sometimes say things competitors won't. That's catnip for the curious. It's a procurement problem for enterprises. The lab's quality has been steadily climbing — the question of whether Musk's edgier brand can win regulated industries remains open.",
        ],
        "articles": [
            ("/articles/78-ai-art-backlash-monet-training-data.html", "Honest Take", "The Art the AI Never Asked Permission to Learn From"),
            ("/articles/29-ai-backlash-america-hates-ai.html", "Society", "America Hates AI and Can't Stop Using It"),
            ("/articles/56-meter-chart-ai-progress-lie.html", "Agents", "The Meter Chart Is Lying to You About AI Progress"),
            ("/articles/38-agentic-development-loop.html", "Agents", "The Agentic Development Loop"),
        ],
        "use_for": [
            "Real-time current events queries via live X integration",
            "Less hedged political and controversial topic analysis",
            "Agentic coding when Sonnet is too expensive — Grok Build undercuts on price",
            "Bulk OCR and document understanding where Grok Vision is good enough at lower cost",
            "Workloads that benefit from a model trained on live conversation",
        ],
        "skip_for": [
            'Production reliability and refusal-aware safety — <a href="/labs/anthropic.html" style="color:#d4a574;">Anthropic Claude</a>',
            'Long-context document analysis — Anthropic Claude at 500K',
            'European data residency — <a href="/labs/mistral.html" style="color:#ff7000;">Mistral</a>',
            'Regulated-industry enterprise procurement — OpenAI, Anthropic, or Google',
            'Top-tier reasoning math — OpenAI GPT-5.4 Think',
        ],
    },

    "mistral": {
        "next_lab": "qwen",
        "next_lab_name": "Qwen (Alibaba)",
        "status": "Frontier",
        "intro": [
            "Paris-based, founded in 2023 by ex-Meta and DeepMind researchers, Mistral became Europe's answer to the question \"where is our frontier AI lab?\". The founders' background gives the lab technical credibility from day one — Mistral Large 3 descends from research lineage at Meta's FAIR. The 2024-2025 raises put it at the heart of <strong>EU AI sovereignty</strong> conversations.",
            "The strategy is a hybrid: open weights for the smaller and specialised models (Mixtral, Codestral), commercial API for the frontier (Mistral Large). <em>Strong on European languages</em> where US labs have weaker coverage. Structured outputs that production systems can rely on. Function calling that doesn't break under load. The bet: European customers pay a premium for sovereign AI.",
            "The catch is scale. Mistral does not have OpenAI's revenue, Anthropic's $200B compute deal, or Meta's distribution. It does have French government support and a growing roster of European enterprise customers who care about where their tokens are processed. Whether that's enough to keep pace with frontier US labs that ship faster and price more aggressively is the strategic question hanging over the next 18 months.",
        ],
        "articles": [
            ("/articles/76-ai-skills-gap-how-to-land-right-side.html", "Business", "The AI Skills Gap Is Real. Here's How to Land on the Right Side of It."),
            ("/articles/73-ai-tool-evaluation-5-question-framework.html", "Tools", "Before You Commit to Any AI Tool, Ask These 5 Questions"),
            ("/articles/74-ai-small-business-honest-roi-guide.html", "Business", "AI for Small Business: The Honest ROI Guide"),
            ("/articles/53-hyperagent-built-aether-intel.html", "Tools", "How I Built a 52-Article AI News Site Using Only Hyperagent"),
        ],
        "use_for": [
            "European data residency requirements (EU sovereignty)",
            "French, German, Spanish, Italian language workloads with native coverage",
            "Self-hosting via Mixtral or Codestral open weights",
            "IDE autocomplete with Codestral (low latency, code-tuned)",
            "Function calling and structured JSON output at production scale",
        ],
        "skip_for": [
            'Top-tier English reasoning — <a href="/labs/openai.html" style="color:#10a37f;">GPT-5.4 Think</a> or <a href="/labs/anthropic.html" style="color:#d4a574;">Claude Opus</a>',
            'Long-context document analysis — Claude or Gemini',
            'Multimodal video — <a href="/labs/google-deepmind.html" style="color:#4285f4;">Gemini Pro</a>',
            'Image generation — OpenAI GPT-Image-2',
            'Bottom-of-the-budget cost optimisation — <a href="/labs/deepseek.html" style="color:#5b8def;">DeepSeek</a>',
        ],
    },

    "qwen": {
        "next_lab": "deepseek",
        "next_lab_name": "DeepSeek",
        "status": "Open Weights",
        "intro": [
            "Alibaba's frontier AI lab, based in Hangzhou, became the most prolific releaser of open-weights AI models in 2025-2026. Where Western open-source labs ship one or two major releases per year, Qwen ships a new variant <em>roughly every six weeks</em> — from 0.5B parameter edge models up to 200B+ flagships. Qwen3 was the step-change. Qwen3.7 caught up to Western benchmarks on most categories.",
            "The strategy is volume. By saturating the open-weights leaderboard at every parameter scale, Qwen makes itself the default open option in two markets: the Chinese domestic market (where Western API access is restricted) and the global self-hosting community looking for open frontier-ish quality. The Qwen3.7 Omni release brought <strong>native multimodal</strong> — audio in and out, video understanding — to the open ecosystem.",
            "The catch is the obvious one: Western enterprise procurement is increasingly cautious about deploying Chinese-origin AI in regulated industries. Concerns range from training data provenance to export controls to data residency. The lab's technical work is undeniable. The geopolitical question of which markets it can sell into is the constraint.",
        ],
        "articles": [
            ("/articles/39-model-routing-cost-collapse.html", "Dev", "The $8 Agent vs. the $400 Agent"),
            ("/articles/22-ai-agent-true-cost-guide.html", "Business", "The Real Cost of Running AI Agents in 2026"),
            ("/articles/44-openclaw-multi-model-unlock.html", "Dev", "Your AI Agent Is Locked to One Model. That's a Liability."),
            ("/articles/64-ai-jobs-80-million-lost-170-million-created.html", "Business", "80 Million Jobs Lost. 170 Million Created."),
        ],
        "use_for": [
            "Chinese + English bilingual workloads where Western labs have weaker coverage",
            "Open-weights deployment with no Western dependency",
            "Cost-sensitive workloads needing frontier-ish quality",
            "Multimodal open-weights — Qwen Omni is currently the only real open option",
            "Fine-tuning for domain-specific tasks where you control the training data",
        ],
        "skip_for": [
            'Frontier closed-source quality on English benchmarks — <a href="/labs/anthropic.html" style="color:#d4a574;">Claude</a> or <a href="/labs/openai.html" style="color:#10a37f;">GPT-5.x</a>',
            'European data residency — <a href="/labs/mistral.html" style="color:#ff7000;">Mistral</a>',
            'Western enterprise procurement in regulated industries (geopolitical caution)',
            'Production reliability — Anthropic Claude is the gold standard',
            'Voice/audio-native applications — Google Gemini Omni',
        ],
    },

    "deepseek": {
        "next_lab": "cohere",
        "next_lab_name": "Cohere",
        "status": "Open Weights",
        "intro": [
            "Hangzhou-based, founded in 2023, DeepSeek shocked Silicon Valley in early 2025 by training a frontier-class reasoning model for what was reported as a tiny fraction of OpenAI's cost. The technical innovation was the mixture-of-experts architecture done right: 671B total parameters but only <em>37B active per token</em>, with engineering tricks that compressed training compute dramatically.",
            "The 2026 strategy is to ride that efficiency. DeepSeek R2 is the open-weights reasoning model that matches GPT-5.4 Think on math and competitive programming at roughly <strong>1/30th the price</strong>. V3.5 is the general-purpose flagship at near-Haiku pricing with near-Sonnet quality. Both are downloadable, both are permissively licensed, both have already been forked dozens of times by the open-source community.",
            "The catch mirrors Qwen's. Western enterprise customers face the same procurement caution about Chinese-origin AI. DeepSeek's response has been to ship faster and cheaper than rivals can ignore — for the open-source community, for the cost-sensitive market, and for everyone who watched the early-2025 cost story and concluded that compute spending isn't quite the moat the US labs claimed.",
        ],
        "articles": [
            ("/articles/39-model-routing-cost-collapse.html", "Dev", "The $8 Agent vs. the $400 Agent"),
            ("/articles/22-ai-agent-true-cost-guide.html", "Business", "The Real Cost of Running AI Agents in 2026"),
            ("/articles/47-ai-bubble-missing-demand.html", "Business", "Ed Zitron Went Looking for AI's Customers. He Found Almost None."),
            ("/articles/32-ai-procurement-hack-lily-mckinsey.html", "Dev", "The $20 Hack That Broke Every AI Procurement Checklist"),
        ],
        "use_for": [
            "Cost-sensitive frontier quality (1/30th the price of GPT-5.x for comparable reasoning)",
            "Open-weights reasoning at production scale via R2",
            "Self-hosted fine-tuning base — permissive license, well-documented",
            "High-volume batch processing where per-token cost is the dominant constraint",
            "IDE coding agents at near-zero per-token cost via DeepSeek Coder V3",
        ],
        "skip_for": [
            'Western enterprise procurement in regulated industries (geopolitical caution)',
            'Production agentic workflows requiring stability — <a href="/labs/anthropic.html" style="color:#d4a574;">Claude Sonnet</a>',
            'Multimodal vision and video — <a href="/labs/google-deepmind.html" style="color:#4285f4;">Gemini</a> or <a href="/labs/openai.html" style="color:#10a37f;">GPT-5.5</a>',
            'European data residency — <a href="/labs/mistral.html" style="color:#ff7000;">Mistral</a>',
            'Refusal-aware safety-conscious workloads — Anthropic',
        ],
    },

    "cohere": {
        "next_lab": "perplexity",
        "next_lab_name": "Perplexity",
        "status": "Enterprise",
        "intro": [
            "Founded in 2019 by Aidan Gomez (one of the original Transformer paper authors), Cohere bet on enterprise from day one rather than consumer chat. While OpenAI was building ChatGPT, Cohere was building Command — a family of models tuned for retrieval-augmented generation, structured outputs, and the kind of mundane production work that doesn't generate consumer headlines but does generate <em>enterprise revenue</em>.",
            "The 2026 strategy looks more right than it did in 2023. Every enterprise customer eventually wants the same thing: AI that <strong>cites its sources</strong>, handles multilingual content, deploys on-premise if procurement demands it, and doesn't hallucinate when the answer is in a provided document. Command A is the flagship. Command R+ is the workhorse. Embed v4 is best-in-class for multimodal vector search.",
            "The catch is the brand. Cohere is quietly profitable and growing, but it lacks the consumer recognition that pulls developers in through curiosity. Customers tend to find Cohere through a specific enterprise need rather than general awareness. That's a real disadvantage when developer mindshare drives most AI tooling decisions. The technical work is excellent. Whether enterprise-first wins the war or just one niche is the open question.",
        ],
        "articles": [
            ("/articles/69-ai-efficiency-lie-mit-study.html", "Business", "The Efficiency Lie: MIT Studied 300 Companies Using AI"),
            ("/articles/32-ai-procurement-hack-lily-mckinsey.html", "Dev", "The $20 Hack That Broke Every AI Procurement Checklist"),
            ("/articles/74-ai-small-business-honest-roi-guide.html", "Business", "AI for Small Business: The Honest ROI Guide"),
            ("/articles/35-ai-labs-mckinsey-mode.html", "Business", "The Model Was Never the Hard Part"),
        ],
        "use_for": [
            "Enterprise RAG workflows where citation-grounding matters",
            "On-premise or private-cloud deployments with strict data residency",
            "Multilingual support across major business languages",
            "Tool-use with structured outputs at half the cost of frontier rivals",
            "Embedding-based vector search — Embed v4 is best-in-class for multimodal",
        ],
        "skip_for": [
            'Consumer chat ecosystem — <a href="/labs/openai.html" style="color:#10a37f;">OpenAI</a>, <a href="/labs/anthropic.html" style="color:#d4a574;">Anthropic</a>, <a href="/labs/google-deepmind.html" style="color:#4285f4;">Google</a>',
            'Frontier reasoning — GPT-5.4 Think or Claude Opus',
            'Multimodal video — Gemini Pro',
            'Self-hosting open weights — <a href="/labs/meta-ai.html" style="color:#1877f2;">Meta</a> / <a href="/labs/qwen.html" style="color:#a370f7;">Qwen</a> / <a href="/labs/deepseek.html" style="color:#5b8def;">DeepSeek</a>',
            'Image generation — OpenAI GPT-Image-2',
        ],
    },

    "perplexity": {
        "next_lab": "perceptron",
        "next_lab_name": "Perceptron",
        "status": "Specialty",
        "intro": [
            "Founded in 2022, Perplexity reframed AI as a <em>search interface</em> rather than a conversation — every claim cited back to a source, every response a structured research synthesis rather than a chat reply. The Sonar model family is fine-tuned on top of open-weights bases (Llama, Mistral) specifically for grounded, citation-aware answering. The bet is straightforward: the future of search is AI that <strong>shows its work</strong>.",
            "2026 strategy: keep narrowing on search rather than chasing the broader chat market. Sonar Pro for everyday grounded queries. Sonar Reasoning for multi-hop research questions that need both web search and chain-of-thought together. The product surface emphasises citations more than personality — every answer is a footnoted essay rather than a friendly reply.",
            "The catch is that Perplexity does not own its own frontier model. It tunes on top of Llama and Mistral bases. That means its quality ceiling tracks the open-weights frontier, and its margins compress when those bases get cheaper or more commoditised. The reframing of AI as search remains compelling. Whether the company can build a moat on top of other people's models is the open strategic question.",
        ],
        "articles": [
            ("/articles/40-ai-search-kills-google-seo.html", "Business", "Your #1 Google Rank Means Nothing to ChatGPT"),
            ("/articles/ai-real-estate-photo-deception.html", "Business", "The House in the Photo Doesn't Exist"),
            ("/articles/30-ai-sycophancy-mental-health-crisis.html", "Society", "AI Was Built to Make You Feel Good. That's Turning Into a Mental Health Crisis."),
            ("/articles/56-meter-chart-ai-progress-lie.html", "Agents", "The Meter Chart Is Lying to You About AI Progress"),
        ],
        "use_for": [
            "Search-native applications that need source citations",
            "Research synthesis where receipts matter — every answer footnoted",
            "Multi-hop questions requiring web context and chain-of-thought together",
            "Replacing traditional search interfaces with grounded AI",
            "Investigative workflows where you need to verify each claim",
        ],
        "skip_for": [
            'Self-hosted or air-gapped — Sonar runs as a service only',
            'Frontier raw reasoning — Sonar Reasoning is good but not best',
            'Multimodal native — <a href="/labs/google-deepmind.html" style="color:#4285f4;">Gemini Pro</a> or <a href="/labs/openai.html" style="color:#10a37f;">GPT-5.5</a>',
            'Image generation — OpenAI GPT-Image-2',
            'Conversational workflows that don\'t need external web context',
        ],
    },

    "perceptron": {
        "next_lab": "nous-research",
        "next_lab_name": "Nous Research",
        "status": "Specialty",
        "intro": [
            "A newer entrant founded in 2025, Perceptron focuses on <em>spatial intelligence</em> — AI that understands the physical world rather than just text. Perceptron Mk1 (Mark One) is the flagship vision-reasoning model, trained on multimodal data with heavy weighting toward 3D scene understanding, robotics simulation trajectories, and embodied environments where the model has to reason about object permanence, depth, and physics.",
            "The pitch is <strong>AI for the layer below chatbots</strong>. Where general-purpose multimodal models like Gemini and GPT-5.5 do okay on visual tasks, Mk1 is purpose-built for spatial relationships — depth estimation from a single image, converting visual scenes into structured plans, video understanding with action-prediction baked in. The natural customer is robotics, AR/VR, and any system that needs to map the physical world rather than describe it.",
            "The catch is that Perceptron is early. The dataset, the benchmarks, the product surface, the customer base — all are at early-stage scale. Whether spatial intelligence ends up being its own category or just a capability that frontier multimodal models absorb is the existential question. For now the technical lead in spatial-specific tasks is real, and the use cases that require it are growing.",
        ],
        "articles": [
            ("/articles/50-physical-ai-sensor-infrastructure-gap.html", "Agents", "The Sensor Gap Killing Physical AI"),
            ("/articles/ai-real-estate-photo-deception.html", "Business", "The House in the Photo Doesn't Exist"),
            ("/articles/38-agentic-development-loop.html", "Agents", "The Agentic Development Loop"),
            ("/articles/63-broken-agents-harness-not-model.html", "Agents", "Broken Agents? It's Not the Model. It's the Harness."),
        ],
        "use_for": [
            "Spatial reasoning and 3D scene understanding",
            "Robotics planning and embodied AI applications",
            "Depth estimation from single images without dedicated sensors",
            "Converting visual scenes into structured plans for robotic execution",
            "Video understanding with spatial focus rather than narrative focus",
        ],
        "skip_for": [
            'Conversational AI — <a href="/labs/openai.html" style="color:#10a37f;">OpenAI</a> or <a href="/labs/anthropic.html" style="color:#d4a574;">Anthropic</a>',
            'Long-context text analysis — Anthropic Claude',
            'Code generation — <a href="/labs/deepseek.html" style="color:#5b8def;">DeepSeek Coder</a> or Claude',
            'Image generation — OpenAI GPT-Image-2',
            'General multimodal chat — <a href="/labs/google-deepmind.html" style="color:#4285f4;">Gemini Pro</a>',
        ],
    },

    "nous-research": {
        "next_lab": "openai",
        "next_lab_name": "OpenAI",
        "status": "Open Weights",
        "intro": [
            "Founded in 2023 as an <em>independent research collective</em> rather than a venture-backed lab, Nous Research occupies a unique position in the AI landscape. The structure is intentionally small, the team is distributed, the output is craftsmanship-focused — meticulously fine-tuned models released as open weights, designed for the agentic-builder community that values control over scale.",
            "The 2026 flagship is Hermes 4 — an open-weights agent model with <strong>native persistent memory</strong>, designed to compound intelligence as it accumulates skills and conversations. Hermes Vision 2 added multimodal screen-reading for vision agents. The cost story is the differentiator: both models are free to download, free to run on any hardware that can host them, with the indie-builder community running them on $9/month Hostinger VPS instances.",
            "The catch is exactly the strength. Nous is not a venture-backed frontier lab and isn't trying to be. There is no Hermes 5 racing to match GPT-5.5 on every benchmark. The models won't be the absolute best at any single category. What they will be is craftable, ownable, and ecosystem-friendly — characteristics that matter to the indie builder economy but not necessarily to enterprise procurement.",
        ],
        "articles": [
            ("/articles/01-hermes-agent-complete-guide.html", "Agents", "The Complete Hermes Agent Guide: Setup, Skills & Income"),
            ("/articles/43-hermes-vs-openclaw-agent-war.html", "Agents", "Hermes Might Have Just Killed OpenClaw"),
            ("/articles/37-hermes-infrastructure-24-7.html", "Agents", "Hermes as Infrastructure, Not Chatbot"),
            ("/articles/20-hermes-agent-vs-chatgpt.html", "Agents", "Hermes Agent vs ChatGPT: Why Persistent Memory Changes Everything"),
        ],
        "use_for": [
            "Self-hosted agentic workflows on a budget ($5-100/month VPS)",
            "Indie builder ecosystem where you need persistent memory in your agent",
            "Custom skill stacks tuned to your specific workflow",
            "Open-weights model that compounds intelligence as you use it",
            "Telegram, Discord, Slack agent deployments at near-zero ongoing cost",
        ],
        "skip_for": [
            'Enterprise procurement — go with <a href="/labs/anthropic.html" style="color:#d4a574;">Anthropic</a> or <a href="/labs/openai.html" style="color:#10a37f;">OpenAI</a>',
            'Frontier reasoning quality — Claude Opus or GPT-5.4 Think',
            'Multimodal video — <a href="/labs/google-deepmind.html" style="color:#4285f4;">Gemini Pro</a>',
            'Top-tier image generation — OpenAI GPT-Image-2',
            'Mission-critical production reliability — Claude Sonnet is the gold standard',
        ],
    },
}


# ── Helper: format model card HTML ──────────────────────────────────────────
def render_model_card(model, lab_accent):
    name = html_lib.escape(model["name"])
    tier = html_lib.escape(model.get("tier", "model").title())
    released = html_lib.escape(model.get("released", "-"))
    context = html_lib.escape(model.get("context", "-"))
    in_per_m = model.get("input_per_m")
    out_per_m = model.get("output_per_m")
    in_str = f"${in_per_m:g} / 1M" if in_per_m and in_per_m > 0 else "Free"
    out_str = f"${out_per_m:g} / 1M" if out_per_m and out_per_m > 0 else "Free"
    if in_per_m is None or in_per_m == 0:
        in_str = "Free"
    if out_per_m is None or out_per_m == 0:
        out_str = "Free"

    blurb = html_lib.escape(model.get("blurb", ""))
    modalities = model.get("modalities", [])
    best_for = model.get("best_for", [])

    modal_pills = "".join(f"<span>{html_lib.escape(m.title())}</span>" for m in modalities)
    best_items = "".join(f"<li>{html_lib.escape(b)}</li>" for b in best_for)

    return f'''
        <article class="lab-model-card">
          <div class="lab-model-card-head">
            <h3 class="lab-model-name">{name}</h3>
            <span class="lab-model-tier">{tier}</span>
          </div>
          <p class="lab-model-blurb">{blurb}</p>
          <div class="lab-model-meta">
            <div class="lab-model-meta-item">
              <span class="lab-model-meta-label">Context</span>
              <span class="lab-model-meta-value">{context}</span>
            </div>
            <div class="lab-model-meta-item">
              <span class="lab-model-meta-label">Released</span>
              <span class="lab-model-meta-value">{released}</span>
            </div>
            <div class="lab-model-meta-item">
              <span class="lab-model-meta-label">Input</span>
              <span class="lab-model-meta-value">{in_str}</span>
            </div>
            <div class="lab-model-meta-item">
              <span class="lab-model-meta-label">Output</span>
              <span class="lab-model-meta-value">{out_str}</span>
            </div>
          </div>
          <div class="lab-model-modal">{modal_pills}</div>
          <div class="lab-model-best">
            <p class="lab-model-best-label">Best for</p>
            <ul>{best_items}</ul>
          </div>
        </article>'''


def render_article_card(path, cat, title, lab_accent):
    # Article hero image: try {slug}-hero.webp first (the more common naming
    # convention — ~66 of 177 articles use it). Fall back to plain {slug}.webp
    # (used by ~12 articles). Final fallback is a brand-accent gradient.
    slug = path.split('/')[-1].replace('.html', '')
    img_url = f"/images/articles/{slug}-hero.webp"
    onerror = (
        f"this.onerror=null;"
        f"this.src='/images/articles/{slug}.webp';"
        f"this.onerror=function(){{this.style.background='linear-gradient(135deg,{lab_accent}22,#07070f66)';this.removeAttribute(\"src\");}}"
    )
    return f'''
        <a href="{path}" class="lab-article-card">
          <img src="{img_url}" alt="" class="lab-article-card-img" loading="lazy" onerror="{onerror}">
          <div class="lab-article-card-body">
            <span class="lab-article-card-cat">{html_lib.escape(cat)}</span>
            <h3 class="lab-article-card-title">{html_lib.escape(title)}</h3>
          </div>
        </a>'''


# ── Template ────────────────────────────────────────────────────────────────
def render_lab_page(lab, content):
    slug = lab["id"]
    name = lab["name"]
    tagline = lab["tagline"]
    accent = lab["color_accent"]
    accent_rgb = ",".join(str(int(accent[i:i+2], 16)) for i in (1, 3, 5))  # "10,163,127"
    country = lab["country"]
    founded = lab["founded"]
    hq = lab["hq"]
    n_models = len(lab["models"])
    status = content["status"]
    next_lab = content["next_lab"]
    next_lab_name = content["next_lab_name"]

    intro_html = "".join(f"<p>{p}</p>\n        " for p in content["intro"])
    articles_html = "".join(render_article_card(p, c, t, accent) for p, c, t in content["articles"])
    models_html = "".join(render_model_card(m, accent) for m in lab["models"])
    use_html = "".join(f"<li>{u}</li>" for u in content["use_for"])
    skip_html = "".join(f"<li>{s}</li>" for s in content["skip_for"])

    # OG title and description
    og_title = f"{name} — {tagline}"
    desc = f"{name}: {tagline}. " + " ".join([m["name"] for m in lab["models"]]) + ". What each model is for, what they cost, what to use this lab for vs. when to look elsewhere."

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{name} — {tagline} | Aether Intel Labs</title>
  <meta name="description" content="{html_lib.escape(desc)}">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="https://ai.quantummerlin.com/labs/{slug}.html">

  <meta property="og:title" content="{html_lib.escape(og_title)}">
  <meta property="og:description" content="{html_lib.escape(desc)}">
  <meta property="og:type" content="article">
  <meta property="og:url" content="https://ai.quantummerlin.com/labs/{slug}.html">
  <meta property="og:image" content="https://ai.quantummerlin.com/images/labs/{slug}-hero.webp">
  <meta property="og:site_name" content="Aether Intel">

  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{html_lib.escape(og_title)}">
  <meta name="twitter:description" content="{html_lib.escape(desc)}">
  <meta name="twitter:image" content="https://ai.quantummerlin.com/images/labs/{slug}-hero.webp">

  <script async src="https://www.googletagmanager.com/gtag/js?id=G-VW4LGE7L1T"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-VW4LGE7L1T');</script>
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3480541530392777" crossorigin="anonymous"></script>

  <link rel="stylesheet" href="/css/style.css">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Space+Grotesk:wght@400;500;700&family=Sora:wght@400;600;700;800&display=swap" onload="this.onload=null;this.rel='stylesheet'">
  <noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Space+Grotesk:wght@400;500;700&family=Sora:wght@400;600;700;800&display=swap"></noscript>
</head>
<body style="--lab-accent:{accent};">

<main>

  <!-- Hero -->
  <div class="alp-hero">
    <img src="/images/labs/{slug}-hero.webp" alt="{html_lib.escape(name)}" class="alp-hero-img" loading="eager" fetchpriority="high">
    <div class="alp-hero-overlay"></div>
    <div class="alp-hero-content">
      <nav class="alp-breadcrumb" aria-label="breadcrumb">
        <a href="/index.html">Home</a>
        <span>&rsaquo;</span>
        <a href="/labs.html">Labs</a>
        <span>&rsaquo;</span>
        <span>{html_lib.escape(name)}</span>
      </nav>
      <span class="badge" style="background:rgba({accent_rgb},0.14);color:{accent};border:1px solid rgba({accent_rgb},0.4);padding:5px 11px;border-radius:5px;font-family:var(--font-display);font-size:0.6rem;font-weight:700;letter-spacing:0.13em;text-transform:uppercase;display:inline-flex;align-items:center;gap:6px;margin-bottom:12px;">{status} Lab · {html_lib.escape(country)}</span>
      <h1 class="alp-hero-title">{html_lib.escape(name)}</h1>
      <p class="alp-hero-desc">{html_lib.escape(tagline)}.</p>
      <div class="alp-hero-actions">
        <a href="/labs.html" class="alp-btn-primary">
          <svg viewBox="0 0 24 24"><polyline points="15 18 9 12 15 6"/></svg>
          All Labs
        </a>
        <a href="#models" class="alp-btn-ghost">
          <svg viewBox="0 0 24 24"><polyline points="6 9 12 15 18 9"/></svg>
          Jump to models
        </a>
      </div>
    </div>
  </div>

  <!-- Stats band -->
  <div class="alp-stats-band">
    <div class="alp-stat">
      <span class="alp-stat-label">Founded</span>
      <span class="alp-stat-value">{founded}</span>
    </div>
    <div class="alp-stat">
      <span class="alp-stat-label">HQ</span>
      <span class="alp-stat-value">{html_lib.escape(hq)}</span>
    </div>
    <div class="alp-stat">
      <span class="alp-stat-label">Country</span>
      <span class="alp-stat-value">{html_lib.escape(country)}</span>
    </div>
    <div class="alp-stat">
      <span class="alp-stat-label">Models tracked</span>
      <span class="alp-stat-value">{n_models}</span>
    </div>
    <div class="alp-stat">
      <span class="alp-stat-label">Status</span>
      <span class="alp-stat-value" style="color:{accent};">{status}</span>
    </div>
  </div>

  <div class="alp-body">

    <!-- The Lab editorial intro -->
    <section class="alp-section">
      <p class="alp-section-title">The Lab</p>
      <div class="lab-intro">
        {intro_html.strip()}
      </div>
    </section>

    <!-- Recent coverage -->
    <section class="alp-section">
      <p class="alp-section-title">Recent Coverage</p>
      <div class="lab-articles-strip">{articles_html}
      </div>
    </section>

    <!-- Models -->
    <section class="alp-section" id="models">
      <p class="alp-section-title">Models</p>
      <div class="lab-models-grid">{models_html}
      </div>
    </section>

    <!-- When to pick / when to skip -->
    <section class="alp-section">
      <p class="alp-section-title">When to Pick {html_lib.escape(name)} · When to Pick Someone Else</p>
      <div class="lab-usage-grid">

        <div class="lab-usage-card use">
          <h4 class="lab-usage-card-title">✓ Pick {html_lib.escape(name)} when</h4>
          <ul>{use_html}</ul>
        </div>

        <div class="lab-usage-card skip">
          <h4 class="lab-usage-card-title">✕ Look elsewhere for</h4>
          <ul>{skip_html}</ul>
        </div>

      </div>
    </section>

    <!-- Bottom CTA -->
    <div class="alp-cta">
      <h2>Explore the other 11 labs</h2>
      <p>Each lab in the atlas comes with its own positioning, model line, and use cases. The point of organising the AI landscape by lab is that the answer to "which model should I use" almost always starts with "which lab is closest to what I'm trying to do."</p>
      <div class="alp-cta-actions">
        <a href="/labs.html" class="alp-btn-primary">
          <svg viewBox="0 0 24 24"><polyline points="15 18 9 12 15 6"/></svg>
          Back to all labs
        </a>
        <a href="/labs/{next_lab}.html" class="alp-btn-ghost">
          Next: {html_lib.escape(next_lab_name)} →
        </a>
      </div>
    </div>

  </div>

</main>

<script src="/js/main.js"></script>
</body>
</html>
'''


# ── Main ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    labs_data = json.load(open("labs.json"))
    lab_by_id = {l["id"]: l for l in labs_data["labs"]}

    os.makedirs("labs-out", exist_ok=True)
    for slug, content in LAB_CONTENT.items():
        lab = lab_by_id[slug]
        html = render_lab_page(lab, content)
        out_path = f"labs-out/{slug}.html"
        with open(out_path, "w") as f:
            f.write(html)
        print(f"  {slug:<22} {len(html):>7} bytes")
    print(f"\nWrote {len(LAB_CONTENT)} lab pages to labs-out/")

