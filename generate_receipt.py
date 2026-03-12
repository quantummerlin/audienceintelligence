from fpdf import FPDF
import os

BRIEF_URL = "https://ai.quantummerlin.com/brief.html"
EMAIL_URL = "mailto:ai@quantummerlin.com"

# ── Dark-theme palette (matches website) ──
BG       = (10, 14, 26)       # --clr-bg   #0a0e1a
SURFACE  = (17, 24, 39)       # --clr-card #111827
BORDER   = (31, 41, 55)       # --clr-border
INDIGO   = (129, 140, 248)    # --clr-primary #818cf8
CYAN     = (34, 211, 238)     # #22d3ee
HEADING  = (243, 244, 246)    # --clr-heading
TEXT     = (209, 213, 219)    # --clr-text
MUTED    = (107, 114, 128)    # --clr-muted
ACCENT_BAR = (99, 102, 241)   # #6366f1


class ReceiptPDF(FPDF):
    def header(self):
        # Full-page dark background
        self.set_fill_color(*BG)
        self.rect(0, 0, 210, 297, "F")

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*MUTED)
        self.cell(0, 10, "ai.quantummerlin.com  |  Delivered within 24 hours", align="C")


pdf = ReceiptPDF()
pdf.add_page()
pdf.set_margins(25, 25, 25)

# ── Top accent gradient bar ──
pdf.set_fill_color(*ACCENT_BAR)
pdf.rect(0, 0, 210, 4, "F")
pdf.set_fill_color(*CYAN)
pdf.rect(0, 4, 210, 2, "F")

pdf.ln(16)

# ── Brand name ──
pdf.set_font("Helvetica", "B", 24)
pdf.set_text_color(*INDIGO)
pdf.cell(0, 12, "Audience Intelligence", align="C", new_x="LMARGIN", new_y="NEXT")

pdf.set_font("Helvetica", "", 11)
pdf.set_text_color(*MUTED)
pdf.cell(0, 8, "What your comments really say", align="C", new_x="LMARGIN", new_y="NEXT")

pdf.ln(8)

# ── Divider ──
pdf.set_draw_color(*BORDER)
pdf.set_line_width(0.4)
pdf.line(30, pdf.get_y(), 180, pdf.get_y())
pdf.ln(10)

# ── Thank-you heading ──
pdf.set_font("Helvetica", "B", 20)
pdf.set_text_color(*HEADING)
pdf.cell(0, 10, "Thank you for your order!", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.ln(4)

pdf.set_font("Helvetica", "", 12)
pdf.set_text_color(*TEXT)
pdf.multi_cell(
    0, 7,
    "Your Audience Intelligence Report is being prepared.\n"
    "Fill out your brief so we know which post to analyse.",
    align="C",
)
pdf.ln(8)

# ── CTA button (clickable) ──
btn_w, btn_h = 140, 28
btn_x = (210 - btn_w) / 2
btn_y = pdf.get_y()

# Button background
pdf.set_fill_color(*ACCENT_BAR)
pdf.rect(btn_x, btn_y, btn_w, btn_h, "F")

# Button text line 1
pdf.set_xy(btn_x, btn_y + 4)
pdf.set_font("Helvetica", "B", 13)
pdf.set_text_color(255, 255, 255)
pdf.cell(btn_w, 7, "Fill Out Your Brief", align="C", new_x="LMARGIN", new_y="NEXT")

# Button text line 2 (URL)
pdf.set_xy(btn_x, btn_y + 14)
pdf.set_font("Helvetica", "", 10)
pdf.set_text_color(199, 210, 254)   # light indigo
pdf.cell(btn_w, 7, "ai.quantummerlin.com/brief.html", align="C", new_x="LMARGIN", new_y="NEXT")

# Clickable link over button area
pdf.link(btn_x, btn_y, btn_w, btn_h, BRIEF_URL)

pdf.set_y(btn_y + btn_h + 12)

# ── What happens next (dark card) ──
pdf.set_fill_color(*SURFACE)
pdf.set_draw_color(*BORDER)
pdf.set_line_width(0.4)

x, y = 25, pdf.get_y()
pdf.rect(x, y, 160, 56, "FD")

pdf.set_xy(x + 10, y + 8)
pdf.set_font("Helvetica", "B", 12)
pdf.set_text_color(*INDIGO)
pdf.cell(140, 7, "What happens next?", new_x="LMARGIN", new_y="NEXT")

pdf.set_xy(x + 10, y + 18)
pdf.set_font("Helvetica", "", 10)
pdf.set_text_color(*TEXT)

steps = [
    "1.  Fill out your brief (link above).",
    "2.  We scrape and analyse every comment on your post.",
    "3.  We compile a plain-English PDF report just for you.",
    "4.  Your report lands in your inbox within 24 hours.",
]
for step in steps:
    pdf.set_xy(x + 10, pdf.get_y())
    pdf.cell(140, 8, step, new_x="LMARGIN", new_y="NEXT")

pdf.set_y(y + 56 + 14)

# ── Deliverables ──
pdf.set_font("Helvetica", "B", 13)
pdf.set_text_color(*HEADING)
pdf.cell(0, 8, "Your report includes:", new_x="LMARGIN", new_y="NEXT")
pdf.ln(3)

pdf.set_font("Helvetica", "", 11)
pdf.set_text_color(*TEXT)
deliverables = [
    ">>  Top themes & topics driving the conversation",
    ">>  Sentiment breakdown (positive / negative / neutral)",
    ">>  Most-engaged comments and power users",
    ">>  Key questions & objections from your audience",
    ">>  Content ideas & viral triggers",
    ">>  Lead & product opportunities",
    ">>  Plain-English summary with actionable insights",
]
for d in deliverables:
    pdf.cell(0, 8, d, new_x="LMARGIN", new_y="NEXT")

pdf.ln(12)

# ── Contact (clickable email) ──
pdf.set_font("Helvetica", "I", 10)
pdf.set_text_color(*MUTED)
pdf.cell(0, 7, "Questions? Email us at", align="C", new_x="LMARGIN", new_y="NEXT")

# Clickable email link
pdf.set_font("Helvetica", "I", 10)
pdf.set_text_color(*CYAN)
email_text = "ai@quantummerlin.com"
email_w = pdf.get_string_width(email_text)
email_x = (210 - email_w) / 2
email_y = pdf.get_y()
pdf.set_x(email_x)
pdf.cell(email_w, 7, email_text, new_x="LMARGIN", new_y="NEXT")
pdf.link(email_x, email_y, email_w, 7, EMAIL_URL)

# ── Bottom accent bar ──
pdf.set_fill_color(*CYAN)
pdf.rect(0, 293, 210, 2, "F")
pdf.set_fill_color(*ACCENT_BAR)
pdf.rect(0, 295, 210, 2, "F")

out_path = os.path.join("outputs", "audience_intelligence_receipt.pdf")
pdf.output(out_path)
print(f"PDF saved to: {out_path}")
