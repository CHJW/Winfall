import csv
import sys
import datetime
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Slider
import matplotlib.gridspec as gridspec
import numpy as np
import math

class Node:
    def __init__(self, data=None, components=None):
        self.data = data if data else {}
        self.components = components if components else []
        self.repair_priority_score = 0
        self.total_repair_cost = 0
        self.total_opportunity_cost = 0

    def __repr__(self):
        return f"Node(id={self.data.get('node_id', 'Unknown')}, priority={self.repair_priority_score:.2f})"
    
    def add_component(self, component):
        self.components.append(component)
        component.node = self  # Link component back to node

class Component:
    def __init__(self, node, name, lifetime_years, serial_number, installation_date, 
                 replacement_cost=0, salvage_value=0, criticality_level="routine", 
                 power_impact_factor=0, repair_hours=24):
        self.node = node
        self.name = name
        self.lifetime_years = lifetime_years
        self.lifetime_days = lifetime_years * 365
        self.current_lifetime_days = self.calculate_remaining_lifetime()
        self.serial_number = serial_number
        self.installation_date = installation_date
        self.replacement_cost = replacement_cost
        self.salvage_value = salvage_value
        self.criticality_level = criticality_level
        self.power_impact_factor = power_impact_factor
        self.repair_hours = repair_hours
        self.health_score = 0
        self.failure_probability = 0

    def calculate_remaining_lifetime(self):
        try:
            days_used = (datetime.date.today() - self.installation_date).days
            return max(0, self.lifetime_days - days_used)
        except AttributeError:
            print(f"No installation date available for component {self.name}")
            return self.lifetime_days
        except Exception as e:
            print(f"Error calculating lifetime for {self.name}: {e}")
            return 0

class CostCalculator:
    """Handles all cost calculations for maintenance operations"""
    
    def __init__(self):
        self.cost_per_distance_unit = 5.0  # $5 per unit distance
        self.base_crew_cost_per_day = 2000
        self.base_vessel_cost_per_day = 5000
        
    def calculate_transportation_cost(self, distance):
        """Calculate cost based on distance traveled"""
        return distance * self.cost_per_distance_unit
    
    def calculate_operation_cost(self, repair_hours):
        """Calculate crew and vessel costs for repair operation"""
        days = math.ceil(repair_hours / 24.0)
        return (self.base_crew_cost_per_day + self.base_vessel_cost_per_day) * days

