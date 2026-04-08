"""
Audience Intelligence — Prompt Builder
=======================================
Paste the Formspree brief email → fields auto-fill → pick comments file → copy prompt.
"""

import os, sys, csv, json, re, traceback
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from datetime import datetime

# ── Paths ──────────────────────────────────────────────────────────────────────
if getattr(sys, 'frozen', False):
    _APP_DIR    = os.path.dirname(sys.executable)   # Desktop (where exe lives)
    _BUNDLE_DIR = sys._MEIPASS                       # temp dir with bundled files
else:
    _APP_DIR    = os.path.dirname(os.path.abspath(__file__))
    _BUNDLE_DIR = _APP_DIR

_CRASH_LOG    = os.path.join(_APP_DIR, "promptbuilder_crash.log")
_ULTRA_PROMPT = os.path.join(_BUNDLE_DIR, "ultra_prompt.txt")
_OUTPUTS_DIR  = os.path.join(_APP_DIR, "outputs")
_CONTEXTS_DIR = os.path.join(_APP_DIR, "contexts")
os.makedirs(_CONTEXTS_DIR, exist_ok=True)


def _crash_handler(exc_type, exc_val, exc_tb):
    msg = "".join(traceback.format_exception(exc_type, exc_val, exc_tb))
    try:
        with open(_CRASH_LOG, "a", encoding="utf-8") as f:
            f.write(f"\n[{datetime.now()}]\n{msg}\n")
    except Exception:
        pass
    try:
        messagebox.showerror("Prompt Builder — Error",
            f"An error occurred:\n\n{exc_val}\n\nDetails saved to:\n{_CRASH_LOG}")
    except Exception:
        pass

sys.excepthook = _crash_handler

# ── Colours ────────────────────────────────────────────────────────────────────
BG        = "#0a0e1a"
SURFACE   = "#111827"
CARD      = "#1a2235"
BORDER    = "#1e2a3a"
PRIMARY   = "#6366f1"
ACCENT    = "#22d3ee"
SUCCESS   = "#34d399"
WARN      = "#fbbf24"
DANGER    = "#f87171"
TEXT      = "#e2e8f0"
MUTED     = "#64748b"
HEADING   = "#f8fafc"
FONT      = ("Inter", 10)
FONT_BOLD = ("Inter", 10, "bold")
FONT_BIG  = ("Inter", 14, "bold")
FONT_SM   = ("Inter", 9)
MONO      = ("Consolas", 9)


# ── Brief parser ───────────────────────────────────────────────────────────────
# Maps what Formspree sends (field name variations) → canonical keys

_FIELD_ALIASES = {
    "client_name":    ["client_name", "your name", "name", "client name"],
    "client_email":   ["client_email", "email", "email address"],
    "order_id":       ["order_id", "order number", "order", "order no"],
    "post_url":       ["post_url", "post url", "url", "link", "post link"],
    "platform":       ["platform"],
    "post_context":   ["post_context", "post context", "about", "what is the post about",
                       "what's the post about", "what is this post about"],
    "focus":          ["focus", "what do you want to learn", "goals", "focus areas"],
    "extra_notes":    ["extra_notes", "extra notes", "notes", "anything specific",
                       "anything else", "additional notes", "special instructions"],
    "relationship":   ["relationship", "your relationship", "relationship to post",
                       "your relationship to the post"],
}

_RELATIONSHIP_MAP = {
    "i created":    "WE MADE THIS POST",
    "we made":      "WE MADE THIS POST",
    "creator":      "WE MADE THIS POST",
    "someone else": "WE ARE SUPPORTERS",
    "supporter":    "WE ARE SUPPORTERS",
    "supporters":   "WE ARE SUPPORTERS",
    "research":     "WE ARE RESEARCHERS",
    "analysing":    "WE ARE RESEARCHERS",
    "analyzing":    "WE ARE RESEARCHERS",
    "opponent":     "WE ARE OPPONENTS",
    "opponents":    "WE ARE OPPONENTS",
}

def _norm(s):
    return re.sub(r"\s+", " ", s.strip().lower().replace("_", " "))


