"""
Reddit Gold Miner — Desktop GUI
Double-click to run, or: python reddit_miner_gui.py
"""

import os
import sys
import traceback
import logging
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime, timezone, timedelta

# ── Resolve paths: PyInstaller --onefile extracts to a temp dir, so use
#    the exe's real folder for user-facing files (outputs, logs, etc.)
if getattr(sys, 'frozen', False):
    _APP_DIR = os.path.dirname(sys.executable)
    # Fix SSL certificates for frozen PyInstaller builds
    _meipass = getattr(sys, '_MEIPASS', None)
    if _meipass:
        _cert = os.path.join(_meipass, 'certifi', 'cacert.pem')
        if os.path.exists(_cert):
            os.environ.setdefault('SSL_CERT_FILE', _cert)
            os.environ.setdefault('REQUESTS_CA_BUNDLE', _cert)
else:
    _APP_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, _APP_DIR)

# ── Crash log — captures ANY startup error before logging is set up ──────
_CRASH_LOG = os.path.join(_APP_DIR, "reddit_crash.log")

def _crash_handler(exc_type, exc_value, exc_tb):
    msg = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    try:
        with open(_CRASH_LOG, "a", encoding="utf-8") as f:
            f.write(f"\n{'='*60}\n{msg}\n")
    except Exception:
        pass
    try:
        import tkinter.messagebox
        tkinter.messagebox.showerror("RedditResearcher — Crash", msg[:800])
    except Exception:
        pass
    sys.__excepthook__(exc_type, exc_value, exc_tb)

sys.excepthook = _crash_handler

# ── Debug log file (always write, so we can diagnose exe issues) ─────────
_LOG_DIR = os.path.join(_APP_DIR, "outputs")
os.makedirs(_LOG_DIR, exist_ok=True)
_LOG_PATH = os.path.join(_LOG_DIR, "reddit_debug.log")
logging.basicConfig(
    filename=_LOG_PATH, level=logging.DEBUG,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%H:%M:%S",
)
_log = logging.getLogger("reddit_gui")
_log.info("=== App starting  frozen=%s  APP_DIR=%s ===", getattr(sys, 'frozen', False), _APP_DIR)

from reddit_comment_exporter.scraper import RedditScraper
_log.info("Scraper imported OK")

# ── Colours ──────────────────────────────────────────────────────────────────
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
FONT_BIG  = ("Inter", 13, "bold")
FONT_SM   = ("Inter", 8)
MONO      = ("Consolas", 8)

OUTPUTS_DIR = os.path.join(_APP_DIR, "outputs")
os.makedirs(OUTPUTS_DIR, exist_ok=True)

# ── Date range presets ───────────────────────────────────────────────────────
DATE_PRESETS = [
    "Today",
    "This week  (7 days)",
    "This month (30 days)",
    "This year  (365 days)",
    "All time",
]

def preset_to_timestamps(label: str):
    """Return (after_ts, before_ts) for a preset label."""
    now = datetime.now(tz=timezone.utc)
    if   "Today"  in label: return int(now.replace(hour=0,minute=0,second=0,microsecond=0).timestamp()), None
    elif "week"   in label: return int((now - timedelta(days=7)).timestamp()),   None
    elif "month"  in label: return int((now - timedelta(days=30)).timestamp()),  None
    elif "year"   in label: return int((now - timedelta(days=365)).timestamp()), None
    else:                   return None, None   # All time


# ── Widget helpers ───────────────────────────────────────────────────────────

def styled_button(parent, text, command, accent=False, danger=False, **kw):
    bg = PRIMARY if accent else (DANGER if danger else CARD)
    btn = tk.Button(
        parent, text=text, command=command,
        bg=bg, fg="#ffffff", activebackground=ACCENT, activeforeground="#000",
        relief="flat", borderwidth=0, padx=14, pady=7,
        font=FONT_BOLD, cursor="hand2", **kw
    )
    btn.bind("<Enter>", lambda e: btn.config(bg=ACCENT if accent else (DANGER if danger else BORDER)))
    btn.bind("<Leave>", lambda e: btn.config(bg=bg))
    return btn


def entry(parent, textvariable=None, width=40, **kw):
    return tk.Entry(
        parent, textvariable=textvariable,
        bg=SURFACE, fg=TEXT, insertbackground=ACCENT,
        relief="flat", borderwidth=0, highlightthickness=1,
        highlightbackground=BORDER, highlightcolor=PRIMARY,
        font=FONT, width=width, **kw
    )


