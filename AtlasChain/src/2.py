import folium
import json
import os
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QCheckBox, QPushButton, QMessageBox
from PyQt5.QtWebEngineWidgets import QWebEngineView

# File paths
base_dir = '/AtlasChain'
map_html_file = os.path.join(base_dir, 'assets', 'infrastructure_map.html')
relocated_data_file = os.path.join(base_dir, 'data', 'relocated_all_infrastructure.json')
relocated_map_file = os.path.join(base_dir, 'assets', 'relocated_map.html')

# Load critical infrastructure data
with open(os.path.join(base_dir, 'data', 'infrastructure_data.json'), 'r') as file:
    infrastructure_data = json.load(file)


# Function to create a dynamic map
def create_map(data, show_threat, show_flood, show_fire):
    dynamic_map = folium.Map(location=[37.9838, 23.7275], zoom_start=6)

    # Add static markers for infrastructure
    for item in data.get("electricity", []):
        folium.Marker(
            location=[item["lat"], item["lon"]],
            icon=folium.Icon(icon="bolt", color="red"),
            popup=item["name"]
        ).add_to(dynamic_map)

    for item in data.get("water", []):
        folium.Marker(
            location=[item["lat"], item["lon"]],
            icon=folium.Icon(icon="tint", color="blue"),
            popup=item["name"]
        ).add_to(dynamic_map)

    for item in data.get("ports", []):
        folium.Marker(
            location=[item["lat"], item["lon"]],
            icon=folium.Icon(icon="anchor", color="darkblue"),
            popup=item["name"]
        ).add_to(dynamic_map)

    # Add dynamic circles
    if show_threat:
        for item in data.get("countries", []):
            score = item.get("score", 0)
            fill_opacity = 0.1 + (score / 10) * 0.7
            radius = (50000 + (score * 10000)) * 2

            adjusted_lat = item.get("lat", 0) - 0.2
            adjusted_lon = item.get("lon", 0) - 0.2

            folium.Circle(
                location=[adjusted_lat, adjusted_lon],
                radius=radius,
                color=None,
                weight=0,
                fill=True,
                fill_color="red",
                fill_opacity=fill_opacity,
                popup=f"Threat level: {score} (Radius: {radius} meters)"
            ).add_to(dynamic_map)

    if show_flood:
        for item in data.get("flood_zones", []):
            severity = item.get("severity", 0)
            fill_opacity = 0.1 + (severity / 10) * 0.7
            radius = (30000 + (severity * 8000)) / 2

            adjusted_lat = item.get("lat", 0) + 0.1
            adjusted_lon = item.get("lon", 0) + 0.1

            folium.Circle(
                location=[adjusted_lat, adjusted_lon],
                radius=radius,
                color=None,
                weight=0,
                fill=True,
                fill_color="blue",
                fill_opacity=fill_opacity,
                popup=f"Flood severity: {severity} (Radius: {radius} meters)"
            ).add_to(dynamic_map)

    if show_fire:
        for item in data.get("fire_risk_zones", []):
            risk = item.get("risk", 0)
            fill_opacity = 0.1 + (risk / 10) * 0.7
            radius = (40000 + (risk * 5000))

            adjusted_lat = item.get("lat", 0) - 0.1
            adjusted_lon = item.get("lon", 0) - 0.1

            folium.Circle(
                location=[adjusted_lat, adjusted_lon],
                radius=radius,
                color=None,
                weight=0,
                fill=True,
                fill_color="orange",
                fill_opacity=fill_opacity,
                popup=f"Fire risk: {risk} (Radius: {radius} meters)"
            ).add_to(dynamic_map)

    return dynamic_map


# Function to create and save the relocated map
def create_relocated_map():
    if not os.path.exists(relocated_data_file):
        QMessageBox.critical(None, "Error", f"Relocated data file not found: {relocated_data_file}")
        return

    with open(relocated_data_file, 'r') as file:
        relocated_data = json.load(file)

    relocated_map = create_map(relocated_data, True, True, True)
    relocated_map.save(relocated_map_file)


