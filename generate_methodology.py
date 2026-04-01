"""
generate_methodology.py
========================
FAIR INCLUSIVE AV -- Project 101250721 (EURO-MEI)
Produces methodology_proposal.pdf: methodology proposal for the feasibility
study of a gender pay gap calculator in the European audiovisual sector.

Requirements: reportlab (pip install reportlab)
Fonts: Helvetica, Courier (built-in only). No Unicode special characters.
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, Image
)

# ---------------------------------------------------------------------------
# COLOUR PALETTE (identical to codebook.pdf)
# ---------------------------------------------------------------------------
DARK_BG   = colors.HexColor("#1A2340")
MID_BG    = colors.HexColor("#2E4080")
ACCENT    = colors.HexColor("#E8A020")
LIGHT_ROW = colors.HexColor("#F0F4FF")
WHITE     = colors.white
TEXT_DARK = colors.HexColor("#1A1A2E")
MUTED     = colors.HexColor("#5A6A8A")
BORDER    = colors.HexColor("#3A5080")

PAGE_W, PAGE_H = A4
LM = 2.0 * cm
RM = 2.0 * cm
TM = 2.2 * cm
BM = 2.2 * cm
AVAIL = PAGE_W - LM - RM

PROJECT_FOOTER = (
    "FAIR INCLUSIVE AV  |  Project 101250721 (EURO-MEI)  |  "
    "Methodology Proposal  |  April 2026"
)

# ---------------------------------------------------------------------------
# PAGE TEMPLATE
# ---------------------------------------------------------------------------

def page_template(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(MID_BG)
    canvas.setLineWidth(0.8)
    canvas.line(LM, 1.5 * cm, PAGE_W - RM, 1.5 * cm)
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(MUTED)
    canvas.drawString(LM, 1.1 * cm, PROJECT_FOOTER)
    canvas.drawRightString(
        PAGE_W - RM, 1.1 * cm, f"Page {canvas._pageNumber}"
    )
    canvas.restoreState()


# ---------------------------------------------------------------------------
# STYLE HELPERS
# ---------------------------------------------------------------------------

def H(text, level=0):
    if level == 0:
        s = ParagraphStyle(
            "H0", fontName="Helvetica-Bold", fontSize=11,
            textColor=WHITE, backColor=DARK_BG,
            spaceAfter=5, spaceBefore=10,
            leftIndent=5, rightIndent=5, leading=16,
        )
    elif level == 1:
        s = ParagraphStyle(
            "H1", fontName="Helvetica-Bold", fontSize=9.5,
            textColor=WHITE, backColor=MID_BG,
            spaceAfter=4, spaceBefore=8,
            leftIndent=4, rightIndent=4, leading=14,
        )
    else:
        s = ParagraphStyle(
            "H2", fontName="Helvetica-Bold", fontSize=9,
            textColor=MID_BG, spaceAfter=2, spaceBefore=6, leading=13,
        )
    return Paragraph(text, s)


BODY = ParagraphStyle(
    "Body", fontName="Helvetica", fontSize=8.5,
    textColor=TEXT_DARK, leading=12, spaceAfter=4,
)
NOTE = ParagraphStyle(
    "Note", fontName="Helvetica-Oblique", fontSize=7.8,
    textColor=MUTED, leading=11, spaceAfter=2, leftIndent=6,
)
CELL = ParagraphStyle(
    "Cell", fontName="Helvetica", fontSize=7.8,
    textColor=TEXT_DARK, leading=10,
)
CELL_B = ParagraphStyle(
    "CellB", fontName="Helvetica-Bold", fontSize=7.8,
    textColor=TEXT_DARK, leading=10,
)
CELL_H = ParagraphStyle(
    "CellH", fontName="Helvetica-Bold", fontSize=8,
    textColor=WHITE, leading=11,
)
SCENARIO_TITLE = ParagraphStyle(
    "ScTitle", fontName="Helvetica-Bold", fontSize=8.5,
    textColor=WHITE, leading=12,
)
SCENARIO_BODY = ParagraphStyle(
    "ScBody", fontName="Helvetica", fontSize=7.8,
    textColor=WHITE, leading=11,
)
SCENARIO_B_BG = colors.HexColor("#3A5080")


def P(text, style=None):
    return Paragraph(text, style or BODY)


def SP(h=0.25):
    return Spacer(1, h * cm)


def HR():
    return HRFlowable(width="100%", thickness=0.6, color=MID_BG, spaceAfter=4)


def bordered_table(rows, col_widths, header_rows=1):
    """Standard bordered table with dark header row(s)."""
    def to_para(cell, i):
        if isinstance(cell, str):
            return Paragraph(cell, CELL_H if i < header_rows else CELL)
        return cell

    data = [[to_para(c, i) for c in row] for i, row in enumerate(rows)]

    style = TableStyle([
        ("BACKGROUND",    (0, 0), (-1, header_rows - 1), DARK_BG),
        ("ROWBACKGROUNDS",(0, header_rows), (-1, -1), [WHITE, LIGHT_ROW]),
        ("GRID",          (0, 0), (-1, -1), 0.5, BORDER),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 5),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 5),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ])
    return Table(data, colWidths=col_widths, style=style, repeatRows=header_rows)


def scenario_box(title, body_paras, bg_color):
    """A coloured scenario box rendered as a 1-cell table."""
    content = [Paragraph(title, SCENARIO_TITLE), Spacer(1, 0.15 * cm)]
    for para in body_paras:
        content.append(Paragraph(para, SCENARIO_BODY))
    inner = Table([[c] for c in content],
                  colWidths=[AVAIL / 2 - 0.4 * cm],
                  style=TableStyle([
                      ("LEFTPADDING",  (0, 0), (-1, -1), 0),
                      ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                      ("TOPPADDING",   (0, 0), (-1, -1), 0),
                      ("BOTTOMPADDING",(0, 0), (-1, -1), 2),
                  ]))
    outer = Table([[inner]],
                  colWidths=[AVAIL / 2 - 0.2 * cm],
                  style=TableStyle([
                      ("BACKGROUND",    (0, 0), (0, 0), bg_color),
                      ("LEFTPADDING",   (0, 0), (0, 0), 6),
                      ("RIGHTPADDING",  (0, 0), (0, 0), 6),
                      ("TOPPADDING",    (0, 0), (0, 0), 6),
                      ("BOTTOMPADDING", (0, 0), (0, 0), 6),
                      ("BOX",           (0, 0), (0, 0), 0.8, BORDER),
                  ]))
    return outer


# ---------------------------------------------------------------------------
# DOCUMENT BUILD
# ---------------------------------------------------------------------------

def build_document(output_path="methodology_proposal.pdf"):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=LM, rightMargin=RM,
        topMargin=TM, bottomMargin=BM,
        title="Methodology Proposal -- FAIR INCLUSIVE AV",
        author="Independent expert -- FAIR INCLUSIVE AV application",
        subject="Feasibility study for a gender pay gap calculator in the "
                "European audiovisual sector",
    )

    story = []

    # ------------------------------------------------------------------ HEADER
    title_style = ParagraphStyle(
        "DocTitle", fontName="Helvetica-Bold", fontSize=14,
        textColor=WHITE, backColor=DARK_BG,
        spaceAfter=0, spaceBefore=0,
        leftIndent=8, rightIndent=8, leading=20, alignment=1,
    )
    sub_style = ParagraphStyle(
        "DocSub", fontName="Helvetica", fontSize=9,
        textColor=LIGHT_ROW, backColor=DARK_BG,
        leading=13, alignment=1, leftIndent=8, rightIndent=8,
        spaceAfter=0,
    )
    accent_style = ParagraphStyle(
        "DocAccent", fontName="Helvetica-Bold", fontSize=8.5,
        textColor=ACCENT, backColor=DARK_BG,
        leading=13, alignment=1, leftIndent=8, rightIndent=8,
        spaceAfter=0,
    )
    meta_style = ParagraphStyle(
        "DocMeta", fontName="Helvetica-Oblique", fontSize=8,
        textColor=LIGHT_ROW, backColor=DARK_BG,
        leading=12, alignment=1, leftIndent=8, rightIndent=8,
        spaceAfter=6,
    )

    story.append(Paragraph(
        "Methodology Proposal: Feasibility Study for a Gender Pay Gap "
        "Calculator in the European Audiovisual Sector",
        title_style
    ))
    story.append(Paragraph(
        "Submitted in response to EURO-MEI Call for Applications, "
        "Project 101250721 -- FAIR INCLUSIVE AV",
        sub_style
    ))
    story.append(Paragraph("April 2026", accent_style))
    story.append(Paragraph(
        "Independent expert in social impact data systems and EU-funded "
        "programme evaluation.",
        meta_style
    ))
    story.append(Paragraph(
        "This proposal is accompanied by a working prototype built on a "
        "693-contract simulated AV sector dataset, including Oaxaca-Blinder "
        "decomposition and MNAR bias analysis.",
        accent_style
    ))
    story.append(SP(0.4))

    # -------------------------------------------- SECTION 1: CONTEXT
    story.append(H("1.  Context and Problem Framing", level=0))
    story.append(SP(0.15))
    story.append(P(
        "The EU Pay Transparency Directive 2023/970 introduces mandatory gender "
        "pay gap reporting obligations that will transform employer accountability "
        "across the European economy. However, its core architecture (employer-"
        "level reporting, annual reference period, coverage threshold of 100 or "
        "more employees) is structurally incompatible with the European audiovisual "
        "sector. The AV sector operates through project-based, multi-employer "
        "contracts in which a single professional may work for four to eight distinct "
        "production companies in a single year, under varying roles and contract types. "
        "The majority of AV workers are legally self-employed or on short-term fixed-"
        "term engagements, placing them outside the SES-derived reference framework "
        "that underpins the Directive's reporting logic."
    ))
    story.append(P(
        "Pay transparency in the AV sector is not primarily a compliance challenge. "
        "It is a collective bargaining capacity challenge. Without structured, "
        "comparable pay data disaggregated by role, production type, and contract "
        "form, trade unions cannot negotiate evidence-based rate cards, freelance "
        "professionals cannot assess whether their fees reflect market norms or "
        "gender-based discrimination, and policy makers cannot enforce the spirit "
        "of the Directive in a sector defined by fragmented employment relations "
        "and structural opacity. The FAIR INCLUSIVE AV project is an opportunity "
        "to design a sector-specific transparency instrument that addresses this "
        "gap directly."
    ))
    story.append(P(
        "Existing pay equity tools cannot be directly adapted to these conditions. "
        "Logib (the Swiss federal methodology endorsed by several EU member states) "
        "is designed for employer-level analysis of permanently employed staff and "
        "assumes a single employer managing a stable workforce. The UK GPG reporting "
        "service and the Austrian Equal Pay Tool share the same architectural "
        "assumption: a single employer, a fixed workforce, and an annual reference "
        "period. None of these tools can aggregate contracts across multiple employers, "
        "handle worker-year FTE conversions from short-term engagements, or accommodate "
        "project-based contract structures. The FAIR INCLUSIVE AV calculator is "
        "therefore purpose-built for sector-specific conditions, not an extension of "
        "any existing tool."
    ))
    story.append(P(
        "Note: Streaming platforms (Netflix, Amazon, Apple TV+) are significant AV "
        "commissioners in FR and IE and are subject to national collective agreements "
        "in those countries; while not the primary focus of Phase 1 fieldwork, their "
        "commissioning relationships with production companies fall within scope of "
        "the data mapping exercise.",
        NOTE
    ))

    # ----------------------------------------- SECTION 2: RESEARCH QUESTIONS
    story.append(H("2.  Research Questions", level=0))
    story.append(SP(0.15))
    rq_rows = [
        [Paragraph("<b>RQ1</b>", CELL),
         Paragraph(
             "What remuneration data currently exists in the European audiovisual "
             "sector, who controls it, and under what conditions can it be "
             "collected and shared for the purpose of a gender pay gap analysis?",
             CELL)],
        [Paragraph("<b>RQ2</b>", CELL),
         Paragraph(
             "Can a comparable unit of analysis be defined across productions, "
             "countries, and contract types that yields a statistically meaningful "
             "and policy-relevant gender pay gap estimate consistent with the "
             "pay definition of Directive Art. 3.c?",
             CELL)],
        [Paragraph("<b>RQ3</b>", CELL),
         Paragraph(
             "Can a calculator be made operationally useful for trade unions and "
             "professional associations as a collective bargaining instrument, "
             "or are alternative transparency strategies (pay reporting frameworks, "
             "union survey toolkits, policy recommendations) required?",
             CELL)],
    ]
    rq_table = Table(
        rq_rows, colWidths=[1.3 * cm, AVAIL - 1.3 * cm],
        style=TableStyle([
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [WHITE, LIGHT_ROW]),
            ("GRID",           (0, 0), (-1, -1), 0.5, BORDER),
            ("VALIGN",         (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING",    (0, 0), (-1, -1), 6),
            ("RIGHTPADDING",   (0, 0), (-1, -1), 6),
            ("TOPPADDING",     (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING",  (0, 0), (-1, -1), 5),
        ])
    )
    story.append(rq_table)

    # ----------------------------------- SECTION 3: CALCULATOR AS UNION INFRA
    story.append(H("3.  The Calculator as Union Infrastructure", level=0))
    story.append(SP(0.15))
    story.append(P(
        "A calculator designed solely to assist employers in meeting Directive Art. 9 "
        "reporting obligations would have limited strategic value for EURO-MEI. The "
        "policy objective of this project is a calculator that builds collective "
        "bargaining capacity: one that provides role-level, production-type, and "
        "contract-type disaggregated pay gap indicators that trade unions and "
        "professional associations can deploy as evidence in negotiations, advocacy "
        "campaigns, and European Commission policy dialogue. "
        "Primary beneficiaries are trade unions and professional associations "
        "(FIA, FIM, Ver.di, IADT, EWA, Collectif 50/50), who will use disaggregated "
        "pay gap indicators as evidence in rate card negotiations, collective agreement "
        "advocacy, and European Commission policy dialogue on Directive Art. 24 "
        "transposition. Public funding bodies and employers committed to best practice "
        "also benefit as pay transparency becomes a compliance and reputational signal "
        "across the sector."
    ))

    # ----------------------------------------- SECTION 4: METHODOLOGY PHASES
    story.append(H("4.  Methodology: Four Phases", level=0))
    story.append(SP(0.15))
    phase_rows = [
        ["Phase", "Key activities", "Timeline", "Outputs"],
        [
            Paragraph("<b>Phase 1</b>\nDesk research", CELL),
            "Systematic mapping of Eurostat SES coverage gaps; CNC France "
            "pay data review; EAO Yearbook analysis; collective agreement "
            "inventory for ES, FR, DE, IE.",
            "Months 1-3",
            "Annotated inventory of existing data sources, access conditions, "
            "and coverage gaps by country."
        ],
        [
            Paragraph("<b>Phase 2</b>\nStakeholder\nconsultations", CELL),
            "Expert group meeting Brussels April 2026; structured interviews "
            "with FIA, FIM, Ver.di, IADT; bilateral meetings with national "
            "film funds; Berlin steering group February 2027.",
            "Months 3-10",
            "Stakeholder needs assessment; data access agreements in principle; "
            "validated role taxonomy draft."
        ],
        [
            Paragraph("<b>Phase 3</b>\nData mapping\nand governance", CELL),
            "Structured inventory of data held by project partners and "
            "associated film funds; GDPR compliance review with EURO-MEI DPO; "
            "data governance framework including k-anonymity protocol.",
            "Months 6-12",
            "Data availability matrix; GDPR-compliant governance protocol; "
            "go / no-go decision for Scenario A or B."
        ],
        [
            Paragraph("<b>Phase 4</b>\nIterative\nprototype", CELL),
            "Calculator development (Scenario A) or alternative strategy "
            "document (Scenario B); testing with steering group; user "
            "testing with union partners; final presentation Berlin "
            "February 2028.",
            "Months 12-24",
            "Calculator plus implementation guide (Scenario A) OR pay "
            "reporting framework, union toolkit, policy recommendation "
            "document (Scenario B)."
        ],
    ]
    story.append(bordered_table(
        phase_rows,
        col_widths=[AVAIL * 0.14, AVAIL * 0.43, AVAIL * 0.15, AVAIL * 0.28]
    ))

    # --------------------------------- SECTION 5: FEASIBILITY SCENARIOS
    story.append(H("5.  Feasibility Scenarios", level=0))
    story.append(SP(0.15))
    story.append(P(
        "Both scenarios produce deliverables of direct policy value; "
        "Scenario B advances the collective bargaining capacity objective "
        "through alternative outputs of equivalent strategic weight."
    ))
    story.append(SP(0.1))

    # Scenario A content
    sc_a_title = "Scenario A: Calculator Viable"
    sc_a_body = [
        "<b>Conditions required:</b>",
        "- Common worker identifier available (union membership number, "
        "national social security number, or AV guild registration ID).",
        "- Pay data accessible for publicly funded productions (via Art. 24 "
        "transposition or film fund data sharing agreement).",
        "- Harmonised role taxonomy agreed across ES, FR, DE, and IE.",
        "- Minimum 50 contracts per role x gender x country (consistent with "
        "Logib minimum cell-size recommendations and required for 80% power "
        "to detect a 10-percentage-point gap at p < 0.05).",
        "",
        "<b>Deliverables:</b>",
        "- Sector-specific GPG calculator aggregating contracts to worker-"
        "year FTE (Eurostat SES 220-day reference).",
        "- Implementation guide for unions, film funds, and professional "
        "associations.",
    ]

    # Scenario B content
    sc_b_title = "Scenario B: Calculator Not Viable"
    sc_b_body = [
        "<b>Conditions triggering this scenario:</b>",
        "- Data fragmentation too severe for cross-employer linkage.",
        "- GDPR constraints prevent cross-border identifier matching.",
        "- Role taxonomy cannot be harmonised within project timeline.",
        "",
        "<b>Alternative deliverables:</b>",
        "- (1) Standardised pay reporting template for publicly funded "
        "productions (Art. 24 transposition tool).",
        "- (2) Union survey toolkit: validated instrument and analysis "
        "template for EURO-MEI member surveys.",
        "- (3) Policy recommendation to adapt Art. 9.1 threshold for the "
        "AV sector, submitted to EC Art. 31 review (2028).",
    ]

    box_a = scenario_box(sc_a_title, sc_a_body, DARK_BG)
    box_b = scenario_box(sc_b_title, sc_b_body, SCENARIO_B_BG)

    scenario_table = Table(
        [[box_a, box_b]],
        colWidths=[AVAIL / 2, AVAIL / 2],
        style=TableStyle([
            ("LEFTPADDING",  (0, 0), (-1, -1), 3),
            ("RIGHTPADDING", (0, 0), (-1, -1), 3),
            ("TOPPADDING",   (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 0),
            ("VALIGN",       (0, 0), (-1, -1), "TOP"),
        ])
    )
    story.append(scenario_table)

    # ------------------------------------------- SECTION 6: RISK REGISTER
    story.append(H("6.  Risk Register", level=0))
    story.append(SP(0.15))
    risk_rows = [
        ["Risk", "Likelihood", "Mitigation strategy"],
        [
            "Data fragmentation: key pay data held by multiple disconnected "
            "parties (film funds, social security, production companies) "
            "with no shared identifier.",
            "High",
            "Begin with four partner countries (ES, FR, DE, IE) where direct "
            "interlocutors exist; treat CNC France as lead data partner; "
            "Scenario B provides viable exit if full linkage is not achievable."
        ],
        [
            "Sector resistance to reporting: production companies and "
            "individual professionals may refuse to disclose pay data.",
            "Medium",
            "Design minimum-input tool requiring only role, daily rate, and "
            "contract type; frame participation as competitive advantage for "
            "talent access; pilot with film funds before sector-wide rollout."
        ],
        [
            "GDPR constraints on data linkage: cross-border transfer of "
            "worker-level pay data requires legal basis that may not be "
            "available across all partner countries.",
            "Medium-High",
            "Work with aggregated production-level data where possible; "
            "consult EURO-MEI DPO before tool architecture decisions; apply "
            "k-anonymity k >= 5 at role x production_type x country level "
            "before any data publication or sharing."
        ],
        [
            "Cross-country comparability: different contract type taxonomies "
            "and collective agreement structures may prevent cross-national "
            "gap estimates.",
            "Medium",
            "Adopt Directive Art. 3.a 'pay' definition as project standard; "
            "develop a minimum 8-role harmonised taxonomy as Phase 2 output "
            "before data collection begins."
        ],
    ]
    story.append(bordered_table(
        risk_rows,
        col_widths=[AVAIL * 0.35, AVAIL * 0.14, AVAIL * 0.51]
    ))

    # --------------------------------------- SECTION 7: PROOF OF CONCEPT
    story.append(H("7.  Technical Proof of Concept", level=0))
    story.append(SP(0.15))
    story.append(P(
        "As a proof of concept accompanying this application, the applicant has "
        "developed a prototype gender pay gap calculator using a simulated European "
        "audiovisual sector dataset (693 contracts, 230 workers, 65 productions, "
        "22 variables, random seed 42). The prototype implements Eurostat-aligned "
        "metrics (unadjusted and adjusted gender pay gap, pay quartile distribution "
        "per Directive Art. 9.1.f, gap by category of workers per Art. 9.1.g) "
        "together with OLS regression for the adjusted gap (controlling for role, "
        "seniority, experience, production type, contract type, and country) and a "
        "simplified Oaxaca-Blinder decomposition consistent with the Logib "
        "methodology. Key finding from the prototype: 14.1% of the total pay gap "
        "is unexplained by structural characteristics (the Art. 10 joint pay "
        "assessment proxy) while the remaining gap is attributable to occupational "
        "segregation and seniority differentials. The prototype also demonstrates "
        "that MNAR (Missing Not At Random) bias in pay reporting for women in "
        "low-paid roles leads to underestimation of the true gap, a methodological "
        "consideration that must be addressed in any real-data implementation. "
        "The full dataset, Python analysis notebook (gpg_analysis.ipynb), and "
        "data codebook are available on request."
    ))
    story.append(SP(0.15))

    # Inline figures (optional enhancement) --------------------------------
    _base = os.path.dirname(os.path.abspath(__file__))
    _fig_ranked  = os.path.join(_base, "figures", "fig5e_gpg_by_role_ranked.png")
    _fig_oaxaca  = os.path.join(_base, "figures", "fig3_oaxaca_blinder.png")
    _img_w = (AVAIL - 0.4 * cm) / 2          # each half of available width

    if os.path.exists(_fig_ranked) and os.path.exists(_fig_oaxaca):
        _caption_style = ParagraphStyle(
            "FigCaption", fontName="Helvetica-Oblique", fontSize=7,
            textColor=MUTED, leading=10, spaceAfter=2, alignment=1,
        )
        _cell_style = TableStyle([
            ("LEFTPADDING",   (0, 0), (-1, -1), 3),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 3),
            ("TOPPADDING",    (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ])
        _fig_left  = [Image(_fig_ranked, width=_img_w, height=_img_w * 0.65),
                      Paragraph(
                          "Figure: Unadjusted GPG by role (prototype dataset, n=693).",
                          _caption_style)]
        _fig_right = [Image(_fig_oaxaca,  width=_img_w, height=_img_w * 0.65),
                      Paragraph(
                          "Figure: Oaxaca-Blinder decomposition -- explained vs. "
                          "unexplained pay gap components.",
                          _caption_style)]
        _fig_table = Table(
            [[_fig_left[0], _fig_right[0]],
             [_fig_left[1], _fig_right[1]]],
            colWidths=[_img_w + 0.2 * cm, _img_w + 0.2 * cm],
            style=_cell_style,
        )
        story.append(_fig_table)
        story.append(SP(0.15))

    story.append(SP(0.1))
    story.append(HR())
    story.append(SP(0.1))
    story.append(P(
        "This methodology proposal is submitted as part of the FAIR INCLUSIVE AV "
        "application process. All prototype data are synthetic. No confidential or "
        "personal data have been used in the development of the proof-of-concept "
        "materials accompanying this application.",
        NOTE
    ))

    # ------------------------------------------------------------------ BUILD
    doc.build(
        story,
        onFirstPage=page_template,
        onLaterPages=page_template,
    )
    print(f"Generated: {output_path}")


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    out = "methodology_proposal.pdf"
    build_document(out)
    size_kb = os.path.getsize(out) / 1024
    print(f"File size: {size_kb:.0f} KB")
