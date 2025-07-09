import csv
import sys
import datetime
import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Slider, TextBox
import numpy as np
import math
from functools import partial
import matplotlib.patches as patches
import matplotlib.transforms as transforms

class Component:
    """Represents a component of a node (e.g., blade, gearbox)."""
    def __init__(self, node, name, lifetime_years, serial_number, installation_date, 
                 replacement_cost=0, salvage_value=0, criticality_level="routine", 
                 power_impact_factor=0, repair_hours=24, prediction_date=None):
        self.node = node
        self.name = name
        self.lifetime_years = lifetime_years
        self.lifetime_days = lifetime_years * 365
        self.serial_number = serial_number
        self.installation_date = installation_date
        self.replacement_cost = replacement_cost
        self.salvage_value = salvage_value
        self.criticality_level = criticality_level
        self.power_impact_factor = power_impact_factor
        self.repair_hours = repair_hours
        self.prediction_date = prediction_date or datetime.date.today()
        
        # Calculate derived properties
        self.remaining_lifetime_days = self.calculate_remaining_lifetime()
        self.health_score = self.calculate_health_score()
        self.failure_probability = self.calculate_failure_probability()
        self.total_repair_cost = self.calculate_repair_cost()
        self.opportunity_cost = self.calculate_opportunity_cost()

    def calculate_remaining_lifetime(self):
        """Calculates the remaining operational days of the component."""
        try:
            days_in_service = (self.prediction_date - self.installation_date).days
            return max(0, self.lifetime_days - days_in_service)
        except AttributeError:
            print(f"No installation date available for component {self.name}")
            return self.lifetime_days
        except Exception as e:
            print(f"Error calculating lifetime for {self.name}: {e}")
            return 0

    def calculate_health_score(self):
        """Calculate health score based on remaining lifetime (0-1 scale)."""
        if self.lifetime_days > 0:
            return self.remaining_lifetime_days / self.lifetime_days
        return 0

    def calculate_failure_probability(self):
        """Calculate failure probability (inverse of health, with exponential curve)."""
        return 1 - (self.health_score ** 2)

    def calculate_repair_cost(self):
        """Calculate the total repair cost including depreciation."""
        # Simple repair cost calculation
        repair_cost = self.replacement_cost * self.failure_probability
        
        # Add depreciation loss
        if self.lifetime_days > 0:
            depreciation_loss = (self.replacement_cost - self.salvage_value) * \
                                (1 - self.health_score)
        else:
            depreciation_loss = self.replacement_cost
        
        return repair_cost + depreciation_loss

    def calculate_opportunity_cost(self):
        """Calculate potential revenue loss due to component failure."""
        if self.failure_probability > 0 and self.node:
            power_loss = self.node.attributes.get('power_rating', 3.0) * self.power_impact_factor
            hours_lost = self.repair_hours * self.failure_probability
            energy_price = self.node.attributes.get('energy_price_mwh', 50.0)
            
            return power_loss * hours_lost * energy_price
        return 0

    def update_calculations(self, prediction_date=None):
        """Recalculate all derived properties (useful when base data changes)."""
        if prediction_date:
            self.prediction_date = prediction_date
        self.remaining_lifetime_days = self.calculate_remaining_lifetime()
        self.health_score = self.calculate_health_score()
        self.failure_probability = self.calculate_failure_probability()
        self.total_repair_cost = self.calculate_repair_cost()
        self.opportunity_cost = self.calculate_opportunity_cost()

    def __repr__(self):
        return (f"Component({self.name}, health={self.health_score:.2f}, "
                f"failure_risk={self.failure_probability:.2f})")


