from fpdf import FPDF
import os

EMAIL_URL = "mailto:ai@quantummerlin.com"
BRIEF_URL = "https://ai.quantummerlin.com/brief.html"
SAMPLE_URL = "https://ai.quantummerlin.com/examples.html"

# ── Dark-theme palette (matches website) ──
BG         = (10, 14, 26)
SURFACE    = (17, 24, 39)
BORDER     = (31, 41, 55)
INDIGO     = (129, 140, 248)
INDIGO_DIM = (99, 102, 241)
CYAN       = (34, 211, 238)
HEADING    = (243, 244, 246)
TEXT       = (209, 213, 219)
MUTED      = (107, 114, 128)
WHITE      = (255, 255, 255)
GREEN      = (52, 211, 153)


class ReceiptPDF(FPDF):
    def header(self):
        self.set_fill_color(*BG)
        self.rect(0, 0, 210, 297, "F")

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "", 7)
        self.set_text_color(*MUTED)
        self.cell(0, 8, "ai.quantummerlin.com", align="C")


def draw_logo(pdf, cx, cy, size=12):
    """Draw the geometric triangle-node brand mark."""
    import math
    # Triangle vertices
    top = (cx, cy - size)
    left = (cx - size, cy + size * 0.7)
    right = (cx + size, cy + size * 0.7)
    mid = (cx, cy + size * 0.1)

    # Outer lines
    pdf.set_draw_color(*INDIGO)
    pdf.set_line_width(0.8)
    pdf.line(top[0], top[1], left[0], left[1])
    pdf.set_draw_color(*CYAN)
    pdf.line(top[0], top[1], right[0], right[1])
    pdf.set_draw_color(*INDIGO)
    pdf.set_line_width(0.6)
    pdf.line(left[0], left[1], right[0], right[1])

    # Inner lines to center
    pdf.set_line_width(0.5)
    pdf.set_draw_color(*CYAN)
    pdf.line(top[0], top[1], mid[0], mid[1])
    pdf.set_draw_color(*INDIGO)
    pdf.line(left[0], left[1], mid[0], mid[1])
    pdf.set_draw_color(*CYAN)
    pdf.line(right[0], right[1], mid[0], mid[1])

    # Nodes
    r = 2.2
    pdf.set_fill_color(*INDIGO)
    pdf.ellipse(top[0] - r, top[1] - r, r * 2, r * 2, "F")
    pdf.set_fill_color(*CYAN)
    pdf.ellipse(left[0] - r, left[1] - r, r * 2, r * 2, "F")
    pdf.set_fill_color(*INDIGO)
    pdf.ellipse(right[0] - r, right[1] - r, r * 2, r * 2, "F")
    # Center node (white, smaller)
    cr = 1.6
    pdf.set_fill_color(*WHITE)
    pdf.ellipse(mid[0] - cr, mid[1] - cr, cr * 2, cr * 2, "F")


def draw_rounded_btn(pdf, x, y, w, h, r, fill_color):
    """Draw a filled rounded rectangle using PDF drawing primitives."""
    pdf.set_fill_color(*fill_color)
    # Center rectangle
    pdf.rect(x + r, y, w - 2 * r, h, "F")
    # Left and right strips
    pdf.rect(x, y + r, r, h - 2 * r, "F")
    pdf.rect(x + w - r, y + r, r, h - 2 * r, "F")
    # Four corner circles
    for cx, cy in [(x + r, y + r), (x + w - r, y + r),
                   (x + r, y + h - r), (x + w - r, y + h - r)]:
        pdf.ellipse(cx - r, cy - r, 2 * r, 2 * r, "F")


def draw_step_number(pdf, x, y, num, color):
    """Draw a small circled number."""
    r = 4
    pdf.set_fill_color(*color)
    pdf.ellipse(x - r, y - r, r * 2, r * 2, "F")
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(*WHITE)
    pdf.set_xy(x - r, y - 3.5)
    pdf.cell(r * 2, 7, str(num), align="C")


