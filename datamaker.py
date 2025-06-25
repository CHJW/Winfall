import csv
import random
import datetime
import math

# Offshore wind farm locations (realistic clusters)
WIND_FARM_CLUSTERS = [
    {"name": "North Sea Alpha", "center_lat": 54.5, "center_lon": 2.0},
    {"name": "North Sea Beta", "center_lat": 55.2, "center_lon": 1.5},
    {"name": "Baltic Wind", "center_lat": 55.8, "center_lon": 15.2},
]

# Component specifications with realistic costs and characteristics
COMPONENT_SPECS = {
    "Blade": {
        "lifetime_years": 20,
        "replacement_cost": 200000,
        "salvage_value": 20000,
        "criticality_level": "critical",
        "power_impact_factor": 0.95,  # 95% power loss if failed
        "repair_hours": 48
    },
    "Gearbox": {
        "lifetime_years": 15,
        "replacement_cost": 500000,
        "salvage_value": 50000,
        "criticality_level": "critical",
        "power_impact_factor": 1.0,  # 100% power loss if failed
        "repair_hours": 72
    },
    "Generator": {
        "lifetime_years": 18,
        "replacement_cost": 300000,
        "salvage_value": 30000,
        "criticality_level": "critical",
        "power_impact_factor": 1.0,
        "repair_hours": 60
    },
    "Transformer": {
        "lifetime_years": 25,
        "replacement_cost": 150000,
        "salvage_value": 15000,
        "criticality_level": "important",
        "power_impact_factor": 1.0,
        "repair_hours": 36
    },
    "Control_System": {
        "lifetime_years": 10,
        "replacement_cost": 80000,
        "salvage_value": 8000,
        "criticality_level": "important",
        "power_impact_factor": 0.2,
        "repair_hours": 24
    },
    "Yaw_System": {
        "lifetime_years": 20,
        "replacement_cost": 120000,
        "salvage_value": 12000,
        "criticality_level": "routine",
        "power_impact_factor": 0.1,
        "repair_hours": 18
    }
}

def generate_clustered_coordinates(cluster, spread_km=10):
    """Generate coordinates within a cluster with realistic spread"""
    # Convert km to approximate degrees (rough approximation)
    lat_spread = spread_km / 111.0  # 1 degree lat ≈ 111 km
    lon_spread = spread_km / (111.0 * math.cos(math.radians(cluster["center_lat"])))
    
    latitude = cluster["center_lat"] + random.uniform(-lat_spread, lat_spread)
    longitude = cluster["center_lon"] + random.uniform(-lon_spread, lon_spread)
    return latitude, longitude

def generate_random_installation_date():
    """Generate installation date within last 10 years"""
    start_date = datetime.date.today() - datetime.timedelta(days=10*365)
    end_date = datetime.date.today() - datetime.timedelta(days=365)  # At least 1 year old
    random_date = start_date + datetime.timedelta(days=random.randint(0, (end_date - start_date).days))
    return random_date

def calculate_water_depth(latitude, longitude):
    """Simulate water depth based on distance from shore (simplified)"""
    # Rough simulation - deeper water further from typical shore coordinates
    distance_factor = abs(latitude - 54.0) + abs(longitude - 1.0)
    base_depth = 20 + (distance_factor * 5)
    return round(base_depth + random.uniform(-5, 15), 1)

def generate_turbine_data():
    """Generate realistic turbine specifications"""
    power_ratings = [2.0, 3.0, 3.6, 5.0, 6.0, 8.0]  # MW
    power_rating = random.choice(power_ratings)
    
    # Current output as percentage of rated (accounting for maintenance issues)
    current_output_factor = random.uniform(0.7, 1.0)
    
    return {
        "power_rating": power_rating,
        "current_output": power_rating * current_output_factor,
        "energy_price_mwh": random.uniform(45, 65)  # $/MWh
    }

# Generate data for 25 nodes across wind farm clusters
nodes_data = []
for i in range(25):
    # Assign to random cluster
    cluster = random.choice(WIND_FARM_CLUSTERS)
    latitude, longitude = generate_clustered_coordinates(cluster)
    
    # Generate turbine specifications
    turbine_data = generate_turbine_data()
    
    # Generate installation date (same for all components on a turbine)
    installation_date = generate_random_installation_date()
    
    # Water depth
    water_depth = calculate_water_depth(latitude, longitude)
    
    # Generate components for this turbine
    components = []
    for comp_name, specs in COMPONENT_SPECS.items():
        # Add some variation to installation dates (±6 months)
        comp_install_date = installation_date + datetime.timedelta(days=random.randint(-180, 180))
        
        # Some components might be replaced (newer installation date)
        if random.random() < 0.2:  # 20% chance of replacement
            comp_install_date = installation_date + datetime.timedelta(days=random.randint(365, 3*365))
        
        components.append({
            "name": comp_name,
            "lifetime_years": specs["lifetime_years"],
            "serial_number": f"{comp_name[:2].upper()}{i+1:02d}",
            "installation_date": comp_install_date,
            "replacement_cost": specs["replacement_cost"],
            "salvage_value": specs["salvage_value"],
            "criticality_level": specs["criticality_level"],
            "power_impact_factor": specs["power_impact_factor"],
            "repair_hours": specs["repair_hours"]
        })
    
    nodes_data.append({
        "node_id": f"WTG_{i+1:02d}",
        "latitude": latitude,
        "longitude": longitude,
        "water_depth": water_depth,
        "power_rating": turbine_data["power_rating"],
        "current_output": turbine_data["current_output"],
        "energy_price_mwh": turbine_data["energy_price_mwh"],
        "cluster_name": cluster["name"],
        "components": components
    })

# Write data to CSV file with enhanced structure
with open('nodes_data.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow([
        "Node_ID", "Latitude", "Longitude", "Water_Depth", "Power_Rating", 
        "Current_Output", "Energy_Price_MWh", "Cluster_Name",
        "Component_Name", "Lifetime_Years", "Serial_Number", "Installation_Date",
        "Replacement_Cost", "Salvage_Value", "Criticality_Level", 
        "Power_Impact_Factor", "Repair_Hours"
    ])
    
    for node in nodes_data:
        for component in node["components"]:
            writer.writerow([
                node["node_id"],
                node["latitude"],
                node["longitude"],
                node["water_depth"],
                node["power_rating"],
                node["current_output"],
                node["energy_price_mwh"],
                node["cluster_name"],
                component["name"],
                component["lifetime_years"],
                component["serial_number"],
                component["installation_date"],
                component["replacement_cost"],
                component["salvage_value"],
                component["criticality_level"],
                component["power_impact_factor"],
                component["repair_hours"]
            ])

print(f"Enhanced CSV file 'nodes_data.csv' has been created with {len(nodes_data)} turbines.")
print(f"Total components: {sum(len(node['components']) for node in nodes_data)}")
print(f"Wind farm clusters: {[cluster['name'] for cluster in WIND_FARM_CLUSTERS]}")