class Node:
    """Represents a single node (e.g., a wind turbine) on the map."""
    def __init__(self, attributes=None, components=None):
        self.attributes = attributes if attributes else {}
        self.components = components if components else []
        
        # Calculate derived properties
        self.total_repair_cost = self.calculate_total_repair_cost()
        self.total_opportunity_cost = self.calculate_total_opportunity_cost()
        self.repair_priority_score = 0  # Will be calculated by map when needed

    def __repr__(self):
        return f"Node(id={self.attributes.get('node_id', 'Unknown')}, priority={self.repair_priority_score:.2f})"
    
    def add_component(self, component):
        """Add a component to this node."""
        self.components.append(component)
        component.node = self  # Link component back to node
        # Recalculate totals
        self.update_calculations()

    def calculate_total_repair_cost(self):
        """Calculate the total repair cost for all components in this node."""
        return sum(component.total_repair_cost for component in self.components)

    def calculate_total_opportunity_cost(self):
        """Calculate the total opportunity cost for all components in this node."""
        return sum(component.opportunity_cost for component in self.components)

    def calculate_repair_priority_score(self, avg_transport_cost=1000):
        """Calculate repair priority score based on benefit/cost ratio."""
        # Total benefit = opportunity cost saved + a portion of depreciation prevented
        total_benefit = self.total_opportunity_cost + (self.total_repair_cost * 0.5)
        
        # Total cost = repair cost + estimated average transportation cost
        total_cost = self.total_repair_cost + avg_transport_cost
        
        # Priority score (benefit-to-cost ratio)
        if total_cost > 0:
            self.repair_priority_score = total_benefit / total_cost
        else:
            self.repair_priority_score = 0
        
        return self.repair_priority_score

    def update_calculations(self, prediction_date=None):
        """Recalculate all derived properties for this node."""
        # First update all components
        for component in self.components:
            component.update_calculations(prediction_date)
        
        # Then update node totals
        self.total_repair_cost = self.calculate_total_repair_cost()
        self.total_opportunity_cost = self.calculate_total_opportunity_cost()

    def meets_repair_threshold(self, threshold_ratio=0.52):
        """Check if this node meets the minimum repair threshold criteria."""
        return self.repair_priority_score >= threshold_ratio

    def get_component_health_summary(self):
        """Get a summary of all component health scores."""
        return {
            component.name: {
                'health_score': component.health_score,
                'failure_probability': component.failure_probability,
                'repair_cost': component.total_repair_cost,
                'opportunity_cost': component.opportunity_cost
            }
            for component in self.components
        }

    def print_node_summary(self):
        """Print a summary of this node's status."""
        print(f"Node {self.attributes.get('node_id')}: "
              f"Total repair cost = ${self.total_repair_cost:,.2f}, "
              f"Opportunity cost = ${self.total_opportunity_cost:,.2f}, "
              f"Priority Score = {self.repair_priority_score:.2f}")
        
        for component in self.components:
            print(f"  Component {component.name} ({component.serial_number}): "
                  f"Health={component.health_score:.2f}, "
                  f"Failure Risk={component.failure_probability:.2f}")

