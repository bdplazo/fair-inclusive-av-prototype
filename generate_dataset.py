"""
generate_dataset.py
====================
FAIR INCLUSIVE AV -- Project 101250721 (EURO-MEI)
Feasibility study: Gender Pay Gap Calculator for the European Audiovisual Sector

CENTRAL METHODOLOGICAL DECISION
================================
Unit of analysis: one row = one CONTRACT (worker x production)

This departs deliberately from the Eurostat SES (Structure of Earnings Survey)
standard, which uses employer x employee as the unit of analysis on an annual
basis. The reasons are structural to the audiovisual sector:

  1. PROJECT-BASED EMPLOYMENT: A single worker typically holds 3-8 distinct
     contracts per year with different employers, under different roles,
     production types, and daily rates. Annual aggregation would collapse
     this heterogeneity and obscure the within-worker variation in pay
     that is central to detecting gender bias.

  2. DIRECTIVE ALIGNMENT: The EU Pay Transparency Directive 2023/970 (Art. 9.1)
     requires reporting at the "category of workers" level. In the AV sector,
     meaningful categories are role-based (director, editor, composer...), not
     employer-based. The contract-level grain allows computing role-specific
     gender pay gaps without relying on a single employer-year anchor.

  3. METHODOLOGICAL ADVANTAGE: Contract-level data enables:
     - Intra-worker analysis (same worker, different roles, different pay gaps)
     - Multiplicity correction (workers with more contracts are not artificially
       up-weighted in a naive employer-level analysis)
     - Detection of intersectional effects (caring duties, migration background)
       that manifest at the contract level, not at the annual level

HOW WORKER-YEAR AGGREGATION WOULD WORK IN PRACTICE (for Directive compliance):
  - Group by worker_id + calendar year (not modelled here: all rows = 1 year)
  - Sum total_pay and working_days across all contracts in the year
  - Compute: fte_equivalent_pay = (sum_total_pay / sum_working_days) * 220
    where 220 days = Eurostat SES reference for full-time annual equivalent
  - Apply this aggregated rate in the gender pay gap calculation per role category
  - This bridges the contract-level collection with the Art. 9.1.b reporting
    requirement without losing within-sector heterogeneity

DATA SOURCES:
  - Gender pay gap by role: CNC (Centre national du cinema et de l'image animee),
    Rapport sur la place des femmes dans l'industrie cinematographique, 2022
  - Female representation by role: European Audiovisual Observatory (EAO),
    Yearbook 2024
  - Intersectionality variables: EU Pay Transparency Directive 2023/970, Art. 3.2.e
  - Pay normalisation: Eurostat SES methodology, 220-day annual FTE reference
  - Missing data patterns: Logib methodology (Swiss Federal Office for Gender
    Equality) and AV-sector reporting bias literature

Author: Begoña lazo Egido
Date: 2026-04
Seed: SEED=42 (fixed for full reproducibility)
"""

import numpy as np
import pandas as pd

SEED = 42
rng = np.random.default_rng(SEED)

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------

N_WORKERS = 230       # unique workers in the simulated panel
N_PRODUCTIONS = 65    # unique productions
TARGET_ROWS = (560, 680)  # target range for total contracts (rows)

# Roles covered (cross-role standardisation is a key calculator challenge)
ROLES = [
    "director",
    "cinematographer",
    "screenwriter",
    "producer",
    "editor",
    "composer",
    "sound_technician",
    "art_technician",
]

# Role sampling weights (approximate sector distribution)
ROLE_WEIGHTS = [0.10, 0.08, 0.14, 0.12, 0.14, 0.08, 0.18, 0.16]

# Gender pay gap by role (unadjusted / raw gap) -- CNC France 2022
# Interpretation: women earn X% LESS than men in this role on average
# Range: 5%-35% across roles as specified
GPG_BY_ROLE = {
    "director":        0.28,
    "cinematographer": 0.24,
    "screenwriter":    0.15,
    "producer":        0.12,
    "editor":          0.08,
    "composer":        0.20,
    "sound_technician":0.10,
    "art_technician":  0.06,
}

