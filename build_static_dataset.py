import csv
import json
import certifi
import ssl
from urllib.request import urlopen

MALARIA_SOURCE_URL = "https://ourworldindata.org/grapher/incidence-of-malaria.csv"
COUNTRY_GEOMETRY_URL = "https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson"

# List of 195 ISO3 Country Codes & Names
ALL_COUNTRIES_RAW = [
    ("AFG", "Afghanistan", True), ("ALB", "Albania", False), ("DZA", "Algeria", False),
    ("AND", "Andorra", False), ("AGO", "Angola", True), ("ATG", "Antigua and Barbuda", False),
    ("ARG", "Argentina", True), ("ARM", "Armenia", False), ("AUS", "Australia", False),
    ("AUT", "Austria", False), ("AZE", "Azerbaijan", False), ("BHS", "Bahamas", False),
    ("BHR", "Bahrain", False), ("BGD", "Bangladesh", False), ("BRB", "Barbados", False),
    ("BLR", "Belarus", False), ("BEL", "Belgium", False), ("BLZ", "Belize", False),
    ("BEN", "Benin", True), ("BTN", "Bhutan", False), ("BOL", "Bolivia", True),
    ("BIH", "Bosnia and Herzegovina", False), ("BWA", "Botswana", False), ("BRA", "Brazil", True),
    ("BRN", "Brunei", False), ("BGR", "Bulgaria", False), ("BFA", "Burkina Faso", True),
    ("BDI", "Burundi", True), ("CPV", "Cabo Verde", False), ("KHM", "Cambodia", False),
    ("CMR", "Cameroon", True), ("CAN", "Canada", False), ("CAF", "Central African Republic", True),
    ("TCD", "Chad", True), ("CHL", "Chile", False), ("CHN", "China", False),
    ("COL", "Colombia", True), ("COM", "Comoros", False), ("COG", "Congo", True),
    ("COD", "Congo (DRC)", True), ("CRI", "Costa Rica", False), ("CIV", "Côte d'Ivoire", True),
    ("HRV", "Croatia", False), ("CUB", "Cuba", False), ("CYP", "Cyprus", False),
    ("CZE", "Czech Republic", False), ("DNK", "Denmark", False), ("DJI", "Djibouti", False),
    ("DMA", "Dominica", False), ("DOM", "Dominican Republic", False), ("ECU", "Ecuador", True),
    ("EGY", "Egypt", False), ("SLV", "El Salvador", False), ("GNQ", "Equatorial Guinea", True),
    ("ERI", "Eritrea", False), ("EST", "Estonia", False), ("SWZ", "Eswatini", False),
    ("ETH", "Ethiopia", True), ("FJI", "Fiji", False), ("FIN", "Finland", False),
    ("FRA", "France", False), ("GAB", "Gabon", True), ("GMB", "Gambia", True),
    ("GEO", "Georgia", False), ("DEU", "Germany", False), ("GHA", "Ghana", True),
    ("GRC", "Greece", False), ("GRD", "Grenada", False), ("GTM", "Guatemala", False),
    ("GIN", "Guinea", True), ("GNB", "Guinea-Bissau", True), ("GUY", "Guyana", True),
    ("HTI", "Haiti", False), ("HND", "Honduras", False), ("HUN", "Hungary", False),
    ("ISL", "Iceland", False), ("IND", "India", False), ("IDN", "Indonesia", False),
    ("IRN", "Iran", False), ("IRQ", "Iraq", False), ("IRL", "Ireland", False),
    ("ISR", "Israel", False), ("ITA", "Italy", False), ("JAM", "Jamaica", False),
    ("JPN", "Japan", False), ("JOR", "Jordan", False), ("KAZ", "Kazakhstan", False),
    ("KEN", "Kenya", True), ("KIR", "Kiribati", False), ("PRK", "North Korea", False),
    ("KOR", "South Korea", False), ("KWT", "Kuwait", False), ("KGZ", "Kyrgyzstan", False),
    ("LAO", "Laos", False), ("LVA", "Latvia", False), ("LBN", "Lebanon", False),
    ("LSO", "Lesotho", False), ("LBR", "Liberia", True), ("LBY", "Libya", False),
    ("LIE", "Liechtenstein", False), ("LTU", "Lithuania", False), ("LUX", "Luxembourg", False),
    ("MDG", "Madagascar", False), ("MWI", "Malawi", False), ("MYS", "Malaysia", False),
    ("MDV", "Maldives", False), ("MLI", "Mali", True), ("MLT", "Malta", False),
    ("MHL", "Marshall Islands", False), ("MRT", "Mauritania", True), ("MUS", "Mauritius", False),
    ("MEX", "Mexico", False), ("FSM", "Micronesia", False), ("MDA", "Moldova", False),
    ("MCO", "Monaco", False), ("MNG", "Mongolia", False), ("MNE", "Montenegro", False),
    ("MAR", "Morocco", False), ("MOZ", "Mozambique", False), ("MMR", "Myanmar", False),
    ("NAM", "Namibia", False), ("NRU", "Nauru", False), ("NPL", "Nepal", False),
    ("NLD", "Netherlands", False), ("NZL", "New Zealand", False), ("NIC", "Nicaragua", False),
    ("NER", "Niger", True), ("NGA", "Nigeria", True), ("MKD", "North Macedonia", False),
    ("NOR", "Norway", False), ("OMN", "Oman", False), ("PAK", "Pakistan", False),
    ("PLW", "Palau", False), ("PAN", "Panama", True), ("PNG", "Papua New Guinea", False),
    ("PRY", "Paraguay", True), ("PER", "Peru", True), ("PHL", "Philippines", False),
    ("POL", "Poland", False), ("PRT", "Portugal", False), ("QAT", "Qatar", False),
    ("ROU", "Romania", False), ("RUS", "Russia", False), ("RWA", "Rwanda", False),
    ("KNA", "Saint Kitts and Nevis", False), ("LCA", "Saint Lucia", False),
    ("VCT", "Saint Vincent and the Grenadines", False), ("WSM", "Samoa", False),
    ("SMR", "San Marino", False), ("STP", "Sao Tome and Principe", False),
    ("SAU", "Saudi Arabia", False), ("SEN", "Senegal", True), ("SRB", "Serbia", False),
    ("SYC", "Seychelles", False), ("SLE", "Sierra Leone", True), ("SGP", "Singapore", False),
    ("SVK", "Slovakia", False), ("SVN", "Slovenia", False), ("SLB", "Solomon Islands", False),
    ("SOM", "Somalia", False), ("ZAF", "South Africa", False), ("SSD", "South Sudan", True),
    ("ESP", "Spain", False), ("LKA", "Sri Lanka", False), ("SDN", "Sudan", True),
    ("SUR", "Suriname", True), ("SWE", "Sweden", False), ("CHE", "Switzerland", False),
    ("SYR", "Syria", False), ("TJK", "Tajikistan", False), ("TZA", "Tanzania", False),
    ("THA", "Thailand", False), ("TLS", "Timor-Leste", False), ("TGO", "Togo", True),
    ("TON", "Tonga", False), ("TTO", "Trinidad and Tobago", False), ("TUN", "Tunisia", False),
    ("TUR", "Turkey", False), ("TKM", "Turkmenistan", False), ("TUV", "Tuvalu", False),
    ("UGA", "Uganda", True), ("UKR", "Ukraine", False), ("ARE", "United Arab Emirates", False),
    ("GBR", "United Kingdom", False), ("USA", "United States", False), ("URY", "Uruguay", False),
    ("UZB", "Uzbekistan", False), ("VUT", "Vanuatu", False), ("VEN", "Venezuela", True),
    ("VNM", "Vietnam", False), ("YEM", "Yemen", False), ("ZMB", "Zambia", False), ("ZWE", "Zimbabwe", False)
]