def parse_brief(text: str) -> dict:
    """
    Parse a Formspree brief email into a dict of canonical field values.
    Handles both  "field_name: value"  and  "Field Name\nvalue"  formats.
    """
    result = {k: "" for k in _FIELD_ALIASES}
    lines = [l.rstrip() for l in text.splitlines()]

    # ── Strategy 1: "key: value" on same line ─────────────────────────────────
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^([^:]{2,60}):\s*(.*)$", line)
        if m:
            raw_key = _norm(m.group(1))
            val = m.group(2).strip()
            # If value is empty, next non-empty line might be the value
            if not val and i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line and not re.match(r"^[^:]{2,60}:", next_line):
                    val = next_line
                    i += 1
            # Match to canonical key
            for canon, aliases in _FIELD_ALIASES.items():
                if raw_key in [_norm(a) for a in aliases]:
                    if canon == "focus" and result[canon]:
                        result[canon] += ", " + val
                    else:
                        result[canon] = val
                    break
        i += 1

    # ── Strategy 2: scan for bare field names as section headers ──────────────
    for canon, aliases in _FIELD_ALIASES.items():
        if result[canon]:
            continue
        for i, line in enumerate(lines):
            norm_line = _norm(line.strip("*-_ "))
            if norm_line in [_norm(a) for a in aliases]:
                # Collect next non-empty lines until next label-like line
                chunks = []
                for j in range(i + 1, min(i + 6, len(lines))):
                    nxt = lines[j].strip()
                    if not nxt:
                        continue
                    if re.match(r"^[^:]{2,60}:", nxt):
                        break
                    chunks.append(nxt)
                if chunks:
                    result[canon] = " ".join(chunks)
                break

    # ── Normalise relationship ─────────────────────────────────────────────────
    rel_raw = result["relationship"].lower()
    for trigger, canonical in _RELATIONSHIP_MAP.items():
        if trigger in rel_raw:
            result["relationship"] = canonical
            break
    else:
        if result["relationship"] and result["relationship"] not in (
            "WE MADE THIS POST", "WE ARE SUPPORTERS",
            "WE ARE RESEARCHERS", "WE ARE OPPONENTS"
        ):
            result["relationship"] = "WE MADE THIS POST"  # safe default

    return result


# ── Comment loader ─────────────────────────────────────────────────────────────

def load_comments_text(path: str):
    """Return (formatted_text_str, count) from CSV or JSON."""
    ext = Path(path).suffix.lower()
    lines = []

    if ext == ".csv":
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                norm = {k.lower().strip(): v for k, v in row.items()}
                text = (norm.get("text") or norm.get("comment") or
                        norm.get("message") or norm.get("content") or
                        norm.get("body") or "").strip()
                if not text:
                    continue
                author = (norm.get("author") or norm.get("name") or
                          norm.get("username") or "anon").strip()
                likes = norm.get("likes") or norm.get("like_count") or ""
                ls = f"  [{likes} likes]" if str(likes).strip() not in ("", "0") else ""
                lines.append(f"{author}: {text}{ls}")

    elif ext == ".json":
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        items = data if isinstance(data, list) else data.get("data", [])
        for item in items:
            if not isinstance(item, dict):
                continue
            text = (item.get("text") or item.get("comment") or
                    item.get("message") or item.get("content") or
                    item.get("body") or "").strip()
            if not text:
                continue
            author = (item.get("author") or item.get("name") or
                      item.get("username") or "anon").strip()
            likes = item.get("likes") or item.get("like_count") or ""
            ls = f"  [{likes} likes]" if str(likes).strip() not in ("", "0") else ""
            lines.append(f"{author}: {text}{ls}")

    return "\n".join(lines), len(lines)


# ── Load analysis instructions from ultra_prompt.txt ──────────────────────────

def load_analysis_instructions() -> str:
    if not os.path.exists(_ULTRA_PROMPT):
        return "(ultra_prompt.txt not found — place it next to this app)"
    with open(_ULTRA_PROMPT, encoding="utf-8") as f:
        content = f.read()
    idx = content.find("ANALYSIS INSTRUCTIONS — DO NOT MODIFY BELOW THIS LINE")
    if idx == -1:
        return content
    start = content.rfind("═" * 10, 0, idx)
    return content[start if start != -1 else idx:]


# ── Assemble prompt ────────────────────────────────────────────────────────────

