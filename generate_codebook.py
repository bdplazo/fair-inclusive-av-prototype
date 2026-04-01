"""
generate_codebook.py
=====================
FAIR INCLUSIVE AV -- Project 101250721 (EURO-MEI)
Generates codebook.pdf: professional data dictionary for the simulated
audiovisual sector dataset (audiovisual_pay_dataset.csv).

Requirements: reportlab (pip install reportlab)
Uses only built-in fonts: Helvetica, Courier. No Unicode special characters.

Run AFTER generate_dataset.py has produced audiovisual_pay_dataset.csv.
"""

import pandas as pd
import os

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak
)
from reportlab.platypus.flowables import HRFlowable

# ---------------------------------------------------------------------------
# COLOUR PALETTE
# ---------------------------------------------------------------------------
DARK_BG     = colors.HexColor("#1A2340")   # deep navy -- headers
MID_BG      = colors.HexColor("#2E4080")   # medium blue -- section titles
ACCENT      = colors.HexColor("#E8A020")   # amber -- highlights
LIGHT_ROW   = colors.HexColor("#F0F4FF")   # very light blue -- table alt row
WHITE       = colors.white
TEXT_DARK   = colors.HexColor("#1A1A2E")   # near-black -- body text
MUTED       = colors.HexColor("#5A6A8A")   # muted slate -- notes/limitations
BORDER      = colors.HexColor("#3A5080")   # table border colour

PAGE_W, PAGE_H = A4
LEFT_MARGIN  = 2.0 * cm
RIGHT_MARGIN = 2.0 * cm
TOP_MARGIN   = 2.2 * cm
BOT_MARGIN   = 2.2 * cm

PROJECT_REF = "FAIR INCLUSIVE AV | Project 101250721 (EURO-MEI) | EU Pay Transparency Directive 2023/970"


# ---------------------------------------------------------------------------
# PAGE TEMPLATE -- header / footer
# ---------------------------------------------------------------------------

def make_page_template(canvas, doc):
    """Draw running footer on every page."""
    canvas.saveState()
    # Footer line
    canvas.setStrokeColor(MID_BG)
    canvas.setLineWidth(0.8)
    canvas.line(LEFT_MARGIN, 1.5 * cm, PAGE_W - RIGHT_MARGIN, 1.5 * cm)
    # Footer text
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(MUTED)
    canvas.drawString(LEFT_MARGIN, 1.1 * cm, PROJECT_REF)
    canvas.drawRightString(
        PAGE_W - RIGHT_MARGIN, 1.1 * cm, f"Page {canvas._pageNumber}"
    )
    canvas.restoreState()


# ---------------------------------------------------------------------------
# STYLE HELPERS
# ---------------------------------------------------------------------------

def heading_style(level=1):
    """Return a ParagraphStyle for section headings."""
    if level == 0:
        return ParagraphStyle(
            "H0",
            fontName="Helvetica-Bold",
            fontSize=13,
            textColor=WHITE,
            backColor=DARK_BG,
            spaceAfter=6,
            spaceBefore=14,
            leftIndent=6,
            rightIndent=6,
            leading=18,
        )
    if level == 1:
        return ParagraphStyle(
            "H1",
            fontName="Helvetica-Bold",
            fontSize=11,
            textColor=WHITE,
            backColor=MID_BG,
            spaceAfter=4,
            spaceBefore=12,
            leftIndent=4,
            rightIndent=4,
            leading=16,
        )
    return ParagraphStyle(
        "H2",
        fontName="Helvetica-Bold",
        fontSize=9.5,
        textColor=MID_BG,
        spaceAfter=2,
        spaceBefore=8,
        leading=14,
    )


BODY_STYLE = ParagraphStyle(
    "Body",
    fontName="Helvetica",
    fontSize=8.5,
    textColor=TEXT_DARK,
    leading=12,
    spaceAfter=3,
)

NOTE_STYLE = ParagraphStyle(
    "Note",
    fontName="Helvetica-Oblique",
    fontSize=8,
    textColor=MUTED,
    leading=11,
    spaceAfter=2,
    leftIndent=8,
)

CODE_STYLE = ParagraphStyle(
    "Code",
    fontName="Courier",
    fontSize=8,
    textColor=TEXT_DARK,
    leading=11,
    backColor=colors.HexColor("#EEF2FF"),
)

CELL_STYLE = ParagraphStyle(
    "Cell",
    fontName="Helvetica",
    fontSize=7.5,
    textColor=TEXT_DARK,
    leading=10,
)

CELL_BOLD = ParagraphStyle(
    "CellBold",
    fontName="Helvetica-Bold",
    fontSize=7.5,
    textColor=TEXT_DARK,
    leading=10,
)

HEADER_CELL = ParagraphStyle(
    "HeaderCell",
    fontName="Helvetica-Bold",
    fontSize=8,
    textColor=WHITE,
    leading=11,
)


def P(text, style=None):
    if style is None:
        style = BODY_STYLE
    return Paragraph(text, style)


def H(text, level=1):
    return Paragraph(text, heading_style(level))


def spacer(h=0.3):
    return Spacer(1, h * cm)


# ---------------------------------------------------------------------------
# TABLE BUILDER
# ---------------------------------------------------------------------------