def generate_receipt(variant="gumroad"):
    """Generate receipt PDF. variant = 'gumroad' or 'etsy'."""
    pdf = ReceiptPDF()
    pdf.add_page()
    pdf.set_margins(25, 25, 25)

    # ── Top accent bar ──
    pdf.set_fill_color(*INDIGO_DIM)
    pdf.rect(0, 0, 210, 3, "F")
    pdf.set_fill_color(*CYAN)
    pdf.rect(0, 3, 210, 1.5, "F")

    # ── Logo + Brand ──
    draw_logo(pdf, 105, 24, size=8)

    pdf.set_y(36)
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(*INDIGO)
    pdf.cell(0, 10, "Audience Intelligence", align="C", new_x="LMARGIN", new_y="NEXT")

    # ── Thin divider ──
    pdf.ln(4)
    pdf.set_draw_color(*BORDER)
    pdf.set_line_width(0.3)
    pdf.line(60, pdf.get_y(), 150, pdf.get_y())
    pdf.ln(7)

    # ── Main heading ──
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 9, "We're building your report.", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(*TEXT)
    if variant == "gumroad":
        pdf.cell(0, 7, "One quick step and we'll get started.", align="C", new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.cell(0, 7, "Send us a quick message and we'll get started.", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)

    # ── CTA BUTTON (rounded) ──
    btn_w, btn_h = 140, 26
    btn_x = (210 - btn_w) / 2
    btn_y = pdf.get_y()

    draw_rounded_btn(pdf, btn_x, btn_y, btn_w, btn_h, 5, INDIGO_DIM)

    if variant == "gumroad":
        pdf.set_xy(btn_x, btn_y + 2)
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(*WHITE)
        pdf.cell(btn_w, 7, "Fill Out Your Brief", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.set_xy(btn_x, btn_y + 13)
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(199, 210, 254)
        pdf.cell(btn_w, 6, "ai.quantummerlin.com/brief.html", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.link(btn_x, btn_y, btn_w, btn_h, BRIEF_URL)
    else:
        pdf.set_xy(btn_x, btn_y + 6)
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(*WHITE)
        pdf.cell(btn_w, 7, "Message Us on Etsy Now", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_y(btn_y + btn_h + 4)

    # Small helper text under button
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(*MUTED)
    if variant == "gumroad":
        pdf.cell(0, 5, "Takes less than 2 minutes. We start as soon as we receive it.", align="C", new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.cell(0, 5, "Just send your post URL. We start as soon as we see your message.", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)

    # ── Steps card ──
    card_x, card_y = 30, pdf.get_y()
    card_w, card_h = 150, 56
    pdf.set_fill_color(*SURFACE)
    pdf.set_draw_color(*BORDER)
    pdf.set_line_width(0.3)
    draw_rounded_btn(pdf, card_x, card_y, card_w, card_h, 4, SURFACE)
    pdf.set_draw_color(*BORDER)
    pdf.rect(card_x, card_y, card_w, card_h, "D")

    pdf.set_xy(card_x + 12, card_y + 6)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*INDIGO)
    pdf.cell(card_w - 24, 6, "How it works", new_x="LMARGIN", new_y="NEXT")

    if variant == "gumroad":
        steps = [
            "Fill out your brief with the post URL",
            "We analyse every comment using AI + human review",
            "Your PDF report arrives within 24-48 hours",
        ]
    else:
        steps = [
            "Message us on Etsy with your post URL",
            "We analyse every comment using AI + human review",
            "Your PDF report is delivered via Etsy within 24-48 hours",
        ]

    for i, step in enumerate(steps):
        sy = card_y + 18 + (i * 13)
        draw_step_number(pdf, card_x + 16, sy, i + 1, INDIGO_DIM if i % 2 == 0 else CYAN)
        pdf.set_xy(card_x + 26, sy - 3)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(*TEXT)
        pdf.cell(card_w - 38, 6, step)

    pdf.set_y(card_y + card_h + 10)

    # ── Warm closing ──
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*TEXT)
    pdf.multi_cell(0, 6,
        "Your audience has been telling you exactly what they want.\n"
        "Most people never hear it. You're about to.",
        align="C",
    )
    pdf.ln(4)

    # ── Sample report teaser ──
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*CYAN)
    teaser_text = "See what a real report looks like: ai.quantummerlin.com/examples.html"
    tw = pdf.get_string_width(teaser_text)
    tx = (210 - tw) / 2
    ty = pdf.get_y()
    pdf.set_x(tx)
    pdf.cell(tw, 6, teaser_text, new_x="LMARGIN", new_y="NEXT")
    pdf.link(tx, ty, tw, 6, SAMPLE_URL)

    pdf.ln(6)

    # ── Contact ──
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(*MUTED)
    pdf.cell(0, 6, "Questions? We're here to help.", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_text_color(*CYAN)
    email_text = "ai@quantummerlin.com"
    ew = pdf.get_string_width(email_text)
    ex = (210 - ew) / 2
    ey = pdf.get_y()
    pdf.set_x(ex)
    pdf.cell(ew, 6, email_text, new_x="LMARGIN", new_y="NEXT")
    pdf.link(ex, ey, ew, 6, EMAIL_URL)

    # ── Bottom accent bar ──
    pdf.set_fill_color(*CYAN)
    pdf.rect(0, 293.5, 210, 1.5, "F")
    pdf.set_fill_color(*INDIGO_DIM)
    pdf.rect(0, 295, 210, 2, "F")

    return pdf


# ── Generate both variants ──
os.makedirs("outputs", exist_ok=True)

gumroad_pdf = generate_receipt("gumroad")
gumroad_path = os.path.join("outputs", "audience_intelligence_receipt.pdf")
gumroad_pdf.output(gumroad_path)
print(f"Gumroad receipt saved to: {gumroad_path}")

etsy_pdf = generate_receipt("etsy")
etsy_path = os.path.join("outputs", "audience_intelligence_receipt_etsy.pdf")
etsy_pdf.output(etsy_path)
print(f"Etsy receipt saved to: {etsy_path}")