class Map:
    """Manages the nodes, calculations, and visualization of the map."""
    def __init__(self, nodes=None):
        self.nodes = nodes if nodes else []
        self.selected_node = None
        self.cost_calculator = CostCalculator()
        self.distance_matrix = None
        self.cost_matrix = None
        self.path_artists = [] # To store plotted route for easy clearing
        self.selected_node_circle =  None
        self.node_circles = []  # To store node circles for visualization
        self.prediction_date = datetime.date.today()

        
        # --- Configuration for interactive UI fields ---
        # This structure is agnostic to the field it can change.
        # To add a new field, simply add a new entry to this dictionary.
        self.interactive_fields = {
            'prediction_date': {
                'label': 'Prediction Date (YYYY-MM-DD)',
                'initial': self.prediction_date.strftime('%Y-%m-%d'),
                'target_obj': self,
                'target_attr': 'prediction_date',
                'type': 'date'
            },
            'repair_threshold_ratio': {
                'label': 'Repair Threshold Ratio',
                'initial': '0.52',
                'target_obj': self,
                'target_attr': 'repair_threshold_ratio',
                'type': float
            },
            'cost_per_distance_unit': {
                'label': 'Cost Per Distance ($)',
                'initial': '5.0',
                'target_obj': self.cost_calculator,
                'target_attr': 'cost_per_distance_unit',
                'type': float
            }
        }
        # Initialize attributes from the dictionary
        for key, config in self.interactive_fields.items():
            if config['type'] == 'date':
                setattr(config['target_obj'], config['target_attr'], self.prediction_date)
            else:
                setattr(config['target_obj'], config['target_attr'], config['type'](config['initial']))

    def add_node(self, node):
        """Add a node to the map."""
        self.nodes.append(node)

    def get_nodes(self):
        """Get all nodes on the map."""
        return self.nodes
    
    def generate_cost_matrix(self):
        """Generate distance and cost matrices between all nodes."""
        num_nodes = len(self.nodes)
        self.distance_matrix = np.zeros((num_nodes, num_nodes))
        self.cost_matrix = np.zeros((num_nodes, num_nodes))
        
        for i in range(num_nodes):
            for j in range(num_nodes):
                if i != j:
                    lat1, lon1 = self.nodes[i].attributes['latitude'], self.nodes[i].attributes['longitude']
                    lat2, lon2 = self.nodes[j].attributes['latitude'], self.nodes[j].attributes['longitude']
                    
                    distance = np.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2)
                    self.distance_matrix[i][j] = distance
                    self.cost_matrix[i][j] = self.cost_calculator.calculate_transportation_cost(distance)
        
        print(f"Generated cost matrix for {num_nodes} nodes based on current cost settings.")

    def calculate_all_repair_priorities(self):
        """Calculate repair priority scores for all nodes."""
        avg_transport_cost = 1000  # Default value
        if self.cost_matrix is not None and self.cost_matrix.size > 0:
            avg_transport_cost = np.mean(self.cost_matrix[self.cost_matrix > 0])
        
        for node in self.nodes:
            node.calculate_repair_priority_score(avg_transport_cost)
    
    def filter_nodes_for_repair(self):
        """Filter nodes that meet the minimum repair threshold criteria."""
        threshold = self.repair_threshold_ratio
        worthy_nodes = [node for node in self.nodes if node.meets_repair_threshold(threshold)]
        
        print(f"Filtered {len(worthy_nodes)} nodes above threshold ratio of {threshold}")
        return worthy_nodes

    def update_all_calculations(self):
        """Update all calculations for all nodes and components."""
        for node in self.nodes:
            node.update_calculations(self.prediction_date)
        
        if self.nodes:
            self.generate_cost_matrix()
        
        self.calculate_all_repair_priorities()

    def get_map_summary(self):
        """Get a summary of the entire map status."""
        # Temporarily filter to get the count without printing the filter message
        worthy_nodes = [node for node in self.nodes if node.meets_repair_threshold(self.repair_threshold_ratio)]
        
        return {
            'total_nodes': len(self.nodes),
            'repair_worthy_nodes': len(worthy_nodes),
            'total_repair_cost': sum(node.total_repair_cost for node in self.nodes),
            'total_opportunity_cost': sum(node.total_opportunity_cost for node in self.nodes),
            'repair_threshold': self.repair_threshold_ratio
        }

    def print_map_summary(self):
        """Print a comprehensive summary of the map."""
        summary = self.get_map_summary()
        print("Map Summary:")
        print(f"Total Nodes: {summary['total_nodes']}")
        print(f"Nodes meeting repair threshold: {summary['repair_worthy_nodes']}")
        print(f"Total repair cost across all nodes: ${summary['total_repair_cost']:,.2f}")
        print(f"Total opportunity cost across all nodes: ${summary['total_opportunity_cost']:,.2f}")
        print(f"Repair threshold ratio: {summary['repair_threshold']}")
        
        print("\nIndividual Node Details:")
        for node in self.nodes:
            node.print_node_summary()
    
    def optimize_route(self, filtered_nodes):
        """Optimize maintenance route using a greedy algorithm weighted by priority."""
        if not filtered_nodes:
            return []
        
        unvisited_nodes = filtered_nodes[:]
        current_node = max(unvisited_nodes, key=lambda node: node.repair_priority_score)
        unvisited_nodes.remove(current_node)
        path = [current_node]
        
        while unvisited_nodes:
            best_next_node = None
            max_score = -1
            current_node_index = self.nodes.index(current_node)
            
            for candidate_node in unvisited_nodes:
                candidate_node_index = self.nodes.index(candidate_node)
                transport_cost = self.cost_matrix[current_node_index][candidate_node_index] if self.cost_matrix is not None else 1
                
                score = candidate_node.repair_priority_score / max(transport_cost, 1)
                
                if score > max_score:
                    max_score = score
                    best_next_node = candidate_node
            
            if best_next_node:
                unvisited_nodes.remove(best_next_node)
                path.append(best_next_node)
                current_node = best_next_node
            else:
                break
        
        print(f"Optimized route with {len(path)} nodes")
        return path
    
    def draw_map(self):
        fig, self.map_ax = plt.subplots(figsize=(16, 12))
        plt.subplots_adjust(left=0.08, right=0.7, top=0.9, bottom=0.10)

        latitudes = [node.attributes['latitude'] for node in self.nodes]
        longitudes = [node.attributes['longitude'] for node in self.nodes]
        
        clusters = sorted(list({node.attributes.get('cluster_name', 'Unknown') for node in self.nodes}))
        # Use tab20 colormap to avoid red and have more color options
        colors = plt.cm.get_cmap('tab20', len(clusters))
        cluster_color_map = {cluster: colors(i) for i, cluster in enumerate(clusters)}
        node_colors = [cluster_color_map[node.attributes.get('cluster_name', 'Unknown')] for node in self.nodes]

        self.scatter = self.map_ax.scatter(latitudes, longitudes, c=node_colors, s=100, alpha=0.8, picker=True)
        self.original_colors = node_colors.copy()  # Store original colors for resetting
        
        self.map_ax.set_title("Maintenance Priority Overview Map", fontsize=16)
        self.map_ax.set_xlabel("Latitude")
        self.map_ax.set_ylabel("Longitude")
        self.map_ax.grid(True, linestyle='--', alpha=0.6)

        legend_elements = [plt.Line2D([0], [0], marker='o', color='w', label=cluster,
                                      markerfacecolor=color, markersize=10)
                           for cluster, color in cluster_color_map.items()]
        # Add selected node legend entry
        legend_elements.append(plt.Line2D([0], [0], marker='o', color='w', label='Selected node',
                                         markerfacecolor='red', markersize=10))
        self.map_ax.legend(handles=legend_elements, title="Clusters")
        
        info_panel_ax = fig.add_axes([0.72, 0.65, 0.25, 0.25])
        info_panel_ax.set_title("Node Details")
        info_panel_ax.axis('off')

        # --- Buttons --- (bottom-aligned with graph)
        generate_button_ax = fig.add_axes([0.72, 0.10, 0.13, 0.06])
        generate_button = Button(generate_button_ax, 'Generate Pathway')
        
        reset_button_ax = fig.add_axes([0.86, 0.10, 0.11, 0.06])
        reset_button = Button(reset_button_ax, 'Reset Map')

        # --- Dynamic Input Fields --- (just above buttons)
        text_boxes = {}
        field_y_pos = 0.35
        for key, config in self.interactive_fields.items():
            ax_label = fig.add_axes([0.72, field_y_pos, 0.1, 0.04])
            ax_label.text(0.5, 0.5, config['label'], ha='center', va='center', fontsize=9)
            ax_label.axis('off')

            ax_box = fig.add_axes([0.83, field_y_pos, 0.14, 0.04])
            text_box = TextBox(ax_box, '', initial=config['initial'])
            
            # Create a partial function to pass arguments to the callback
            update_callback = partial(self._create_update_callback, 
                                      text_box=text_box,
                                      target_obj=config['target_obj'], 
                                      attr=config['target_attr'],
                                      value_type=config['type'])
            text_box.on_submit(update_callback)
            text_boxes[key] = text_box
            field_y_pos -= 0.06 # Decrement y-position for the next field

        def update_info_panel(node):
            info_panel_ax.clear()
            info_panel_ax.set_title("Node Details")
            info_panel_ax.axis('off')
            
            if node:
                info_text = (f"Node ID: {node.attributes.get('node_id', 'N/A')}\n"
                             f"Cluster: {node.attributes.get('cluster_name', 'N/A')}\n"
                             f"Priority Score: {node.repair_priority_score:.2f}\n"
                             f"Power Rating: {node.attributes.get('power_rating', 0):.1f} MW\n\n"
                             f"--- Components ---")
                
                component_texts = []
                for comp in node.components:
                    comp_text = (f"\n{comp.name} ({comp.serial_number})\n"
                                 f"  Health: {comp.health_score:.2f} | "
                                 f"Failure Risk: {comp.failure_probability:.2f}\n"
                                 f"  Criticality: {comp.criticality_level}")
                    component_texts.append(comp_text)
                
                all_text = info_text + "".join(component_texts)
            else:
                all_text = "Click on a node to see details."
            
            info_panel_ax.text(0.05, 0.95, all_text, transform=info_panel_ax.transAxes, 
                               fontsize=9, verticalalignment='top', fontfamily='monospace', wrap=True)
            fig.canvas.draw_idle()

        def on_click(event):
            if event.inaxes == self.map_ax:
                contains, index_info = self.scatter.contains(event)
                if contains:
                    node_index = index_info['ind'][0]
                    self.selected_node = self.nodes[node_index]
                    update_info_panel(self.selected_node)

                    # Reset all nodes to original colors
                    current_colors = self.original_colors.copy()
                    # Set selected node to red
                    current_colors[node_index] = 'red'
                    self.scatter.set_color(current_colors)
                    
                    fig.canvas.draw_idle()


        def generate_pathway_action(event):
            print("\n=== GENERATING OPTIMIZED MAINTENANCE PATHWAY ===")
            reset_map_action(event) # Clear previous path before drawing a new one

            self.update_all_calculations()
            worthy_nodes = self.filter_nodes_for_repair()
            optimized_path = self.optimize_route(worthy_nodes)
            
            if not optimized_path:
                print("No nodes meet the repair threshold criteria.")
                no_repairs_text = self.map_ax.text(0.5, 0.5, "No high-priority repairs found.", 
                                       transform=self.map_ax.transAxes, ha='center',
                                       fontsize=14, color='red', bbox=dict(facecolor='white', alpha=0.8))
                self.path_artists.append(no_repairs_text) # Add to artists to be cleared
                fig.canvas.draw_idle()
                return
            
            path_lat = [node.attributes['latitude'] for node in optimized_path]
            path_lon = [node.attributes['longitude'] for node in optimized_path]
            
            route_line, = self.map_ax.plot(path_lat, path_lon, 'r-o', linewidth=2, markersize=8, label='Optimized Route')
            start_marker = self.map_ax.scatter(path_lat[0], path_lon[0], c='lime', s=250, marker='*', label='Start Point', zorder=5)
            self.path_artists.extend([route_line, start_marker])
            
            if len(path_lat) > 1:
                end_marker = self.map_ax.scatter(path_lat[-1], path_lon[-1], c='red', s=200, marker='X', label='End Point', zorder=5)
                self.path_artists.append(end_marker)

            handles, labels = self.map_ax.get_legend_handles_labels()
            self.map_ax.legend(handles, labels)
            fig.canvas.draw_idle()
            
            total_benefit = sum(n.total_opportunity_cost + n.total_repair_cost * 0.5 for n in optimized_path)
            total_cost = sum(n.total_repair_cost for n in optimized_path)
            print("\n=== PATHWAY SUMMARY ===")
            print(f"Nodes to visit: {len(optimized_path)}")
            print(f"Total estimated benefit: ${total_benefit:,.2f}")
            print(f"Total estimated cost: ${total_cost:,.2f}")
            if total_cost > 0:
                print(f"Overall benefit/cost ratio: {total_benefit/total_cost:.2f}")

        def reset_map_action(event):
            """Clears the generated path and markers from the map."""
            if not self.path_artists:
                print("Map is already clear. Nothing to reset.")
                return
            
            print("Resetting map view...")
            for artist in self.path_artists:
                artist.remove()
            self.path_artists.clear()
            
            # Redraw legend without path elements
            handles, labels = self.map_ax.get_legend_handles_labels()
            # Filter out the labels associated with the path
            filtered_handles = [h for h, l in zip(handles, labels) if l not in ['Optimized Route', 'Start Point', 'End Point']]
            filtered_labels = [l for l in labels if l not in ['Optimized Route', 'Start Point', 'End Point']]
            self.map_ax.legend(filtered_handles, filtered_labels, title="Clusters")

            fig.canvas.draw_idle()

        generate_button.on_clicked(generate_pathway_action)
        reset_button.on_clicked(reset_map_action)
        fig.canvas.mpl_connect('button_press_event', on_click)
        update_info_panel(None)
        plt.show()

    def _create_update_callback(self, text, text_box, target_obj, attr, value_type):
        """A generic callback factory for handling text box submissions."""
        try:
            if value_type == 'date':
                new_value = datetime.datetime.strptime(text, '%Y-%m-%d').date()
                # Validate that the date is not before today
                if new_value < datetime.date.today():
                    messagebox.showerror("Invalid Date", "Prediction date cannot be before today's date.")
                    text_box.color = '0.9'
                    plt.gcf().canvas.draw_idle()
                    return
                setattr(target_obj, attr, new_value)
                # Update all calculations with the new prediction date
                if attr == 'prediction_date':
                    self.update_all_calculations()
                text_box.color = 'white'
                print(f"Updated '{attr}' to {new_value}")
            else:
                new_value = value_type(text)
                setattr(target_obj, attr, new_value)
                text_box.color = 'white'
                print(f"Updated '{attr}' to {new_value}")
        except ValueError:
            if value_type == 'date':
                messagebox.showerror("Invalid Date Format", "Please enter date in YYYY-MM-DD format.")
                text_box.color = '0.9'
            else:
                print(f"Invalid input: '{text}'. Please enter a valid {value_type.__name__}.")
                text_box.color = '0.9'
        plt.gcf().canvas.draw_idle()


