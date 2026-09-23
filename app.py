from datetime import date, timedelta
import ast
import base64
import json
import ssl
from pathlib import Path
from urllib.request import Request, urlopen

import certifi

import streamlit as st
import plotly.graph_objects as go


def find_data_file(filename):
	for data_path in [Path(__file__).with_name(filename), Path(__file__).parent / ".venv" / "bin" / filename]:
		if data_path.exists():
			return data_path
	return None


def load_country_catalog():
	generator_path = find_data_file("build_static_dataset.py")
	if generator_path is None:
		return []
	tree = ast.parse(generator_path.read_text(encoding="utf-8"))
	for node in tree.body:
		if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "ALL_COUNTRIES_RAW" for target in node.targets):
			return [{"code": code, "name": name, "is_yf_endemic": endemic} for code, name, endemic in ast.literal_eval(node.value)]
	return []


def load_vaccine_data():
	vaccine_path = find_data_file("countries_vaccines.json")
	if vaccine_path is None:
		return {}
	with vaccine_path.open(encoding="utf-8") as data_file:
		return {country["name"]: country for country in json.load(data_file)}


def load_yellow_fever_risk_data():
	risk_path = find_data_file("yellow_fever_risk_countries.json")
	if risk_path is None:
		return set()
	with risk_path.open(encoding="utf-8") as data_file:
		return {country["name"] for country in json.load(data_file)["countries"]}


def load_malaria_data():
	malaria_path = find_data_file("malaria_risk_countries.json")
	if malaria_path is None:
		return {}
	with malaria_path.open(encoding="utf-8") as data_file:
		return {country["code"]: country for country in json.load(data_file)["countries"]}


def load_country_centroids():
	centroid_path = find_data_file("country_centroids.json")
	if centroid_path is None:
		return {}
	with centroid_path.open(encoding="utf-8") as data_file:
		return json.load(data_file)


@st.cache_data(ttl=1800)
def load_who_outbreak_news():
	request = Request(
		"https://extranet.who.int/publicemergency/api/Indicators",
		data=b"",
		method="POST",
		headers={"User-Agent": "VaxTrack/1.0"},
	)
	context = ssl.create_default_context(cafile=certifi.where())
	with urlopen(request, timeout=10, context=context) as response:
		payload = json.load(response)
	return payload.get("Data", [])


def load_children_vaccine_data():
	children_path = find_data_file("travel_vaccines_children.py")
	if children_path is None:
		return []
	tree = ast.parse(children_path.read_text(encoding="utf-8"))
	for node in tree.body:
		if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "VACCINES" for target in node.targets):
			return eval(compile(ast.Expression(node.value), str(children_path), "eval"), {"__builtins__": {}}, {})
	return []


COUNTRY_CATALOG = load_country_catalog()
VACCINE_DATA = load_vaccine_data()
YELLOW_FEVER_RISK_COUNTRIES = load_yellow_fever_risk_data()
MALARIA_DATA = load_malaria_data()
COUNTRY_CENTROIDS = load_country_centroids()
CHILDREN_VACCINES = load_children_vaccine_data()
ICON_PATH = find_data_file("icon.png")


def load_emergency_numbers():
	data_paths = [
		Path(__file__).with_name("emergency_numbers.json"),
		Path(__file__).parent / ".venv" / "bin" / "emergency_numbers.json",
	]
	for data_path in data_paths:
		if data_path.exists():
			with data_path.open(encoding="utf-8") as data_file:
				return json.load(data_file)["countries"]
	return []


EMERGENCY_NUMBERS = {country["name"]: country for country in load_emergency_numbers()}

st.set_page_config(page_title="VaxTrack", page_icon=str(ICON_PATH) if ICON_PATH else "✈️", layout="wide")
if "overview_shown" not in st.session_state:
	st.session_state.overview_shown = False

