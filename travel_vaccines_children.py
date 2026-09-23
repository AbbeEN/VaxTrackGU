"""
Travel Vaccine Recommendations for Infants and Children
=========================================================
An interactive reference tool built from CDC MMWR / ACIP Recommendations
and Reports. Enter a child's age to see which travel-related vaccines
apply, at what dose/schedule, and under what travel circumstances.

SOURCES (all CDC MMWR Recommendations and Reports):
  - Cholera Vaccine: ACIP Recommendations, 2022 (MMWR 71, No. 2)
  - Japanese Encephalitis Vaccine: ACIP Recommendations, 2019 (MMWR 68, No. 2)
  - Updated Recommendations for Use of Typhoid Vaccine, ACIP 2015 (MMWR 64, No. 11)
  - Meningococcal Vaccination: ACIP Recommendations, 2020 (MMWR 69, No. 9)
  - Prevention of Hepatitis A Virus Infection, ACIP 2020 (MMWR 69, No. 5)
  - Dengue Vaccine: ACIP Recommendations, 2021 (MMWR 70, No. 6)
  - Use of a Modified Preexposure Prophylaxis Vaccination Schedule to
    Prevent Human Rabies, ACIP 2022 (MMWR 71, No. 18)

DISCLAIMER: This tool is for general educational reference only. It is
not medical advice and does not replace a pretravel consultation with a
clinician or travel medicine specialist, who can weigh itinerary,
destination-specific risk, and the child's individual health history.
"""

import streamlit as st

# ----------------------------------------------------------------------
# Data: one entry per vaccine, with age-banded dosing/eligibility info
# pulled directly from the ACIP recommendations named above.
# ----------------------------------------------------------------------

