"""
===============================================================
🌱 KISHAN SATHI – PDF Report Generator
Uses ReportLab to build professional crop analysis reports
===============================================================
"""

import os
import io
import logging
from datetime import datetime

from django.conf import settings

logger = logging.getLogger('apps.reports')


# ──────────────────────────────────────────────────────────────
# 🎨 BRAND COLORS
# ──────────────────────────────────────────────────────────────
GREEN_DARK   = (0.10, 0.24, 0.16)   # #1a3d28
GREEN_MID    = (0.16, 0.58, 0.40)   # #289466
GREEN_LIGHT  = (0.88, 0.97, 0.91)   # #e0f7e8
AMBER        = (0.91, 0.63, 0.13)   # #e8a020
RED          = (0.89, 0.25, 0.25)   # #e24040
WHITE        = (1, 1, 1)
GREY_DARK    = (0.20, 0.20, 0.20)
GREY_MID     = (0.45, 0.45, 0.45)
GREY_LIGHT   = (0.93, 0.93, 0.93)


def generate_single_analysis_pdf(user, crop_image, result) -> bytes:
    """
    Generate a single-analysis PDF report.
    Returns raw PDF bytes — caller saves to disk or serves inline.
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import cm, mm
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table,
            TableStyle, HRFlowable, Image as RLImage,
        )
        from reportlab.graphics.shapes import Drawing, Rect, String
        from reportlab.graphics import renderPDF
    except ImportError:
        logger.error("ReportLab not installed. Run: pip install reportlab")
        raise

    buffer = io.BytesIO()
    PAGE_W, PAGE_H = A4

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.8*cm,
        leftMargin=1.8*cm,
        topMargin=1.5*cm,
        bottomMargin=2*cm,
        title=f"Kishan Sathi – Crop Analysis Report",
        author="Kishan Sathi AI Platform",
    )

    rl_green_dark  = colors.Color(*GREEN_DARK)
    rl_green_mid   = colors.Color(*GREEN_MID)
    rl_green_light = colors.Color(*GREEN_LIGHT)
    rl_amber       = colors.Color(*AMBER)
    rl_red         = colors.Color(*RED)
    rl_grey_dark   = colors.Color(*GREY_DARK)
    rl_grey_mid    = colors.Color(*GREY_MID)
    rl_grey_light  = colors.Color(*GREY_LIGHT)

    styles = getSampleStyleSheet()

    # ── Custom Styles ──────────────────────────────────────────
    def style(name, **kwargs):
        return ParagraphStyle(name, **kwargs)

    s_title = style('Title',
        fontName='Helvetica-Bold', fontSize=20,
        textColor=WHITE, alignment=TA_CENTER, spaceAfter=2)
    s_sub   = style('Sub',
        fontName='Helvetica', fontSize=10,
        textColor=colors.Color(0.8, 0.95, 0.85), alignment=TA_CENTER)
    s_section = style('Section',
        fontName='Helvetica-Bold', fontSize=12,
        textColor=rl_green_dark, spaceBefore=10, spaceAfter=6,
        borderPad=(0, 0, 4, 0))
    s_label = style('Label',
        fontName='Helvetica-Bold', fontSize=9,
        textColor=rl_grey_mid)
    s_value = style('Value',
        fontName='Helvetica', fontSize=10,
        textColor=rl_grey_dark, spaceAfter=4)
    s_body  = style('Body',
        fontName='Helvetica', fontSize=9.5,
        textColor=rl_grey_dark, leading=14, spaceAfter=6)
    s_small = style('Small',
        fontName='Helvetica', fontSize=8,
        textColor=rl_grey_mid)
    s_footer = style('Footer',
        fontName='Helvetica', fontSize=8,
        textColor=rl_grey_mid, alignment=TA_CENTER)

    story = []

    # ─────────────────────────────────────────────────────────
    # 1) HEADER BANNER
    # ─────────────────────────────────────────────────────────
    header_data = [[
        Paragraph("🌱 KISHAN SATHI", s_title),
    ]]
    header_table = Table(header_data, colWidths=[PAGE_W - 3.6*cm])
    header_table.setStyle(TableStyle([
        ('BACKGROUND',  (0,0), (-1,-1), rl_green_dark),
        ('TOPPADDING',  (0,0), (-1,-1), 18),
        ('BOTTOMPADDING',(0,0),(-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 20),
        ('RIGHTPADDING',(0,0), (-1,-1), 20),
        ('ROUNDEDCORNERS', [8]),
    ]))
    story.append(header_table)

    sub_data = [[Paragraph("AI Crop Disease Detection Platform  |  Crop Analysis Report", s_sub)]]
    sub_table = Table(sub_data, colWidths=[PAGE_W - 3.6*cm])
    sub_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), rl_green_mid),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING',(0,0),(-1,-1), 10),
    ]))
    story.append(sub_table)
    story.append(Spacer(1, 16))

    # ─────────────────────────────────────────────────────────
    # 2) REPORT META INFO
    # ─────────────────────────────────────────────────────────
    now = datetime.now().strftime("%d %B %Y, %I:%M %p")
    meta_data = [
        [Paragraph("<b>Report Generated:</b>", s_label),
         Paragraph(now, s_value),
         Paragraph("<b>Farmer Name:</b>", s_label),
         Paragraph(user.get_full_name() or user.username, s_value)],
        [Paragraph("<b>Report ID:</b>", s_label),
         Paragraph(str(crop_image.id)[:12] + "...", s_value),
         Paragraph("<b>Email:</b>", s_label),
         Paragraph(user.email, s_value)],
        [Paragraph("<b>Crop Type:</b>", s_label),
         Paragraph(crop_image.get_crop_type_display(), s_value),
         Paragraph("<b>State:</b>", s_label),
         Paragraph(user.state or "—", s_value)],
    ]
    meta_table = Table(meta_data, colWidths=[3.5*cm, 7*cm, 3.5*cm, 5.5*cm])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,-1), rl_green_light),
        ('BOX',           (0,0), (-1,-1), 0.5, rl_green_mid),
        ('INNERGRID',     (0,0), (-1,-1), 0.25, colors.Color(0.7, 0.87, 0.77)),
        ('TOPPADDING',    (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING',   (0,0), (-1,-1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 18))

    # ─────────────────────────────────────────────────────────
    # 3) DISEASE RESULT BANNER
    # ─────────────────────────────────────────────────────────
    is_healthy   = result.is_healthy
    banner_color = rl_green_mid if is_healthy else rl_red
    status_text  = "✅ HEALTHY CROP" if is_healthy else f"⚠️ DISEASE DETECTED"
    conf_text    = f"Confidence: {result.confidence_score:.1f}%"

    result_style = style('ResultBanner',
        fontName='Helvetica-Bold', fontSize=16,
        textColor=WHITE, alignment=TA_CENTER)
    conf_style   = style('ConfBanner',
        fontName='Helvetica', fontSize=11,
        textColor=WHITE, alignment=TA_CENTER)

    banner_data = [
        [Paragraph(status_text, result_style)],
        [Paragraph(conf_text,   conf_style)],
    ]
    banner_table = Table(banner_data, colWidths=[PAGE_W - 3.6*cm])
    banner_table.setStyle(TableStyle([
        ('BACKGROUND',   (0,0), (-1,-1), banner_color),
        ('TOPPADDING',   (0,0), (-1,-1), 12),
        ('BOTTOMPADDING',(0,0), (-1,-1), 12),
        ('ROUNDEDCORNERS', [6]),
    ]))
    story.append(banner_table)
    story.append(Spacer(1, 16))

    # ─────────────────────────────────────────────────────────
    # 4) DIAGNOSIS DETAILS
    # ─────────────────────────────────────────────────────────
    story.append(Paragraph("📋 Diagnosis Details", s_section))
    story.append(HRFlowable(width="100%", thickness=1, color=rl_green_mid, spaceAfter=8))

    diag_data = [
        ["Disease Name",    result.disease_name,
         "Scientific Name", result.scientific_name or "—"],
        ["Severity",        result.get_severity_display(),
         "Confidence",      f"{result.confidence_score:.1f}%"],
        ["Analyzed At",     result.analyzed_at.strftime("%d %b %Y, %I:%M %p"),
         "Model Version",   result.model_version],
    ]

    severity_colors = {
        'none': rl_green_mid, 'low': rl_green_mid,
        'moderate': rl_amber, 'high': rl_red, 'critical': rl_red
    }
    sev_color = severity_colors.get(result.severity, rl_amber)

    diag_table = Table(diag_data, colWidths=[3.5*cm, 6.5*cm, 3.5*cm, 6*cm])
    diag_table.setStyle(TableStyle([
        ('FONTNAME',      (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME',      (2,0), (2,-1), 'Helvetica-Bold'),
        ('FONTSIZE',      (0,0), (-1,-1), 9),
        ('TEXTCOLOR',     (0,0), (0,-1), rl_grey_mid),
        ('TEXTCOLOR',     (2,0), (2,-1), rl_grey_mid),
        ('BACKGROUND',    (0,0), (-1,-1), colors.white),
        ('ROWBACKGROUNDS',(0,0), (-1,-1), [colors.white, rl_grey_light]),
        ('BOX',           (0,0), (-1,-1), 0.5, rl_green_mid),
        ('INNERGRID',     (0,0), (-1,-1), 0.25, rl_grey_light),
        ('TOPPADDING',    (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('LEFTPADDING',   (0,0), (-1,-1), 8),
    ]))
    story.append(diag_table)
    story.append(Spacer(1, 16))

    # ─────────────────────────────────────────────────────────
    # 5) UPLOADED IMAGE (if accessible)
    # ─────────────────────────────────────────────────────────
    try:
        img_path = crop_image.image.path
        if os.path.exists(img_path):
            story.append(Paragraph("🖼️ Analyzed Crop Image", s_section))
            story.append(HRFlowable(width="100%", thickness=1, color=rl_green_mid, spaceAfter=8))
            rl_img = RLImage(img_path, width=8*cm, height=6*cm, kind='proportional')
            img_table = Table([[rl_img]], colWidths=[PAGE_W - 3.6*cm])
            img_table.setStyle(TableStyle([
                ('ALIGN',   (0,0), (-1,-1), 'CENTER'),
                ('BOX',     (0,0), (-1,-1), 0.5, rl_green_mid),
                ('TOPPADDING',    (0,0), (-1,-1), 8),
                ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ]))
            story.append(img_table)
            story.append(Spacer(1, 14))
    except Exception:
        pass  # Skip image silently if unavailable

    # ─────────────────────────────────────────────────────────
    # 6) DESCRIPTION & SYMPTOMS
    # ─────────────────────────────────────────────────────────
    def section_block(title, content):
        story.append(Paragraph(title, s_section))
        story.append(HRFlowable(width="100%", thickness=1, color=rl_green_mid, spaceAfter=6))
        story.append(Paragraph(content or "No information available.", s_body))
        story.append(Spacer(1, 10))

    section_block("🔬 About This Disease",       result.description)
    section_block("🌿 Observable Symptoms",      result.symptoms)
    section_block("🦠 Causal Agent",             result.cause)

    # ─────────────────────────────────────────────────────────
    # 7) TREATMENT RECOMMENDATIONS
    # ─────────────────────────────────────────────────────────
    story.append(Paragraph("💊 Treatment Recommendations", s_section))
    story.append(HRFlowable(width="100%", thickness=1, color=rl_green_mid, spaceAfter=6))

    treat_data = [
        [Paragraph("<b>🧪 Chemical Treatment</b>", s_label),
         Paragraph(result.chemical_treatment or "Not required.", s_body)],
        [Paragraph("<b>🌿 Organic Treatment</b>", s_label),
         Paragraph(result.organic_treatment or "Not required.", s_body)],
        [Paragraph("<b>🛡️ Preventive Measures</b>", s_label),
         Paragraph(result.preventive_measures or "Continue regular monitoring.", s_body)],
    ]
    treat_table = Table(treat_data, colWidths=[4.5*cm, PAGE_W - 3.6*cm - 4.5*cm])
    treat_table.setStyle(TableStyle([
        ('VALIGN',        (0,0), (-1,-1), 'TOP'),
        ('ROWBACKGROUNDS',(0,0), (-1,-1), [rl_green_light, colors.white, rl_green_light]),
        ('BOX',           (0,0), (-1,-1), 0.5, rl_green_mid),
        ('INNERGRID',     (0,0), (-1,-1), 0.25, rl_grey_light),
        ('TOPPADDING',    (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING',   (0,0), (-1,-1), 8),
    ]))
    story.append(treat_table)
    story.append(Spacer(1, 16))

    # ─────────────────────────────────────────────────────────
    # 8) ALTERNATIVE PREDICTIONS TABLE
    # ─────────────────────────────────────────────────────────
    alts = result.alternative_predictions
    if alts:
        story.append(Paragraph("📊 Alternative Predictions", s_section))
        story.append(HRFlowable(width="100%", thickness=1, color=rl_green_mid, spaceAfter=6))

        alt_rows = [[
            Paragraph("<b>Disease</b>", s_label),
            Paragraph("<b>Confidence</b>", s_label),
        ]]
        for alt in alts:
            alt_rows.append([
                Paragraph(str(alt.get('disease', '—')), s_body),
                Paragraph(f"{alt.get('confidence', 0):.1f}%", s_body),
            ])

        alt_table = Table(alt_rows, colWidths=[12*cm, 4*cm])
        alt_table.setStyle(TableStyle([
            ('BACKGROUND',    (0,0), (-1,0), rl_green_dark),
            ('TEXTCOLOR',     (0,0), (-1,0), WHITE),
            ('ROWBACKGROUNDS',(0,1), (-1,-1), [colors.white, rl_grey_light]),
            ('BOX',           (0,0), (-1,-1), 0.5, rl_green_mid),
            ('INNERGRID',     (0,0), (-1,-1), 0.25, rl_grey_light),
            ('TOPPADDING',    (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING',   (0,0), (-1,-1), 8),
        ]))
        story.append(alt_table)
        story.append(Spacer(1, 16))

    # ─────────────────────────────────────────────────────────
    # 9) DISCLAIMER & FOOTER
    # ─────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=rl_grey_light, spaceBefore=10))
    disclaimer = (
        "<b>Disclaimer:</b> This report is generated by an AI model and is intended as a "
        "decision-support tool only. Always consult a qualified agricultural officer or "
        "agronomist before applying any pesticide or treatment."
    )
    story.append(Paragraph(disclaimer, s_small))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        f"© {datetime.now().year} Kishan Sathi | AI Crop Disease Detection Platform | "
        "kishansathi.in",
        s_footer
    ))

    # ─────────────────────────────────────────────────────────
    # BUILD PDF
    # ─────────────────────────────────────────────────────────
    doc.build(story)
    buffer.seek(0)
    return buffer.read()


def generate_summary_pdf(user, crop_images, period_label="Last 30 Days") -> bytes:
    """
    Generate a summary PDF with multiple analyses.
    Returns raw PDF bytes.
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import cm
        from reportlab.lib import colors
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.enums import TA_CENTER
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table,
            TableStyle, HRFlowable,
        )
    except ImportError:
        raise

    buffer = io.BytesIO()
    PAGE_W, _ = A4
    rl_green_dark  = colors.Color(*GREEN_DARK)
    rl_green_mid   = colors.Color(*GREEN_MID)
    rl_green_light = colors.Color(*GREEN_LIGHT)
    rl_grey_light  = colors.Color(*GREY_LIGHT)
    WHITE_c        = colors.Color(*WHITE)

    doc = SimpleDocTemplate(buffer, pagesize=A4,
        rightMargin=1.8*cm, leftMargin=1.8*cm,
        topMargin=1.5*cm, bottomMargin=2*cm)

    s_title   = ParagraphStyle('T', fontName='Helvetica-Bold', fontSize=18, textColor=WHITE_c, alignment=TA_CENTER)
    s_section = ParagraphStyle('S', fontName='Helvetica-Bold', fontSize=11, textColor=rl_green_dark, spaceBefore=10, spaceAfter=6)
    s_label   = ParagraphStyle('L', fontName='Helvetica-Bold', fontSize=9,  textColor=colors.Color(*GREY_MID))
    s_body    = ParagraphStyle('B', fontName='Helvetica',      fontSize=9,  textColor=colors.Color(*GREY_DARK))
    s_footer  = ParagraphStyle('F', fontName='Helvetica',      fontSize=8,  textColor=colors.Color(*GREY_MID), alignment=TA_CENTER)

    story = []

    # Header
    hdr = Table([[Paragraph("🌱 KISHAN SATHI — Summary Report", s_title)]],
                colWidths=[PAGE_W - 3.6*cm])
    hdr.setStyle(TableStyle([
        ('BACKGROUND',   (0,0),(-1,-1), rl_green_dark),
        ('TOPPADDING',   (0,0),(-1,-1), 16),
        ('BOTTOMPADDING',(0,0),(-1,-1), 16),
    ]))
    story.append(hdr)
    story.append(Spacer(1, 12))

    # Summary stats
    total    = len(crop_images)
    healthy  = sum(1 for c in crop_images if c.has_result and c.result.is_healthy)
    diseased = total - healthy

    stats_data = [
        [Paragraph("<b>Farmer</b>", s_label),   Paragraph(user.get_full_name() or user.username, s_body),
         Paragraph("<b>Period</b>", s_label),    Paragraph(period_label, s_body)],
        [Paragraph("<b>Total Analyses</b>", s_label), Paragraph(str(total), s_body),
         Paragraph("<b>Healthy / Disease</b>", s_label), Paragraph(f"{healthy} / {diseased}", s_body)],
    ]
    stats_table = Table(stats_data, colWidths=[3.5*cm, 7*cm, 3.5*cm, 5.5*cm])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND',   (0,0),(-1,-1), rl_green_light),
        ('BOX',          (0,0),(-1,-1), 0.5, rl_green_mid),
        ('INNERGRID',    (0,0),(-1,-1), 0.25, colors.Color(0.7, 0.87, 0.77)),
        ('TOPPADDING',   (0,0),(-1,-1), 6),
        ('BOTTOMPADDING',(0,0),(-1,-1), 6),
        ('LEFTPADDING',  (0,0),(-1,-1), 8),
    ]))
    story.append(stats_table)
    story.append(Spacer(1, 16))

    # Analyses table
    story.append(Paragraph("📋 All Analyses", s_section))
    story.append(HRFlowable(width="100%", thickness=1, color=rl_green_mid, spaceAfter=6))

    rows = [[
        Paragraph("<b>#</b>",          s_label),
        Paragraph("<b>Crop</b>",       s_label),
        Paragraph("<b>Disease</b>",    s_label),
        Paragraph("<b>Confidence</b>", s_label),
        Paragraph("<b>Date</b>",       s_label),
        Paragraph("<b>Status</b>",     s_label),
    ]]
    for i, ci in enumerate(crop_images, 1):
        res = ci.result if ci.has_result else None
        rows.append([
            Paragraph(str(i), s_body),
            Paragraph(ci.get_crop_type_display(), s_body),
            Paragraph(res.disease_name if res else "Pending", s_body),
            Paragraph(f"{res.confidence_score:.1f}%" if res else "—", s_body),
            Paragraph(ci.uploaded_at.strftime("%d %b %Y"), s_body),
            Paragraph("Healthy" if (res and res.is_healthy) else "Disease", s_body),
        ])

    tbl = Table(rows, colWidths=[1*cm, 3*cm, 6*cm, 2.5*cm, 3*cm, 2*cm])
    tbl.setStyle(TableStyle([
        ('BACKGROUND',    (0,0),(-1,0), rl_green_dark),
        ('TEXTCOLOR',     (0,0),(-1,0), WHITE_c),
        ('ROWBACKGROUNDS',(0,1),(-1,-1), [colors.white, rl_grey_light]),
        ('BOX',           (0,0),(-1,-1), 0.5, rl_green_mid),
        ('INNERGRID',     (0,0),(-1,-1), 0.25, rl_grey_light),
        ('TOPPADDING',    (0,0),(-1,-1), 5),
        ('BOTTOMPADDING', (0,0),(-1,-1), 5),
        ('LEFTPADDING',   (0,0),(-1,-1), 6),
        ('FONTSIZE',      (0,0),(-1,-1), 8),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 20))

    story.append(HRFlowable(width="100%", thickness=0.5, color=rl_grey_light))
    story.append(Paragraph(
        f"© {datetime.now().year} Kishan Sathi AI Platform | kishansathi.in",
        s_footer
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()
