import csv
import random
import datetime

# Function to generate random latitude and longitude
def generate_random_coordinates():
    latitude = random.uniform(-90, 90)
    longitude = random.uniform(-180, 180)
    return latitude, longitude

# Function to generate random installation date
def generate_random_installation_date():
    # Randomly choose a date within the last 5 years
    start_date = datetime.date.today() - datetime.timedelta(days=5*365)
    end_date = datetime.date.today()
    random_date = start_date + datetime.timedelta(days=random.randint(0, (end_date - start_date).days))
    return random_date

# Generate data for 20 nodes
nodes_data = []
for i in range(20):
    latitude, longitude = generate_random_coordinates()
    installation_date = generate_random_installation_date()
    components = [
        {"name": "Blade", "lifetime": 20, "serial_number": f"BL{i+1}A", "installation_date": installation_date},
        {"name": "Blade", "lifetime": 20, "serial_number": f"BL{i+1}B", "installation_date": installation_date},
        {"name": "Blade", "lifetime": 20, "serial_number": f"BL{i+1}C", "installation_date": installation_date},
        {"name": "Motor", "lifetime": 15, "serial_number": f"MT{i+1}", "installation_date": installation_date},
        {"name": "Shaft", "lifetime": 25, "serial_number": f"SH{i+1}", "installation_date": installation_date},
        {"name": "Casing", "lifetime": 30, "serial_number": f"CS{i+1}", "installation_date": installation_date}
    ]
    nodes_data.append({
        "latitude": latitude,
        "longitude": longitude,
        "components": components
    })

# Write data to CSV file
with open('nodes_data.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Latitude", "Longitude", "Component Name", "Lifetime", "Serial Number", "Installation Date"])
    for node in nodes_data:
        for component in node["components"]:
            writer.writerow([
                node["latitude"],
                node["longitude"],
                component["name"],
                component["lifetime"],
                component["serial_number"],
                component["installation_date"]
            ])

print("CSV file 'nodes_data.csv' has been created.")