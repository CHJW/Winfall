import csv
import sys
import datetime
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Slider
import matplotlib.gridspec as gridspec
import numpy as np

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
        fig = plt.figure(figsize=(12, 6))
        gs = gridspec.GridSpec(1, 2, width_ratios=[3, 1])
        
        ax_map = fig.add_subplot(gs[0])
        ax_panel = fig.add_subplot(gs[1])
        
        x = [node.data['latitude'] for node in self.nodes]
        y = [node.data['longitude'] for node in self.nodes]
        scatter = ax_map.scatter(x, y)
        
        ax_map.set_title("Windmill Map")
        ax_map.set_xlabel("Latitude")
        ax_map.set_ylabel("Longitude")
        
        ax_panel.set_title("Node Components")
        ax_panel.axis('off')
        
        slider_ax = fig.add_axes([0.93, 0.25, 0.02, 0.5], facecolor='lightgoldenrodyellow')
        slider = Slider(slider_ax, 'Scroll', 0, 1, valinit=1, orientation='vertical')

        def update_panel(node):
            ax_panel.clear()
            ax_panel.set_title("Node Components")
            ax_panel.axis('off')
            
            if node.components:
                component_texts = [f"Name: {component.name}\nInstallation Date: {component.installation_date}\nCurrent Lifetime: {component.current_lifetime}" for component in node.components]
            else:
                component_texts = ["No components found."]
            
            spacing = 0.2
            scroll_offset = (1 - slider.val) * len(component_texts) * spacing
            
            for i, text in enumerate(component_texts):
                ax_panel.text(0.1, 1 - spacing * (i + 1) + scroll_offset, text, transform=ax_panel.transAxes, fontsize=10, verticalalignment='top')
            
            fig.canvas.draw_idle()
        
        def on_click(event):
            if event.inaxes == ax_map:
                cont, ind = scatter.contains(event)
                if cont:
                    self.selected_node = self.nodes[ind['ind'][0]]
                    update_panel(self.selected_node)
        
        def generate_pathway(event):
            if len(self.nodes) < 2:
                print("Not enough nodes to generate a pathway.")
                return
            
            # Nearest Neighbor Algorithm
            unvisited = self.nodes[:]
            current_node = unvisited.pop(0)
            path = [current_node]
            
            while unvisited:
                next_node = min(unvisited, key=lambda node: np.hypot(node.data['latitude'] - current_node.data['latitude'], node.data['longitude'] - current_node.data['longitude']))
                unvisited.remove(next_node)
                path.append(next_node)
                current_node = next_node
            
            # Draw the path
            path_x = [node.data['latitude'] for node in path]
            path_y = [node.data['longitude'] for node in path]
            ax_map.plot(path_x, path_y, 'r-', label='Pathway')
            ax_map.legend()
            fig.canvas.draw_idle()

        # Center the generate pathway button beneath the slider
        generate_pathway_button_ax = fig.add_axes([0.85, 0.05, 0.1, 0.075])
        generate_pathway_button = Button(generate_pathway_button_ax, 'Generate Pathway')
        generate_pathway_button.on_clicked(generate_pathway)

        slider.on_changed(lambda val: update_panel(self.selected_node) if self.selected_node else None)

        fig.canvas.mpl_connect('button_press_event', on_click)
        plt.show()

def opendata(file_path):
    with open(file_path, mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        nodes = []
        current_node_data = None
        current_components = []
        
        for row in reader:
            latitude, longitude, component_name, lifetime, serial_number, installation_date = row
            latitude = float(latitude)
            longitude = float(longitude)
            lifetime = int(lifetime)
            installation_date = datetime.datetime.strptime(installation_date, "%Y-%m-%d").date()
            
            # Check if we are still on the same node
            if current_node_data is None or (current_node_data['latitude'] != latitude or current_node_data['longitude'] != longitude):
                # If we have collected components for a node, add it to the list
                if current_node_data is not None:
                    nodes.append(Node(data=current_node_data, components=current_components))
                
                # Start a new node
                current_node_data = {"latitude": latitude, "longitude": longitude}
                current_components = []
            
            # Add the component to the current node
            component = Component(node=None, name=component_name, lifetime=lifetime, serial_number=serial_number, installation_date=installation_date)
            current_components.append(component)
        
        # Add the last node
        if current_node_data is not None:
            nodes.append(Node(data=current_node_data, components=current_components))
        
        windmill_map = Map(nodes)
        print(f"Loaded {len(windmill_map.get_nodes())} nodes from file.")
        windmill_map.draw_map()
    
    
def main(file_path=None):
    if file_path is None:
        return print(f"No file path inputed. If you want to generate a demo map, use the datamaker.py to create d .")
    else:
        try:
            opendata(file_path)
        except FileNotFoundError:
            print(f"File not found: {file_path}")
        except Exception as e:
            print(f"An error occurred while processing the file: {e}")            

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)