icon_data = base64.b64encode(ICON_PATH.read_bytes()).decode("ascii") if ICON_PATH else ""
icon_markup = f'<img src="data:image/png;base64,{icon_data}" width="112" style="display:block; border-radius:12px;">' if icon_data else ""
st.markdown(
	"""
	<style>
		html, body {
			overflow-x: hidden !important;
		}
		[data-testid="stAppViewContainer"] > .main {
			padding-top: 1rem;
			position: relative;
			z-index: 2;
		}
		[data-testid="stAppViewContainer"],
		[data-testid="stAppViewContainer"] > .main {
			overflow: visible !important;
		}
		[data-testid="stAppViewContainer"] {
			overflow-x: hidden !important;
		}
		section[data-testid="stSidebar"] {
			display: none !important;
		}
	</style>
	""",
	unsafe_allow_html=True,
)
st.markdown(
	f"""
	<div style="background:#ffd928; padding:1rem 1.5rem; position:relative; left:50%; transform:translateX(-50%); width:100vw; box-sizing:border-box; z-index:10000; display:flex; align-items:center; gap:1.25rem; border-bottom:1px solid #d6b500;">
		{icon_markup}
		<div style="color:#14213d; max-width:900px;">
			<div style="font-size:0.9rem; font-weight:600; text-transform:uppercase;">Travel health planner</div>
			<div style="font-size:2rem; font-weight:800; line-height:1.15; margin:0.2rem 0 0.45rem;">Plan with confidence</div>
			<div style="font-size:1rem; line-height:1.5;">Tell us where you are travelling from and where you are going. VaxTrack gathers the entry vaccination requirements, recommended vaccines and current health advisories for that route in one place.</div>
		</div>
	</div>
	""",
	unsafe_allow_html=True,
)
input_column, dashboard_column = st.columns([0.28, 0.72])
with input_column:
	st.header("Trip inputs")
	country_names = [country["name"] for country in COUNTRY_CATALOG]
	departure_country = st.selectbox("Departure country", country_names, index=country_names.index("Sweden"))
	destination_country = st.selectbox("Destination country", country_names, index=country_names.index("Vietnam"))
	departure_date = st.date_input("Departure date", value=date.today() + timedelta(days=30), min_value=date.today())
	traveler_count = st.slider("Number of travelers", min_value=1, max_value=6, value=2)
	st.subheader("Traveler ages")
	traveler_ages = []
	for traveler_number in range(traveler_count):
		traveler_ages.append(
			st.number_input(
				f"Traveler {traveler_number + 1}",
				min_value=0,
				max_value=120,
				value=42 if traveler_number == 0 else 10,
				key=f"traveler_age_{traveler_number}",
			)
		)
	if st.button("Show my travel health overview", type="primary", use_container_width=True):
		st.session_state.overview_shown = True

