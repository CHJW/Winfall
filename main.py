import csv
import sys
import os
import datetime
import math
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import matplotlib.gridspec as gridspec
import tkinter as tk
from tkinter import ttk

class Node:
    def __init__(self, data=None, components=None):
        self.data = data if data else {}
        self.components = components if components else []

    def __repr__(self):
        return f"Node(data={self.data}, components={self.components})"
    
    def add_component(self, component):
        self.components.append(component)

class Component:
    def __init__(self, node, name, lifetime, serial_number, installation_date):
        self.node = node
        self.name = name
        self.lifetime = lifetime
        self.current_lifetime = self.calculate_lifetime(lifetime)
        self.serial_number = serial_number
        self.installation_date = installation_date

    def calculate_lifetime(self, lifetime):
        try:
            return lifetime - (datetime.date.today() - self.installation_date).days
        except AttributeError:
            print("No data available to process.")
        except Exception as e:
            print(f"An error occurred: {e}")

class Map:
    def __init__(self, nodes=None):
        self.nodes = nodes if nodes else []
        self.selected_node = None

    def add_node(self, node):
        self.nodes.append(node)

    def get_nodes(self):
        return self.nodes
    
    def draw_map(self):
        fig = plt.figure(figsize=(10, 5))
        gs = gridspec.GridSpec(1, 2, width_ratios=[3, 1])
        
        ax_map = fig.add_subplot(gs[0])
        ax_panel = fig.add_subplot(gs[1])
        
        x = [node.data['latitude'] for node in self.nodes]
        y = [node.data['longtitude'] for node in self.nodes]
        scatter = ax_map.scatter(x, y)
        
        ax_map.set_title("Windmill Map")
        ax_map.set_xlabel("Latitude")
        ax_map.set_ylabel("Longitude")
        
        ax_panel.set_title("Node Components")
        ax_panel.axis('off')
        
        def update_panel(node):
            ax_panel.clear()
            ax_panel.set_title("Node Components")
            ax_panel.axis('off')
            if node.components:
                y_offset = 0.9
                for component in node.components:
                    ax_panel.text(0.1, y_offset, f"Name: {component.name}", transform=ax_panel.transAxes)
                    ax_panel.text(0.1, y_offset - 0.1, f"Installation Date: {component.installation_date}", transform=ax_panel.transAxes)
                    ax_panel.text(0.1, y_offset - 0.2, f"Current Lifetime: {component.current_lifetime}", transform=ax_panel.transAxes)
                    y_offset -= 0.3
            else:
                ax_panel.text(0.1, 0.9, "No components found.", transform=ax_panel.transAxes)
            fig.canvas.draw_idle()
        
        def on_click(event):
            if event.inaxes == ax_map:
                cont, ind = scatter.contains(event)
                if cont:
                    self.selected_node = self.nodes[ind['ind'][0]]
                    update_panel(self.selected_node)
        
        def add_node(event):
            root = tk.Tk()
            root.title("Add Node")
            
            node_frame = ttk.LabelFrame(root, text="Node Data")
            node_frame.pack(padx=10, pady=10, fill="x", expand=True)
            
            node_data = {}
            node_labels = ["Latitude", "Longitude", "Power", "Manufacturer", "Location"] # Need to make dynamic based on the keys
            node_entries = {}
            for label in node_labels:
                row = ttk.Frame(node_frame)
                row.pack(fill="x", expand=True)
                ttk.Label(row, text=label).pack(side="left")
                entry = ttk.Entry(row)
                entry.pack(side="right", fill="x", expand=True)
                node_entries[label] = entry
            
            component_frame = ttk.LabelFrame(root, text="Components")
            component_frame.pack(padx=10, pady=10, fill="x", expand=True)
            
            components = []
            component_entries = []
            
            def add_component():
                component_data = {}
                component_labels = ["Name", "Lifetime", "Serial Number", "Installation Date (YYYY-MM-DD)"] #Need to make dynamic based on the keys
                component_entry = {}
                for label in component_labels:
                    row = ttk.Frame(component_frame)
                    row.pack(fill="x", expand=True)
                    ttk.Label(row, text=label).pack(side="left")
                    entry = ttk.Entry(row)
                    entry.pack(side="right", fill="x", expand=True)
                    component_entry[label] = entry
                component_entries.append(component_entry)
            
            add_component_button = ttk.Button(root, text="Add Component", command=add_component)
            add_component_button.pack(pady=5)
            
            def submit():
                for label in node_labels:
                    node_data[label.lower()] = node_entries[label].get()
                
                for component_entry in component_entries:
                    name = component_entry["Name"].get()
                    lifetime = int(component_entry["Lifetime"].get())
                    serial_number = component_entry["Serial Number"].get()
                    installation_date = component_entry["Installation Date (YYYY-MM-DD)"].get()
                    installation_date = datetime.datetime.strptime(installation_date, "%Y-%m-%d").date()
                    component = Component(node=None, name=name, lifetime=lifetime, serial_number=serial_number, installation_date=installation_date)
                    components.append(component)
                
                new_node = Node(data=node_data, components=components)
                self.add_node(new_node)
                ax_map.clear()
                ax_map.set_title("Windmill Map")
                ax_map.set_xlabel("Latitude")
                ax_map.set_ylabel("Longitude")
                x = [node.data['latitude'] for node in self.nodes]
                y = [node.data['longtitude'] for node in self.nodes]
                ax_map.scatter(x, y)
                fig.canvas.draw_idle()
                root.destroy()
            
            submit_button = ttk.Button(root, text="Submit", command=submit)
            submit_button.pack(pady=5)
            
            add_component()  # Add default components
            add_component()  # Add default components
            
            root.mainloop()

        add_node_button_ax = fig.add_axes([0.8, 0.05, 0.1, 0.075])
        add_node_button = Button(add_node_button_ax, 'Add Node')
        add_node_button.on_clicked(add_node)

        fig.canvas.mpl_connect('button_press_event', on_click)
        plt.show()

def generateDemoMap():
    nodeData1 = {"latitude": 100, 
                 "longtitude": 120,
                 "power": 1.5, 
                 "manufacturer": "WindTech", 
                 "location": "North Field"}
    nodeData2 = {"latitude": 50, 
                 "longtitude": 70,
                 "power": 1.5, 
                 "manufacturer": "WindTech", 
                 "location": "North Field"}
    component1 = Component(node=None, name="Rotor", lifetime=10, serial_number="RT12345", installation_date=datetime.date(2023, 1, 1))
    component2 = Component(node=None, name="Blade", lifetime=15, serial_number="BL67890", installation_date=datetime.date(2022, 6, 15))
    node1 = Node(data=nodeData1, components=[component1, component2])
    node2 = Node(data=nodeData2)
    windmill_map = Map([node1, node2])
    windmill_map.draw_map()
    return windmill_map

def main(file_path=None):
    if file_path is None:
        return print(f"No file path inputed. If you want to generate a demo map, please input 'Demo' as the file path.")
    elif file_path == 'Demo':
        generateDemoMap()
        return 
    else:
        try:
            with open(file_path, mode='r') as file:
                reader = csv.reader(file)
                nodes = []
                for row in reader:
                    x, y = map(float, row)
                    nodes.append(Node(x, y))
                windmill_map = Map(nodes)
                print(f"Loaded {len(windmill_map.get_nodes())} nodes from file.")
        except FileNotFoundError:
            print(f"File {file_path} not found.")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)