class CostCalculator:
    """Handles all cost calculations for maintenance operations."""
    def __init__(self):
        self.cost_per_distance_unit = 5.0  # $5 per unit distance
        self.base_crew_cost_per_day = 2000
        self.base_vessel_cost_per_day = 5000
        
    def calculate_transportation_cost(self, distance):
        """Calculate cost based on distance traveled."""
        return distance * self.cost_per_distance_unit
    
    def calculate_operation_cost(self, repair_hours):
        """Calculate crew and vessel costs for a repair operation."""
        days_for_repair = math.ceil(repair_hours / 24.0)
        return (self.base_crew_cost_per_day + self.base_vessel_cost_per_day) * days_for_repair

def load_data_from_csv(file_path):
    """Loads node and component data from a CSV file."""
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        header = next(reader)
        
        nodes = []
        current_node_attributes = None
        components_for_current_node = []
        
        for row in reader:
            (node_id, latitude, longitude, water_depth, power_rating, 
             current_output, energy_price_mwh, cluster_name,
             component_name, lifetime_years, serial_number, installation_date_str,
             replacement_cost, salvage_value, criticality_level, 
             power_impact_factor, repair_hours) = row
            
            # A unique key to identify a node based on its core properties
            node_key = (node_id, latitude, longitude)
            
            if current_node_attributes is None or current_node_attributes['node_key'] != node_key:
                # If we have collected components, finalize the previous node
                if current_node_attributes is not None:
                    node_obj = Node(attributes=current_node_attributes)
                    for comp in components_for_current_node:
                        node_obj.add_component(comp)
                    nodes.append(node_obj)
                
                # Start a new node
                current_node_attributes = {
                    "node_key": node_key, "node_id": node_id,
                    "latitude": float(latitude), "longitude": float(longitude),
                    "water_depth": float(water_depth), "power_rating": float(power_rating),
                    "current_output": float(current_output), "energy_price_mwh": float(energy_price_mwh),
                    "cluster_name": cluster_name
                }
                components_for_current_node = []
            
            # Add the component for the current node
            component = Component(
                node=None, # Will be linked when the node is finalized
                name=component_name,
                lifetime_years=int(lifetime_years),
                serial_number=serial_number,
                installation_date=datetime.datetime.strptime(installation_date_str, "%Y-%m-%d").date(),
                replacement_cost=float(replacement_cost),
                salvage_value=float(salvage_value),
                criticality_level=criticality_level,
                power_impact_factor=float(power_impact_factor),
                repair_hours=float(repair_hours),
                prediction_date=datetime.date.today()
            )
            components_for_current_node.append(component)
        
        # Add the last processed node
        if current_node_attributes is not None:
            node_obj = Node(attributes=current_node_attributes)
            for comp in components_for_current_node:
                node_obj.add_component(comp)
            nodes.append(node_obj)
            
        asset_map = Map(nodes)
        print(f"Loaded {len(asset_map.get_nodes())} nodes from file.")
        print(f"Total components: {sum(len(node.components) for node in nodes)}")
        return asset_map

