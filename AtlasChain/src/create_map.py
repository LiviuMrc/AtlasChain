import folium
import json

# Load critical infrastructure data from JSON file
with open('../data/infrastructure_data.json', 'r') as file:
    infrastructure_data = json.load(file)

# Create a folium map centered on Greece
greece_map = folium.Map(location=[37.9838, 23.7275], zoom_start=6)


# Function to add markers for electricity
def add_electricity_map(map_object, data):
    for item in data:
        folium.Marker(
            location=[item["lat"], item["lon"]],
            icon=folium.Icon(icon="star", color="red"),
            popup=item["name"]
        ).add_to(map_object)


# Function to add markers for water
def add_water_map(map_object, data):
    for item in data:
        folium.Marker(
            location=[item["lat"], item["lon"]],
            icon=folium.Icon(icon="star", color="blue"),
            popup=item["name"]
        ).add_to(map_object)


# Function to add highway line
def add_highway_map(map_object, data):
    # Extract the coordinates for the line segment
    coordinates = [[item["lat"], item["lon"]] for item in data]

    # Add the line segment to the map
    folium.PolyLine(
        locations=coordinates,
        color="red",  # Line color
        weight=5,  # Line thickness
        opacity=0.8,  # Transparency
        popup="Highway Segment"  # Optional popup for the segment
    ).add_to(map_object)


# Function to add markers for ports/airports
def add_ports_airports_map(map_object, data):
    for item in data:
        folium.Marker(
            location=[item["lat"], item["lon"]],
            icon=folium.Icon(color="blue"),
            popup=item["name"]
        ).add_to(map_object)


# Function to add markers for military bases
def add_military_base_map(map_object, data):
    for item in data:
        folium.Marker(
            location=[item["lat"], item["lon"]],
            icon=folium.Icon(color="darkred"),
            popup=item["name"]
        ).add_to(map_object)


# Function to add large circles for neighboring countries based on scores
def add_country_circles(map_object, data):
    for item in data:
        # Map the score to opacity (1 = very light, 10 = max 80%)
        score = item["score"]
        fill_opacity = 0.1 + (score / 10) * 0.7  # Scale between 0.1 and 0.8
        border_opacity = fill_opacity * 0.5  # Border fades more than fill

        # Add a circle for each country with fading border and fill
        folium.Circle(
            location=[item["lat"], item["lon"]],
            radius=50000 + (score * 10000),  # Adjust radius dynamically
            color="red",  # Border color
            weight=2,  # Thin border
            opacity=border_opacity,  # Fading border effect
            fill=True,
            fill_color="red",
            fill_opacity=fill_opacity,  # Dynamic fill opacity
            popup=f"{item['name']} (Score: {score}, Fill Opacity: {fill_opacity:.1f}, Border Opacity: {border_opacity:.1f})"
        ).add_to(map_object)

# Add different types of infrastructure to the map
add_electricity_map(greece_map, infrastructure_data["electricity"])
add_water_map(greece_map, infrastructure_data["water"])
add_highway_map(greece_map, infrastructure_data["highways"])
add_ports_airports_map(greece_map, infrastructure_data["ports"])
add_ports_airports_map(greece_map, infrastructure_data["airports"])
add_military_base_map(greece_map, infrastructure_data["military_bases"])

# Add neighboring countries with scores
add_country_circles(greece_map, infrastructure_data["countries"])

# Save the map as an HTML file
greece_map.save('../assets/infrastructure_map.html')

print("Map created successfully and saved to 'infrastructure_map.html'")