VACCINES = [
    {
        "name": "Hepatitis A",
        "min_age_months": 6,
        "source": "MMWR 69(5), 2020 — Prevention of Hepatitis A Virus Infection",
        "summary": (
            "Routine 2-dose childhood series begins at 12–23 months. For "
            "infants 6–11 months traveling outside the United States, CDC "
            "provides guidance for an additional travel-related dose."
        ),
        "age_bands": [
            {
                "label": "6–11 months",
                "min_m": 6, "max_m": 11,
                "detail": (
                    "HepA vaccine should be given to infants aged 6–11 months "
                    "traveling outside the U.S. when protection against HAV is "
                    "recommended. This travel dose does NOT count toward the "
                    "routine 2-dose series — the routine series should still be "
                    "started at age 12 months with the age-appropriate dose/schedule."
                ),
            },
            {
                "label": "12 months – 18 years",
                "min_m": 12, "max_m": 18 * 12,
                "detail": (
                    "Routine 2-dose series (Vaqta: 25 units/dose; Havrix: 720 "
                    "ELISA units/dose), doses given 6–18 months apart depending "
                    "on product. If not previously vaccinated, catch-up "
                    "vaccination is recommended for children/adolescents aged "
                    "2–18 years before travel to a country with high or "
                    "intermediate HAV endemicity."
                ),
            },
        ],
        "travel_trigger": "Travel to a country with high or intermediate hepatitis A endemicity.",
    },
    {
        "name": "Japanese Encephalitis (Ixiaro/JE-VC)",
        "min_age_months": 2,
        "source": "MMWR 68(2), 2019 — Japanese Encephalitis Vaccine",
        "summary": (
            "Licensed for children as young as 2 months. Recommended for "
            "longer-term (≥1 month) travelers to JE-endemic countries in Asia "
            "and the western Pacific, and considered for shorter trips with "
            "elevated risk (rural areas, transmission season, outdoor exposure)."
        ),
        "age_bands": [
            {
                "label": "2–35 months",
                "min_m": 2, "max_m": 35,
                "detail": (
                    "2 doses of 0.25 mL each, given on days 0 and 28. Booster "
                    "(0.25 mL) at ≥1 year after the 2nd dose if ongoing/renewed "
                    "exposure is expected."
                ),
            },
            {
                "label": "3–17 years",
                "min_m": 36, "max_m": 17 * 12,
                "detail": (
                    "2 doses of 0.5 mL each, given on days 0 and 28. Booster "
                    "(0.5 mL) at ≥1 year after the 2nd dose if ongoing/renewed "
                    "exposure is expected."
                ),
            },
        ],
        "travel_trigger": (
            "Longer-term (≥1 month) or frequent travel to JE-endemic areas; "
            "consider for shorter trips with rural, outdoor, or "
            "season-of-transmission exposure."
        ),
    },
    {
        "name": "Typhoid (Vi polysaccharide / Ty21a)",
        "min_age_months": 24,
        "source": "MMWR 64(11), 2015 — Updated Recommendations for Typhoid Vaccine",
        "summary": (
            "Recommended for travelers to areas with recognized risk of "
            "Salmonella Typhi exposure — most travel-associated U.S. cases "
            "occur in travelers to India, Bangladesh, or Pakistan, often "
            "visiting friends or relatives."
        ),
        "age_bands": [
            {
                "label": "2–5 years",
                "min_m": 24, "max_m": 5 * 12,
                "detail": (
                    "Vi polysaccharide vaccine only (injectable): 1 dose "
                    "(0.5 mL IM), given ≥2 weeks before potential exposure. "
                    "Booster every 2 years if continued/renewed exposure is "
                    "expected. (Oral Ty21a is not approved below age 6.)"
                ),
            },
            {
                "label": "6–17 years",
                "min_m": 6 * 12, "max_m": 17 * 12,
                "detail": (
                    "Either Vi polysaccharide (1 dose IM, ≥2 weeks before "
                    "travel, booster every 2 years) OR oral live-attenuated "
                    "Ty21a (4 enteric-coated capsules on alternating days over "
                    "1 week, completed ≥1 week before travel, booster series "
                    "every 5 years). Ty21a should not be given to "
                    "immunocompromised children or those on antibacterial drugs."
                ),
            },
        ],
        "travel_trigger": (
            "Travel to areas with recognized typhoid risk, especially with "
            "prolonged exposure to food/water or when visiting friends/relatives."
        ),
    },
    {
        "name": "Meningococcal (MenACWY)",
        "min_age_months": 2,
        "source": "MMWR 69(9), 2020 — Meningococcal Vaccination",
        "summary": (
            "Routinely recommended at age 11–12 years (booster at 16), but "
            "also recommended from age 2 months for children at increased "
            "risk — including travel to countries where meningococcal disease "
            "is hyperendemic or epidemic (e.g., the African meningitis belt) "
            "or for pilgrimage travel (e.g., Hajj)."
        ),
        "age_bands": [
            {
                "label": "2–8 months",
                "min_m": 2, "max_m": 8,
                "detail": (
                    "Age-specific primary series (schedule varies by product and "
                    "indication) for children at increased risk, including travel "
                    "to hyperendemic/epidemic regions. Discuss product choice and "
                    "dosing with a pediatric/travel medicine provider."
                ),
            },
            {
                "label": "9–23 months",
                "min_m": 9, "max_m": 23,
                "detail": (
                    "Age-appropriate MenACWY primary series for children at "
                    "increased risk (dosing schedule varies by product)."
                ),
            },
            {
                "label": "2 years – 10 years",
                "min_m": 24, "max_m": 10 * 12,
                "detail": (
                    "MenACWY recommended for children at increased risk, "
                    "including travel to hyperendemic/epidemic areas; booster "
                    "interval depends on age at prior dose."
                ),
            },
            {
                "label": "11–12 years (routine)",
                "min_m": 11 * 12, "max_m": 12 * 12,
                "detail": (
                    "Routine MenACWY dose recommended for ALL adolescents "
                    "(not just travelers), with a booster at age 16."
                ),
            },
        ],
        "travel_trigger": (
            "Travel to countries where meningococcal disease is hyperendemic "
            "or epidemic (e.g., sub-Saharan meningitis belt), or travel "
            "requiring proof of vaccination (e.g., Hajj/Umrah)."
        ),
    },
    {
        "name": "Cholera (CVD 103-HgR / Vaxchora)",
        "min_age_months": 24,
        "source": "MMWR 71(2), 2022 — Cholera Vaccine",
        "summary": (
            "Only cholera vaccine licensed in the U.S. Recommended for "
            "travelers aged 2–64 years going to an area with active cholera "
            "transmission. No data on safety/efficacy in children under 2 "
            "or adults 65+, so it is not recommended for those ages."
        ),
        "age_bands": [
            {
                "label": "2–17 years",
                "min_m": 24, "max_m": 17 * 12,
                "detail": (
                    "Single oral dose, given ≥10 days before travel. Efficacy "
                    "data in this age group are based on immune-response "
                    "(immunobridging) rather than direct efficacy trials, but "
                    "ACIP still recommends it for travel to areas with active "
                    "cholera transmission. Not studied in children under 2 — "
                    "not recommended below that age."
                ),
            },
        ],
        "travel_trigger": "Travel to a specific area with active (endemic or epidemic) cholera transmission.",
    },
    {
        "name": "Dengue (Dengvaxia)",
        "min_age_months": 9 * 12,
        "source": "MMWR 70(6), 2021 — Dengue Vaccine",
        "summary": (
            "Narrow, specific indication — NOT a general child-travel "
            "vaccine. Only for children aged 9–16 living in a dengue-endemic "
            "area (Puerto Rico, U.S. Virgin Islands, American Samoa, and "
            "some Pacific freely associated states) who have laboratory-"
            "confirmed evidence of a PRIOR dengue infection. Not available "
            "or recommended for visitors/travelers, and not for seronegative "
            "children (increased risk of severe dengue on first infection "
            "after vaccination)."
        ),
        "age_bands": [
            {
                "label": "9–16 years",
                "min_m": 9 * 12, "max_m": 16 * 12,
                "detail": (
                    "3-dose series (0.5 mL each) given 6 months apart (months "
                    "0, 6, 12) — but ONLY for children who (a) live in a "
                    "dengue-endemic U.S. area/territory AND (b) have "
                    "laboratory-confirmed evidence of previous DENV infection. "
                    "Not recommended for use in the continental United States "
                    "or for short-term travelers."
                ),
            },
        ],
        "travel_trigger": (
            "Not a travel vaccine in the usual sense — relevant only to "
            "children who reside in a dengue-endemic U.S. territory with "
            "confirmed prior infection."
        ),
    },
    {
        "name": "Rabies Preexposure Prophylaxis (PrEP)",
        "min_age_months": 0,
        "source": "MMWR 71(18), 2022 — Rabies Preexposure Prophylaxis",
        "summary": (
            "No specific lower age limit is set by risk category — decision "
            "is based on the child's risk of exposure (e.g., extended travel "
            "to areas with limited access to safe post-exposure treatment, "
            "or activities with animal contact), not age alone. Young "
            "children may be at higher unrecognized-exposure risk because "
            "bites/scratches (e.g., from bats or dogs) may go unreported."
        ),
        "age_bands": [
            {
                "label": "All pediatric ages (risk-based, not age-based)",
                "min_m": 0, "max_m": 18 * 12,
                "detail": (
                    "2 intramuscular doses on days 0 and 7 (deltoid, or "
                    "anterolateral thigh in young children). Whether PrEP is "
                    "indicated depends on the ACIP risk category (e.g., "
                    "risk category 4: short-term travel with likely animal "
                    "contact and limited access to safe post-exposure "
                    "prophylaxis) rather than on the child's age itself. PrEP "
                    "does NOT eliminate the need for post-exposure treatment "
                    "if a bite/scratch occurs — it simplifies that treatment."
                ),
            },
        ],
        "travel_trigger": (
            "Travel to a rabies-endemic destination with likely animal "
            "contact and/or difficulty accessing prompt, safe post-exposure "
            "care (rabies immunoglobulin can be scarce outside major cities "
            "in many countries)."
        ),
    },
]


