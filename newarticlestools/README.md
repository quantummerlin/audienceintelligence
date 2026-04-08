# MindBloom — Complete Article Collection

A collection of 210 long-form editorial articles across 30 topic categories, written in a human, conversational style for the MindBloom web platform. Each article is a standalone HTML file that shares a single CSS stylesheet.

---

## Project Structure

```
mindbloom/
├── index.html              # Site homepage
├── shared.css              # Global stylesheet (all articles reference this)
├── sitemap.xml             # XML sitemap for all 212 URLs
├── README.md               # This file
└── articles/
    ├── index.html          # Article hub — browse all 30 categories
    ├── dating-relationships/       (articles 01–12)
    ├── finance-economic-anxiety/   (articles 13–24)
    ├── housing-urban-life/         (articles 25–32)
    ├── workplace-corporate/        (articles 33–40)
    ├── mental-health-loneliness/   (articles 41–48)
    ├── health-wellness/            (articles 49–56)
    ├── future-of-work/             (articles 57–63)
    ├── gig-economy/                (articles 64–69)
    ├── hidden-costs-tech/          (articles 70–75)
    ├── technology-ai/              (articles 76–81)
    ├── future-of-ai/               (articles 82–87)
    ├── education-parenting/        (articles 88–93)
    ├── environment-climate/        (articles 94–99)
    ├── consumer-product/           (articles 100–105)
    ├── addiction-recovery/         (articles 106–111)
    ├── community-social/           (articles 112–117)
    ├── media-journalism/           (articles 118–123)
    ├── psychology-betrayal/        (articles 124–129)
    ├── society-politics/           (articles 130–135)
    ├── parenting-paradoxes/        (articles 136–141)
    ├── memory-nostalgia/           (articles 142–147)
    ├── ethics-ai-art/              (articles 148–154)
    ├── neurodivergent/             (articles 155–161)
    ├── law-governance/             (articles 162–168)
    ├── corporate-accountability/   (articles 169–175)
    ├── creator-economy/            (articles 176–182)
    ├── immigrant-experience/       (articles 183–189)
    ├── ethics-philosophy/          (articles 190–196)
    ├── meta-narratives/            (articles 197–203)
    └── safety-justice/             (articles 204–210)
```

---

## Article Counts

| Category | Articles | Numbers |
|---|---|---|
| dating-relationships | 12 | 01–12 |
| finance-economic-anxiety | 12 | 13–24 |
| housing-urban-life | 8 | 25–32 |
| workplace-corporate | 8 | 33–40 |
| mental-health-loneliness | 8 | 41–48 |
| health-wellness | 8 | 49–56 |
| future-of-work | 7 | 57–63 |
| gig-economy | 6 | 64–69 |
| hidden-costs-tech | 6 | 70–75 |
| technology-ai | 6 | 76–81 |
| future-of-ai | 6 | 82–87 |
| education-parenting | 6 | 88–93 |
| environment-climate | 6 | 94–99 |
| consumer-product | 6 | 100–105 |
| addiction-recovery | 6 | 106–111 |
| community-social | 6 | 112–117 |
| media-journalism | 6 | 118–123 |
| psychology-betrayal | 6 | 124–129 |
| society-politics | 6 | 130–135 |
| parenting-paradoxes | 6 | 136–141 |
| memory-nostalgia | 6 | 142–147 |
| ethics-ai-art | 7 | 148–154 |
| neurodivergent | 7 | 155–161 |
| law-governance | 7 | 162–168 |
| corporate-accountability | 7 | 169–175 |
| creator-economy | 7 | 176–182 |
| immigrant-experience | 7 | 183–189 |
| ethics-philosophy | 7 | 190–196 |
| meta-narratives | 7 | 197–203 |
| safety-justice | 7 | 204–210 |
| **TOTAL** | **210** | |

---

## Writing Style & Format

Every article follows the same standards:

- **Length:** 2,500–4,500 words of flowing prose (11–14 minute read)
- **Voice:** Conversational, curious, evidence-driven — no dry academic tone
- **No em dashes** anywhere in the prose
- **No Oxford comma** before "and" in lists
- **Blockquotes** formatted as Reddit/forum-style community quotes with subreddit attribution and upvote counts
- **Citations** woven into prose (author, publication, year) rather than footnotes
- **Upvote badge** in the article hero showing community validation score
- **Ad slots** at the top and bottom of each article body (placeholder divs, ready for ad network integration)
- **Related articles** grid at the bottom of each article with 4–6 cross-category links

---

## Technical Spec

- **HTML5** semantic markup
- **Single shared stylesheet:** `shared.css` — referenced via relative path from each article
  - Articles two levels deep (e.g. `articles/category/article.html`) use `../../shared.css`
  - The articles hub (`articles/index.html`) uses `../shared.css`
  - The site root (`index.html`) references `shared.css` directly
- **No JavaScript dependencies** — pure HTML and CSS
- **CSS custom properties** used throughout for theming (dark mode ready)
- **Responsive layout** — mobile-first grid, fluid typography via `clamp()`
- **Print-friendly** — ad slots and nav collapse cleanly

---

## Deploying

Because everything is static HTML and CSS, you can deploy this anywhere:

**Option 1 — Serve locally:**
```bash
cd /path/to/mindbloom
python3 -m http.server 8080
# Then open http://localhost:8080
```

**Option 2 — Deploy to any static host:**
Upload the entire directory to Netlify, Vercel, GitHub Pages, AWS S3 static hosting, Cloudflare Pages, or any web server. No build step required.

**Option 3 — Nginx / Apache:**
Point your document root at the project folder. All links are relative so the site works at any path prefix.

---

## Sitemap

`sitemap.xml` contains all 212 URLs (homepage, articles hub and all 210 articles) using `https://mindbloom.app/` as the base URL. Update the `<loc>` base if you deploy to a different domain.

---

## Ad Integration

Each article contains two ad slot divs:

```html
<div class="ad-slot">Advertisement</div>
```

One appears above the article hero and one at the bottom of the article body. Replace the inner text with your ad network embed code (Google AdSense, Carbon Ads, etc.).

---

## License

Content is original editorial writing created for the MindBloom platform. All rights reserved.