class Map:
    def __init__(self, nodes=None):
        self.nodes = nodes if nodes else []
        self.selected_node = None
        self.cost_calculator = CostCalculator()
        self.distance_matrix = None
        self.cost_matrix = None
        self.repair_threshold_ratio = 3.0  # 3:1 benefit to cost ratio

    def add_node(self, node):
        self.nodes.append(node)

    def get_nodes(self):
        return self.nodes
    
    def calculate_component_health(self):
        """Calculate health scores for all components"""
        for node in self.nodes:
            for component in node.components:
                # Health score based on remaining lifetime (0-1 scale)
                if component.lifetime_days > 0:
                    component.health_score = component.current_lifetime_days / component.lifetime_days
                else:
                    component.health_score = 0
                
                # Failure probability (inverse of health, with curve)
                component.failure_probability = 1 - (component.health_score ** 2)
                
                print(f"Component {component.name} ({component.serial_number}): "
                      f"Health={component.health_score:.2f}, "
                      f"Failure Risk={component.failure_probability:.2f}")
    
    def calculate_repair_costs(self):
        """Calculate repair costs for all components"""
        for node in self.nodes:
            node_total_cost = 0
            for component in node.components:
                # Simple repair cost calculation
                repair_cost = component.replacement_cost * component.failure_probability
                
                # Add depreciation loss
                if component.lifetime_days > 0:
                    depreciation_loss = (component.replacement_cost - component.salvage_value) * \
                                      (1 - component.health_score)
                else:
                    depreciation_loss = component.replacement_cost
                
                component.total_repair_cost = repair_cost + depreciation_loss
                node_total_cost += component.total_repair_cost
                
            node.total_repair_cost = node_total_cost
            print(f"Node {node.data.get('node_id')}: Total repair cost = ${node_total_cost:,.2f}")
    
    def calculate_opportunity_cost(self):
        """Calculate energy production opportunity costs"""
        for node in self.nodes:
            node_opportunity_cost = 0
            
            for component in node.components:
                if component.failure_probability > 0:
                    # Calculate potential revenue loss
                    power_loss = node.data.get('power_rating', 3.0) * component.power_impact_factor
                    hours_lost = component.repair_hours * component.failure_probability
                    energy_price = node.data.get('energy_price_mwh', 50.0)
                    
                    opportunity_cost = power_loss * hours_lost * energy_price
                    component.opportunity_cost = opportunity_cost
                    node_opportunity_cost += opportunity_cost
            
            node.total_opportunity_cost = node_opportunity_cost
            print(f"Node {node.data.get('node_id')}: Opportunity cost = ${node_opportunity_cost:,.2f}")
    
    def generate_cost_matrix(self):
        """Generate distance and cost matrices between all nodes"""
        n = len(self.nodes)
        self.distance_matrix = np.zeros((n, n))
        self.cost_matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    # Calculate distance using Haversine formula (simplified)
                    lat1, lon1 = self.nodes[i].data['latitude'], self.nodes[i].data['longitude']
                    lat2, lon2 = self.nodes[j].data['latitude'], self.nodes[j].data['longitude']
                    
                    distance = np.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2)
                    self.distance_matrix[i][j] = distance
                    self.cost_matrix[i][j] = self.cost_calculator.calculate_transportation_cost(distance)
        
        print(f"Generated cost matrix for {n} nodes")
    
    def calculate_repair_priority(self):
        """Calculate repair priority scores combining all factors"""
        for node in self.nodes:
            # Total benefit (opportunity cost saved + depreciation prevented)
            total_benefit = node.total_opportunity_cost + (node.total_repair_cost * 0.5)
            
            # Total cost (repair + estimated transportation)
            avg_transport_cost = np.mean(self.cost_matrix[0]) if self.cost_matrix is not None else 1000
            total_cost = node.total_repair_cost + avg_transport_cost
            
            # Priority score (benefit/cost ratio)
            if total_cost > 0:
                node.repair_priority_score = total_benefit / total_cost
            else:
                node.repair_priority_score = 0
            
            print(f"Node {node.data.get('node_id')}: "
                  f"Priority Score = {node.repair_priority_score:.2f} "
                  f"(Benefit: ${total_benefit:,.0f}, Cost: ${total_cost:,.0f})")
    
    def filter_repair_worthy_nodes(self):
        """Filter nodes that meet repair threshold criteria"""
        worthy_nodes = [node for node in self.nodes 
                       if node.repair_priority_score >= self.repair_threshold_ratio]
        
        print(f"Filtered {len(worthy_nodes)} nodes above threshold ratio of {self.repair_threshold_ratio}")
        return worthy_nodes
    
    def optimize_route(self, filtered_nodes):
        """Optimize route using modified TSP with cost considerations"""
        if len(filtered_nodes) < 2:
            return filtered_nodes
        
        # Simple greedy algorithm weighted by priority score
        unvisited = filtered_nodes[:]
        current_node = max(unvisited, key=lambda n: n.repair_priority_score)  # Start with highest priority
        unvisited.remove(current_node)
        path = [current_node]
        
        while unvisited:
            # Find next node balancing distance and priority
            best_score = -1
            best_node = None
            
            current_idx = self.nodes.index(current_node)
            
            for candidate in unvisited:
                candidate_idx = self.nodes.index(candidate)
                distance_cost = self.cost_matrix[current_idx][candidate_idx] if self.cost_matrix is not None else 1
                
                # Score = priority / distance_cost (higher is better)
                score = candidate.repair_priority_score / max(distance_cost, 1)
                
                if score > best_score:
                    best_score = score
                    best_node = candidate
            
            if best_node:
                unvisited.remove(best_node)
                path.append(best_node)
                current_node = best_node
        
        print(f"Optimized route with {len(path)} nodes")
        return path
    
    def draw_map(self):
        fig = plt.figure(figsize=(15, 8))
        gs = gridspec.GridSpec(2, 3, width_ratios=[2, 2, 1], height_ratios=[3, 1])
        
        # Main overview map
        ax_overview = fig.add_subplot(gs[0, :2])
        ax_panel = fig.add_subplot(gs[0, 2])
        
        # Region-specific maps
        ax_region1 = fig.add_subplot(gs[1, 0])
        ax_region2 = fig.add_subplot(gs[1, 1])
        ax_region3 = fig.add_subplot(gs[1, 2])
        
        x = [node.data['latitude'] for node in self.nodes]
        y = [node.data['longitude'] for node in self.nodes]
        
        # Color nodes by priority score
        colors = [node.repair_priority_score for node in self.nodes]
        scatter = ax_overview.scatter(x, y, c=colors, cmap='RdYlGn', s=100, alpha=0.7, picker=True)
        
        ax_overview.set_title("Offshore Wind Farm - Maintenance Priority Overview")
        ax_overview.set_xlabel("Latitude")
        ax_overview.set_ylabel("Longitude")
        
        # Add colorbar
        cbar = plt.colorbar(scatter, ax=ax_overview)
        cbar.set_label('Repair Priority Score')
        
        # Group nodes by cluster for region views
        clusters = {}
        for node in self.nodes:
            cluster_name = node.data.get('cluster_name', 'Unknown')
            if cluster_name not in clusters:
                clusters[cluster_name] = []
            clusters[cluster_name].append(node)
        
        # Draw region-specific views
        region_axes = [ax_region1, ax_region2, ax_region3]
        cluster_names = list(clusters.keys())[:3]  # Show up to 3 clusters
        
        for i, (cluster_name, ax_region) in enumerate(zip(cluster_names, region_axes)):
            if cluster_name in clusters:
                cluster_nodes = clusters[cluster_name]
                cluster_x = [node.data['latitude'] for node in cluster_nodes]
                cluster_y = [node.data['longitude'] for node in cluster_nodes]
                cluster_colors = [node.repair_priority_score for node in cluster_nodes]
                
                ax_region.scatter(cluster_x, cluster_y, c=cluster_colors, cmap='RdYlGn', s=80, alpha=0.7)
                ax_region.set_title(f"{cluster_name} Region")
                ax_region.set_xlabel("Latitude")
                ax_region.set_ylabel("Longitude")
                ax_region.tick_params(labelsize=8)
                
                # Add grid for better readability
                ax_region.grid(True, alpha=0.3)
            else:
                ax_region.set_title("No Data")
                ax_region.axis('off')
        
        # Make overview map interactive with zoom
        ax_overview.set_navigate(True)  # Enable pan/zoom
        ax_overview.grid(True, alpha=0.3)
        
        ax_panel.set_title("Node Details")
        ax_panel.axis('off')
        
        slider_ax = fig.add_axes([0.87, 0.3, 0.02, 0.4], facecolor='lightgoldenrodyellow')
        slider = Slider(slider_ax, 'Scroll', 0, 1, valinit=1, orientation='vertical')

        def update_panel(node):
            ax_panel.clear()
            ax_panel.set_title("Node Details")
            ax_panel.axis('off')
            
            if node and node.components:
                info_text = f"Node: {node.data.get('node_id', 'Unknown')}\n"
                info_text += f"Priority Score: {node.repair_priority_score:.2f}\n"
                info_text += f"Power Rating: {node.data.get('power_rating', 0):.1f} MW\n"
                info_text += f"Water Depth: {node.data.get('water_depth', 0):.1f} m\n\n"
                
                component_texts = []
                for component in node.components:
                    comp_text = f"{component.name} ({component.serial_number})\n"
                    comp_text += f"  Health: {component.health_score:.2f}\n"
                    comp_text += f"  Failure Risk: {component.failure_probability:.2f}\n"
                    comp_text += f"  Criticality: {component.criticality_level}\n"
                    component_texts.append(comp_text)
                
                all_text = info_text + "\n".join(component_texts)
            else:
                all_text = "No node selected or no components found."
            
            ax_panel.text(0.05, 0.95, all_text, transform=ax_panel.transAxes, 
                         fontsize=8, verticalalignment='top', fontfamily='monospace')
            
            fig.canvas.draw_idle()
        
        def on_click(event):
            if event.inaxes == ax_overview:
                cont, ind = scatter.contains(event)
                if cont:
                    self.selected_node = self.nodes[ind['ind'][0]]
                    update_panel(self.selected_node)
        
        def generate_pathway(event):
            print("\n=== GENERATING OPTIMIZED MAINTENANCE PATHWAY ===")
            
            # Run all analysis steps
            self.calculate_component_health()
            self.calculate_repair_costs()
            self.calculate_opportunity_cost()
            self.generate_cost_matrix()
            self.calculate_repair_priority()
            
            # Filter and optimize
            worthy_nodes = self.filter_repair_worthy_nodes()
            optimized_path = self.optimize_route(worthy_nodes)
            
            if len(optimized_path) < 1:
                print("No nodes meet the repair threshold criteria.")
                return
            
            # Draw the optimized path on overview map
            path_x = [node.data['latitude'] for node in optimized_path]
            path_y = [node.data['longitude'] for node in optimized_path]
            ax_overview.plot(path_x, path_y, 'r-', linewidth=2, label='Optimized Maintenance Route')
            
            # Highlight start and end
            if optimized_path:
                ax_overview.scatter(path_x[0], path_y[0], c='green', s=200, marker='s', label='Start')
                if len(optimized_path) > 1:
                    ax_overview.scatter(path_x[-1], path_y[-1], c='red', s=200, marker='X', label='End')
            
            ax_overview.legend()
            fig.canvas.draw_idle()
            
            # Print summary
            total_benefit = sum(node.total_opportunity_cost + node.total_repair_cost * 0.5 
                              for node in optimized_path)
            total_cost = sum(node.total_repair_cost for node in optimized_path)
            
            print(f"\n=== PATHWAY SUMMARY ===")
            print(f"Nodes to visit: {len(optimized_path)}")
            print(f"Total estimated benefit: ${total_benefit:,.2f}")
            print(f"Total estimated cost: ${total_cost:,.2f}")
            print(f"Overall benefit/cost ratio: {total_benefit/max(total_cost, 1):.2f}")

        # Generate pathway button
        generate_pathway_button_ax = fig.add_axes([0.02, 0.02, 0.12, 0.06])
        generate_pathway_button = Button(generate_pathway_button_ax, 'Generate\nPathway')
        generate_pathway_button.on_clicked(generate_pathway)

        # Add zoom instruction text
        fig.text(0.02, 0.92, 'Use mouse wheel or toolbar to zoom in/out on overview map', 
                fontsize=10, style='italic', alpha=0.7)

        slider.on_changed(lambda val: update_panel(self.selected_node) if self.selected_node else None)
        fig.canvas.mpl_connect('button_press_event', on_click)
        plt.show()