def section_frame(parent):
    return tk.Frame(parent, bg=CARD, relief="flat", bd=0,
                    highlightthickness=1, highlightbackground=BORDER)


# ── Main App ─────────────────────────────────────────────────────────────────

class RedditMinerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Reddit Gold Miner")
        self.configure(bg=BG)
        self.resizable(True, True)
        self.minsize(600, 700)

        # State
        self.subreddit_var  = tk.StringVar()
        self.mode_var       = tk.StringVar(value="full")
        self.date_var       = tk.StringVar(value="All time")
        self.format_var     = tk.StringVar(value="csv")
        self.post_cap_var   = tk.StringVar(value="500")
        self.comment_cap_var = tk.StringVar(value="1000")
        self.output_dir     = OUTPUTS_DIR
        self._worker_thread = None
        self._scraper       = None
        self._stop_flag     = threading.Event()

        self._build_ui()
        self._center_window(640, 760)

    # ── UI Build ─────────────────────────────────────────────────────────────

    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=20, pady=(22, 4))
        tk.Label(hdr, text="🪙  Reddit Gold Miner", bg=BG, fg=HEADING,
                 font=FONT_BIG).pack(side="left")
        tk.Label(hdr, text="  PullPush.io + Reddit JSON  ·  no API key needed",
                 bg=BG, fg=MUTED, font=FONT_SM).pack(side="left", pady=(4, 0))

        # ── Subreddit ────────────────────────────────────────────────────
        sub_frame = section_frame(self)
        sub_frame.pack(fill="x", padx=18, pady=(6, 4))
        tk.Label(sub_frame, text="Subreddit", bg=CARD, fg=MUTED,
                 font=FONT_SM).pack(anchor="w", padx=14, pady=(10, 2))
        row = tk.Frame(sub_frame, bg=CARD)
        row.pack(fill="x", padx=14, pady=(0, 12))
        tk.Label(row, text="r/", bg=CARD, fg=ACCENT, font=FONT_BOLD).pack(side="left")
        sub_entry = entry(row, textvariable=self.subreddit_var, width=40)
        sub_entry.pack(side="left", fill="x", expand=True, ipady=5)

        # ── Mine Mode ────────────────────────────────────────────────────
        mode_frame = section_frame(self)
        mode_frame.pack(fill="x", padx=18, pady=4)
        tk.Label(mode_frame, text="What to mine", bg=CARD, fg=MUTED,
                 font=FONT_SM).pack(anchor="w", padx=14, pady=(10, 4))
        mode_row = tk.Frame(mode_frame, bg=CARD)
        mode_row.pack(fill="x", padx=14, pady=(0, 12))

        self._mode_buttons = {}
        for val, emoji, lbl_text in [
            ("full",     "⛏",  "Posts + Comments"),
            ("posts",    "📄",  "Posts only"),
            ("comments", "💬",  "Comments only"),
            ("post",     "🔗",  "Single post"),
        ]:
            rb = tk.Radiobutton(
                mode_row, text=f"{emoji}  {lbl_text}",
                variable=self.mode_var, value=val,
                command=self._on_mode_change,
                bg=CARD, fg=TEXT, selectcolor=SURFACE,
                activebackground=CARD, activeforeground=ACCENT,
                font=FONT, indicatoron=False, relief="flat", borderwidth=0,
                highlightthickness=1, highlightbackground=BORDER,
                padx=12, pady=7, cursor="hand2"
            )
            rb.pack(side="left", padx=(0, 6))
            self._mode_buttons[val] = rb
        self._refresh_mode_buttons()
        self.mode_var.trace_add("write", lambda *_: self._refresh_mode_buttons())

        # ── Single post URL (hidden until mode=post) ──────────────────────
        self.post_url_frame = section_frame(self)
        tk.Label(self.post_url_frame, text="Post URL or ID", bg=CARD, fg=MUTED,
                 font=FONT_SM).pack(anchor="w", padx=14, pady=(10, 2))
        post_row = tk.Frame(self.post_url_frame, bg=CARD)
        post_row.pack(fill="x", padx=14, pady=(0, 12))
        self.post_url_var = tk.StringVar()
        entry(post_row, textvariable=self.post_url_var, width=52).pack(
            side="left", fill="x", expand=True, ipady=5)

        # ── Date Range ───────────────────────────────────────────────────
        date_frame = section_frame(self)
        date_frame.pack(fill="x", padx=18, pady=4)
        tk.Label(date_frame, text="Date range", bg=CARD, fg=MUTED,
                 font=FONT_SM).pack(anchor="w", padx=14, pady=(10, 4))
        date_row = tk.Frame(date_frame, bg=CARD)
        date_row.pack(fill="x", padx=14, pady=(0, 12))

        self._date_buttons = {}
        for preset in DATE_PRESETS:
            short = preset.split("(")[0].strip()
            rb = tk.Radiobutton(
                date_row, text=short,
                variable=self.date_var, value=preset,
                command=self._refresh_date_buttons,
                bg=CARD, fg=TEXT, selectcolor=SURFACE,
                activebackground=CARD, activeforeground=ACCENT,
                font=FONT_SM, indicatoron=False, relief="flat", borderwidth=0,
                highlightthickness=1, highlightbackground=BORDER,
                padx=10, pady=6, cursor="hand2"
            )
            rb.pack(side="left", padx=(0, 5))
            self._date_buttons[preset] = rb
        self._refresh_date_buttons()

        # ── Options ──────────────────────────────────────────────────────
        opts_frame = section_frame(self)
        opts_frame.pack(fill="x", padx=18, pady=4)
        tk.Label(opts_frame, text="Options", bg=CARD, fg=MUTED,
                 font=FONT_SM).pack(anchor="w", padx=14, pady=(10, 4))
        opts_inner = tk.Frame(opts_frame, bg=CARD)
        opts_inner.pack(fill="x", padx=14, pady=(0, 12))

        # Format
        fmt_row = tk.Frame(opts_inner, bg=CARD)
        fmt_row.pack(fill="x", pady=(0, 8))
        tk.Label(fmt_row, text="Output format", bg=CARD, fg=TEXT,
                 font=FONT, width=16, anchor="w").pack(side="left")
        for val, lbl_text in [("csv","CSV"), ("json","JSON"), ("both","Both")]:
            tk.Radiobutton(
                fmt_row, text=lbl_text, variable=self.format_var, value=val,
                bg=CARD, fg=TEXT, selectcolor=SURFACE,
                activebackground=CARD, font=FONT
            ).pack(side="left", padx=(0, 12))

        # Caps
        cap_row = tk.Frame(opts_inner, bg=CARD)
        cap_row.pack(fill="x", pady=(0, 0))
        tk.Label(cap_row, text="Max posts", bg=CARD, fg=TEXT,
                 font=FONT, width=16, anchor="w").pack(side="left")
        entry(cap_row, textvariable=self.post_cap_var, width=8).pack(side="left", ipady=4)
        tk.Label(cap_row, text="  Max comments", bg=CARD, fg=TEXT,
                 font=FONT).pack(side="left")
        entry(cap_row, textvariable=self.comment_cap_var, width=8).pack(side="left", padx=(4,0), ipady=4)
        tk.Label(cap_row, text="  (blank = unlimited, be careful!)", bg=CARD, fg=MUTED,
                 font=FONT_SM).pack(side="left")

        # ── Output folder ────────────────────────────────────────────────
        dir_frame = section_frame(self)
        dir_frame.pack(fill="x", padx=18, pady=4)
        tk.Label(dir_frame, text="Save to", bg=CARD, fg=MUTED,
                 font=FONT_SM).pack(anchor="w", padx=14, pady=(10, 2))
        dir_row = tk.Frame(dir_frame, bg=CARD)
        dir_row.pack(fill="x", padx=14, pady=(0, 12))
        self.dir_lbl = tk.Label(dir_row, text=self.output_dir, bg=CARD,
                                fg=ACCENT, font=FONT_SM, anchor="w")
        self.dir_lbl.pack(side="left", fill="x", expand=True)
        styled_button(dir_row, "Browse…", self._choose_dir).pack(side="right")

        # ── Progress bar ─────────────────────────────────────────────────
        prog_frame = section_frame(self)
        prog_frame.pack(fill="x", padx=18, pady=4)
        prog_inner = tk.Frame(prog_frame, bg=CARD)
        prog_inner.pack(fill="x", padx=14, pady=10)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            prog_inner, variable=self.progress_var,
            maximum=100, mode="indeterminate", length=400
        )
        self.progress_bar.pack(fill="x")
        self.status_lbl = tk.Label(prog_inner, text="Ready  ·  enter a subreddit and press Mine",
                                   bg=CARD, fg=MUTED, font=FONT_SM, anchor="w")
        self.status_lbl.pack(anchor="w", pady=(4, 0))

        # ── Action buttons ───────────────────────────────────────────────
        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(fill="x", padx=18, pady=(8, 4))

        self.mine_btn = styled_button(btn_row, "⛏  Mine", self._start_mine, accent=True)
        self.mine_btn.pack(side="left")

        self.stop_btn = styled_button(btn_row, "■  Stop", self._stop_mine, danger=True)
        self.stop_btn.pack(side="left", padx=(8, 0))
        self.stop_btn.config(state="disabled")

        styled_button(btn_row, "📂  Open folder", self._open_folder).pack(side="left", padx=(8, 0))
        styled_button(btn_row, "🕒  History",     self._show_history).pack(side="left", padx=(8, 0))

        # ── Log ──────────────────────────────────────────────────────────
        log_frame = section_frame(self)
        log_frame.pack(fill="both", expand=True, padx=18, pady=(4, 18))
        tk.Label(log_frame, text="Log", bg=CARD, fg=MUTED,
                 font=FONT_SM).pack(anchor="w", padx=14, pady=(8, 2))
        log_inner = tk.Frame(log_frame, bg=CARD)
        log_inner.pack(fill="both", expand=True, padx=14, pady=(0, 12))
        self.log_text = tk.Text(
            log_inner, bg=SURFACE, fg=TEXT, insertbackground=ACCENT,
            relief="flat", borderwidth=0, font=MONO,
            wrap="word", height=9, state="disabled"
        )
        scroll = ttk.Scrollbar(log_inner, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scroll.set)
        self.log_text.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self._on_mode_change()

    # ── UI helpers ───────────────────────────────────────────────────────────

    def _center_window(self, w, h):
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def _refresh_mode_buttons(self):
        sel = self.mode_var.get()
        for val, rb in self._mode_buttons.items():
            if val == sel:
                rb.config(fg=ACCENT, highlightbackground=PRIMARY)
            else:
                rb.config(fg=TEXT, highlightbackground=BORDER)

    def _refresh_date_buttons(self):
        sel = self.date_var.get()
        for preset, rb in self._date_buttons.items():
            if preset == sel:
                rb.config(fg=ACCENT, highlightbackground=PRIMARY)
            else:
                rb.config(fg=TEXT, highlightbackground=BORDER)

    def _on_mode_change(self):
        mode = self.mode_var.get()
        if mode == "post":
            self.post_url_frame.pack(fill="x", padx=18, pady=4,
                                     before=self._get_date_frame())
        else:
            self.post_url_frame.pack_forget()

    def _get_date_frame(self):
        """Return the date section frame widget."""
        for child in self.winfo_children():
            if isinstance(child, tk.Frame) and child.cget("bg") == CARD:
                for grandchild in child.winfo_children():
                    if isinstance(grandchild, tk.Label):
                        if "Date range" in (grandchild.cget("text") or ""):
                            return child
        # fallback: just pack after last section
        return None

    def _log(self, msg: str, colour=None):
        """Append a line to the log area (thread-safe)."""
        def _append():
            self.log_text.config(state="normal")
            tag = colour or TEXT
            self.log_text.insert("end", msg + "\n", tag)
            self.log_text.tag_config(tag, foreground=tag)
            self.log_text.see("end")
            self.log_text.config(state="disabled")
        self.after(0, _append)

    def _set_status(self, msg: str, colour=None):
        self.after(0, lambda: self.status_lbl.config(
            text=msg, fg=colour or MUTED))

    def _choose_dir(self):
        d = filedialog.askdirectory(initialdir=self.output_dir)
        if d:
            self.output_dir = d
            self.dir_lbl.config(text=d)

    def _open_folder(self):
        import subprocess
        subprocess.Popen(f'explorer "{self.output_dir}"')

    def _show_history(self):
        history = RedditScraper.load_history()
        if not history:
            messagebox.showinfo("History", "No mining history yet.")
            return
        lines = []
        for i, rec in enumerate(history[:15], 1):
            sub  = rec.get("subreddit", "?")
            mode = rec.get("mode", "?")
            at   = rec.get("scraped_at", "")
            posts    = rec.get("posts", "")
            comments = rec.get("comments", "")
            counts   = "  ".join(filter(None, [
                f"{posts} posts" if posts else "",
                f"{comments} comments" if comments else ""
            ]))
            lines.append(f"[{i}] r/{sub}  ({mode})  {at}")
            if counts: lines.append(f"     {counts}")
            for f in rec.get("files", []):
                lines.append(f"     → {os.path.basename(f)}")
            lines.append("")
        messagebox.showinfo("Mining History", "\n".join(lines))

    # ── Mining ───────────────────────────────────────────────────────────────

    def _parse_cap(self, val: str):
        val = val.strip()
        if not val:
            return None
        try:
            return int(val)
        except ValueError:
            return None

    def _extract_post_id(self, url_or_id: str) -> str:
        url_or_id = url_or_id.strip().rstrip("/")
        if "reddit.com" in url_or_id:
            parts = url_or_id.split("/")
            try:
                idx = parts.index("comments")
                return parts[idx + 1]
            except (ValueError, IndexError):
                pass
        return url_or_id.split("/")[-1]

    def _start_mine(self):
        raw_sub = self.subreddit_var.get().strip().lower()
        subreddit = raw_sub[2:] if raw_sub.startswith("r/") else raw_sub
        if not subreddit:
            messagebox.showerror("Missing subreddit", "Please enter a subreddit name.")
            return

        mode = self.mode_var.get()
        if mode == "post":
            post_raw = self.post_url_var.get().strip()
            if not post_raw:
                messagebox.showerror("Missing post", "Please enter a post URL or ID.")
                return

        # Clear log
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.config(state="disabled")

        self.mine_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self._stop_flag.clear()
        self.progress_bar.config(mode="indeterminate")
        self.progress_bar.start(12)

        self._worker_thread = threading.Thread(target=self._mine_worker, daemon=True)
        self._worker_thread.start()

    def _stop_mine(self):
        self._stop_flag.set()
        self._log("Stop requested — finishing current batch…", WARN)
        self._set_status("Stopping…", WARN)

    def _mine_done(self, success: bool, summary: str):
        self.after(0, self._on_mine_done, success, summary)

    def _on_mine_done(self, success: bool, summary: str):
        self.progress_bar.stop()
        self.progress_bar.config(mode="determinate")
        self.progress_var.set(100 if success else 0)
        self.mine_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        colour = SUCCESS if success else DANGER
        self._set_status(summary, colour)
        self._log(f"\n{'✓' if success else '✗'}  {summary}", colour)

    def _mine_worker(self):
        raw_sub = self.subreddit_var.get().strip().lower()
        subreddit = raw_sub[2:] if raw_sub.startswith("r/") else raw_sub
        mode         = self.mode_var.get()
        date_preset  = self.date_var.get()
        fmt          = self.format_var.get()
        post_cap     = self._parse_cap(self.post_cap_var.get())
        comment_cap  = self._parse_cap(self.comment_cap_var.get())
        after_ts, before_ts = preset_to_timestamps(date_preset)

        _log.info("MINE START sub=%r mode=%s date=%s fmt=%s post_cap=%s comment_cap=%s after=%s before=%s",
                  subreddit, mode, date_preset, fmt, post_cap, comment_cap, after_ts, before_ts)

        def on_progress(msg):
            if self._stop_flag.is_set():
                raise InterruptedError("Stopped by user")
            _log.debug("progress: %s", msg)
            self._log(f"  {msg}")
            self._set_status(msg)

        scraper = RedditScraper(
            subreddit    = subreddit,
            after        = after_ts,
            before       = before_ts,
            max_posts    = post_cap,
            max_comments = comment_cap,
            output_dir   = self.output_dir,
            on_progress  = on_progress,
        )

        saved_files = []
        CHECKPOINT_EVERY = 200

        def _save_file(data, content_type, label=""):
            """Write data to CSV/JSON. Overwrites same path each time for live checkpoints."""
            ts_tag = datetime.now().strftime("%Y%m%d_%H%M%S")
            tag    = label or content_type
            paths  = []
            if fmt in ("csv", "both"):
                path = os.path.join(self.output_dir, f"reddit_{subreddit}_{tag}.csv")
                if content_type in ("posts",):
                    scraper.save_posts_csv(data, path)
                else:
                    scraper.save_comments_csv(data, path)
                if path not in saved_files:
                    saved_files.append(path)
                paths.append(path)
            if fmt in ("json", "both"):
                path = os.path.join(self.output_dir, f"reddit_{subreddit}_{tag}.json")
                scraper.save_json(data, path)
                if path not in saved_files:
                    saved_files.append(path)
                paths.append(path)
            return paths

        try:
            self._log(f"⛏  Mining r/{subreddit}  [{date_preset.split('(')[0].strip()}]  mode={mode}")
            _log.info("Entering try block, mode=%s", mode)

            posts_count = comments_count = 0

            # ── Posts ────────────────────────────────────────────────
            if mode in ("full", "posts"):
                self._log("\n  Fetching posts…")
                _log.info("Starting iter_posts")
                posts = []
                try:
                    for post in scraper.iter_posts():
                        posts.append(post)
                        if len(posts) % CHECKPOINT_EVERY == 0:
                            _save_file(posts, "posts")
                            self._log(f"  💾 Saved checkpoint — {len(posts)} posts so far", ACCENT)
                except Exception as e:
                    _log.error("iter_posts error: %s", e, exc_info=True)
                    self._log(f"  ⚠ Stopped fetching posts: {e}", WARN)
                posts_count = len(posts)
                _log.info("Posts collected: %d", posts_count)
                if posts:
                    paths = _save_file(posts, "posts")
                    self._log(f"  ✓ {posts_count:,} posts saved → {paths[0]}", SUCCESS)

            # ── Comments ─────────────────────────────────────────────
            if mode in ("full", "comments"):
                self._log("\n  Fetching comments…")
                comments = []
                try:
                    for comment in scraper.iter_comments():
                        comments.append(comment)
                        if len(comments) % CHECKPOINT_EVERY == 0:
                            _save_file(comments, "comments")
                            self._log(f"  💾 Saved checkpoint — {len(comments)} comments so far", ACCENT)
                except Exception as e:
                    self._log(f"  ⚠ Stopped fetching comments: {e}", WARN)
                comments_count = len(comments)
                if comments:
                    paths = _save_file(comments, "comments")
                    self._log(f"  ✓ {comments_count:,} comments saved → {paths[0]}", SUCCESS)

            # ── Single post ──────────────────────────────────────────
            if mode == "post":
                post_id = self._extract_post_id(self.post_url_var.get())
                self._log(f"\n  Fetching comments for post: {post_id}…")
                comments = []
                try:
                    for comment in scraper.iter_comments(post_id=post_id):
                        comments.append(comment)
                        if len(comments) % CHECKPOINT_EVERY == 0:
                            _save_file(comments, "comments", f"post_{post_id}")
                            self._log(f"  💾 Saved checkpoint — {len(comments)} comments so far", ACCENT)
                except Exception as e:
                    self._log(f"  ⚠ Stopped fetching comments: {e}", WARN)
                comments_count = len(comments)
                if comments:
                    paths = _save_file(comments, "comments", f"post_{post_id}")
                    self._log(f"  ✓ {comments_count:,} comments saved → {paths[0]}", SUCCESS)

            # Save history
            record = {
                "mode":       mode,
                "subreddit":  subreddit,
                "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "date_range": date_preset.split("(")[0].strip(),
                "files":      saved_files,
            }
            if posts_count:    record["posts"]    = posts_count
            if comments_count: record["comments"] = comments_count
            scraper.save_history(record)

            counts = []
            if posts_count:    counts.append(f"{posts_count:,} posts")
            if comments_count: counts.append(f"{comments_count:,} comments")
            summary = "Done — " + (", ".join(counts) if counts else "nothing found")
            _log.info("MINE DONE: %s", summary)
            self._mine_done(True, summary)

        except InterruptedError:
            _log.info("Stopped by user")
            self._mine_done(False, "Stopped by user.")
        except Exception as exc:
            _log.error("MINE EXCEPTION: %s", exc, exc_info=True)
            self._log(f"\nERROR: {exc}", DANGER)
            self._mine_done(False, f"Error: {exc}")


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    try:
        app = RedditMinerApp()
        app.mainloop()
    except Exception:
        msg = traceback.format_exc()
        try:
            with open(_CRASH_LOG, "a", encoding="utf-8") as f:
                f.write(f"\n{'='*60}\n{msg}\n")
        except Exception:
            pass
        try:
            messagebox.showerror("RedditResearcher — Crash", msg[:800])
        except Exception:
            pass