# Female share by role -- EAO Yearbook 2024
FEMALE_SHARE_BY_ROLE = {
    "director":        0.26,
    "cinematographer": 0.14,
    "screenwriter":    0.30,
    "producer":        0.32,
    "editor":          0.38,
    "composer":        0.12,
    "sound_technician":0.22,
    "art_technician":  0.35,
}

# Baseline daily rates (EUR) calibrated for men at mid-seniority level
# Approximate industry norms; not from a single public source
BASE_DAILY_RATE_BY_ROLE = {
    "director":        620,
    "cinematographer": 560,
    "screenwriter":    420,
    "producer":        720,
    "editor":          360,
    "composer":        480,
    "sound_technician":310,
    "art_technician":  290,
}

# Seniority levels and pay multipliers
SENIORITY_LEVELS = ["junior", "mid", "senior", "lead"]
SENIORITY_WEIGHTS = [0.20, 0.35, 0.30, 0.15]
SENIORITY_MULTIPLIER = {
    "junior": 0.80,
    "mid":    1.00,
    "senior": 1.22,
    "lead":   1.45,
}

# Contract types in the AV sector
# freelance_cache: flat fee contract common in FR/BE/ES -- highest reporting bias
CONTRACT_TYPES = ["permanent", "fixed_term", "freelance_cache", "intermittent"]
CONTRACT_WEIGHTS = [0.08, 0.35, 0.42, 0.15]

# Production types
PRODUCTION_TYPES = [
    "feature_film", "documentary", "tv_series", "short_film", "advertising"
]
PRODUCTION_WEIGHTS = [0.25, 0.20, 0.30, 0.10, 0.15]

# Funding types.
# At EU level, Art. 24 of Directive 2023/970 allows Member States to use public
# procurement and public funding as a leverage point: producers with an unjustified
# gender pay gap above 5% CAN be excluded from public contracts and subsidies.
# However, Art. 24 is a permission granted to Member States, NOT a direct mandatory
# disclosure obligation at EU level. Implementation is discretionary per country.
# The French CNC model goes further by making pay transparency a condition of
# national public funding -- but that is national policy, not EU law. A real
# calculator should map the Art. 24 transposition status per Member State before
# treating public funding as a guaranteed data access lever.
FUNDING_TYPES = ["public", "private", "mixed"]
FUNDING_WEIGHTS = [0.30, 0.45, 0.25]

# EU Member States with significant AV industry (ISO 3166-1 alpha-2)
COUNTRIES = ["FR", "DE", "ES", "IT", "PL", "NL", "BE", "SE", "PT", "RO"]
COUNTRY_WEIGHTS = [0.22, 0.18, 0.14, 0.12, 0.08, 0.07, 0.06, 0.05, 0.04, 0.04]

# Migration background (Art. 3.2.e Directive 2023/970 -- intersectionality)
MIGRATION_CATEGORIES = ["national", "EU_mobile", "non_EU"]
MIGRATION_WEIGHTS = [0.78, 0.12, 0.10]

# Age groups
AGE_GROUPS = ["18-25", "26-35", "36-45", "46-55", "56+"]
AGE_WEIGHTS = [0.08, 0.30, 0.32, 0.20, 0.10]

# Age-to-experience mapping (min, max years of experience)
AGE_EXP_MAP = {
    "18-25": (0, 4),
    "26-35": (2, 10),
    "36-45": (8, 20),
    "46-55": (15, 30),
    "56+":   (20, 38),
}


# ---------------------------------------------------------------------------
# STEP 1 -- GENERATE WORKERS
# ---------------------------------------------------------------------------