def assemble_prompt(ctx: dict, comments_text: str, count: int,
                    comments_file: str = "") -> str:

    focus = ctx.get("focus", "") or "(not specified)"
    extra = ctx.get("extra_notes", "") or ""
    goal_parts = [f"Analyse: {focus}"]
    if extra:
        goal_parts.append(f"Special focus: {extra}")
    client_goal = "\n".join(goal_parts)

    rel = ctx.get("relationship") or "WE ARE RESEARCHERS"
    want_reply = "YES" if "reply" in (ctx.get("focus") or "").lower() else "NO"

    context_block = f"""═══════════════════════════════════════════════════════════════════════════════
AUDIENCE INTELLIGENCE REPORT — MASTER PROMPT
═══════════════════════════════════════════════════════════════════════════════

──────────────────────────────────────────────────────────────────────────────
SECTION A — WHO IS THIS REPORT FOR?
──────────────────────────────────────────────────────────────────────────────

CLIENT NAME / ORGANISATION:
{ctx.get("client_name") or "[Not specified]"}

CLIENT GOAL:
{client_goal}

POST AUTHOR / CONTENT CREATOR:
{ctx.get("post_author") or "(see CLIENT RELATIONSHIP below)"}

CLIENT RELATIONSHIP TO POST:
→ {rel}

CLIENT'S OWN PLATFORMS:
{ctx.get("client_platforms") or "(not specified)"}

──────────────────────────────────────────────────────────────────────────────
SECTION B — REPLY PREFERENCES
──────────────────────────────────────────────────────────────────────────────

DO YOU WANT REPLY RECOMMENDATIONS?
→ {want_reply}

PRIMARY GOALS FROM REPLYING:
{ctx.get("reply_goals") or "(see focus areas above)"}

REPLY CAPACITY:
→ MEDIUM

TOPICS TO AVOID ENGAGING WITH:
{ctx.get("avoid_topics") or "(none specified)"}

──────────────────────────────────────────────────────────────────────────────
SECTION C — YOUR VOICE (if replying)
──────────────────────────────────────────────────────────────────────────────

PAGE NAME / HANDLE:
{ctx.get("page_name") or "(not specified)"}

REPLY TONE / VOICE:
{ctx.get("reply_tone") or "Professional, helpful, on-brand"}

──────────────────────────────────────────────────────────────────────────────
SECTION D — POST INFORMATION
──────────────────────────────────────────────────────────────────────────────

POST URL:
{ctx.get("post_url") or "(not provided)"}

POST PLATFORM:
{ctx.get("platform") or "(not specified)"}

WHAT IS THIS POST / VIDEO ABOUT?:
{ctx.get("post_context") or "(not provided — AI will infer from comments)"}

APPROXIMATE COMMENT COUNT:
{count:,} comments

──────────────────────────────────────────────────────────────────────────────
COMMENTS TO ANALYSE:
[{count:,} comments — source: {Path(comments_file).name if comments_file else "pasted directly"}]
──────────────────────────────────────────────────────────────────────────────

{comments_text}

"""
    return context_block + load_analysis_instructions()


# ── Main App ───────────────────────────────────────────────────────────────────

class PromptBuilderApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("AI Prompt Builder — Audience Intelligence")
        self.configure(bg=BG)
        self.resizable(True, True)
        self.minsize(680, 700)
        self._comments_path = ""
        self._ctx = {}
        self._build_ui()
        self._center(720, 820)

    # ── Build UI ───────────────────────────────────────────────────────────────

    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=20, pady=(20, 6))
        tk.Label(hdr, text="📋  Prompt Builder", bg=BG, fg=HEADING,
                 font=FONT_BIG).pack(side="left")
        tk.Label(hdr, text="  paste brief → pick comments → copy prompt",
                 bg=BG, fg=MUTED, font=FONT_SM).pack(side="left", pady=(4, 0))

        # ── Step 1: Paste brief ────────────────────────────────────────────────
        self._section_lbl(self, "  Step 1  —  Paste the client brief email here").pack(
            fill="x", padx=20, pady=(10, 3))

        paste_card = self._card(self)
        paste_card.pack(fill="x", padx=20, pady=(0, 4))
        pf = tk.Frame(paste_card, bg=CARD)
        pf.pack(fill="x", padx=14, pady=12)

        self._brief_box = tk.Text(
            pf, height=9, bg=SURFACE, fg=TEXT, insertbackground=ACCENT,
            relief="flat", font=FONT_SM, wrap="word",
            highlightthickness=1, highlightbackground=BORDER,
        )
        sb = ttk.Scrollbar(pf, command=self._brief_box.yview)
        self._brief_box.configure(yscrollcommand=sb.set)
        self._brief_box.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self._brief_box.insert("1.0",
            "Paste the Formspree email here, then click  Parse Brief  ↓\n\n"
            "Example format:\n"
            "  client_name: Jane Smith\n"
            "  post_url: https://www.facebook.com/...\n"
            "  platform: Facebook\n"
            "  relationship: I created this post\n"
            "  focus: Sentiment, Reply strategy\n"
            "  post_context: A reel about our new product launch\n"
        )
        self._brief_box.config(fg=MUTED)
        self._brief_box.bind("<FocusIn>", self._clear_placeholder)
        self._brief_box.bind("<FocusOut>", self._restore_placeholder)

        parse_row = tk.Frame(self, bg=BG)
        parse_row.pack(fill="x", padx=20, pady=(2, 4))
        self._btn(parse_row, "⚡  Parse Brief", self._parse_brief, accent=True).pack(side="left")
        self._parse_status = tk.Label(parse_row, text="", bg=BG, fg=MUTED, font=FONT_SM)
        self._parse_status.pack(side="left", padx=(12, 0))

        # ── Step 2: Parsed fields (editable) ──────────────────────────────────
        self._section_lbl(self, "  Step 2  —  Check & edit the parsed fields").pack(
            fill="x", padx=20, pady=(10, 3))

        fields_card = self._card(self)
        fields_card.pack(fill="x", padx=20, pady=(0, 4))
        ff = tk.Frame(fields_card, bg=CARD)
        ff.pack(fill="x", padx=14, pady=12)

        self._fv = {}  # field StringVars/Texts

        def row(label, key, multiline=False, height=2, width=60):
            tk.Label(ff, text=label, bg=CARD, fg=MUTED, font=FONT_SM,
                     anchor="w").pack(fill="x", pady=(6, 1))
            if multiline:
                t = tk.Text(ff, height=height, bg=SURFACE, fg=TEXT,
                            insertbackground=ACCENT, relief="flat", font=FONT,
                            highlightthickness=1, highlightbackground=BORDER, wrap="word")
                t.pack(fill="x", pady=(0, 2))
                self._fv[key] = t
            else:
                v = tk.StringVar()
                e = tk.Entry(ff, textvariable=v, bg=SURFACE, fg=TEXT,
                             insertbackground=ACCENT, relief="flat", font=FONT,
                             highlightthickness=1, highlightbackground=BORDER,
                             highlightcolor=PRIMARY, width=width)
                e.pack(fill="x", ipady=4)
                self._fv[key] = v

        row("Client / Organisation name",   "client_name")
        row("Post URL",                      "post_url")
        row("Platform",                      "platform")

        # Relationship dropdown
        tk.Label(ff, text="Client relationship to post", bg=CARD, fg=MUTED,
                 font=FONT_SM, anchor="w").pack(fill="x", pady=(6, 1))
        self._fv["relationship"] = tk.StringVar(value="WE MADE THIS POST")
        ttk.Combobox(ff, textvariable=self._fv["relationship"],
                     values=["WE MADE THIS POST", "WE ARE SUPPORTERS",
                             "WE ARE RESEARCHERS", "WE ARE OPPONENTS"],
                     state="readonly", width=40).pack(anchor="w", ipady=3)

        row("What is this post about?",      "post_context", multiline=True, height=2)
        row("What the client wants to learn (focus areas)", "focus")
        row("Extra notes / special focus",   "extra_notes")
        row("Client's own platforms",        "client_platforms")
        row("Reply page name / handle",      "page_name")
        row("Reply tone (optional)",         "reply_tone")
        row("Topics to avoid (optional)",    "avoid_topics")

        # Save / Load context buttons
        save_row = tk.Frame(ff, bg=CARD)
        save_row.pack(fill="x", pady=(10, 0))
        self._btn(save_row, "💾 Save context", self._save_ctx).pack(side="left")
        self._btn(save_row, "📂 Load context", self._load_ctx).pack(side="left", padx=(8, 0))

        # ── Step 3: Comments file ──────────────────────────────────────────────
        self._section_lbl(self, "  Step 3  —  Pick the scraped comments file").pack(
            fill="x", padx=20, pady=(10, 3))

        file_card = self._card(self)
        file_card.pack(fill="x", padx=20, pady=(0, 4))
        fcf = tk.Frame(file_card, bg=CARD)
        fcf.pack(fill="x", padx=14, pady=12)

        frow = tk.Frame(fcf, bg=CARD)
        frow.pack(fill="x")
        self._file_lbl = tk.Label(frow, text="No file selected",
                                  bg=CARD, fg=MUTED, font=FONT_SM, anchor="w")
        self._file_lbl.pack(side="left", fill="x", expand=True)
        self._btn(frow, "Browse…", self._browse).pack(side="right")

        self._count_lbl = tk.Label(fcf, text="", bg=CARD, fg=MUTED,
                                   font=FONT_SM, anchor="w")
        self._count_lbl.pack(anchor="w", pady=(4, 0))

        # Recent outputs dropdown
        recent = sorted(
            [str(p) for p in Path(_OUTPUTS_DIR).glob("*.csv")] +
            [str(p) for p in Path(_OUTPUTS_DIR).glob("*.json")
             if "comments" in p.name.lower() or "_checkpoint_" in p.name],
            key=os.path.getmtime, reverse=True
        )[:12] if Path(_OUTPUTS_DIR).exists() else []

        if recent:
            tk.Label(fcf, text="Recent outputs:", bg=CARD, fg=MUTED,
                     font=FONT_SM).pack(anchor="w", pady=(8, 2))
            self._recent_var = tk.StringVar()
            self._recent_paths = recent
            cmb = ttk.Combobox(fcf, textvariable=self._recent_var,
                               values=[Path(p).name for p in recent],
                               state="readonly", width=60)
            cmb.pack(anchor="w")
            cmb.bind("<<ComboboxSelected>>", self._pick_recent)

        # ── Step 4: Build ──────────────────────────────────────────────────────
        self._section_lbl(self, "  Step 4  —  Build prompt").pack(
            fill="x", padx=20, pady=(10, 3))

        btn_card = self._card(self)
        btn_card.pack(fill="x", padx=20, pady=(0, 4))
        bcf = tk.Frame(btn_card, bg=CARD)
        bcf.pack(fill="x", padx=14, pady=14)

        brow = tk.Frame(bcf, bg=CARD)
        brow.pack(fill="x")
        self._btn(brow, "📋  Copy to Clipboard", self._copy, accent=True).pack(side="left")
        self._btn(brow, "💾  Save to file",       self._save_file).pack(side="left", padx=(8, 0))

        self._status = tk.Label(bcf, text="Ready — complete steps 1–3 above",
                                bg=CARD, fg=MUTED, font=FONT_SM, anchor="w")
        self._status.pack(anchor="w", pady=(8, 0))

    # ── Helpers ────────────────────────────────────────────────────────────────

    def _section_lbl(self, parent, text):
        return tk.Label(parent, text=text, bg=BG, fg=ACCENT,
                        font=FONT_BOLD, anchor="w")

    def _card(self, parent):
        return tk.Frame(parent, bg=CARD, highlightthickness=1,
                        highlightbackground=BORDER)

    def _btn(self, parent, text, cmd, accent=False):
        bg = PRIMARY if accent else CARD
        b = tk.Button(parent, text=text, command=cmd,
                      bg=bg, fg="#fff", activebackground=ACCENT,
                      activeforeground="#000", relief="flat",
                      padx=14, pady=7, font=FONT_BOLD, cursor="hand2")
        b.bind("<Enter>", lambda e: b.config(bg=ACCENT))
        b.bind("<Leave>", lambda e: b.config(bg=bg))
        return b

    def _clear_placeholder(self, _event):
        if self._brief_box.cget("fg") == MUTED:
            self._brief_box.delete("1.0", "end")
            self._brief_box.config(fg=TEXT)

    def _restore_placeholder(self, _event):
        if not self._brief_box.get("1.0", "end").strip():
            self._brief_box.insert("1.0",
                "Paste the Formspree email here, then click  Parse Brief  ↓")
            self._brief_box.config(fg=MUTED)

    def _center(self, w, h):
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def _fget(self, key):
        w = self._fv.get(key)
        if w is None:
            return ""
        if isinstance(w, tk.StringVar):
            return w.get().strip()
        return w.get("1.0", "end").strip()

    def _fset(self, key, val):
        w = self._fv.get(key)
        if w is None:
            return
        if isinstance(w, tk.StringVar):
            w.set(val)
        else:
            w.delete("1.0", "end")
            w.insert("1.0", val)

    # ── Parse ──────────────────────────────────────────────────────────────────

    def _parse_brief(self):
        raw = self._brief_box.get("1.0", "end").strip()
        if not raw or raw.startswith("Paste the Formspree"):
            messagebox.showwarning("Nothing to parse", "Paste the brief email first.")
            return

        parsed = parse_brief(raw)
        self._ctx = parsed

        # Populate fields
        self._fset("client_name",    parsed.get("client_name", ""))
        self._fset("post_url",       parsed.get("post_url", ""))
        self._fset("platform",       parsed.get("platform", ""))
        self._fset("post_context",   parsed.get("post_context", ""))
        self._fset("focus",          parsed.get("focus", ""))
        self._fset("extra_notes",    parsed.get("extra_notes", ""))
        rel = parsed.get("relationship")
        if rel in ("WE MADE THIS POST", "WE ARE SUPPORTERS",
                   "WE ARE RESEARCHERS", "WE ARE OPPONENTS"):
            self._fv["relationship"].set(rel)

        filled = sum(1 for k in ("client_name", "post_url", "platform",
                                 "post_context", "focus", "relationship")
                     if parsed.get(k))
        self._parse_status.config(
            text=f"✓ {filled} fields found — check and edit below",
            fg=SUCCESS)

    # ── Context save/load ──────────────────────────────────────────────────────

    def _gather_ctx(self):
        return {k: self._fget(k) for k in self._fv}

    def _save_ctx(self):
        name = self._fget("client_name") or "context"
        safe = re.sub(r"[^\w\- ]", "_", name)[:40]
        path = filedialog.asksaveasfilename(
            initialdir=_CONTEXTS_DIR, initialfile=f"{safe}.json",
            defaultextension=".json", filetypes=[("JSON", "*.json")])
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._gather_ctx(), f, indent=2, ensure_ascii=False)
        self._status.config(text=f"Context saved: {Path(path).name}", fg=SUCCESS)

    def _load_ctx(self):
        path = filedialog.askopenfilename(
            initialdir=_CONTEXTS_DIR, filetypes=[("JSON", "*.json"), ("All", "*.*")])
        if not path:
            return
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        for key, val in d.items():
            self._fset(key, val)
        self._status.config(text=f"Context loaded: {Path(path).name}", fg=SUCCESS)

    # ── Comments file ──────────────────────────────────────────────────────────

    def _browse(self):
        p = filedialog.askopenfilename(
            initialdir=_OUTPUTS_DIR, title="Select comments file",
            filetypes=[("CSV/JSON", "*.csv *.json"), ("All", "*.*")])
        if p:
            self._set_file(p)

    def _pick_recent(self, _event):
        name = self._recent_var.get()
        for p in self._recent_paths:
            if Path(p).name == name:
                self._set_file(p)
                return

    def _set_file(self, path):
        self._comments_path = path
        self._file_lbl.config(text=Path(path).name, fg=ACCENT)
        try:
            _, count = load_comments_text(path)
            self._count_lbl.config(text=f"{count:,} comments loaded", fg=SUCCESS)
        except Exception as e:
            self._count_lbl.config(text=f"Error: {e}", fg=DANGER)

    # ── Build ──────────────────────────────────────────────────────────────────

    def _build(self):
        ctx = self._gather_ctx()
        comments_text, count = "", 0
        if self._comments_path and os.path.exists(self._comments_path):
            comments_text, count = load_comments_text(self._comments_path)
        return assemble_prompt(ctx, comments_text, count, self._comments_path)

    def _copy(self):
        try:
            prompt = self._build()
            self.clipboard_clear()
            self.clipboard_append(prompt)
            chars = len(prompt)
            words = len(prompt.split())
            self._status.config(
                text=f"✓ Copied! {chars:,} chars · ~{words:,} words — paste into Claude / ChatGPT / Gemini",
                fg=SUCCESS)
            messagebox.showinfo("Prompt Ready!",
                f"Copied to clipboard.\n\n{chars:,} characters (~{words:,} words)\n\n"
                "Paste into Claude, ChatGPT, or Gemini.")
        except Exception as e:
            self._status.config(text=f"Error: {e}", fg=DANGER)

    def _save_file(self):
        try:
            prompt = self._build()
            name = self._fget("client_name") or "prompt"
            safe = re.sub(r"[^\w\- ]", "_", name)[:40]
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = filedialog.asksaveasfilename(
                initialdir=_APP_DIR,
                initialfile=f"prompt_{safe}_{ts}.txt",
                defaultextension=".txt", filetypes=[("Text", "*.txt"), ("All", "*.*")])
            if not path:
                return
            with open(path, "w", encoding="utf-8") as f:
                f.write(prompt)
            self._status.config(text=f"Saved: {Path(path).name}", fg=SUCCESS)
        except Exception as e:
            self._status.config(text=f"Error: {e}", fg=DANGER)


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    try:
        app = PromptBuilderApp()
        app.mainloop()
    except Exception as e:
        _crash_handler(type(e), e, e.__traceback__)