with dashboard_column:
	st.header("Trip summary")
	days_until_departure = (departure_date - date.today()).days
	summary_columns = st.columns(3)
	summary_columns[0].metric("Route", f"{departure_country} → {destination_country}")
	summary_columns[1].metric("Travelers", traveler_count)
	summary_columns[2].metric("Days until departure", days_until_departure)
	if days_until_departure <= 14:
		st.info("Preparation reminder: this demo trip is within 14 days. Treat this as an interface trigger, not a medical deadline.")

	st.header("Latest WHO outbreak information")
	selected_country = next((country for country in COUNTRY_CATALOG if country["name"] == destination_country), None)
	try:
		who_news = load_who_outbreak_news()
		matching_news = [item for item in who_news if item.get("level_code", "").lower() == "donsindicators" and selected_country and item.get("value3", "").upper() == selected_country["code"]]
		if matching_news:
			latest_news = max(matching_news, key=lambda item: item.get("value4", ""))
			st.info(f"**{latest_news.get('value1', 'Disease outbreak news')}** — {latest_news.get('value4', 'Date unavailable')}\n\nWHO reports the latest listed Disease Outbreak News item for **{destination_country}**. [Read the WHO report]({latest_news.get('value5', 'https://extranet.who.int/publicemergency/#')})")
		else:
			st.info(f"No destination-specific Disease Outbreak News item is currently listed by WHO for {destination_country}.")
		st.caption("WHO Health Emergency Dashboard data refreshes approximately every 30 minutes and is not a comprehensive list of all health events.")
	except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError):
		st.warning("WHO outbreak information is temporarily unavailable. View the [WHO Health Emergency Dashboard](https://extranet.who.int/publicemergency/#) directly.")

	st.header("Travel health overview")
	if not st.session_state.overview_shown:
		st.info("Choose your trip details and select “Show my travel health overview” to see the demo results.")
	else:
		route_data = VACCINE_DATA.get(destination_country)
		if route_data is None:
			st.info("This destination is not covered by the vaccine dataset. Missing data does not mean there are no requirements or recommendations.")
		else:
			st.caption("Requirements and recommendations are loaded from the local vaccine dataset.")
			for section_name, data_key, empty_text in [("Entry vaccination requirements", "requiredVaccines", "No entry requirements are listed in the dataset."), ("Recommended vaccinations", "recommendedVaccines", "No recommendations are listed in the dataset.")]:
				st.subheader(section_name)
				items = route_data[data_key]
				if data_key == "requiredVaccines" and route_data.get("requiresYellowFeverCertFromEndemicZone") and departure_country in YELLOW_FEVER_RISK_COUNTRIES:
					st.error(f"Yellow fever certificate condition triggered: {departure_country} is listed as a yellow-fever-risk origin, and {destination_country} requires proof when arriving from a risk country.")
				if not items:
					st.info(empty_text)
				for item in items:
					with st.container(border=True):
						status = "Required" if data_key == "requiredVaccines" else "Recommended"
						status_color = "#f8d7da" if status == "Required" else "#fff3cd"
						status_text_color = "#842029" if status == "Required" else "#664d03"
						st.markdown(f"**{item}**")
						st.markdown(f'<span style="background-color: {status_color}; color: {status_text_color}; padding: 0.2rem 0.5rem; border-radius: 0.25rem; font-size: 0.85rem;">{status}</span>', unsafe_allow_html=True)

		if any(age <= 18 for age in traveler_ages):
			st.subheader("Child traveler information")
			st.caption("Age-banded reference information from the local children vaccine dataset. This is educational information, not medical advice.")
			for traveler_number, age in enumerate(traveler_ages, start=1):
				if age > 18:
					continue
				age_months = age * 12
				matching_vaccines = []
				for vaccine in CHILDREN_VACCINES:
					matching_bands = [band for band in vaccine["age_bands"] if band["min_m"] <= age_months <= band["max_m"]]
					if age_months >= vaccine["min_age_months"] and matching_bands:
						matching_vaccines.append((vaccine, matching_bands))
				with st.container(border=True):
					st.markdown(f"**Traveler {traveler_number}: age {age}**")
					if not matching_vaccines:
						st.info("No child vaccine information in the dataset matches this age.")
					for vaccine, matching_bands in matching_vaccines:
						st.markdown(f"**{vaccine['name']}**")
						st.write(vaccine["summary"])
						for band in matching_bands:
							st.success(f"Applicable age band: {band['label']} — {band['detail']}")
						st.caption(f"Travel context: {vaccine['travel_trigger']} Source: {vaccine['source']}")

st.header("Health risk map")
map_view = st.radio("Map view", ["Yellow fever", "Malaria"], horizontal=True)
if map_view == "Yellow fever":
	map_caption = "Countries highlighted in yellow are listed in the local yellow-fever risk dataset."
	map_rows = [{
		"iso3": country["code"],
		"country": country["name"],
		"risk": 1 if country["name"] in YELLOW_FEVER_RISK_COUNTRIES else 0,
		"detail": "Listed yellow-fever risk" if country["name"] in YELLOW_FEVER_RISK_COUNTRIES else "No listed yellow-fever risk",
	} for country in COUNTRY_CATALOG]
	colorscale = [[0, "#e7edf3"], [0.49, "#e7edf3"], [0.5, "#f2c94c"], [1, "#f2c94c"]]