def generate_workers(n_workers, rng):
    """
    Generate a panel of N_WORKERS unique workers with demographic characteristics.

    Each worker has a primary_role (the role they work in most often) from which
    gender probability is derived using EAO 2024 female representation rates.

    Returns a DataFrame with one row per worker.
    """
    workers = []
    for i in range(n_workers):
        # Assign primary role; female probability derived from role-specific EAO data
        role = rng.choice(ROLES, p=ROLE_WEIGHTS)
        female_prob = FEMALE_SHARE_BY_ROLE[role]
        gender = "female" if rng.random() < female_prob else "male"

        age_group = rng.choice(AGE_GROUPS, p=AGE_WEIGHTS)
        lo, hi = AGE_EXP_MAP[age_group]
        experience_years = int(rng.integers(lo, hi + 1))

        # --- GDPR NOTE ON INTERSECTIONALITY VARIABLES ---
        # (a) Directive 2023/970, Art. 3.3 explicitly states that the obligation to
        #     collect data under the Directive does NOT extend to grounds of
        #     discrimination other than sex. Intersectionality variables are therefore
        #     outside the mandatory scope of the Directive.
        # (b) Collecting these variables is nonetheless PERMITTED for analytical
        #     purposes, but requires either explicit informed consent from the data
        #     subject (GDPR Art. 6.1.a) or a legal basis such as substantial public
        #     interest (GDPR Art. 6.1.e) or scientific research purposes (Art. 9.2.j).
        # (c) migration_background touches on racial/ethnic origin in the broad sense
        #     of GDPR Art. 9 (special category data), requiring a stronger legal
        #     justification and enhanced security measures. National law may impose
        #     additional restrictions (e.g. France prohibits collecting ethnic origin
        #     data entirely under Loi Informatique et Libertes).
        # (d) In a real data collection, these variables would be collected on an
        #     opt-in, anonymised, aggregated basis only -- never at the individual
        #     contract level as modelled here. Aggregate distributions would be
        #     used for sector-level reporting, with individual records suppressed.
        # (e) In this SIMULATED dataset, migration_background and
        #     caring_responsibilities are included solely as a methodological
        #     demonstration of intersectional pay effects. They do NOT constitute
        #     a recommendation to collect these variables at the contract level
        #     in any real implementation of the calculator.

        # Migration background -- distributed independently of gender
        # (intersectionality is captured at contract level via combined effects)
        migration_background = rng.choice(MIGRATION_CATEGORIES, p=MIGRATION_WEIGHTS)

        # Caring responsibilities (Art. 3.2.e): 25% women, 5% men -- EIGE / Eurofound
        caring = rng.random() < (0.25 if gender == "female" else 0.05)

        workers.append({
            "worker_id":             f"W{i + 1:04d}",
            "gender":                gender,
            "age_group":             age_group,
            "experience_years":      experience_years,
            "migration_background":  migration_background,
            "caring_responsibilities": caring,
            "primary_role":          role,
        })

    return pd.DataFrame(workers)


# ---------------------------------------------------------------------------
# STEP 2 -- GENERATE PRODUCTIONS
# ---------------------------------------------------------------------------

def generate_productions(n_prod, rng):
    """
    Generate a panel of N_PRODUCTIONS unique productions.

    Production-level variables are structural covariates that affect:
    - Data accessibility (funding_type: public productions disclose more)
    - Pay levels (production_type, employer_size_proxy)
    - Female representation (is_debut, documentary -- EAO 2024 boost)

    Returns a DataFrame with one row per production.
    """
    productions = []
    for i in range(n_prod):
        prod_type = rng.choice(PRODUCTION_TYPES, p=PRODUCTION_WEIGHTS)
        is_debut = rng.random() < 0.12   # ~12% debut productions in sample
        funding_type = rng.choice(FUNDING_TYPES, p=FUNDING_WEIGHTS)
        country = rng.choice(COUNTRIES, p=COUNTRY_WEIGHTS)
        employer_size = rng.choice(
            ["micro", "small", "medium", "large"],
            p=[0.35, 0.30, 0.22, 0.13]
        )
        productions.append({
            "production_id":     f"P{i + 1:03d}",
            "production_type":   prod_type,
            "is_debut":          is_debut,
            "funding_type":      funding_type,
            "country":           country,
            "employer_size_proxy": employer_size,
        })

    return pd.DataFrame(productions)


# ---------------------------------------------------------------------------
# STEP 3 -- GENERATE CONTRACTS (worker x production rows)
# ---------------------------------------------------------------------------

