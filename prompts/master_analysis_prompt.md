# Master Analysis Prompt — Audience Intelligence Report

Use this prompt with a large-context AI model (e.g., Claude Sonnet 4, GPT-4 Turbo, Gemini Pro) after extracting comments from a social media post.

---

## Instructions

Paste the raw comment data (CSV or JSON) after this prompt. Replace the placeholder fields in the CONTEXT section with the actual values.

---

## Prompt

```
CONTEXT:
- Platform: [TikTok / Instagram / Facebook / Reddit]
- Post URL: [paste URL]
- Client / Creator: [name or handle]
- Total comments provided: [number]

TASK:
You are a professional audience intelligence analyst. Analyse the following social media comments and produce a comprehensive Audience Intelligence Report. Follow the structure below exactly.

Before analysing, clean the data:
- Remove spam, bot comments, and single-emoji-only comments
- Merge duplicate or near-duplicate comments
- Note the number removed and the final clean count

═══════════════════════════════════════
AUDIENCE INTELLIGENCE REPORT STRUCTURE
═══════════════════════════════════════

1. OVERVIEW
   - Platform, post URL, total comments (raw and cleaned)
   - One-paragraph executive summary of what the audience is saying

2. SENTIMENT ANALYSIS
   - Breakdown: Positive / Negative / Neutral / Curious percentages
   - Dominant emotional tones (excitement, confusion, anger, curiosity, etc.)
   - Notable sentiment shifts if comment timestamps are available

3. KEY THEMES & CLUSTERS
   - Group similar comments into 5–10 clusters
   - Name each cluster, provide the count, and list 2–3 representative comments
   - Rank clusters by frequency

4. AUDIENCE QUESTIONS
   - List the most frequently asked questions (with count)
   - Group similar questions together
   - Flag unanswered questions that represent content opportunities

5. AUDIENCE FRUSTRATIONS
   - Pain points, complaints, and confusion expressed in comments
   - Common objections or negative reactions
   - Rank by frequency and emotional intensity

6. AUDIENCE DESIRES & REQUESTS
   - What the audience explicitly asks for (tutorials, products, follow-ups, etc.)
   - Implicit desires inferred from comment patterns
   - "I wish..." and "Can you..." style requests

7. VIRAL CONTENT TRIGGERS
   - What elements of the content drove the most engagement?
   - Curiosity hooks, debate starters, identity triggers, controversy
   - Emotional drivers: fear, aspiration, relatability, humor, shock

8. CONTENT OPPORTUNITIES
   - 5–10 specific content ideas derived from comment patterns
   - For each: title/hook suggestion, format recommendation, why it would work
   - Prioritised by predicted engagement

9. ENGAGEMENT OPPORTUNITIES
   - Specific comments the creator should respond to and why
   - Suggested reply strategies for different comment types
   - Community-building tactics based on audience behaviour

10. LEAD & SALES OPPORTUNITIES
    - Comments signalling buying intent ("where can I buy", "how much", "link?")
    - Comments requesting services or consultations
    - Suggested response templates to convert leads
    - Lead quality rating: Hot / Warm / Cold with counts

11. FUTURE PRODUCT OPPORTUNITIES
    - Unmet needs expressed by the audience
    - "I wish there was..." or "Does this exist?" patterns
    - 3–5 specific product/service ideas with market validation from comments

12. AUDIENCE PROFILE
    - Inferred demographics from language, slang, interests, references
    - Psychographic traits (values, lifestyle indicators)
    - Experience level with the topic (beginner / intermediate / expert mix)
    - Geographic indicators if detectable from language or references

13. TOP 10 COMMENTS TO REPLY TO
    - Select 10 comments with the highest strategic value
    - For each: the comment text, why it matters, and a suggested reply
    - Prioritise by: conversion potential, engagement potential, community building

14. STRATEGIC RECOMMENDATIONS
    - 3–5 actionable next steps for the creator/brand
    - Content strategy adjustments based on audience feedback
    - Community management recommendations
    - Monetisation opportunities identified

15. VIRAL PROBABILITY SCORE
    - Score: 1–10 with reasoning
    - Key drivers: curiosity factor, debate potential, emotional resonance, shareability
    - Comparison to typical engagement patterns for this platform
    - One-sentence prediction for similar future content

FORMAT RULES:
- Use clear headers and bullet points
- Include specific comment quotes as evidence (use "[paraphrased]" if needed to shorten)
- All counts should be approximate where exact matching is difficult
- Use tables where they improve readability
- Keep the tone professional but accessible
- Total report length: 2,000–4,000 words depending on comment volume
```

---

## Usage Notes

- **Time per report:** 2–5 minutes AI generation + 5–10 minutes human review/formatting
- **Best models:** Claude Sonnet 4 or Opus (200K context), GPT-4 Turbo (128K), Gemini 1.5 Pro (1M)
- **Minimum useful comment count:** ~100 comments for meaningful patterns
- **Sweet spot:** 500–3,000 comments gives the richest insights
- **Multi-language:** Works well with mixed-language comments — the AI will analyse in-context and report in English
- **Tip:** For posts with 5,000+ comments, consider splitting into batches and merging the analysis