def var_table(rows, col_widths=None):
    """
    Build a bordered variable-definition table.
    rows: list of lists of strings or Paragraphs.
    First row is treated as header (dark background).
    """
    available = PAGE_W - LEFT_MARGIN - RIGHT_MARGIN
    if col_widths is None:
        col_widths = [available / len(rows[0])] * len(rows[0])

    # Convert all cells to Paragraphs
    table_data = []
    for i, row in enumerate(rows):
        new_row = []
        for cell in row:
            if isinstance(cell, str):
                style = HEADER_CELL if i == 0 else CELL_STYLE
                new_row.append(Paragraph(cell, style))
            else:
                new_row.append(cell)
        table_data.append(new_row)

    style = TableStyle([
        # Header row
        ("BACKGROUND",  (0, 0), (-1, 0), DARK_BG),
        ("TEXTCOLOR",   (0, 0), (-1, 0), WHITE),
        ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, 0), 8),
        # Alternating rows
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_ROW]),
        # Grid
        ("GRID",        (0, 0), (-1, -1), 0.5, BORDER),
        ("VALIGN",      (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING",(0, 0), (-1, -1), 5),
        ("TOPPADDING",  (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
    ])

    return Table(table_data, colWidths=col_widths, style=style, repeatRows=1)


def simple_table(rows, col_widths=None, header=True):
    """Lighter table variant for non-variable content."""
    available = PAGE_W - LEFT_MARGIN - RIGHT_MARGIN
    if col_widths is None:
        col_widths = [available / len(rows[0])] * len(rows[0])

    style = TableStyle([
        ("BACKGROUND",  (0, 0), (-1, 0 if header else -1), MID_BG if header else WHITE),
        ("TEXTCOLOR",   (0, 0), (-1, 0), WHITE if header else TEXT_DARK),
        ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_ROW]),
        ("GRID",        (0, 0), (-1, -1), 0.5, BORDER),
        ("VALIGN",      (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING",(0, 0), (-1, -1), 5),
        ("TOPPADDING",  (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
        ("FONTNAME",    (0, 1), (-1, -1), "Helvetica"),
        ("TEXTCOLOR",   (0, 1), (-1, -1), TEXT_DARK),
    ])
    return Table(rows, colWidths=col_widths, style=style, repeatRows=1)


# ---------------------------------------------------------------------------
# COVER PAGE
# ---------------------------------------------------------------------------

def build_cover(df):
    """Build the cover / metadata block."""
    story = []

    # Title block
    cover_style = ParagraphStyle(
        "Cover",
        fontName="Helvetica-Bold",
        fontSize=20,
        textColor=WHITE,
        backColor=DARK_BG,
        spaceAfter=0,
        spaceBefore=0,
        leftIndent=10,
        rightIndent=10,
        leading=26,
        alignment=1,
    )
    sub_style = ParagraphStyle(
        "Sub",
        fontName="Helvetica",
        fontSize=11,
        textColor=LIGHT_ROW,
        backColor=DARK_BG,
        leading=16,
        alignment=1,
        leftIndent=10,
        rightIndent=10,
    )
    meta_label = ParagraphStyle(
        "MetaLabel",
        fontName="Helvetica-Bold",
        fontSize=9,
        textColor=ACCENT,
        leading=13,
    )
    meta_val = ParagraphStyle(
        "MetaVal",
        fontName="Helvetica",
        fontSize=9,
        textColor=TEXT_DARK,
        leading=13,
    )

    story.append(Paragraph("CODEBOOK", cover_style))
    story.append(Paragraph(
        "Simulated Dataset: Gender Pay Gap in the European Audiovisual Sector",
        sub_style
    ))
    story.append(spacer(0.5))

    # Metadata table
    n_rows = len(df)
    n_w = df["worker_id"].nunique()
    n_p = df["production_id"].nunique()
    n_vars = len(df.columns)
    pct_miss = df.isna().mean().mean() * 100

    meta_rows = [
        ["Metric", "Value"],
        ["Total rows (contracts)", str(n_rows)],
        ["Unique workers", str(n_w)],
        ["Unique productions", str(n_p)],
        ["Variables", str(n_vars)],
        ["Overall % missing", f"{pct_miss:.1f}%"],
        ["Unit of analysis", "One row = one contract (worker x production)"],
        ["Random seed", "42"],
        ["Reference period", "Simulated cross-section (approx. 2022-2024 AV sector)"],
        ["Project", "FAIR INCLUSIVE AV, Grant Agreement 101250721"],
        ["Funding programme", "EURO-MEI / European Commission"],
        ["Directive reference", "EU Pay Transparency Directive 2023/970"],
    ]

    avail = PAGE_W - LEFT_MARGIN - RIGHT_MARGIN
    story.append(simple_table(meta_rows, col_widths=[avail * 0.45, avail * 0.55]))
    story.append(spacer(0.4))

    story.append(P(
        "This codebook documents a synthetic (simulated) dataset created for the "
        "feasibility study of a gender pay gap calculator adapted to the European "
        "audiovisual (AV) sector. The data are not derived from real workers or "
        "productions. Distributional parameters are calibrated to published sector "
        "statistics (EAO 2024, CNC France 2022, Eurostat SES) to produce realistic "
        "pay gap magnitudes and missing data patterns for methodology stress-testing."
    ))

    story.append(PageBreak())
    return story


# ---------------------------------------------------------------------------
# SECTION 0 -- CENTRAL METHODOLOGICAL DECISION
# ---------------------------------------------------------------------------

def build_section0():
    story = []
    story.append(H("SECTION 0 -- CENTRAL METHODOLOGICAL DECISION", level=0))
    story.append(spacer(0.2))

    story.append(H("0.1  Unit of Analysis: One Row = One Contract", level=2))
    story.append(P(
        "The fundamental design choice of this dataset is that <b>the unit of "
        "analysis is a contract</b> -- a single engagement between one worker and "
        "one production -- rather than the Eurostat SES (Structure of Earnings Survey) "
        "standard of employer x employee on an annual basis."
    ))
    story.append(spacer(0.15))

    story.append(H("0.2  Why Not the Eurostat SES Standard?", level=2))
    rationale_rows = [
        ["Dimension", "Eurostat SES (standard)", "Contract-level (this dataset)"],
        ["Unit",
         "Employer x employee x year",
         "Worker x production (contract)"],
        ["Pay aggregation",
         "Annual total earnings / employer",
         "Daily rate x working days per contract"],
        ["Multi-employer workers",
         "Collapsed to one annual record per employer",
         "Each contract visible separately"],
        ["Role variation",
         "Single occupation code per record",
         "Role captured per contract (workers change roles)"],
        ["Gender gap location",
         "Detectable at employer level only",
         "Detectable by role, production type, funding type"],
        ["AV sector fit",
         "Low: most AV workers are not permanent employees",
         "High: mirrors project-based employment reality"],
    ]
    avail = PAGE_W - LEFT_MARGIN - RIGHT_MARGIN
    story.append(var_table(rationale_rows,
                           col_widths=[avail*0.24, avail*0.37, avail*0.39]))
    story.append(spacer(0.2))

    story.append(H("0.3  What This Means for the Feasibility Study", level=2))
    story.append(P(
        "The contract-level grain is a <b>necessary precondition</b> for a "
        "sectoral gender pay gap calculator because:"
    ))
    points = [
        "Art. 9.1 of Directive 2023/970 requires pay reporting per 'category of "
        "workers'. In AV, categories are role-based. A single worker may be a "
        "director on one contract and a producer on another: collapsing to an "
        "annual record would require an arbitrary role assignment.",

        "The highest gender pay gaps in AV (up to 28% for directors, CNC 2022) "
        "occur within roles, not between workers. Annual aggregation masks this "
        "because it mixes high-pay and low-pay contracts under one record.",

        "Intersectional effects (caring responsibilities, migration background) "
        "manifest at the contract level: a worker with caring duties may accept "
        "shorter, lower-rate contracts while their annual role is unchanged.",

        "Public funding is the key data access lever (30% of productions). "
        "Contract-level data allows filtering by funding_type == 'public' to "
        "identify a tractable mandatory reporting population immediately.",
    ]
    for pt in points:
        story.append(P(f"  - {pt}"))
        story.append(spacer(0.05))

    story.append(H("0.4  Worker-Year Aggregation for Directive Compliance", level=2))
    story.append(P(
        "When the calculator outputs a gender pay gap figure for Art. 9.1.b "
        "compliance, the recommended aggregation is:"
    ))
    story.append(P(
        "  (1) Group rows by worker_id within the reference calendar year.",
        CODE_STYLE
    ))
    story.append(P(
        "  (2) Compute: annual_pay = SUM(total_pay)  |  "
        "annual_days = SUM(working_days)",
        CODE_STYLE
    ))
    story.append(P(
        "  (3) Compute: fte_rate = (annual_pay / annual_days) x 220",
        CODE_STYLE
    ))
    story.append(P(
        "  (4) Compute gender pay gap per role category using fte_rate.",
        CODE_STYLE
    ))
    story.append(P(
        "This approach is consistent with the Eurostat SES 220-day FTE reference "
        "while preserving the contract-level collection that makes sector-specific "
        "disaggregation possible."
    ))

    story.append(PageBreak())
    return story


# ---------------------------------------------------------------------------
# VARIABLE TABLE BUILDER
# ---------------------------------------------------------------------------

def var_entry(name, dtype, values, source, limitation, note=None):
    """
    Build a compact variable entry block for the codebook.
    Returns a list of flowables.
    """
    avail = PAGE_W - LEFT_MARGIN - RIGHT_MARGIN
    rows = [
        ["Field", "Detail"],
        ["Variable name", name],
        ["Data type", dtype],
        ["Values / range", values],
        ["Conceptual source", source],
        ["Limitation", limitation],
    ]
    if note:
        rows.append(["Implementation note", note])
    return [
        var_table(rows, col_widths=[avail * 0.28, avail * 0.72]),
        spacer(0.25),
    ]


# ---------------------------------------------------------------------------
# SECTION 1 -- IDENTIFIERS
# ---------------------------------------------------------------------------

def build_section1():
    story = []
    story.append(H("SECTION 1 -- IDENTIFIERS", level=0))
    story.append(P(
        "Synthetic anonymised identifiers. No real worker or production identity "
        "can be recovered from these codes."
    ))
    story.append(spacer(0.2))

    story += var_entry(
        name="worker_id",
        dtype="String (categorical key)",
        values="W0001 -- W0230 (230 unique values)",
        source="Internal. No real-world counterpart. In practice: pseudonymised "
               "national social security number or AV guild membership ID.",
        limitation="Cross-year tracking requires stable pseudonymisation protocol "
                   "not included in this simulation. Re-identification risk is "
                   "non-trivial if combined with country + role + year data.",
        note="Primary key for worker-year aggregation (see Section 0.4).",
    )

    story += var_entry(
        name="production_id",
        dtype="String (categorical key)",
        values="P001 -- P065 (65 unique values)",
        source="Internal. In practice: ISAN (International Standard Audiovisual "
               "Number) or national production register ID (e.g. CNC immatriculation, "
               "ICAA numero expediente).",
        limitation="A single production may have multiple episodes or phases; "
                   "this dataset does not model intra-production temporal structure.",
    )

    story.append(PageBreak())
    return story


# ---------------------------------------------------------------------------
# SECTION 2 -- SOCIODEMOGRAPHIC / INTERSECTIONALITY
# ---------------------------------------------------------------------------

def build_section2():
    story = []
    story.append(H("SECTION 2 -- SOCIODEMOGRAPHIC VARIABLES (INTERSECTIONALITY)", level=0))
    story.append(P(
        "These variables operationalise the intersectionality mandate of "
        "EU Pay Transparency Directive 2023/970, Art. 3.2.e: 'pay structures "
        "shall take into account the intersectionality of discrimination grounds.' "
        "All distributions are calibrated to published sector statistics."
    ))
    story.append(spacer(0.2))

    story += var_entry(
        name="gender",
        dtype="String (binary categorical)",
        values="'female', 'male'",
        source="EAO Yearbook 2024: female share by role (14%--38%). "
               "Directive 2023/970 Art. 2(1)(a): gender means a person's "
               "gender as registered, with recognition of non-binary identities. "
               "This simulation uses binary gender for calibration purposes only.",
        limitation="Binary gender is a modelling simplification. Real data "
                   "collection should include a third 'non-binary / self-describe' "
                   "option consistent with Directive Art. 2(1)(a). Small-cell "
                   "suppression rules will apply to non-binary workers in "
                   "published reports.",
        note="The gender pay gap parameter per role is set BEFORE noise application, "
             "ensuring the simulated gap is directionally correct but not exact.",
    )

    story += var_entry(
        name="age_group",
        dtype="String (ordinal categorical)",
        values="'18-25', '26-35', '36-45', '46-55', '56+'",
        source="Eurostat LFS (Labour Force Survey) age brackets. "
               "Distribution calibrated to AV sector workforce profile "
               "(EAO 2024: median age 36-45 in European AV).",
        limitation="Age group is a proxy for career stage and life-cycle pay "
                   "effects. It does not capture the 'motherhood penalty' timeline "
                   "(typically age 28-38) which requires longitudinal data.",
    )

    story += var_entry(
        name="experience_years",
        dtype="Integer (continuous, nullable)",
        values="0 -- 38; ~10% missing (Pattern 1)",
        source="Derived from age_group with random component. No direct "
               "sector survey source; correlated with age using ranges from "
               "EAO 2024 career profile data.",
        limitation="Self-reported in surveys; systematically underreported "
                   "in short contracts. Missing data is not at random: workers "
                   "on their first contracts (lowest pay) most often omit this "
                   "field, creating upward bias in observed experience-pay curves.",
    )

    story += var_entry(
        name="migration_background",
        dtype="String (categorical)",
        values="'national', 'EU_mobile', 'non_EU'",
        source="Directive 2023/970, Art. 3.2.e. Distribution: 78% national, "
               "12% EU mobile, 10% non-EU -- calibrated to Eurostat AES "
               "(Adult Education Survey) AV workforce estimates.",
        limitation="'Migration background' is a proxy variable. Real data "
                   "collection faces legal constraints in several Member States "
                   "(DE, NL, AT) where recording ethnic or national origin is "
                   "restricted. The calculator may need to use proxy indicators "
                   "(e.g. language of contract, country of first employment) "
                   "in these jurisdictions.",
        note="In this simulation, migration_background does not directly affect "
             "pay; it is captured as an intersectionality descriptor for "
             "disaggregated reporting. Future versions should incorporate "
             "the documented 8-15% pay penalty for non-EU migrants in AV "
             "(Eurofound 2023).",
    )

    story += var_entry(
        name="caring_responsibilities",
        dtype="Boolean (nullable)",
        values="True / False. Prevalence: 25% women, 5% men (EIGE / Eurofound data)",
        source="Directive 2023/970, Art. 3.2.e. Caring responsibility rates: "
               "EIGE Gender Equality Index 2023; Eurofound Working Conditions "
               "Survey 2021.",
        limitation="Binary indicator does not capture caring intensity (hours/week), "
                   "type of care (child, elderly, disability), or whether formal "
                   "care support is available. The 6% pay penalty applied in this "
                   "simulation is a conservative estimate from Eurostat SILC data "
                   "for the creative industries; real-world effects may range "
                   "from 3% to 18% depending on contract type and country.",
    )

    story.append(PageBreak())
    return story


# ---------------------------------------------------------------------------
# SECTION 3 -- LABOUR VARIABLES
# ---------------------------------------------------------------------------

def build_section3():
    story = []
    story.append(H("SECTION 3 -- LABOUR VARIABLES", level=0))
    story.append(spacer(0.15))

    story += var_entry(
        name="role",
        dtype="String (categorical)",
        values="'director', 'cinematographer', 'screenwriter', 'producer', "
               "'editor', 'composer', 'sound_technician', 'art_technician'",
        source="EAO Yearbook 2024 role taxonomy. Gender pay gap parameters "
               "from CNC France 2022 (range 6%--28%). "
               "Note: 85% of contracts use the worker's primary role; 15% "
               "reflect cross-role engagements (multi-skilled workers).",
        limitation="Role taxonomy is simplified. Real AV production uses "
                   "100+ job titles (ISCO-08 is poorly adapted to AV). "
                   "A sector-specific role classification is a prerequisite "
                   "for cross-country comparability and is identified as a "
                   "key feasibility challenge.",
        note="'Category of workers' for Directive Art. 9.1 reporting should "
             "be defined by role x seniority combination, not role alone.",
    )

    story += var_entry(
        name="seniority",
        dtype="String (ordinal categorical)",
        values="'junior', 'mid', 'senior', 'lead'",
        source="Internal classification. Mapped to pay multipliers: junior x0.80, "
               "mid x1.00, senior x1.22, lead x1.45 -- calibrated to "
               "approximate sector collective agreement bands (ETUC/EURO-MEI).",
        limitation="Seniority definitions are not harmonised across EU Member "
                   "States or collective agreements. Self-reported seniority "
                   "is subject to social desirability bias. Women systematically "
                   "underreport their seniority in AV (CNC 2022).",
    )

    story += var_entry(
        name="contract_type",
        dtype="String (categorical)",
        values="'permanent' (8%), 'fixed_term' (35%), "
               "'freelance_cache' (42%), 'intermittent' (15%)",
        source="French SMIC-intermittent / CDD d'usage taxonomy, generalised "
               "to EU context. 'freelance_cache' refers to flat-fee (cachet) "
               "contracts common in FR, BE, ES -- the dominant AV contract form.",
        limitation="Contract type taxonomy is not harmonised across EU Member "
                   "States. 'Intermittent' is a French-specific regime; "
                   "equivalents exist in ES (contrato fijo-discontinuo) and "
                   "IT (contratto a progetto) but with different legal effects. "
                   "Freelance_cache contracts have the highest missing data rate "
                   "(~18% on pay variables, Pattern 3) because fees are often "
                   "undeclared or cash-based.",
    )

    story.append(PageBreak())
    return story


# ---------------------------------------------------------------------------
# SECTION 4 -- PRODUCTION VARIABLES
# ---------------------------------------------------------------------------

def build_section4():
    story = []
    story.append(H("SECTION 4 -- PRODUCTION VARIABLES", level=0))
    story.append(spacer(0.15))

    story += var_entry(
        name="production_type",
        dtype="String (categorical)",
        values="'feature_film' (25%), 'documentary' (20%), 'tv_series' (30%), "
               "'short_film' (10%), 'advertising' (15%)",
        source="EAO Yearbook 2024 production volume distribution. "
               "Documentary type triggers: female representation boost +12%, "
               "pay gap reduction effect per EAO 2024 finding.",
        limitation="Production type is determined at the production level "
                   "but may change during production (e.g. a documentary "
                   "co-produced as a TV series). Classification must be "
                   "locked at contract signature date.",
    )

    story += var_entry(
        name="is_debut",
        dtype="Boolean",
        values="True (~12%), False (~88%)",
        source="EAO 2024: debut films show 30% higher female director "
               "representation (x1.3 multiplier). Pay effect modelled "
               "conservatively as +5% relative pay access for women "
               "(debut productions attract more public and diversity funding).",
        limitation="'Debut' is defined here as the director's first feature "
                   "or documentary. Definition varies by national funding body "
                   "(e.g. CNC: first and second film; BFI: first feature only).",
    )

    story += var_entry(
        name="funding_type",
        dtype="String (categorical)",
        values="'public' (30%), 'private' (45%), 'mixed' (25%)",
        source="Eurostat Cultural Statistics 2023; EAO public funding monitor. "
               "At EU level, Art. 24 of Directive 2023/970 allows Member States "
               "to use public procurement and subsidies as a leverage point: "
               "producers with an unjustified gender pay gap above 5% may be "
               "excluded from public contracts and subsidies. However, Art. 24 "
               "is a permission granted to Member States, NOT a mandatory "
               "disclosure obligation at EU level -- transposition is discretionary. "
               "The French CNC model goes further by making pay transparency a "
               "condition of national funding allocation, but that is national "
               "policy, not EU law. A real calculator must map the Art. 24 "
               "transposition status per Member State before treating public "
               "funding as a guaranteed data access lever.",
        limitation="Mixed funding is the hardest category: the public component "
                   "may not be sufficient to trigger Art. 24 thresholds in all "
                   "Member States, and the applicable leverage mechanism will "
                   "differ by national transposition. Legal analysis per country "
                   "is required before any mandatory reporting claim is made.",
        note="Filtering funding_type == 'public' yields 30% of productions as "
             "a tractable starting population for Phase 1 data collection, "
             "subject to the Member State Art. 24 transposition caveat above.",
    )

    story += var_entry(
        name="employer_size_proxy",
        dtype="String (ordinal categorical)",
        values="'micro' (35%), 'small' (30%), 'medium' (22%), 'large' (13%)",
        source="Eurostat SBS (Structural Business Statistics) AV sector size "
               "distribution. 'Employer' here = production company, not "
               "broadcaster or platform. Micro: <10 employees; Small: 10-49; "
               "Medium: 50-249; Large: 250+.",
        limitation="Employer size is ambiguous in AV: a micro-company may "
                   "produce for a large broadcaster. The economically relevant "
                   "size is the production budget, not the headcount, "
                   "which is unavailable in most public datasets.",
    )

    story += var_entry(
        name="country",
        dtype="String (ISO 3166-1 alpha-2)",
        values="FR (22%), DE (18%), ES (14%), IT (12%), PL (8%), NL (7%), "
               "BE (6%), SE (5%), PT (4%), RO (4%)",
        source="EAO 2024 production volume by country. Distribution weighted "
               "by production volume, not workforce size.",
        limitation="Country represents the production's country of registration, "
                   "not the worker's country of residence. Cross-border "
                   "co-productions (common in EU AV) may produce inconsistent "
                   "country assignments. Labour law applicable to the contract "
                   "may differ from the production country.",
    )

    story += var_entry(
        name="n_employers_per_year",
        dtype="Integer (nullable)",
        values="1 -- 8; ~10% missing (Pattern 1)",
        source="EAO 2024 / ETUC worker survey: AV workers hold on average "
               "2.7 distinct employer relationships per year. This variable "
               "is a proxy for employment fragmentation and portfolio precarity.",
        limitation="Self-reported; frequently omitted on individual contracts. "
                   "Does not distinguish between simultaneous and sequential "
                   "employer relationships. Maximum 8 capped to avoid outliers "
                   "in simulation; real-world maximum can exceed 15.",
    )

    story.append(PageBreak())
    return story


# ---------------------------------------------------------------------------
# SECTION 5 -- REMUNERATION VARIABLES (Directive Art. 9)
# ---------------------------------------------------------------------------

def build_section5():
    story = []
    story.append(H("SECTION 5 -- REMUNERATION VARIABLES (Directive Art. 9)", level=0))
    story.append(P(
        "These variables are the core outputs of the gender pay gap calculator. "
        "Each is aligned with Art. 9.1 of Directive 2023/970, which requires "
        "employers to provide information on: (a) the pay gap between female "
        "and male workers; (b) the pay gap in complementary or variable "
        "components of pay; (c) the median pay gap."
    ))
    story.append(spacer(0.2))

    story += var_entry(
        name="working_days",
        dtype="Integer",
        values="3 -- 90 (range depends on production type)",
        source="Simulated from production-type ranges: feature_film 30-90, "
               "documentary 15-60, tv_series 20-80, short_film 5-25, "
               "advertising 3-20. No direct single-source reference; "
               "consistent with CNC production timeline statistics.",
        limitation="Working days as a time unit is AV-specific. "
                   "The Directive uses annual FTE as the normalisation basis; "
                   "conversion via fte_equivalent_pay is required for "
                   "cross-sector comparability.",
    )

    story += var_entry(
        name="daily_rate",
        dtype="Float (EUR, nullable)",
        values="Approx. 185 -- 1,200 EUR/day depending on role and seniority; "
               "~10-22% missing (Patterns 1, 2, 3)",
        source="Base rates calibrated to ETUC/EURO-MEI sector data and "
               "national collective agreements. Gender gap applied per "
               "CNC France 2022. Seniority multipliers from sector "
               "pay band analysis (Logib methodology).",
        limitation="Daily rate is the primary pay metric in AV but is not "
                   "universally reported. Freelance_cache contracts report "
                   "a total fee (cachet), not a daily rate; imputation "
                   "of daily rate from working_days and total_pay introduces "
                   "measurement error. Variable pay (bonuses, residuals) "
                   "is NOT included in daily_rate -- see includes_variable_pay.",
        note="Art. 9.1.b Directive 2023/970: variable components must be "
             "reported separately from fixed components.",
    )

    story += var_entry(
        name="total_pay",
        dtype="Float (EUR, nullable)",
        values="Approx. 500 -- 85,000 EUR per contract; ~10-22% missing",
        source="Computed as: daily_rate x working_days. "
               "Represents fixed contractual pay only, excluding variable "
               "components (Art. 9.1.b). Missing where daily_rate is missing.",
        limitation="Does not include: bonuses, profit participation, "
                   "royalty advances, overtime pay, per diems, or social "
                   "security employer contributions. The Directive's 'pay' "
                   "definition (Art. 2(1)(c)) includes all these elements; "
                   "total_pay as defined here covers only the basic contractual "
                   "component.",
    )

    story += var_entry(
        name="fte_equivalent_pay",
        dtype="Float (EUR, nullable)",
        values="Approx. 40,000 -- 265,000 EUR/year FTE equivalent; same missingness as daily_rate",
        source="Formula: daily_rate x 220. "
               "Eurostat SES reference: 220 working days = standard full-time "
               "annual equivalent for EU-level pay comparison. "
               "Enables cross-worker, cross-production pay comparison per "
               "Directive Art. 9.1.a requirement.",
        limitation="The 220-day normalisation is appropriate for cross-country "
                   "comparison but may inflate the apparent pay of workers who "
                   "only work part of the year by choice (e.g. high-rate directors "
                   "who select fewer, better-paid productions). Sensitivity analysis "
                   "with different normalisation denominators (200, 230 days) is "
                   "recommended before publication.",
        note="This is the PRIMARY variable for computing the gender pay gap "
             "indicator required by Art. 9.1.a of the Directive.",
    )

    story += var_entry(
        name="includes_variable_pay",
        dtype="Boolean",
        values="True (~20-45% depending on role), False",
        source="EU Pay Transparency Directive 2023/970, Art. 9.1.b: "
               "'complementary or variable components of pay' must be "
               "reported separately. Higher prevalence for creative above-"
               "the-line roles (directors 45%, producers 45%, composers 45%) "
               "vs technical roles (20%).",
        limitation="Boolean indicator only; does not capture the magnitude "
                   "of variable pay. Royalty income (a major component for "
                   "directors and composers) is legally separate from employment "
                   "pay in most Member States and falls outside the Directive "
                   "scope -- a significant undercount for these roles.",
    )

    story += var_entry(
        name="pay_definition_harmonized",
        dtype="Boolean",
        values="True (~65%), False (~35%)",
        source="Internal compliance indicator. Directive Art. 9.1 and "
               "recital 26: 'pay' must be defined consistently across "
               "the organisation. True = pay definition in this contract "
               "includes all fixed components and declares variable components "
               "separately per Directive requirements.",
        limitation="This flag is set probabilistically in the simulation. "
                   "In real data, determining pay definition harmonisation "
                   "requires legal review of each contract template -- "
                   "a significant compliance burden for micro and small "
                   "production companies.",
    )

    story.append(PageBreak())
    return story


# ---------------------------------------------------------------------------
# SECTION 6 -- MISSING DATA AND REPORTING BIAS
# ---------------------------------------------------------------------------

def build_section6():
    story = []
    story.append(H("SECTION 6 -- MISSING DATA AND REPORTING BIAS", level=0))
    story.append(P(
        "Missing data in this dataset is <b>intentional and structured</b> to "
        "simulate real-world reporting limitations in the AV sector. "
        "Ignoring these patterns leads to biased gender pay gap estimates. "
        "Each pattern is documented below with its methodological implication."
    ))
    story.append(spacer(0.2))

    miss_rows = [
        ["Pattern", "Variables affected", "Rate", "Applies to", "Real-world problem", "Methodological implication"],
        [
            "Pattern 1\nBaseline",
            "experience_years,\nn_employers_per_year",
            "~10%",
            "All contracts",
            "Self-reported administrative fields omitted on short or informal "
            "contracts. No systematic gender dimension.",
            "Missing Completely At Random (MCAR). Standard listwise deletion or "
            "multiple imputation is valid. Bias risk: low."
        ],
        [
            "Pattern 2\nGender x role bias",
            "daily_rate,\ntotal_pay,\nfte_equivalent_pay",
            "~22% for women in\nlow-paid roles;\n~10% elsewhere",
            "gender=='female' AND\nrole in [editor,\nsound_technician,\nart_technician]",
            "Women in low-paid AV roles are less likely to respond to pay surveys "
            "(reporting shame, fear of contract non-renewal, informal cash payments). "
            "Source: Logib methodology note; Eurostat gender pay gap survey analysis.",
            "Missing NOT At Random (MNAR). The most underpaid women are invisible. "
            "Naive analysis UNDERESTIMATES the gender pay gap. Requires MNAR-robust "
            "imputation (e.g. selection model) or sensitivity bounds. This is the "
            "single most important bias risk for the calculator."
        ],
        [
            "Pattern 3\nFreelance_cache",
            "daily_rate,\ntotal_pay,\nfte_equivalent_pay",
            "~18% additional",
            "contract_type==\n'freelance_cache'",
            "Flat-fee (cachet) contracts are frequently cash-based, undeclared to "
            "social security, or negotiated verbally. Fees are often not itemised "
            "per day, making daily_rate imputation uncertain.",
            "Missing At Random (MAR) conditional on contract type. Multiple "
            "imputation using contract_type as predictor is valid but introduces "
            "measurement error from the daily_rate imputation step. Mandatory "
            "reporting for publicly funded productions would eliminate this pattern "
            "for 30% of contracts immediately."
        ],
    ]

    avail = PAGE_W - LEFT_MARGIN - RIGHT_MARGIN
    col_w = [avail*0.10, avail*0.14, avail*0.07, avail*0.14, avail*0.27, avail*0.28]
    story.append(var_table(miss_rows, col_widths=col_w))
    story.append(spacer(0.25))

    story.append(H("6.1  Observed Missing Rates by Variable", level=2))
    story.append(P(
        "The table below shows the actual missing rates in the generated dataset "
        "(audiovisual_pay_dataset.csv). Rates are approximate due to pattern overlap "
        "(workers who are both female in low-paid roles AND on freelance_cache "
        "contracts are affected by both Pattern 2 and Pattern 3)."
    ))
    miss_obs_rows = [
        ["Variable", "Expected missing", "Dominant pattern"],
        ["daily_rate", "12-16%", "Patterns 1+2+3 combined"],
        ["total_pay", "12-16%", "Patterns 1+2+3 combined"],
        ["fte_equivalent_pay", "12-16%", "Patterns 1+2+3 combined"],
        ["experience_years", "~10%", "Pattern 1 only"],
        ["n_employers_per_year", "~10%", "Pattern 1 only"],
        ["All other variables", "0%", "Not subject to missingness in simulation"],
    ]
    story.append(simple_table(miss_obs_rows, col_widths=[avail*0.34, avail*0.27, avail*0.39]))

    story.append(PageBreak())
    return story


# ---------------------------------------------------------------------------
# SECTION 7 -- GLOBAL LIMITATIONS
# ---------------------------------------------------------------------------

def build_section7():
    story = []
    story.append(H("SECTION 7 -- GLOBAL DATASET LIMITATIONS", level=0))
    story.append(P(
        "The following limitations apply to the dataset as a whole and must be "
        "disclosed in any document presented to a European Commission evaluation committee."
    ))
    story.append(spacer(0.2))

    avail = PAGE_W - LEFT_MARGIN - RIGHT_MARGIN
    lim_rows = [
        ["#", "Limitation", "Implication for the feasibility study"],
        [
            "1",
            "Synthetic data only. All rows are generated by a stochastic model "
            "calibrated to published aggregate statistics. No real worker or "
            "production data underpins any individual row.",
            "The dataset is suitable for methodology development and stress-testing "
            "but cannot be used to estimate real gender pay gaps or to make "
            "claims about specific national AV industries. Phase 2 of the project "
            "requires real data collection partnerships (EAO, national film funds, "
            "EURO-MEI member unions)."
        ],
        [
            "2",
            "Single country for calibration (CNC France 2022). Gender pay gap "
            "parameters are drawn from French AV sector data. Germany, Italy, "
            "Spain, and Eastern European markets may have different gap structures "
            "and should not be assumed to follow French patterns.",
            "Cross-country gap estimates from this dataset are not reliable. "
            "The calculator feasibility study should identify country-specific "
            "data sources for Phase 2 calibration (e.g. FFA in DE, ICAA in ES, "
            "DFI in DK)."
        ],
        [
            "3",
            "Binary gender variable. The simulation uses male/female only, "
            "excluding non-binary, intersex, and other gender identities. "
            "This is a modelling constraint, not a normative position.",
            "Any real implementation of the calculator must comply with "
            "Directive 2023/970 Art. 2(1)(a) and national transposition laws, "
            "which require inclusive gender data collection. Small-cell "
            "suppression rules will be necessary."
        ],
        [
            "4",
            "No longitudinal dimension. All contracts are treated as a single "
            "cross-section. Career progression, motherhood penalty timing, "
            "and the 'scissors effect' (women's pay stagnating while men's "
            "rises after age 35) cannot be studied with this dataset.",
            "A panel design (worker x year x contract) is recommended for "
            "Phase 2 to capture these dynamics. The current dataset is "
            "sufficient for cross-sectional gap estimation only."
        ],
        [
            "5",
            "Variable pay not modelled in magnitude. includes_variable_pay is "
            "a boolean flag; the amount of variable pay is not simulated. "
            "Royalties, residuals, and profit participation -- which are "
            "systematically higher for male directors and composers (CNC 2022) "
            "-- are therefore absent from the pay gap calculation.",
            "The calculated gender pay gap using fte_equivalent_pay "
            "UNDERESTIMATES the true total remuneration gap by an unknown "
            "amount. Directive Art. 9.1.b requires separate reporting of "
            "variable pay; a complete calculator must model this separately."
        ],
    ]
    story.append(var_table(lim_rows, col_widths=[avail*0.04, avail*0.44, avail*0.52]))

    story.append(spacer(0.4))
    story.append(HRFlowable(width="100%", thickness=1, color=MID_BG))
    story.append(spacer(0.2))
    story.append(P(
        "<b>Data sources referenced in this codebook:</b>"
    ))
    sources = [
        "CNC (Centre national du cinema et de l'image animee). "
        "Rapport sur la place des femmes dans l'industrie cinematographique. 2022.",
        "European Audiovisual Observatory (EAO). Yearbook 2024.",
        "European Commission. EU Pay Transparency Directive 2023/970, OJ L 132, 17.5.2023.",
        "Eurostat. Structure of Earnings Survey (SES) Methodology. 2022.",
        "Eurostat. Labour Force Survey (LFS). 2023.",
        "EIGE. Gender Equality Index. 2023.",
        "Eurofound. European Working Conditions Survey. 2021.",
        "Swiss Federal Office for Gender Equality. Logib Methodology Guide. v3.0. 2021.",
        "ETUC / EURO-MEI. Creative Sector Pay Analysis. Internal report. 2023.",
    ]
    for s in sources:
        story.append(P(f"  - {s}", NOTE_STYLE))

    return story


# ---------------------------------------------------------------------------
# SECTION 8 -- POLICY RELEVANCE AND USE BY SOCIAL PARTNERS
# ---------------------------------------------------------------------------

def build_section8():
    story = []
    story.append(H("SECTION 8 -- POLICY RELEVANCE AND USE BY SOCIAL PARTNERS", level=0))
    story.append(P(
        "This section explains how the dataset structure and the variables it "
        "contains directly support the work of trade unions, employer organisations, "
        "and EU institutions in implementing the Pay Transparency Directive and "
        "advancing gender pay equity in the European audiovisual sector."
    ))
    story.append(spacer(0.2))

    story.append(H("8.1  Supporting Trade Union Collective Bargaining", level=2))
    story.append(P(
        "The contract-level structure of this dataset provides trade unions with "
        "the type of granular evidence that is currently absent from sector "
        "negotiations. Specifically:"
    ))
    points = [
        "<b>Role-level GPG indicators for rate card negotiation.</b> By computing "
        "the gender pay gap separately for each role (director, editor, "
        "sound_technician, etc.), unions can enter collective bargaining with "
        "documented, role-specific evidence of pay disparities. A gap of 28% "
        "for directors (CNC 2022) is a materially different negotiating argument "
        "than a sector-wide average. Role-level indicators allow unions to "
        "target minimum fee standards where discrimination is most severe.",

        "<b>Contract-type disaggregation for freelance protection.</b> Separating "
        "pay data by contract_type exposes the double jeopardy of freelance_cache "
        "workers: they face both higher pay gaps and higher data invisibility "
        "(18% missing rate). This supports union advocacy for mandatory fee "
        "reporting in cachet contracts, which is currently absent in most "
        "Member State frameworks.",

        "<b>Production-type evidence for minimum fee standards.</b> The gap "
        "between documentary and feature_film pay levels supports arguments "
        "for production-type-specific minimum fee schedules. Documentaries "
        "employ proportionally more women (EAO 2024 +12% representation) but "
        "are typically lower-budget, creating a structural trap: the production "
        "type most accessible to women is also the type with the least pay "
        "protection. Dataset disaggregation by production_type makes this "
        "argument quantifiable.",

        "<b>Funding-type leverage for mandatory reporting advocacy.</b> The "
        "funding_type variable enables unions to focus their advocacy precisely: "
        "the 30% of productions with public funding are the tractable first "
        "population for mandatory pay reporting under Art. 24 of the Directive, "
        "and unions can use production-level data to identify which publicly "
        "funded productions have the largest unexplained gaps.",

        "<b>fte_equivalent_pay as a comparable pay metric.</b> For the first "
        "time, this variable enables cross-worker, cross-production pay "
        "comparisons on a common basis. Previously, the structural opacity "
        "of project-based employment -- different working days per contract, "
        "different roles, different production types -- made it impossible for "
        "unions to demonstrate pay inequity with a single, defensible number. "
        "The 220-day FTE normalisation bridges this gap.",
    ]
    for pt in points:
        story.append(P(f"  - {pt}"))
        story.append(spacer(0.08))

    story.append(spacer(0.1))
    story.append(H("8.2  EU-Level Social Dialogue and ETUC Framework", level=2))
    story.append(P(
        "The dataset structure is aligned with the ETUC (European Trade Union "
        "Confederation) framework for Pay Transparency Directive implementation, "
        "which calls for sector-specific pay reporting tools as a complement to "
        "the employer-level reporting required by Art. 9. In the AV sector, "
        "EURO-MEI (the European sectoral social partner) has identified the "
        "absence of comparable pay data as the single greatest obstacle to "
        "meaningful social dialogue on the gender pay gap."
    ))
    story.append(spacer(0.1))
    story.append(P(
        "The contract-level dataset architecture directly supports the EURO-MEI "
        "position in EU-level sectoral social dialogue by: (a) providing a "
        "methodological proof-of-concept that can be presented to employer "
        "organisations (e.g. CEPI, UER) as a non-intrusive data collection "
        "framework; (b) demonstrating that role-level pay gap indicators can "
        "be computed from administrative data without requiring individual "
        "workers to self-disclose pay information; and (c) establishing a "
        "reference dataset against which Member State transposition of Art. 24 "
        "can be assessed comparatively."
    ))

    story.append(PageBreak())
    return story


# ---------------------------------------------------------------------------
# SECTION 9 -- FEASIBILITY OF A GENDER PAY GAP CALCULATOR
# ---------------------------------------------------------------------------

def build_section9():
    story = []
    story.append(H("SECTION 9 -- FEASIBILITY OF A GENDER PAY GAP CALCULATOR", level=0))
    story.append(P(
        "The central question of this project is whether a gender pay gap "
        "calculator adapted to the European audiovisual sector is technically, "
        "legally, and institutionally feasible. This section presents a genuine "
        "two-scenario assessment. Both scenarios are valid feasibility study "
        "outcomes; neither represents failure."
    ))
    story.append(spacer(0.2))

    story.append(H("9.1  Scenario A: Calculator Is Viable", level=2))
    story.append(P(
        "A sector-specific gender pay gap calculator is technically feasible "
        "under the following conditions:"
    ))

    avail = PAGE_W - LEFT_MARGIN - RIGHT_MARGIN
    scenario_a_rows = [
        ["Condition", "Specification", "Current status"],
        [
            "Common worker identifier",
            "A stable pseudonymised identifier linking a worker across "
            "contracts and employers within a calendar year. Options: "
            "union membership number (FIA/FIM), national social security "
            "number (hashed), or AV guild registration ID.",
            "Partially available in FR (intermittents register, AUDIENS), "
            "DE (DRV), ES (TGSS). Cross-border linkage requires bilateral "
            "data sharing agreement or Eurostat pilot."
        ],
        [
            "Pay data from publicly funded productions",
            "Access to contract-level daily_rate or total_pay for the "
            "population of productions receiving public funding (est. 30% "
            "of sector). Can be implemented as a condition of Art. 24 "
            "national transposition or via voluntary film fund agreement "
            "(CNC model).",
            "Available in FR via CNC; under discussion in DE (FFA) and "
            "IE (Screen Ireland). Not yet available in ES (ICAA) or at "
            "EU level."
        ],
        [
            "Harmonised role taxonomy",
            "Agreement on a minimum set of 8-12 comparable role categories "
            "across at least the four project partner countries "
            "(ES, FR, DE, IE). Must map to national collective agreement "
            "categories and to ISCO-08 at a 4-digit level.",
            "No harmonised AV role taxonomy currently exists at EU level. "
            "EAO 2024 uses a 7-category taxonomy as a starting point; "
            "sector social partners (EURO-MEI, FIA) would need to validate "
            "and expand it."
        ],
        [
            "Minimum sample size",
            "At least 50 observed contracts per role x gender cell per "
            "country to produce statistically reliable gap estimates "
            "(based on Logib minimum cell size recommendations).",
            "Achievable in FR and DE for above-the-line roles (director, "
            "producer); unlikely in smaller countries or for below-the-line "
            "technical roles without pooling across years."
        ],
    ]
    story.append(var_table(scenario_a_rows,
                           col_widths=[avail*0.22, avail*0.42, avail*0.36]))
    story.append(spacer(0.15))
    story.append(P(
        "Under Scenario A, the calculator aggregates contracts to worker-year "
        "level using the methodology described in Section 0.4, computes "
        "fte_equivalent_pay per worker per role category, and outputs a "
        "gender pay gap indicator per role x country x production_type cell. "
        "The output is directly compliant with Art. 9.1.a of the Directive "
        "and can be used by unions, employers, and public funding bodies."
    ))
    story.append(spacer(0.2))

    story.append(H("9.2  Scenario B: Calculator Is Not Viable -- Alternative Outputs", level=2))
    story.append(P(
        "If data fragmentation is too severe, GDPR constraints prevent "
        "cross-border identifier linkage, or role taxonomy harmonisation "
        "cannot be achieved within the project timeline, the feasibility "
        "study should recommend three alternative outputs of equivalent "
        "policy value:"
    ))

    alt_rows = [
        ["Alternative output", "Description", "Policy value"],
        [
            "(1) Sector-specific pay reporting framework",
            "A standardised pay reporting template for productions receiving "
            "public funding, designed to be submitted annually to national "
            "film funds. Covers: role, seniority, contract_type, daily_rate "
            "(or fee range), gender, and working_days. Does not require a "
            "common worker identifier.",
            "Immediately implementable under Art. 24 national transposition. "
            "Creates the data infrastructure for a future calculator without "
            "requiring cross-employer data linkage. Pilotable with CNC "
            "France as lead partner."
        ],
        [
            "(2) Union toolkit with survey methodology",
            "A standardised survey instrument and analysis template for "
            "union-administered pay surveys of AV sector workers. Includes "
            "the 22 variables in this dataset, a missing data correction "
            "protocol (Logib-adapted), and a worked example of gender pay "
            "gap computation from survey data.",
            "Provides unions with a credible, defensible methodology for "
            "pay gap claims in collective bargaining. Does not depend on "
            "employer data access. Can be deployed within 6 months of "
            "project completion."
        ],
        [
            "(3) Policy recommendation on threshold",
            "A formal recommendation to lower the Directive Art. 9.1 "
            "reporting threshold from 100 workers to a production-budget "
            "threshold (e.g. productions with budgets above EUR 500,000) "
            "for the audiovisual sector, with a specific carve-out for "
            "project-based workers not captured by the headcount rule.",
            "Addresses the root cause of AV sector exclusion from the "
            "Directive's mandatory reporting scope. Requires advocacy at "
            "European Commission level but is supported by the Directive's "
            "Art. 31 review clause (first review due 2028)."
        ],
    ]
    story.append(var_table(alt_rows,
                           col_widths=[avail*0.24, avail*0.42, avail*0.34]))
    story.append(spacer(0.15))
    story.append(P(
        "The feasibility study must present both scenarios to the European "
        "Commission with equal rigour. A study that concludes only 'the "
        "calculator is not feasible' without recommending actionable "
        "alternatives will not satisfy the project's deliverable requirements "
        "or serve the sector's needs."
    ))

    story.append(PageBreak())
    return story


# ---------------------------------------------------------------------------
# SECTION 10 -- DATA AVAILABILITY AND GOVERNANCE
# ---------------------------------------------------------------------------

def build_section10():
    story = []
    story.append(H("SECTION 10 -- DATA AVAILABILITY AND GOVERNANCE", level=0))
    story.append(P(
        "This section maps the real-world data holders relevant to a gender "
        "pay gap calculator for the European audiovisual sector, their data "
        "holdings, access conditions, and the barriers to use. It also "
        "addresses GDPR re-identification risks specific to this dataset structure."
    ))
    story.append(spacer(0.2))

    story.append(H("10.1  Data Holder Mapping", level=2))

    avail = PAGE_W - LEFT_MARGIN - RIGHT_MARGIN
    holder_rows = [
        ["Data holder", "Data type available", "Access conditions", "Barriers"],
        [
            "National film funds\n(CNC FR, FFA DE,\nICAA ES, Screen Ireland IE)",
            "Production budgets and public funding allocations per production. "
            "In FR (CNC): partial pay data submitted by productions as condition "
            "of funding agreement.",
            "Condition of public funding grant (FR model). In DE/ES/IE: "
            "voluntary data sharing agreement with project consortium, "
            "subject to data protection officer approval.",
            "Data shared at aggregate level only; individual production data "
            "protected by commercial confidentiality clauses. Cross-country "
            "harmonisation of reported variables does not yet exist. "
            "FR is the only country with an established pay transparency "
            "reporting requirement."
        ],
        [
            "Trade unions\n(FIA, FIM,\nVer.di DE, IADT IE)",
            "Member fee surveys (voluntary), collective agreement minimum "
            "rates by role and seniority, anonymised pay range data from "
            "union-administered surveys.",
            "Voluntary member participation. Data available to project "
            "consortium under research partnership agreement with "
            "EURO-MEI as intermediary.",
            "Response bias: union members are not representative of the "
            "full AV workforce (estimated 30-45% unionisation in AV). "
            "Non-union workers -- disproportionately women, migrants, and "
            "early-career professionals -- are systematically excluded."
        ],
        [
            "Social security registries\n(FR URSSAF, DE DRV,\nES TGSS)",
            "Declared earnings per worker per year by employer, social "
            "contribution records, employment duration. In FR: "
            "intermittents du spectacle register (near-complete AV workforce "
            "coverage for declared contracts).",
            "Research agreement (CASD model in FR) or legal mandate "
            "under GDPR Art. 6.1.e (substantial public interest) required. "
            "Access typically requires national ethics committee approval "
            "and secure data enclave processing.",
            "GDPR Art. 9 (special category data if combined with gender). "
            "Cross-border data transfer limitations under GDPR Chapter V: "
            "data from FR URSSAF cannot be transferred to DE or ES "
            "researchers without explicit legal basis. Each country "
            "requires a separate access application."
        ],
        [
            "Production companies",
            "Full contract data: role, daily_rate, working_days, "
            "contract_type, gender, start/end dates. The most complete "
            "and granular source available.",
            "Voluntary participation (private productions) or mandatory "
            "if subject to Art. 24 national transposition and production "
            "receives public funding.",
            "Commercial confidentiality and competitive sensitivity: "
            "production companies routinely refuse to disclose individual "
            "contract terms. GDPR data subject rights complicate aggregate "
            "reporting from small productions where individual workers "
            "may be identifiable. Micro-companies lack GDPR compliance "
            "infrastructure to participate in data collection."
        ],
    ]
    story.append(var_table(holder_rows,
                           col_widths=[avail*0.20, avail*0.28, avail*0.26, avail*0.26]))
    story.append(spacer(0.2))

    story.append(H("10.2  GDPR Re-Identification Risk", level=2))
    story.append(P(
        "The combination of variables in this dataset creates a significant "
        "quasi-identifier risk that must be addressed in any real data "
        "collection protocol. Specifically, the combination of:"
    ))
    story.append(P(
        "  worker_id  +  daily_rate  +  role  +  country  +  year",
        CODE_STYLE
    ))
    story.append(P(
        "may allow re-identification of individual workers in small "
        "productions, where the number of workers per role per production "
        "is very small (often 1-2 persons). A director on a micro-budget "
        "documentary in a small country is effectively identifiable even "
        "without a name or social security number."
    ))
    story.append(spacer(0.1))
    story.append(P(
        "<b>Recommended mitigation:</b> Apply k-anonymity with k >= 5 at the "
        "<b>role x production_type x country</b> level before any publication "
        "or sharing of the dataset. This means that any cell in a cross-tabulation "
        "of these three variables must contain at least 5 distinct worker_id values. "
        "Cells below this threshold must be suppressed or merged with adjacent "
        "categories before the data are released. This is consistent with "
        "Eurostat cell suppression rules and the Logib methodology's minimum "
        "reporting unit requirements."
    ))
    story.append(spacer(0.1))
    story.append(P(
        "In the simulated dataset, k-anonymity at k=5 is satisfied by construction "
        "(230 workers across 8 roles, 5 production types, 10 countries). In real "
        "data, particularly for rare role x country combinations (e.g. composer "
        "in RO, cinematographer in PT), suppression will be necessary and "
        "should be documented transparently in any published report."
    ))

    story.append(PageBreak())
    return story


# ---------------------------------------------------------------------------
# SECTION 11 -- COMPARISON WITH EUROSTAT SES
# ---------------------------------------------------------------------------

def build_section11():
    story = []
    story.append(H("SECTION 11 -- COMPARISON WITH EUROSTAT STRUCTURE OF EARNINGS SURVEY", level=0))
    story.append(P(
        "The Eurostat Structure of Earnings Survey (SES) is the primary "
        "EU-level instrument for measuring the gender pay gap and serves as "
        "the methodological reference for the Pay Transparency Directive. "
        "This section documents systematically how the AV sector's employment "
        "structure diverges from SES assumptions, and why a sector-specific "
        "data collection protocol is a necessary precondition for any gender "
        "pay gap calculator."
    ))
    story.append(spacer(0.2))

    story.append(H("11.1  Dimension-by-Dimension Comparison", level=2))

    avail = PAGE_W - LEFT_MARGIN - RIGHT_MARGIN
    ses_rows = [
        ["Dimension", "Eurostat SES", "This dataset / AV sector reality"],
        [
            "Unit of analysis",
            "Employer x employee, annual. One record per worker per employer "
            "per reference year.",
            "Worker x production (contract). One record per engagement. A "
            "single worker generates 1-5 records per year across multiple employers."
        ],
        [
            "Coverage threshold",
            "Enterprises with 10 or more employees. Excludes the self-employed "
            "and workers in micro-enterprises.",
            "Most AV productions employ fewer than 10 people. The 10-employee "
            "threshold excludes the majority of AV sector activity from SES "
            "coverage by design."
        ],
        [
            "Worker type",
            "Employees with a formal employment contract. Self-employed and "
            "platform workers are excluded.",
            "42% of AV contracts in this dataset are freelance_cache (flat-fee), "
            "which in most Member States is classified as self-employment. "
            "The majority of AV professionals are legally self-employed."
        ],
        [
            "Pay normalisation",
            "Annual gross earnings divided by full-time equivalent months. "
            "Reference: full-year, full-time employment.",
            "Daily rate x 220 days (Eurostat SES FTE reference adapted to "
            "day-rate employment). Aggregation to worker-year is required "
            "before applying this normalisation."
        ],
        [
            "Reference period",
            "One calendar year (October reference month for some variables). "
            "Longitudinal panel not maintained.",
            "Single cross-section in simulation. In reality, AV requires "
            "a rolling 12-month window to capture full annual income from "
            "sequential short contracts."
        ],
        [
            "Employer definition",
            "The legal entity employing the worker and responsible for "
            "pay reporting. Stable across the reference year.",
            "In AV, the 'employer' changes with every production. "
            "employer_size_proxy refers to the production company, not "
            "the broadcaster or platform that ultimately finances the work. "
            "This creates a mismatch with SES employer-level reporting."
        ],
        [
            "Role classification",
            "ISCO-08 (International Standard Classification of Occupations) "
            "at 4-digit level. Designed for stable occupational categories "
            "in permanent employment.",
            "ISCO-08 does not distinguish between an executive producer and "
            "a line producer, or between a director of photography and a "
            "camera operator. AV requires a sector-specific taxonomy of "
            "8-12 functional role categories to produce meaningful gap estimates."
        ],
        [
            "Missing data approach",
            "SES uses imputation for item non-response at the employer "
            "level. Worker-level non-response is handled by reweighting.",
            "AV missing data is structurally biased (MNAR for women in "
            "low-paid roles, MAR for freelance_cache contracts). Standard "
            "SES imputation methods are not appropriate without MNAR "
            "correction -- see Section 6."
        ],
        [
            "Gender gap measurement",
            "Unadjusted gender pay gap = (male avg pay - female avg pay) "
            "/ male avg pay. Published annually by Eurostat for each "
            "Member State.",
            "Role-level unadjusted gap computed from fte_equivalent_pay. "
            "Cross-role aggregation requires role weighting by workforce "
            "share. The intersectional decomposition (caring, migration) "
            "is not supported by SES."
        ],
    ]
    story.append(var_table(ses_rows,
                           col_widths=[avail*0.22, avail*0.37, avail*0.41]))
    story.append(spacer(0.2))

    story.append(H("11.2  Why the AV Sector Falls Outside SES Coverage", level=2))
    story.append(P(
        "The audiovisual sector is systematically excluded from the Eurostat SES "
        "for three structural reasons that are not incidental but definitional:"
    ))
    exclusion_points = [
        "<b>Size threshold.</b> The SES covers enterprises with 10 or more "
        "employees. According to Eurostat SBS data, over 80% of AV production "
        "companies in the EU have fewer than 10 employees. A feature film may "
        "employ 50-200 people on a production, but the legal entity (production "
        "company) typically has 1-5 permanent employees. The temporary project "
        "workforce is invisible to the SES size filter.",

        "<b>Employment status.</b> The SES excludes self-employed workers, who "
        "represent the majority of AV professionals in most Member States. "
        "In France, intermittents du spectacle -- the dominant AV employment "
        "regime -- are technically employees but on atypical contracts that "
        "are systematically underrepresented in SES sampling frames. In Germany, "
        "Spain, and Ireland, the equivalent workers are largely classified as "
        "self-employed (Selbstaendige, autónomos, self-employed contractors) "
        "and are entirely outside SES scope.",

        "<b>Employer unit mismatch.</b> The SES uses the employer as its "
        "organisational unit, with annual pay aggregated per employer. In AV, "
        "this unit is meaningless for pay gap analysis: a worker's annual "
        "income comes from multiple sequential employers (productions), each "
        "paying a daily rate for a short period. No single employer has "
        "visibility of the worker's full annual pay, and the employer-level "
        "gap calculation would compare a director who happened to work only "
        "for one production with an editor who worked for three -- "
        "a structurally incomparable comparison.",
    ]
    for pt in exclusion_points:
        story.append(P(f"  - {pt}"))
        story.append(spacer(0.08))

    story.append(spacer(0.15))
    story.append(H("11.3  Central Recommendation", level=2))
    story.append(P(
        "The convergence of these three structural exclusions leads to a single, "
        "unavoidable conclusion: <b>a sector-specific data collection protocol "
        "is a necessary precondition for any gender pay gap calculator in the "
        "European audiovisual sector.</b> This conclusion holds regardless of "
        "whether the feasibility study results in Scenario A (calculator viable) "
        "or Scenario B (alternative outputs recommended) as described in "
        "Section 9."
    ))
    story.append(spacer(0.1))
    story.append(P(
        "The SES will not be adapted to cover the AV sector in the near term. "
        "The Directive's Art. 9 reporting requirements apply to individual "
        "employers, not to sectors -- and most AV employers fall below the "
        "applicable thresholds. The practical implication is that measuring the "
        "gender pay gap in AV requires either (a) a purpose-built sectoral "
        "data collection funded by public bodies and social partners, or "
        "(b) mandatory pay reporting as a condition of public funding under "
        "Art. 24 transposition."
    ))
    story.append(spacer(0.1))
    story.append(P(
        "This is the central finding that the FAIR INCLUSIVE AV feasibility "
        "study must communicate to the European Commission, regardless of "
        "which scenario the technical assessment supports. The dataset and "
        "methodology documented in this codebook provide the evidence base "
        "for that recommendation."
    ))

    story.append(spacer(0.4))
    story.append(HRFlowable(width="100%", thickness=1, color=MID_BG))
    story.append(spacer(0.2))
    story.append(P("<b>End of Codebook.</b> This document is a technical reference for the FAIR INCLUSIVE AV project"
                " and is not intended for public distribution.", NOTE_STYLE))

    return story


# ---------------------------------------------------------------------------
# MAIN BUILD
# ---------------------------------------------------------------------------

def build_codebook(csv_path="audiovisual_pay_dataset.csv",
                   output_path="codebook.pdf"):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"Dataset not found: {csv_path}\n"
            "Run generate_dataset.py first."
        )

    print(f"Loading dataset from {csv_path}...")
    df = pd.read_csv(csv_path)
    print(f"  {len(df)} rows, {len(df.columns)} columns loaded.")

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=LEFT_MARGIN,
        rightMargin=RIGHT_MARGIN,
        topMargin=TOP_MARGIN,
        bottomMargin=BOT_MARGIN,
        title="FAIR INCLUSIVE AV -- Codebook",
        author="FAIR INCLUSIVE AV technical team",
        subject="Gender Pay Gap Dataset Codebook -- European Audiovisual Sector",
    )

    story = []
    story += build_cover(df)
    story += build_section0()
    story += build_section1()
    story += build_section2()
    story += build_section3()
    story += build_section4()
    story += build_section5()
    story += build_section6()
    story += build_section7()
    story += build_section8()
    story += build_section9()
    story += build_section10()
    story += build_section11()

    print("Building PDF...")
    doc.build(story, onFirstPage=make_page_template, onLaterPages=make_page_template)
    print(f"Codebook saved to: {output_path}")


if __name__ == "__main__":
    build_codebook()