def build_full_dataset(filename="countries_vaccines.json"):
    dataset = []
    
    for code, name, is_yf_endemic in ALL_COUNTRIES_RAW:
        # Default baseline vaccine profiles based on regional risk profile
        req_vaccines = []
        rec_vaccines = ["Hepatitis A", "Tetanus Booster"]
        malaria_note = "Low or no malaria transmission in most urban regions."
        
        # Require Yellow Fever certification if traveling to high-risk tropical areas
        yf_cert = True if is_yf_endemic else False
        if is_yf_endemic:
            req_vaccines.append("Yellow Fever Certificate (if coming from or transiting endemic zone)")
            malaria_note = "High risk present in tropical rural regions. Anti-malarial prophylaxis advised."
            rec_vaccines.extend(["Typhoid", "Hepatitis B", "Yellow Fever Vaccine"])

        dataset.append({
            "code": code,
            "name": name,
            "who_url": f"https://www.who.int/countries/{code.lower()}/",
            "isYellowFeverEndemic": is_yf_endemic,
            "requiresYellowFeverCertFromEndemicZone": yf_cert,
            "requiredVaccines": req_vaccines,
            "recommendedVaccines": list(set(rec_vaccines)),
            "malariaRisk": malaria_note
        })

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
    print(f"Generated static database for {len(dataset)} countries -> '{filename}'")