def opendata(file_path):
    with open(file_path, mode='r') as file:
        reader = csv.reader(file)
        header = next(reader)  # Read header row
        
        nodes = []
        current_node_data = None
        current_components = []
        
        for row in reader:
            (node_id, latitude, longitude, water_depth, power_rating, 
             current_output, energy_price_mwh, cluster_name,
             component_name, lifetime_years, serial_number, installation_date,
             replacement_cost, salvage_value, criticality_level, 
             power_impact_factor, repair_hours) = row
            
            # Convert data types
            latitude = float(latitude)
            longitude = float(longitude)
            water_depth = float(water_depth)
            power_rating = float(power_rating)
            current_output = float(current_output)
            energy_price_mwh = float(energy_price_mwh)
            lifetime_years = int(lifetime_years)
            replacement_cost = float(replacement_cost)
            salvage_value = float(salvage_value)
            power_impact_factor = float(power_impact_factor)
            repair_hours = float(repair_hours)
            installation_date = datetime.datetime.strptime(installation_date, "%Y-%m-%d").date()
            
            # Check if we are still on the same node
            node_key = (node_id, latitude, longitude)
            if current_node_data is None or current_node_data['node_key'] != node_key:
                # If we have collected components for a node, add it to the list
                if current_node_data is not None:
                    nodes.append(Node(data=current_node_data, components=current_components))
                
                # Start a new node
                current_node_data = {
                    "node_key": node_key,
                    "node_id": node_id,
                    "latitude": latitude,
                    "longitude": longitude,
                    "water_depth": water_depth,
                    "power_rating": power_rating,
                    "current_output": current_output,
                    "energy_price_mwh": energy_price_mwh,
                    "cluster_name": cluster_name
                }
                current_components = []
            
            # Add the component to the current node
            component = Component(
                node=None,  # Will be set when added to node
                name=component_name,
                lifetime_years=lifetime_years,
                serial_number=serial_number,
                installation_date=installation_date,
                replacement_cost=replacement_cost,
                salvage_value=salvage_value,
                criticality_level=criticality_level,
                power_impact_factor=power_impact_factor,
                repair_hours=repair_hours
            )
            current_components.append(component)
        
        # Add the last node
        if current_node_data is not None:
            nodes.append(Node(data=current_node_data, components=current_components))
        
        # Link components back to their nodes
        for node in nodes:
            for component in node.components:
                component.node = node
        
        windmill_map = Map(nodes)
        print(f"Loaded {len(windmill_map.get_nodes())} nodes from file.")
        print(f"Total components: {sum(len(node.components) for node in nodes)}")
        windmill_map.draw_map()

def main(file_path=None):
    if file_path is None:
        return print("No file path inputted. Please provide the path to the CSV file.")
    else:
        try:
            opendata(file_path)
        except FileNotFoundError:
            print(f"File not found: {file_path}")
        except Exception as e:
            print(f"An error occurred while processing the file: {e}")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)