def months_from_years_months(years: int, months: int) -> int:
    return years * 12 + months


def band_matches(band: dict, age_m: int) -> bool:
    return band["min_m"] <= age_m <= band["max_m"]


def format_age(age_m: int) -> str:
    y, m = divmod(age_m, 12)
    parts = []
    if y:
        parts.append(f"{y} yr{'s' if y != 1 else ''}")
    if m or not y:
        parts.append(f"{m} mo")
    return " ".join(parts)


# ----------------------------------------------------------------------
# Streamlit UI
# ----------------------------------------------------------------------

st.set_page_config(
    page_title="Travel Vaccines for Infants & Children",
    page_icon="🧳",
    layout="wide",
)

st.title("🧳 Travel Vaccine Recommendations for Infants and Children")
st.caption(
    "Reference tool based on CDC MMWR / ACIP Recommendations and Reports "
    "(cholera, Japanese encephalitis, typhoid, meningococcal, hepatitis A, "
    "dengue, and rabies)."
)

st.warning(
    "**Not medical advice.** This tool summarizes published ACIP "
    "recommendations for general reference. Always confirm with a "
    "pediatrician or travel medicine clinic — destination, itinerary, "
    "season, and the child's own health history all affect what's actually "
    "advised.",
    icon="⚠️",
)