# Main Map Window
class MapWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Critical Infrastructure Map")
        self.setGeometry(100, 100, 1000, 800)

        # State for toggles
        self.show_threat_circles = False
        self.show_flood_circles = False
        self.show_fire_risk_circles = False

        # Create central widget and layout
        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)

        self.webview = QWebEngineView()
        self.refresh_map()

        # Checkboxes
        self.add_threat_circles_checkbox = QCheckBox("Add/Remove Threat Circles")
        self.add_flood_circles_checkbox = QCheckBox("Add/Remove Flood Zones")
        self.add_fire_risk_circles_checkbox = QCheckBox("Add/Remove Fire Risk Zones")

        # Connect checkboxes to their respective methods
        self.add_threat_circles_checkbox.stateChanged.connect(self.update_threat_circles)
        self.add_flood_circles_checkbox.stateChanged.connect(self.update_flood_circles)
        self.add_fire_risk_circles_checkbox.stateChanged.connect(self.update_fire_risk_circles)

        # Recommend Improvements Button
        self.recommend_button = QPushButton("Recommend Improvements")
        self.recommend_button.clicked.connect(self.recommend_improvements)

        # Add widgets to layout
        layout.addWidget(self.webview)
        layout.addWidget(self.add_threat_circles_checkbox)
        layout.addWidget(self.add_flood_circles_checkbox)
        layout.addWidget(self.add_fire_risk_circles_checkbox)
        layout.addWidget(self.recommend_button)

        self.setCentralWidget(central_widget)

    def update_threat_circles(self):
        self.show_threat_circles = self.add_threat_circles_checkbox.isChecked()
        self.refresh_map()

    def update_flood_circles(self):
        self.show_flood_circles = self.add_flood_circles_checkbox.isChecked()
        self.refresh_map()

    def update_fire_risk_circles(self):
        self.show_fire_risk_circles = self.add_fire_risk_circles_checkbox.isChecked()
        self.refresh_map()

    def refresh_map(self):
        dynamic_map = create_map(
            infrastructure_data,
            self.show_threat_circles,
            self.show_flood_circles,
            self.show_fire_risk_circles
        )
        dynamic_map.save(map_html_file)
        self.webview.setUrl(QUrl.fromLocalFile(map_html_file))

    def recommend_improvements(self):
        recommendations = []

        for item in infrastructure_data["countries"]:
            if item["score"] > 7:
                recommendations.append(
                    f"High-threat area near ({item['lat']}, {item['lon']}). Increase security measures."
                )

        for item in infrastructure_data["flood_zones"]:
            if item["severity"] > 6:
                recommendations.append(
                    f"Flood-prone area near ({item['lat']}, {item['lon']}). Improve drainage systems."
                )

        for item in infrastructure_data["fire_risk_zones"]:
            if item["risk"] > 6:
                recommendations.append(
                    f"High fire risk near ({item['lat']}, {item['lon']}). Implement vegetation control."
                )

        if recommendations:
            QMessageBox.information(self, "Recommendations", "\n".join(recommendations))
        else:
            QMessageBox.information(self, "Recommendations", "No critical improvements needed.")

        create_relocated_map()
        self.relocated_map_window = RelocatedMapWindow()
        self.relocated_map_window.show()


# Class for displaying the relocated infrastructure map
class RelocatedMapWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Relocated Infrastructure Map")
        self.setGeometry(150, 150, 1000, 800)

        # State for toggles
        self.show_threat_circles = True
        self.show_flood_circles = True
        self.show_fire_risk_circles = True

        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)

        self.webview = QWebEngineView()
        self.refresh_map()

        # Add toggle checkboxes for the relocated map
        self.add_threat_circles_checkbox = QCheckBox("Add/Remove Threat Circles")
        self.add_flood_circles_checkbox = QCheckBox("Add/Remove Flood Zones")
        self.add_fire_risk_circles_checkbox = QCheckBox("Add/Remove Fire Risk Zones")

        self.add_threat_circles_checkbox.setChecked(True)
        self.add_flood_circles_checkbox.setChecked(True)
        self.add_fire_risk_circles_checkbox.setChecked(True)

        # Connect checkboxes to their respective handlers
        self.add_threat_circles_checkbox.stateChanged.connect(self.update_threat_circles)
        self.add_flood_circles_checkbox.stateChanged.connect(self.update_flood_circles)
        self.add_fire_risk_circles_checkbox.stateChanged.connect(self.update_fire_risk_circles)

        layout.addWidget(self.webview)
        layout.addWidget(self.add_threat_circles_checkbox)
        layout.addWidget(self.add_flood_circles_checkbox)
        layout.addWidget(self.add_fire_risk_circles_checkbox)
        self.setCentralWidget(central_widget)

    def update_threat_circles(self):
        self.show_threat_circles = self.add_threat_circles_checkbox.isChecked()
        self.refresh_map()

    def update_flood_circles(self):
        self.show_flood_circles = self.add_flood_circles_checkbox.isChecked()
        self.refresh_map()

    def update_fire_risk_circles(self):
        self.show_fire_risk_circles = self.add_fire_risk_circles_checkbox.isChecked()
        self.refresh_map()

    def refresh_map(self):
        with open(relocated_data_file, 'r') as file:
            relocated_data = json.load(file)

        dynamic_map = create_map(
            relocated_data,
            self.show_threat_circles,
            self.show_flood_circles,
            self.show_fire_risk_circles
        )
        dynamic_map.save(relocated_map_file)
        self.webview.setUrl(QUrl.fromLocalFile(relocated_map_file))


# Initialize application
app = QApplication([])

# Start the main window
main_window = MapWindow()
main_window.show()

# Run the application event loop
app.exec_()
