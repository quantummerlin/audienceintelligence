from fpdf import FPDF
import os

class ReceiptPDF(FPDF):
    def header(self):
        pass
    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(160, 160, 160)
        self.cell(0, 10, "audienceintelligence.com  |  Delivered within 24 hours", align="C")

pdf = ReceiptPDF()
pdf.add_page()
pdf.set_margins(25, 25, 25)

# Top accent bar
pdf.set_fill_color(37, 99, 235)   # blue-600
pdf.rect(0, 0, 210, 6, "F")

pdf.ln(14)

# Logo / brand name
pdf.set_font("Helvetica", "B", 22)
pdf.set_text_color(37, 99, 235)
pdf.cell(0, 12, "Audience Intelligence", align="C", new_x="LMARGIN", new_y="NEXT")

pdf.set_font("Helvetica", "", 11)
pdf.set_text_color(100, 100, 100)
pdf.cell(0, 8, "What your comments really say", align="C", new_x="LMARGIN", new_y="NEXT")

pdf.ln(10)

# Divider
pdf.set_draw_color(220, 220, 220)
pdf.set_line_width(0.5)
pdf.line(25, pdf.get_y(), 185, pdf.get_y())
pdf.ln(10)

# Thank-you heading
pdf.set_font("Helvetica", "B", 18)
pdf.set_text_color(20, 20, 20)
pdf.cell(0, 10, "Thank you for your order!", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.ln(4)

# Sub-message
pdf.set_font("Helvetica", "", 12)
pdf.set_text_color(60, 60, 60)
pdf.multi_cell(
    0, 7,
    "Your Audience Intelligence Report is being prepared.\n"
    "Fill out your brief so we know which post to analyse.",
    align="C",
)
pdf.ln(6)

# Brief link CTA box
pdf.set_fill_color(219, 234, 254)   # blue-100
pdf.set_draw_color(96, 165, 250)    # blue-400
pdf.set_line_width(0.6)
cta_x, cta_y = 35, pdf.get_y()
pdf.rect(cta_x, cta_y, 140, 20, "FD")
pdf.set_xy(cta_x, cta_y + 3)
pdf.set_font("Helvetica", "B", 12)
pdf.set_text_color(30, 64, 175)
pdf.cell(140, 7, "Fill out your brief here:", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.set_xy(cta_x, cta_y + 11)
pdf.set_font("Helvetica", "", 11)
pdf.set_text_color(37, 99, 235)
pdf.cell(140, 7, "ai.quantummerlin.com/brief.html", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.ln(10)

# Info box
pdf.set_fill_color(239, 246, 255)   # blue-50
pdf.set_draw_color(191, 219, 254)   # blue-200
pdf.set_line_width(0.4)
pdf.round_corner_rect = None       # not needed

x, y = 25, pdf.get_y()
pdf.rect(x, y, 160, 52, "FD")

pdf.set_xy(x + 8, y + 7)
pdf.set_font("Helvetica", "B", 11)
pdf.set_text_color(30, 64, 175)    # blue-800
pdf.cell(144, 7, "What happens next?", new_x="LMARGIN", new_y="NEXT")

pdf.set_xy(x + 8, y + 17)
pdf.set_font("Helvetica", "", 10)
pdf.set_text_color(55, 65, 81)

steps = [
    "1.  Fill out your brief at ai.quantummerlin.com/brief.html",
    "2.  We scrape and analyse every comment on your post.",
    "3.  We compile a plain-English PDF report just for you.",
    "4.  Your report lands in your inbox within 24 hours.",
]
for step in steps:
    pdf.set_xy(x + 8, pdf.get_y())
    pdf.cell(144, 7, step, new_x="LMARGIN", new_y="NEXT")

pdf.ln(14)

# Deliverables
pdf.set_font("Helvetica", "B", 12)
pdf.set_text_color(20, 20, 20)
pdf.cell(0, 8, "Your report includes:", new_x="LMARGIN", new_y="NEXT")
pdf.ln(2)

pdf.set_font("Helvetica", "", 11)
pdf.set_text_color(60, 60, 60)
deliverables = [
    ">>  Top themes & topics driving the conversation",
    ">>  Sentiment breakdown (positive / negative / neutral)",
    ">>  Most-engaged comments and power users",
    ">>  Key questions & objections from your audience",
    ">>  Plain-English summary with actionable insights",
]
for d in deliverables:
    pdf.cell(0, 8, d, new_x="LMARGIN", new_y="NEXT")

pdf.ln(10)

# CTA
pdf.set_font("Helvetica", "I", 10)
pdf.set_text_color(130, 130, 130)
pdf.multi_cell(
    0, 7,
    "Questions? Email us at ai@quantummerlin.com\n"
    "and we'll get back to you quickly.",
    align="C",
)

# Bottom accent bar
pdf.set_fill_color(37, 99, 235)
pdf.rect(0, 291, 210, 6, "F")

out_path = os.path.join("outputs", "audience_intelligence_receipt.pdf")
pdf.output(out_path)
print(f"PDF saved to: {out_path}")