def build_malaria_dataset(filename="malaria_risk_countries.json"):
    """Download the latest OWID malaria-incidence value for each ISO3 country."""
    context = ssl.create_default_context(cafile=certifi.where())
    with urlopen(MALARIA_SOURCE_URL, timeout=20, context=context) as response:
        rows = list(csv.DictReader(response.read().decode("utf-8").splitlines()))

    latest_by_code = {}
    for row in rows:
        if not row["Code"]:
            continue
        current = latest_by_code.get(row["Code"])
        if current is None or int(row["Year"]) > int(current["year"]):
            latest_by_code[row["Code"]] = {
                "code": row["Code"],
                "name": row["Entity"],
                "year": int(row["Year"]),
                "incidence_per_1000_at_risk": float(row["Incidence of malaria (per 1,000 population at risk)"]),
            }

    with open(filename, "w", encoding="utf-8") as output_file:
        json.dump({
            "source_url": MALARIA_SOURCE_URL,
            "indicator": "New cases of malaria per 1,000 people at risk",
            "unit": "per 1,000 population at risk",
            "source": "World Health Organization (Global Health Observatory), via World Bank (2026), processed by Our World in Data",
            "countries": list(latest_by_code.values()),
        }, output_file, indent=2, ensure_ascii=False)
    print(f"Generated OWID malaria dataset for {len(latest_by_code)} countries -> '{filename}'")


def build_country_centroids(filename="country_centroids.json"):
    """Create simple map centroids from Natural Earth country geometry."""
    context = ssl.create_default_context(cafile=certifi.where())
    with urlopen(COUNTRY_GEOMETRY_URL, timeout=30, context=context) as response:
        features = json.load(response)["features"]

    centroids = {}
    for feature in features:
        code = feature["properties"].get("ISO3166-1-Alpha-3")
        coordinates = feature["geometry"]["coordinates"]
        points = []

        def collect_points(value):
            if value and isinstance(value[0], (int, float)):
                points.append(value)
            else:
                for child in value:
                    collect_points(child)

        collect_points(coordinates)
        if code and points:
            centroids[code] = {
                "longitude": sum(point[0] for point in points) / len(points),
                "latitude": sum(point[1] for point in points) / len(points),
            }

    with open(filename, "w", encoding="utf-8") as output_file:
        json.dump(centroids, output_file, indent=2)
    print(f"Generated centroids for {len(centroids)} countries -> '{filename}'")

if __name__ == "__main__":
    build_full_dataset()
    build_malaria_dataset()
    build_country_centroids()