def generate_contracts(workers_df, productions_df, rng, target_rows=(560, 680)):
    """
    Assign workers to productions to create contract rows.

    Central rule: one row = one contract (worker x production).
    A single worker may appear in 1-5 contracts, reflecting typical
    AV sector portfolio employment (project-based, multi-employer).

    Pay is computed as:
      daily_rate = BASE_RATE x seniority_multiplier x (1 - gpg if female)
                   x caring_penalty x noise

      total_pay = daily_rate x working_days

      fte_equivalent_pay = daily_rate x 220
        (Eurostat SES reference: 220 working days = full-time annual FTE)

    Gender pay gap sources: CNC France 2022
    EAO 2024 documentary boost: applied to female REPRESENTATION probability only
      (+0.12 to female_prob for documentary productions, capped at 0.65).
      It does NOT affect pay -- the EAO 2024 finding is about who works in
      documentaries, not about documentary pay being higher for women.
    Debut film: +5% pay access effect for women (conservative translation of
      the EAO 2024 x1.3 representation boost via diversity funding access).
    Caring penalty: 6% for women with caring duties (Eurostat SILC data)
    """
    contracts = []
    n_workers = len(workers_df)
    prod_ids = productions_df["production_id"].values

    # Assign number of contracts per worker (1-5) to approximate target row count
    contracts_per_worker = rng.integers(1, 6, size=n_workers)
    total = contracts_per_worker.sum()
    target_mean = (target_rows[0] + target_rows[1]) // 2
    if total < target_rows[0]:
        extra = target_rows[0] - int(total)
        idx = rng.choice(n_workers, size=extra, replace=True)
        for ix in idx:
            contracts_per_worker[ix] += 1

    for _, worker in workers_df.iterrows():
        n_c = int(contracts_per_worker[worker.name])

        # Sample productions for this worker
        assigned_prods = rng.choice(prod_ids, size=n_c, replace=(n_c > len(prod_ids)))

        for prod_id in assigned_prods:
            prod_row = productions_df[
                productions_df["production_id"] == prod_id
            ].iloc[0]
            prod_type = prod_row["production_type"]

            # Default gender from worker record; may be overridden below for
            # documentary variant-role contracts (representation boost).
            gender = worker["gender"]

            # Role: 85% primary role, 15% variant role (multi-skilled workers).
            # For documentary productions, the EAO 2024 +0.12 female representation
            # boost is applied to the female_prob of variant-role draws, capped at
            # 0.65. Worker gender for primary-role contracts is fixed at worker
            # creation time (from FEMALE_SHARE_BY_ROLE), so the documentary boost
            # manifests primarily through variant-role assignment diversity.
            # NOTE: this boost affects WHO works in documentaries, NOT pay rates.
            if rng.random() < 0.85:
                role = worker["primary_role"]
            else:
                role = rng.choice(ROLES, p=ROLE_WEIGHTS)
                # For documentary variant-role contracts, re-draw worker gender
                # with boosted female probability (EAO 2024 +0.12, cap 0.65)
                if prod_type == "documentary":
                    boosted_female_prob = min(
                        FEMALE_SHARE_BY_ROLE[role] + 0.12, 0.65
                    )
                    gender = worker["gender"]  # default: keep worker's gender
                    # Only override if the worker's primary role differs from variant
                    if role != worker["primary_role"]:
                        gender = "female" if rng.random() < boosted_female_prob else "male"

            seniority = rng.choice(SENIORITY_LEVELS, p=SENIORITY_WEIGHTS)
            contract_type = rng.choice(CONTRACT_TYPES, p=CONTRACT_WEIGHTS)

            # Working days by production type
            wd_ranges = {
                "feature_film":  (30, 90),
                "documentary":   (15, 60),
                "tv_series":     (20, 80),
                "short_film":    (5,  25),
                "advertising":   (3,  20),
            }
            lo, hi = wd_ranges[prod_type]
            working_days = int(rng.integers(lo, hi + 1))

            # --- Daily rate computation ---
            rate = BASE_DAILY_RATE_BY_ROLE[role] * SENIORITY_MULTIPLIER[seniority]

            if gender == "female":
                # Apply gender pay gap (CNC France 2022): female = male * (1 - gpg)
                rate *= (1 - GPG_BY_ROLE[role])

                # Debut film: slightly improved pay access for women (EAO 2024 x1.3
                # representation; conservative pay translation = +5%)
                if prod_row["is_debut"]:
                    rate *= 1.05

            # Caring responsibilities pay penalty for women (Art. 3.2.e, Eurostat SILC)
            # 6% penalty reflects part-time / intermittent work pattern due to caring
            if gender == "female" and worker["caring_responsibilities"]:
                rate *= (1 - 0.06)

            # Random noise +/- 15% to simulate real-world negotiation variation
            noise = float(rng.normal(1.0, 0.10))
            noise = max(0.70, min(noise, 1.35))
            rate = round(rate * noise, 2)

            total_pay = round(rate * working_days, 2)

            # fte_equivalent_pay: normalised to 220-day FTE (Eurostat SES)
            # Allows cross-production, cross-worker pay comparison for Art. 9.1.b
            fte_equivalent_pay = round(rate * 220, 2)

            # Variable pay (Art. 9.1.b Directive 2023/970): bonuses, royalties,
            # profit-sharing -- more common in creative/above-the-line roles
            includes_variable_pay = bool(rng.random() < (
                0.45 if role in ["director", "producer", "composer"] else 0.20
            ))

            # Pay definition harmonised: True if pay definition in this contract
            # aligns with the Directive Art. 9.1 "pay" definition (all fixed elements
            # included; variable elements separately declared)
            pay_definition_harmonized = bool(rng.random() < 0.65)

            # n_employers_per_year: proxy for employment fragmentation
            # Self-reported; correlated with n_c but with noise
            n_employers = max(1, min(int(n_c + int(rng.integers(-1, 3))), 8))

            contracts.append({
                "worker_id":               worker["worker_id"],
                "production_id":           prod_id,
                "gender":                  gender,
                "age_group":               worker["age_group"],
                "experience_years":        worker["experience_years"],
                "migration_background":    worker["migration_background"],
                "caring_responsibilities": worker["caring_responsibilities"],
                "role":                    role,
                "seniority":               seniority,
                "contract_type":           contract_type,
                "production_type":         prod_type,
                "is_debut":                bool(prod_row["is_debut"]),
                "funding_type":            prod_row["funding_type"],
                "employer_size_proxy":     prod_row["employer_size_proxy"],
                "country":                 prod_row["country"],
                "n_employers_per_year":    n_employers,
                "working_days":            working_days,
                "daily_rate":              rate,
                "total_pay":               total_pay,
                "fte_equivalent_pay":      fte_equivalent_pay,
                "includes_variable_pay":   includes_variable_pay,
                "pay_definition_harmonized": pay_definition_harmonized,
            })

    return pd.DataFrame(contracts)


