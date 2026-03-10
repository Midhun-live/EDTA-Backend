from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_assessment_pdf(assessment, user=None):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    
    if "Bold" not in styles:
        styles.add(ParagraphStyle(name="Bold", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=11, spaceAfter=4, spaceBefore=4))
    if "CardTitle" not in styles:
        styles.add(ParagraphStyle(name="CardTitle", parent=styles["Heading2"], fontSize=13, spaceAfter=8, textColor=colors.HexColor("#2C3E50")))
    if "Bullet" not in styles:
        styles.add(ParagraphStyle(name="Bullet", parent=styles["Normal"], fontSize=10, leftIndent=10, spaceAfter=3))
        
    elements = []

    # Title & Subtitle
    elements.append(Paragraph("Equipment Recommendation Report", styles["Title"]))
    title_sub = ParagraphStyle(name="SubTitle", parent=styles["Heading2"], alignment=1, textColor=colors.HexColor("#6C757D"))
    elements.append(Paragraph("Eldersmiles Discharge Triage Assessment", title_sub))
    elements.append(Spacer(1, 25))

    # Patient Summary (3-Column Layout)
    patient = assessment.patient if assessment.patient else {}
    p_name = patient.get("name", "Unknown")
    p_age = patient.get("age", "Unknown")
    p_date = patient.get("discharge_date", "Unknown")

    summary_data = [
        [
            Paragraph("<b>Patient Name:</b><br/>" + str(p_name), styles["Normal"]),
            Paragraph("<b>Age:</b><br/>" + str(p_age), styles["Normal"]),
            Paragraph("<b>Discharge Date:</b><br/>" + str(p_date), styles["Normal"])
        ]
    ]
    
    col_width_summary = 523 / 3.0
    summary_table = Table(summary_data, colWidths=[col_width_summary]*3)
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8F9FA")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#E9ECEF")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('PADDING', (0, 0), (-1, -1), 12),
    ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 25))

    # Assessment Categories in Specific Order
    categories = [
        "mobility",
        "feeding",
        "elimination",
        "respiratory",
        "pressure_injury",
        "wound_care",
        "home_environment",
        "cognitive"
    ]

    output_data = assessment.output_data if assessment.output_data else {}
    
    cards = []

    for cat in categories:
        if cat in output_data:
            section = output_data[cat]
            if not isinstance(section, dict):
                continue

            card_elements = []
            # Section Title
            card_elements.append(Paragraph(cat.replace("_", " ").title(), styles["CardTitle"]))
            
            # Equipment List
            equipment = section.get("equipment")
            if equipment and isinstance(equipment, list) and len(equipment) > 0:
                card_elements.append(Paragraph("Equipment:", styles["Bold"]))
                for item in equipment:
                    # Clean the string for raw arrays if generated incorrectly
                    item_str = str(item).replace("[", "").replace("]", "").replace("'", "")
                    card_elements.append(Paragraph(f"• {item_str}", styles["Bullet"]))
            
            # Care Instructions
            instructions = section.get("care_instructions")
            if instructions:
                card_elements.append(Paragraph("Care Instructions:", styles["Bold"]))
                card_elements.append(Paragraph(str(instructions), styles["Normal"]))
            
            # Only append if we actually extracted equipment or instructions
            if len(card_elements) > 1:
                cards.append(card_elements)

    # Group cards into pairs for 2-column layout Grid
    table_data = []
    for i in range(0, len(cards), 2):
        row = []
        row.append(cards[i])
        if i + 1 < len(cards):
            row.append(cards[i+1])
        else:
            row.append([]) # Empty cell to balance the last row
        table_data.append(row)
        
    if table_data:
        col_width_cards = 523 / 2.0
        cards_table = Table(table_data, colWidths=[col_width_cards, col_width_cards])
        cards_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('PADDING', (0, 0), (-1, -1), 12),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#DEE2E6")),
            ('INNERGRID', (0, 0), (-1, -1), 1, colors.HexColor("#DEE2E6")),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FFFFFF")),
        ]))
        elements.append(cards_table)

    doc.build(elements)
    buffer.seek(0)
    return buffer.read()