else:
	map_caption = "Malaria colors show the latest OWID incidence of new cases per 1,000 people at risk. Darker red indicates a higher reported incidence; grey means no OWID value."
	map_rows = [{
		"iso3": country["code"],
		"country": country["name"],
		"risk": MALARIA_DATA.get(country["code"], {}).get("incidence_per_1000_at_risk"),
		"detail": f"{MALARIA_DATA[country['code']]['incidence_per_1000_at_risk']:.1f} cases per 1,000 people at risk ({MALARIA_DATA[country['code']]['year']})" if country["code"] in MALARIA_DATA else "No OWID malaria value",
	} for country in COUNTRY_CATALOG]
	colorscale = "Reds"
st.caption(f"{map_caption} This is a screening reference, not a complete medical or travel-entry assessment.")
map_figure = go.Figure(go.Choropleth(
	locations=[row["iso3"] for row in map_rows],
	locationmode="ISO-3",
	z=[row["risk"] if row["risk"] is not None else 0 for row in map_rows],
	text=[row["country"] for row in map_rows],
	customdata=[[row["detail"]] for row in map_rows],
	colorscale=colorscale,
	zmin=0,
	zmax=max((row["risk"] or 0 for row in map_rows), default=1) if map_view == "Malaria" else 1,
	showscale=False,
	marker_line_color="white",
	marker_line_width=0.35,
	hovertemplate="<b>%{text}</b><br>%{customdata[0]}<extra></extra>",
))
origin = next((country for country in COUNTRY_CATALOG if country["name"] == departure_country), None)
destination = next((country for country in COUNTRY_CATALOG if country["name"] == destination_country), None)
if origin and destination and origin["code"] in COUNTRY_CENTROIDS and destination["code"] in COUNTRY_CENTROIDS:
	origin_point = COUNTRY_CENTROIDS[origin["code"]]
	destination_point = COUNTRY_CENTROIDS[destination["code"]]
	map_figure.add_trace(go.Scattergeo(
		lon=[origin_point["longitude"], destination_point["longitude"]],
		lat=[origin_point["latitude"], destination_point["latitude"]],
		mode="lines+markers",
		line={"color": "#14213d", "width": 3, "dash": "dash"},
		marker={"size": 9, "color": ["#14213d", "#d94841"]},
		text=[f"Origin: {departure_country}", f"Destination: {destination_country}"],
		hovertemplate="%{text}<extra></extra>",
		name="Trip route",
	))
map_figure.update_geos(showframe=False, showcoastlines=True, coastlinecolor="#aab4c0", projection_type="natural earth")
map_figure.update_layout(height=480, margin={"r": 0, "t": 0, "l": 0, "b": 0}, paper_bgcolor="rgba(0,0,0,0)")
st.plotly_chart(map_figure, use_container_width=True, config={"displayModeBar": False})

st.header("Emergency numbers")
emergency_data = EMERGENCY_NUMBERS.get(destination_country)
if emergency_data is None:
	st.info("Emergency numbers are not covered for this destination in the dataset.")
else:
	st.caption(f"Dataset status: {emergency_data['status']}. Numbers are for {emergency_data['name']} and may not provide nationwide coverage.")
	emergency_columns = st.columns(3)
	for contact_index, contact in enumerate(emergency_data["contacts"]):
		services = []
		for service in contact["services"]:
			service_label = service.title()
			if service == "other":
				service_label = f"Other ({contact['dialing_notes']})"
			services.append(service_label)
		with emergency_columns[contact_index % 3]:
			st.metric(", ".join(services), contact["number"])
	if emergency_data["services_not_documented"]:
		missing_services = ", ".join(service.title() for service in emergency_data["services_not_documented"])
		st.caption(f"Services not documented in the dataset: {missing_services}.")
	st.caption(f"Source: [{emergency_data['source']['name']}]({emergency_data['source']['url']})")

st.header("Sources")
st.write("Use these resources to verify current information. The supplied WHO document is from 2022 and does not replace current official guidance or medical advice.")
st.markdown("- [WHO travel advice](https://www.who.int/health-topics/travel-and-health)\n- [CDC Travelers' Health](https://wwwnc.cdc.gov/travel)")