# ---------------------------------------------------------------------------
# STEP 4 -- APPLY MISSING DATA PATTERNS
# ---------------------------------------------------------------------------

def apply_missing_data(df, rng):
    """
    Apply intentional missing data patterns to simulate real-world reporting bias.

    PATTERN 1 -- Baseline (~10% missing):
      Variables: experience_years, n_employers_per_year
      Rationale: These are self-reported administrative variables, commonly
      omitted in short-term contracts or when the worker holds multiple
      parallel contracts. No systematic bias by gender.

    PATTERN 2 -- Women in low-paid roles (~22% missing on pay variables):
      Applies to: daily_rate, total_pay, fte_equivalent_pay
      Condition: gender == 'female' AND role IN [editor, sound_technician,
                 art_technician]
      Rationale: Women in low-paid AV roles are less likely to respond to
      pay surveys (reporting shame, precarity fear, informal contracts).
      This is a known bias documented in Logib methodology notes and
      Eurostat gender pay gap survey analysis. If left uncorrected, it
      leads to UNDERESTIMATION of the gender pay gap (the worst-paid
      women are invisible in the data).
      Methodological implication: Any calculator must apply missing-not-
      at-random (MNAR) correction or sensitivity analysis before publishing
      a gender pay gap figure.

    PATTERN 3 -- freelance_cache contracts (~18% missing on pay variables):
      Applies to: daily_rate, total_pay, fte_equivalent_pay
      Condition: contract_type == 'freelance_cache'
      Rationale: Flat-fee (cachet) contracts are often cash-based,
      undeclared to social security, or negotiated verbally in AV
      production. This is the dominant contract form (~42% of contracts)
      and the hardest for a pay calculator to capture without mandatory
      reporting obligations. This pattern directly justifies the
      recommendation for sector-specific data collection protocols.
    """
    df = df.copy()
    n = len(df)

    # Pattern 1: Baseline 10% missing on administrative self-reported variables
    for var in ["experience_years", "n_employers_per_year"]:
        mask = rng.random(n) < 0.10
        df.loc[mask, var] = np.nan

    pay_vars = ["daily_rate", "total_pay", "fte_equivalent_pay"]
    low_paid_roles = ["editor", "sound_technician", "art_technician"]
    female_low_paid = (df["gender"] == "female") & (df["role"].isin(low_paid_roles))

    # Pattern 2: Women in low-paid roles -- 22% missing on pay variables
    for var in pay_vars:
        mask_bias = female_low_paid & (rng.random(n) < 0.22)
        mask_base = (~female_low_paid) & (rng.random(n) < 0.10)
        df.loc[mask_bias | mask_base, var] = np.nan

    # Pattern 3: freelance_cache -- additional 18% missing on pay variables
    freelance_mask = df["contract_type"] == "freelance_cache"
    for var in pay_vars:
        not_yet_missing = df[var].notna()
        extra_mask = freelance_mask & not_yet_missing & (rng.random(n) < 0.18)
        df.loc[extra_mask, var] = np.nan

    return df


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("FAIR INCLUSIVE AV -- Dataset Generator")
    print("Project 101250721 (EURO-MEI)")
    print(f"Random seed: {SEED}")
    print("=" * 60)

    print("\n[1/4] Generating workers...")
    workers_df = generate_workers(N_WORKERS, rng)
    print(f"      {len(workers_df)} unique workers created.")

    print("[2/4] Generating productions...")
    productions_df = generate_productions(N_PRODUCTIONS, rng)
    print(f"      {len(productions_df)} unique productions created.")

    print("[3/4] Generating contracts (one row = one contract)...")
    contracts_df = generate_contracts(workers_df, productions_df, rng, TARGET_ROWS)
    print(f"      {len(contracts_df)} contracts before missing data application.")

    print("[4/4] Applying missing data patterns...")
    contracts_df = apply_missing_data(contracts_df, rng)

    # ---- Validation ----
    n_rows = len(contracts_df)
    n_w = contracts_df["worker_id"].nunique()
    n_p = contracts_df["production_id"].nunique()

    assert n_w == N_WORKERS, f"Worker count mismatch: expected {N_WORKERS}, got {n_w}"
    assert TARGET_ROWS[0] <= n_rows, f"Too few rows: {n_rows}"

    # ---- Summary ----
    pct_missing_overall = contracts_df.isna().mean().mean() * 100
    print("\n" + "=" * 60)
    print("DATASET SUMMARY")
    print("=" * 60)
    print(f"  Total contracts (rows):   {n_rows}")
    print(f"  Unique workers:           {n_w}")
    print(f"  Unique productions:       {n_p}")
    print(f"  Variables:                {len(contracts_df.columns)}")
    print(f"  Overall % missing:        {pct_missing_overall:.1f}%")

    print("\nMissing data by pay variable:")
    for v in ["daily_rate", "total_pay", "fte_equivalent_pay",
              "experience_years", "n_employers_per_year"]:
        pct = contracts_df[v].isna().mean() * 100
        print(f"  {v:<30s}: {pct:.1f}% missing")

    print("\nGender pay gap verification (observed mean daily_rate by role):")
    gpg_check = (
        contracts_df.groupby(["role", "gender"])["daily_rate"]
        .mean()
        .unstack()
    )
    if "male" in gpg_check.columns and "female" in gpg_check.columns:
        gpg_check["obs_gpg"] = (
            (gpg_check["male"] - gpg_check["female"]) / gpg_check["male"]
        ).round(3)
        print(gpg_check.to_string())

    # ---- Save ----
    output_path = "audiovisual_pay_dataset.csv"
    contracts_df.to_csv(output_path, index=False)
    print(f"\nDataset saved to: {output_path}")
    print("Run generate_codebook.py to produce codebook.pdf")
    print("=" * 60)

    return contracts_df


if __name__ == "__main__":
    main()
