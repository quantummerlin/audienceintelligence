"""
Social Media Downloader — Desktop GUI
Double-click to run, or: python downloader_gui.py
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fb_video_downloader.downloader import FacebookVideoDownloader, PLATFORM_PATTERNS
import re as _re

def detect_platform(url):
    for pattern, name in PLATFORM_PATTERNS:
        if _re.search(pattern, url, _re.IGNORECASE):
            return name
    return "Unknown"

# ── Colours matching the brand ───────────────────────────────────────────────
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
FONT      = ("Inter", 10) if sys.platform == "win32" else ("Helvetica", 10)
FONT_BOLD = ("Inter", 10, "bold") if sys.platform == "win32" else ("Helvetica", 10, "bold")
FONT_BIG  = ("Inter", 13, "bold") if sys.platform == "win32" else ("Helvetica", 13, "bold")
FONT_SM   = ("Inter", 8) if sys.platform == "win32" else ("Helvetica", 8)


def styled_button(parent, text, command, accent=False, danger=False, **kw):
    bg = PRIMARY if accent else (DANGER if danger else CARD)
    fg = "#ffffff"
    btn = tk.Button(
        parent, text=text, command=command,
        bg=bg, fg=fg, activebackground=ACCENT, activeforeground="#000",
        relief="flat", borderwidth=0, padx=14, pady=7,
        font=FONT_BOLD, cursor="hand2", **kw
    )
    btn.bind("<Enter>", lambda e: btn.config(bg=ACCENT if accent else (DANGER if danger else BORDER)))
    btn.bind("<Leave>", lambda e: btn.config(bg=bg))
    return btn


def entry(parent, textvariable=None, show=None, width=40, **kw):
    return tk.Entry(
        parent, textvariable=textvariable, show=show,
        bg=SURFACE, fg=TEXT, insertbackground=ACCENT,
        relief="flat", borderwidth=0, highlightthickness=1,
        highlightbackground=BORDER, highlightcolor=PRIMARY,
        font=FONT, width=width, **kw
    )


def label(parent, text, muted=False, heading=False, **kw):
    fg = MUTED if muted else (HEADING if heading else TEXT)
    f = FONT_BIG if heading else FONT
    return tk.Label(parent, text=text, bg=BG, fg=fg, font=f, **kw)


def section_frame(parent):
    f = tk.Frame(parent, bg=CARD, relief="flat", bd=0,
                 highlightthickness=1, highlightbackground=BORDER)
    return f


class DownloaderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Social Media Downloader")
        self.configure(bg=BG)
        self.resizable(True, True)
        self.minsize(580, 640)

        # ── Variables ──────────────────────────────────────────────────────
        self.url_var       = tk.StringVar()
        self.mode_var      = tk.StringVar(value="video")
        self.quality_var   = tk.StringVar(value="best")
        self.filename_var  = tk.StringVar()
        self.browser_var   = tk.StringVar(value="none")
        self.embed_art_var = tk.BooleanVar(value=False)
        self.subtitles_var = tk.BooleanVar(value=False)
        self.output_dir    = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
        self._dl_thread    = None
        self._downloader   = None

        self._build_ui()
        self._center_window(620, 720)

    # ── Layout ──────────────────────────────────────────────────────────────

    def _build_ui(self):
        pad = dict(padx=18, pady=8)

        # Header
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=20, pady=(22, 4))
        tk.Label(hdr, text="⬇  Social Media Downloader", bg=BG, fg=HEADING,
                 font=FONT_BIG).pack(side="left")

        # ── URL ──────────────────────────────────────────────────────────
        url_frame = section_frame(self)
        url_frame.pack(fill="x", padx=18, pady=(6, 4))
        tk.Label(url_frame, text="URL", bg=CARD, fg=MUTED,
                 font=FONT_SM).pack(anchor="w", padx=14, pady=(10, 2))
        row = tk.Frame(url_frame, bg=CARD)
        row.pack(fill="x", padx=14, pady=(0, 12))
        url_entry = entry(row, textvariable=self.url_var, width=52)
        url_entry.pack(side="left", fill="x", expand=True, ipady=5)
        url_entry.bind("<FocusIn>", lambda e: self._detect_platform())
        url_entry.bind("<KeyRelease>", lambda e: self._detect_platform())
        self.platform_lbl = tk.Label(row, text="", bg=CARD, fg=ACCENT,
                                     font=FONT_SM, width=12)
        self.platform_lbl.pack(side="left", padx=(8, 0))

        paste_btn = styled_button(row, "Paste", self._paste_url)
        paste_btn.pack(side="left", padx=(6, 0))

        # ── Mode ─────────────────────────────────────────────────────────
        mode_frame = section_frame(self)
        mode_frame.pack(fill="x", padx=18, pady=4)
        tk.Label(mode_frame, text="Mode", bg=CARD, fg=MUTED,
                 font=FONT_SM).pack(anchor="w", padx=14, pady=(10, 4))
        mode_row = tk.Frame(mode_frame, bg=CARD)
        mode_row.pack(fill="x", padx=14, pady=(0, 12))

        for val, lbl_text, emoji in [
            ("video",     "Video (MP4)",     "🎬"),
            ("audio",     "Audio (MP3)",     "🎵"),
            ("thumbnail", "Thumbnail (IMG)", "🖼"),
        ]:
            rb = tk.Radiobutton(
                mode_row, text=f"{emoji}  {lbl_text}",
                variable=self.mode_var, value=val,
                command=self._on_mode_change,
                bg=CARD, fg=TEXT, selectcolor=SURFACE,
                activebackground=CARD, activeforeground=ACCENT,
                font=FONT, indicatoron=False,
                relief="flat", borderwidth=0,
                highlightthickness=1, highlightbackground=BORDER,
                padx=14, pady=7, cursor="hand2"
            )
            rb.pack(side="left", padx=(0, 8))
            self._style_radio(rb, val)

        # ── Options ──────────────────────────────────────────────────────
        self.options_frame = section_frame(self)
        self.options_frame.pack(fill="x", padx=18, pady=4)
        tk.Label(self.options_frame, text="Options", bg=CARD, fg=MUTED,
                 font=FONT_SM).pack(anchor="w", padx=14, pady=(10, 4))

        opts_inner = tk.Frame(self.options_frame, bg=CARD)
        opts_inner.pack(fill="x", padx=14, pady=(0, 12))

        # Quality
        qual_row = tk.Frame(opts_inner, bg=CARD)
        qual_row.pack(fill="x", pady=(0, 8))
        tk.Label(qual_row, text="Quality", bg=CARD, fg=TEXT,
                 font=FONT, width=14, anchor="w").pack(side="left")
        self.quality_cb = ttk.Combobox(
            qual_row, textvariable=self.quality_var,
            values=["best", "1080", "720", "480", "360", "worst"],
            state="readonly", width=12, font=FONT
        )
        self.quality_cb.pack(side="left")
        self._style_combobox(self.quality_cb)

        # Filename
        fn_row = tk.Frame(opts_inner, bg=CARD)
        fn_row.pack(fill="x", pady=(0, 8))
        tk.Label(fn_row, text="Filename", bg=CARD, fg=TEXT,
                 font=FONT, width=14, anchor="w").pack(side="left")
        entry(fn_row, textvariable=self.filename_var, width=32).pack(
            side="left", fill="x", expand=True, ipady=4)
        tk.Label(fn_row, text="  (leave blank for default)", bg=CARD,
                 fg=MUTED, font=FONT_SM).pack(side="left")

        # Browser cookies
        browser_row = tk.Frame(opts_inner, bg=CARD)
        browser_row.pack(fill="x", pady=(0, 8))
        tk.Label(browser_row, text="Browser cookies", bg=CARD, fg=TEXT,
                 font=FONT, width=14, anchor="w").pack(side="left")
        self.browser_cb = ttk.Combobox(
            browser_row, textvariable=self.browser_var,
            values=["none", "chrome", "firefox", "edge", "safari"],
            state="readonly", width=12, font=FONT
        )
        self.browser_cb.pack(side="left")
        self._style_combobox(self.browser_cb)
        tk.Label(browser_row, text="  (for private/login-required videos)", bg=CARD,
                 fg=MUTED, font=FONT_SM).pack(side="left")

        # Checkboxes
        chk_row = tk.Frame(opts_inner, bg=CARD)
        chk_row.pack(fill="x", pady=(0, 4))

        self.embed_chk = tk.Checkbutton(
            chk_row, text="Embed thumbnail as album art",
            variable=self.embed_art_var,
            bg=CARD, fg=TEXT, selectcolor=SURFACE,
            activebackground=CARD, font=FONT
        )
        self.embed_chk.pack(side="left", padx=(0, 20))

        self.subs_chk = tk.Checkbutton(
            chk_row, text="Download subtitles",
            variable=self.subtitles_var,
            bg=CARD, fg=TEXT, selectcolor=SURFACE,
            activebackground=CARD, font=FONT
        )
        self.subs_chk.pack(side="left")

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

        # ── Progress ─────────────────────────────────────────────────────
        prog_frame = section_frame(self)
        prog_frame.pack(fill="x", padx=18, pady=4)

        prog_inner = tk.Frame(prog_frame, bg=CARD)
        prog_inner.pack(fill="x", padx=14, pady=12)

        pb_row = tk.Frame(prog_inner, bg=CARD)
        pb_row.pack(fill="x", pady=(0, 6))
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            pb_row, variable=self.progress_var,
            maximum=100, mode="determinate", length=400
        )
        self.progress_bar.pack(side="left", fill="x", expand=True)
        self.pct_lbl = tk.Label(pb_row, text="0%", bg=CARD, fg=MUTED,
                                font=FONT_SM, width=5)
        self.pct_lbl.pack(side="left", padx=(8, 0))

        self.status_lbl = tk.Label(prog_inner, text="Ready", bg=CARD,
                                   fg=MUTED, font=FONT_SM, anchor="w")
        self.status_lbl.pack(anchor="w")

        # ── Buttons ──────────────────────────────────────────────────────
        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(fill="x", padx=18, pady=(8, 4))

        self.download_btn = styled_button(
            btn_row, "⬇  Download", self._start_download, accent=True
        )
        self.download_btn.pack(side="left")

        self.stop_btn = styled_button(
            btn_row, "■  Stop", self._stop_download, danger=True
        )
        self.stop_btn.pack(side="left", padx=(8, 0))
        self.stop_btn.config(state="disabled")

        styled_button(btn_row, "📂  Open folder", self._open_folder).pack(
            side="left", padx=(8, 0))

        self.open_file_btn = styled_button(
            btn_row, "▶  Play / Open", self._open_last_file)
        self.open_file_btn.pack(side="left", padx=(8, 0))
        self.open_file_btn.config(state="disabled")

        # ── Log ──────────────────────────────────────────────────────────
        log_frame = section_frame(self)
        log_frame.pack(fill="both", expand=True, padx=18, pady=(4, 18))
        tk.Label(log_frame, text="Log", bg=CARD, fg=MUTED,
                 font=FONT_SM).pack(anchor="w", padx=14, pady=(8, 2))
        log_inner = tk.Frame(log_frame, bg=CARD)
        log_inner.pack(fill="both", expand=True, padx=14, pady=(0, 12))
        self.log_text = tk.Text(
            log_inner, bg=SURFACE, fg=TEXT, insertbackground=ACCENT,
            relief="flat", borderwidth=0, font=("Consolas", 8),
            wrap="word", height=8, state="disabled"
        )
        scroll = ttk.Scrollbar(log_inner, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scroll.set)
        self.log_text.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self._last_file = None
        self._on_mode_change()

    # ── Helpers ─────────────────────────────────────────────────────────────

    def _center_window(self, w, h):
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _style_radio(self, rb, val):
        def refresh(*_):
            if self.mode_var.get() == val:
                rb.config(fg=ACCENT, highlightbackground=PRIMARY)
            else:
                rb.config(fg=TEXT, highlightbackground=BORDER)
        self.mode_var.trace_add("write", refresh)
        refresh()

    def _style_combobox(self, cb):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TCombobox",
                         fieldbackground=SURFACE, background=CARD,
                         foreground=TEXT, selectbackground=PRIMARY,
                         selectforeground="#fff", bordercolor=BORDER)
        style.map("TCombobox", fieldbackground=[("readonly", SURFACE)],
                  foreground=[("readonly", TEXT)])
        style.configure("TProgressbar", troughcolor=SURFACE,
                         background=PRIMARY, thickness=8)

    def _log(self, msg, colour=None):
        self.log_text.config(state="normal")
        self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def _set_status(self, msg, colour=MUTED):
        self.status_lbl.config(text=msg, fg=colour)

    def _detect_platform(self):
        url = self.url_var.get().strip()
        if url:
            plat = detect_platform(url)
            self.platform_lbl.config(text=plat if plat != "Unknown" else "")
        else:
            self.platform_lbl.config(text="")

    def _on_mode_change(self):
        mode = self.mode_var.get()
        is_audio = mode == "audio"
        is_video = mode == "video"
        self.quality_cb.config(state="readonly" if is_video else "disabled")
        self.embed_chk.config(state="normal" if (is_audio or is_video) else "disabled")
        self.subs_chk.config(state="normal" if is_video else "disabled")

    def _paste_url(self):
        try:
            text = self.clipboard_get()
            self.url_var.set(text.strip())
            self._detect_platform()
        except tk.TclError:
            pass

    def _choose_dir(self):
        d = filedialog.askdirectory(initialdir=self.output_dir)
        if d:
            self.output_dir = d
            self.dir_lbl.config(text=d)

    def _open_folder(self):
        os.makedirs(self.output_dir, exist_ok=True)
        os.startfile(self.output_dir)

    def _open_last_file(self):
        if not self._last_file:
            return
        # The file might have been converted (e.g. m4a → mp3) after the hook fired
        target = self._last_file
        if not os.path.exists(target):
            base = os.path.splitext(target)[0]
            for ext in ('mp3', 'mp4', 'm4a', 'webm', 'mkv'):
                candidate = f"{base}.{ext}"
                if os.path.exists(candidate):
                    target = candidate
                    break
        if os.path.exists(target):
            os.startfile(target)

    # ── Download ────────────────────────────────────────────────────────────

    def _start_download(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("No URL", "Please paste a URL first.")
            return
        if not url.startswith("http"):
            messagebox.showwarning("Invalid URL", "URL must start with http:// or https://")
            return
        if self._dl_thread and self._dl_thread.is_alive():
            return

        self.download_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.open_file_btn.config(state="disabled")
        self.progress_var.set(0)
        self.pct_lbl.config(text="0%")
        self._set_status("Starting…", ACCENT)
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.config(state="disabled")
        self._last_file = None

        self._dl_thread = threading.Thread(target=self._download_worker, daemon=True)
        self._dl_thread.start()

    def _stop_download(self):
        if self._downloader:
            try:
                self._downloader._ydl_opts_stop = True
            except Exception:
                pass
        self._set_status("Stopping…", WARN)

    def _download_worker(self):
        url   = self.url_var.get().strip()
        mode  = self.mode_var.get()
        fname = self.filename_var.get().strip() or None

        chrome_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "chrome_profile"
        )
        chrome_dir = chrome_dir if os.path.isdir(chrome_dir) else None

        browser_choice = self.browser_var.get()
        cookies_from_browser = browser_choice if browser_choice != "none" else None

        def on_progress(d):
            if d.get("status") == "downloading":
                total   = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
                downloaded = d.get("downloaded_bytes", 0)
                speed   = d.get("speed") or 0
                eta     = d.get("eta") or 0
                pct = (downloaded / total * 100) if total else 0

                speed_str = f"{speed/1024/1024:.1f} MB/s" if speed > 0 else ""
                eta_str   = f"ETA {eta}s" if eta > 0 else ""
                status    = "  ".join(filter(None, [speed_str, eta_str]))

                self.after(0, lambda p=pct, s=status: self._update_progress(p, s))

            elif d.get("status") == "finished":
                self.after(0, lambda: self._update_progress(99, "Processing…"))

        try:
            self._downloader = FacebookVideoDownloader(
                output_dir=self.output_dir,
                quality=self.quality_var.get() if mode == "video" else "best",
                audio_only=(mode == "audio"),
                thumbnail_only=(mode == "thumbnail"),
                subtitles=self.subtitles_var.get() and mode == "video",
                embed_thumbnail=self.embed_art_var.get(),
                filename_template=fname,
                chrome_profile_dir=chrome_dir,
                cookies_from_browser=cookies_from_browser,
                progress_callback=on_progress,
            )

            self.after(0, lambda: self._log(f"→ Downloading: {url}"))
            result = self._downloader.download(url)

            if result.success:
                self._last_file = result.filename or None
                dur = ""
                if result.duration_seconds:
                    m, s = divmod(int(result.duration_seconds), 60)
                    dur = f"  Duration: {m}m {s:02d}s"

                self.after(0, lambda: (
                    self._update_progress(100, "Done!"),
                    self._log(f"✓ {result.title or 'Done'}"),
                    self._log(f"  Platform : {result.platform}"),
                    self._log(f"  File     : {os.path.basename(result.filename or '')}"),
                    self._log(dur) if dur else None,
                    self._set_status("Download complete ✓", SUCCESS),
                    self.open_file_btn.config(state="normal"),
                ))
            else:
                err = result.error or "Unknown error"
                self.after(0, lambda e=err: (
                    self._log(f"✗ Error: {e}"),
                    self._set_status("Failed", DANGER),
                    self._update_progress(0, ""),
                ))

        except Exception as exc:
            msg = str(exc)
            self.after(0, lambda m=msg: (
                self._log(f"✗ {m}"),
                self._set_status("Error", DANGER),
                self._update_progress(0, ""),
            ))
        finally:
            self._downloader = None
            self.after(0, lambda: (
                self.download_btn.config(state="normal"),
                self.stop_btn.config(state="disabled"),
            ))

    def _update_progress(self, pct, status_msg):
        self.progress_var.set(pct)
        self.pct_lbl.config(text=f"{int(pct)}%")
        if status_msg:
            self._set_status(status_msg, ACCENT if pct < 100 else SUCCESS)


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = DownloaderApp()
    app.mainloop()