def show_startup_instructions():
    """Displays a modal dialog with instructions and returns user choice."""
    root = tk.Tk()
    root.withdraw()  # Hide the main tkinter window
    
    title = "User Instructions"
    message = (
        "Welcome to the Maintenance Optimization Tool.\n\n"
        "Instructions:\n"
        "1. The map displays all assets, color-coded by their cluster.\n"
        "2. Click on any node on the map to view its details in the panel.\n"
        "3. Click 'Generate Optimized Pathway' to run the analysis.\n\n"
        "Do you wish to proceed?"
    )
    
    # askquestion returns 'yes' or 'no'
    response = messagebox.askquestion(title, message, icon='info')
    root.destroy()
    return response == 'yes'

def main(file_path=None):
    if file_path is None:
        print("Error: No file path provided. Please provide the path to the CSV file.")
        print("Usage: python your_script_name.py path/to/your/data.csv")
        return

    # Show instructions and wait for user to accept
    if not show_startup_instructions():
        print("User declined. Exiting program.")
        sys.exit() # Exit if user clicks "Decline" / "No"
        
    print("User accepted. Loading data and launching map...")
    try:
        asset_map = load_data_from_csv(file_path)
        asset_map.draw_map()
    except FileNotFoundError:
        print(f"Error: The file was not found at {file_path}")
    except Exception as e:
        print(f"An unexpected error occurred while processing the file: {e}")

if __name__ == "__main__":
    # Check if a file path argument is provided, otherwise set to None
    file_arg = sys.argv[1] if len(sys.argv) > 1 else None
    main(file_path=file_arg)