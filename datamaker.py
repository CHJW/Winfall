import csv
import random
import datetime
import math
import os
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import simpledialog

class DataMakerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Wind Farm Data Generator")
        self.root.geometry("500x700")
        
        # Track last generated file
        self.last_generated_file = None
        
        # Default values
        self.default_values = {
            'filename': 'nodes_data',
            'installation_date': datetime.date.today() - datetime.timedelta(days=2*365),
            'num_clusters': 3,
            'blade_lifetime': 20,
            'gearbox_lifetime': 15,
            'generator_lifetime': 18,
            'transformer_lifetime': 25,
            'control_system_lifetime': 10,
            'yaw_system_lifetime': 20,
            'blade_cost': 200000,
            'gearbox_cost': 500000,
            'generator_cost': 300000,
            'transformer_cost': 150000,
            'control_system_cost': 80000,
            'yaw_system_cost': 120000
        }
        
        self.entries = {}
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Wind Farm Data Generator", 
                               font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        row = 1
        
        # Filename Field
        ttk.Label(main_frame, text="File Name (without .csv):", 
                 font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky=tk.W, pady=5)
        self.entries['filename'] = ttk.Entry(main_frame, width=20)
        self.entries['filename'].grid(row=row, column=1, sticky=tk.W, pady=5)
        self.entries['filename'].insert(0, self.default_values['filename'])
        row += 1
        
        # Separator after filename
        ttk.Separator(main_frame, orient='horizontal').grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        row += 1
        
        # Installation Date
        ttk.Label(main_frame, text="Installation Date (YYYY-MM-DD):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.entries['installation_date'] = ttk.Entry(main_frame, width=20)
        self.entries['installation_date'].grid(row=row, column=1, sticky=tk.W, pady=5)
        self.entries['installation_date'].insert(0, self.default_values['installation_date'].strftime('%Y-%m-%d'))
        row += 1
        
        # Number of Clusters
        ttk.Label(main_frame, text="Number of Clusters (max 6):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.entries['num_clusters'] = ttk.Entry(main_frame, width=20)
        self.entries['num_clusters'].grid(row=row, column=1, sticky=tk.W, pady=5)
        self.entries['num_clusters'].insert(0, str(self.default_values['num_clusters']))
        row += 1
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        row += 1
        
        # Lifetime Years Section
        ttk.Label(main_frame, text="Component Lifetime (Years)", 
                 font=("Arial", 12, "bold")).grid(row=row, column=0, columnspan=2, pady=(10, 5))
        row += 1
        
        lifetime_components = [
            ('Blade Lifetime:', 'blade_lifetime'),
            ('Gearbox Lifetime:', 'gearbox_lifetime'),
            ('Generator Lifetime:', 'generator_lifetime'),
            ('Transformer Lifetime:', 'transformer_lifetime'),
            ('Control System Lifetime:', 'control_system_lifetime'),
            ('Yaw System Lifetime:', 'yaw_system_lifetime')
        ]
        
        for label_text, key in lifetime_components:
            ttk.Label(main_frame, text=label_text).grid(row=row, column=0, sticky=tk.W, pady=2)
            self.entries[key] = ttk.Entry(main_frame, width=20)
            self.entries[key].grid(row=row, column=1, sticky=tk.W, pady=2)
            self.entries[key].insert(0, str(self.default_values[key]))
            row += 1
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        row += 1
        
        # Replacement Cost Section
        ttk.Label(main_frame, text="Component Replacement Cost ($)", 
                 font=("Arial", 12, "bold")).grid(row=row, column=0, columnspan=2, pady=(10, 5))
        row += 1
        
        cost_components = [
            ('Blade Cost:', 'blade_cost'),
            ('Gearbox Cost:', 'gearbox_cost'),
            ('Generator Cost:', 'generator_cost'),
            ('Transformer Cost:', 'transformer_cost'),
            ('Control System Cost:', 'control_system_cost'),
            ('Yaw System Cost:', 'yaw_system_cost')
        ]
        
        for label_text, key in cost_components:
            ttk.Label(main_frame, text=label_text).grid(row=row, column=0, sticky=tk.W, pady=2)
            self.entries[key] = ttk.Entry(main_frame, width=20)
            self.entries[key].grid(row=row, column=1, sticky=tk.W, pady=2)
            self.entries[key].insert(0, str(self.default_values[key]))
            row += 1
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        # OK Button
        ok_button = ttk.Button(button_frame, text="Generate Data", command=self.generate_data)
        ok_button.grid(row=0, column=0, padx=5)
        
        # Clear Button
        clear_button = ttk.Button(button_frame, text="Clear Values", command=self.clear_values)
        clear_button.grid(row=0, column=1, padx=5)
        
        # Cancel Button
        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.root.destroy)
        cancel_button.grid(row=0, column=2, padx=5)
        
    def clear_values(self):
        """Clear all input fields to default values"""
        for key, entry in self.entries.items():
            entry.delete(0, tk.END)
            if key == 'installation_date':
                entry.insert(0, self.default_values[key].strftime('%Y-%m-%d'))
            else:
                entry.insert(0, str(self.default_values[key]))
    
    def validate_inputs(self):
        """Validate all input fields"""
        try:
            # Validate filename (mandatory)
            filename = self.entries['filename'].get().strip()
            if not filename:
                raise ValueError("File name is required")
            
            # Check for invalid characters in filename
            invalid_chars = '<>:"/\\|?*'
            if any(char in filename for char in invalid_chars):
                raise ValueError("File name contains invalid characters")
            
            # Validate installation date
            installation_date = datetime.datetime.strptime(
                self.entries['installation_date'].get(), '%Y-%m-%d'
            ).date()
            
            # Validate number of clusters
            num_clusters = int(self.entries['num_clusters'].get())
            if num_clusters < 1 or num_clusters > 6:
                raise ValueError("Number of clusters must be between 1 and 6")
            
            # Validate lifetime years
            lifetimes = {}
            for key in ['blade_lifetime', 'gearbox_lifetime', 'generator_lifetime', 
                       'transformer_lifetime', 'control_system_lifetime', 'yaw_system_lifetime']:
                lifetimes[key] = int(self.entries[key].get())
                if lifetimes[key] < 1 or lifetimes[key] > 50:
                    raise ValueError(f"{key.replace('_', ' ').title()} must be between 1 and 50 years")
            
            # Validate costs
            costs = {}
            for key in ['blade_cost', 'gearbox_cost', 'generator_cost', 
                       'transformer_cost', 'control_system_cost', 'yaw_system_cost']:
                costs[key] = float(self.entries[key].get())
                if costs[key] < 0:
                    raise ValueError(f"{key.replace('_', ' ').title()} must be non-negative")
            
            return filename, installation_date, num_clusters, lifetimes, costs
            
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
            return None
    
    def generate_data(self):
        """Generate the CSV data based on user inputs"""
        validation_result = self.validate_inputs()
        if validation_result is None:
            return
        
        filename, installation_date, num_clusters, lifetimes, costs = validation_result
        
        # Check if file already exists and warn user
        csv_filename = f"{filename}.csv"
        if os.path.exists(csv_filename):
            response = messagebox.askyesno(
                "File Exists", 
                f"A file named '{csv_filename}' already exists.\n\nDo you want to overwrite it?"
            )
            if not response:
                return  # User chose not to overwrite
        
        # Generate wind farm clusters
        cluster_names = [
            "North Sea Alpha", "North Sea Beta", "Baltic Wind", 
            "Atlantic Storm", "Celtic Sea", "Norwegian Deep"
        ]
        
        wind_farm_clusters = []
        for i in range(num_clusters):
            if i < len(cluster_names):
                name = cluster_names[i]
            else:
                name = f"Cluster_{i+1}"
            
            # Generate cluster coordinates
            base_coords = [
                (54.5, 2.0), (55.2, 1.5), (55.8, 15.2),
                (52.0, -4.0), (51.5, -5.0), (60.0, 2.0)
            ]
            
            if i < len(base_coords):
                center_lat, center_lon = base_coords[i]
            else:
                center_lat = 50.0 + random.uniform(0, 10)
                center_lon = random.uniform(-10, 20)
            
            wind_farm_clusters.append({
                "name": name,
                "center_lat": center_lat,
                "center_lon": center_lon
            })
        
        # Component specifications with user inputs
        component_specs = {
            "Blade": {
                "lifetime_years": lifetimes['blade_lifetime'],
                "replacement_cost": costs['blade_cost'],
                "salvage_value": costs['blade_cost'] * 0.1,
                "criticality_level": "critical",
                "power_impact_factor": 0.95,
                "repair_hours": 48
            },
            "Gearbox": {
                "lifetime_years": lifetimes['gearbox_lifetime'],
                "replacement_cost": costs['gearbox_cost'],
                "salvage_value": costs['gearbox_cost'] * 0.1,
                "criticality_level": "critical",
                "power_impact_factor": 1.0,
                "repair_hours": 72
            },
            "Generator": {
                "lifetime_years": lifetimes['generator_lifetime'],
                "replacement_cost": costs['generator_cost'],
                "salvage_value": costs['generator_cost'] * 0.1,
                "criticality_level": "critical",
                "power_impact_factor": 1.0,
                "repair_hours": 60
            },
            "Transformer": {
                "lifetime_years": lifetimes['transformer_lifetime'],
                "replacement_cost": costs['transformer_cost'],
                "salvage_value": costs['transformer_cost'] * 0.1,
                "criticality_level": "important",
                "power_impact_factor": 1.0,
                "repair_hours": 36
            },
            "Control_System": {
                "lifetime_years": lifetimes['control_system_lifetime'],
                "replacement_cost": costs['control_system_cost'],
                "salvage_value": costs['control_system_cost'] * 0.1,
                "criticality_level": "important",
                "power_impact_factor": 0.2,
                "repair_hours": 24
            },
            "Yaw_System": {
                "lifetime_years": lifetimes['yaw_system_lifetime'],
                "replacement_cost": costs['yaw_system_cost'],
                "salvage_value": costs['yaw_system_cost'] * 0.1,
                "criticality_level": "routine",
                "power_impact_factor": 0.1,
                "repair_hours": 18
            }
        }
        
        # Generate the data
        nodes_data = self.generate_nodes_data(
            wind_farm_clusters, component_specs, installation_date
        )
        
        # Write to CSV
        self.write_csv(nodes_data, csv_filename)
        
        # Store the generated filename
        self.last_generated_file = csv_filename
        
        # Success message
        messagebox.showinfo("Success", 
                           f"CSV file '{csv_filename}' has been created with {len(nodes_data)} turbines.\n"
                           f"Total components: {sum(len(node['components']) for node in nodes_data)}\n"
                           f"Wind farm clusters: {[cluster['name'] for cluster in wind_farm_clusters]}")
        
        # Ensure window is properly closed
        self.root.quit()
        self.root.destroy()
    
    def generate_clustered_coordinates(self, cluster, spread_km=10):
        """Generate coordinates within a cluster with realistic spread"""
        lat_spread = spread_km / 111.0
        lon_spread = spread_km / (111.0 * math.cos(math.radians(cluster["center_lat"])))
        
        latitude = cluster["center_lat"] + random.uniform(-lat_spread, lat_spread)
        longitude = cluster["center_lon"] + random.uniform(-lon_spread, lon_spread)
        return latitude, longitude
    
    def calculate_water_depth(self, latitude, longitude):
        """Simulate water depth based on distance from shore"""
        distance_factor = abs(latitude - 54.0) + abs(longitude - 1.0)
        base_depth = 20 + (distance_factor * 5)
        return round(base_depth + random.uniform(-5, 15), 1)
    
    def generate_turbine_data(self):
        """Generate realistic turbine specifications"""
        power_ratings = [2.0, 3.0, 3.6, 5.0, 6.0, 8.0]
        power_rating = random.choice(power_ratings)
        current_output_factor = random.uniform(0.7, 1.0)
        
        return {
            "power_rating": power_rating,
            "current_output": power_rating * current_output_factor,
            "energy_price_mwh": random.uniform(45, 65)
        }
    
    def generate_nodes_data(self, wind_farm_clusters, component_specs, base_installation_date):
        """Generate node data with specified parameters"""
        nodes_data = []
        
        for i in range(25):
            cluster = random.choice(wind_farm_clusters)
            latitude, longitude = self.generate_clustered_coordinates(cluster)
            
            turbine_data = self.generate_turbine_data()
            water_depth = self.calculate_water_depth(latitude, longitude)
            
            # Generate components for this turbine
            components = []
            for comp_name, specs in component_specs.items():
                # Use base installation date with some variation
                comp_install_date = base_installation_date + datetime.timedelta(
                    days=random.randint(-90, 90)
                )
                
                # Some components might be replaced
                if random.random() < 0.2:
                    comp_install_date = base_installation_date + datetime.timedelta(
                        days=random.randint(365, 3*365)
                    )
                
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
        
        return nodes_data
    
    def write_csv(self, nodes_data, filename):
        """Write the generated data to CSV file"""
        with open(filename, mode='w', newline='') as file:
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
    
    def run(self):
        """Run the GUI application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = DataMakerGUI()
    app.run()