with st.sidebar:
    st.header("Child's age")
    col_y, col_m = st.columns(2)
    with col_y:
        years = st.number_input("Years", min_value=0, max_value=18, value=2, step=1)
    with col_m:
        months = st.number_input("Months", min_value=0, max_value=11, value=0, step=1)
    age_in_months = months_from_years_months(years, months)
    st.markdown(f"**Age entered:** {format_age(age_in_months)}")

    st.divider()
    st.header("Destination context (optional)")
    st.caption(
        "These checkboxes just filter which vaccines are shown — they don't "
        "change the dosing information, which is age-specific only."
    )
    ctx_hep_a = st.checkbox("Region with high/intermediate hepatitis A risk", value=True)
    ctx_je = st.checkbox("Rural / extended travel in JE-endemic Asia or western Pacific")
    ctx_typhoid = st.checkbox("Region with typhoid risk (e.g., South Asia)")
    ctx_meningo = st.checkbox("Meningitis-belt / hyperendemic region or pilgrimage travel")
    ctx_cholera = st.checkbox("Area with active cholera transmission")
    ctx_dengue = st.checkbox("Resident of a dengue-endemic U.S. territory, prior dengue infection")
    ctx_rabies = st.checkbox("Likely animal contact / limited access to post-exposure care")

    context_flags = {
        "Hepatitis A": ctx_hep_a,
        "Japanese Encephalitis (Ixiaro/JE-VC)": ctx_je,
        "Typhoid (Vi polysaccharide / Ty21a)": ctx_typhoid,
        "Meningococcal (MenACWY)": ctx_meningo,
        "Cholera (CVD 103-HgR / Vaxchora)": ctx_cholera,
        "Dengue (Dengvaxia)": ctx_dengue,
        "Rabies Preexposure Prophylaxis (PrEP)": ctx_rabies,
    }
    any_context_checked = any(context_flags.values())

st.subheader(f"Vaccines to discuss for a child aged {format_age(age_in_months)}")

shown_any = False
for vac in VACCINES:
    if any_context_checked and not context_flags.get(vac["name"], False):
        continue

    matching_bands = [b for b in vac["age_bands"] if band_matches(b, age_in_months)]
    eligible_by_age = age_in_months >= vac["min_age_months"]

    if not eligible_by_age:
        continue

    shown_any = True
    with st.container(border=True):
        st.markdown(f"### {vac['name']}")
        st.markdown(f"*{vac['summary']}*")
        st.markdown(f"**When it applies:** {vac['travel_trigger']}")

        if matching_bands:
            for band in matching_bands:
                st.success(f"**Applicable age band — {band['label']}**\n\n{band['detail']}")
        else:
            st.info(
                "No specific age band in this dataset matches exactly — check "
                "the age bands below and confirm with a clinician."
            )
            for band in vac["age_bands"]:
                st.markdown(f"- **{band['label']}:** {band['detail']}")

        st.caption(f"Source: {vac['source']}")

if not shown_any:
    st.info(
        "No travel vaccines in this dataset apply at the selected age "
        "(and/or destination filters). Try unchecking destination filters "
        "in the sidebar, or double-check the age entered."
    )

st.divider()
with st.expander("📚 Full reference table (all vaccines, all age bands)"):
    for vac in VACCINES:
        st.markdown(f"**{vac['name']}**  \n_{vac['source']}_")
        for band in vac["age_bands"]:
            st.markdown(f"- {band['label']}: {band['detail']}")
        st.markdown("")

st.caption(
    "Built from: Cholera Vaccine ACIP 2022 (MMWR 71:2); Japanese Encephalitis "
    "Vaccine ACIP 2019 (MMWR 68:2); Typhoid Vaccine ACIP 2015 (MMWR 64:11); "
    "Meningococcal Vaccination ACIP 2020 (MMWR 69:9); Hepatitis A Prevention "
    "ACIP 2020 (MMWR 69:5); Dengue Vaccine ACIP 2021 (MMWR 70:6); Rabies PrEP "
    "ACIP 2022 (MMWR 71:18)."
)
