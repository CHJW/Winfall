# Offshore Wind Farm Maintenance Optimization

## Overview

This project implements an intelligent maintenance scheduling system for offshore wind farms, solving a modified Traveling Salesman Problem (TSP) where the "salesman" (maintenance vessel) visits wind turbines based on **opportunity cost analysis** rather than pure distance optimization.

### The Problem
Offshore wind farm maintenance involves:
- **Discrete transportation** via boats (not continuous like land-based transport)
- **High operational costs** due to weather windows and vessel requirements
- **Complex cost structures** involving real costs, projected depreciation, and opportunity costs
- **Critical decision making** about which turbines warrant expensive offshore visits

### The Solution
Our system calculates the **optimal maintenance pathway** by:
1. **Analyzing component health** and failure probability
2. **Calculating comprehensive costs** (repair, transportation, opportunity)
3. **Prioritizing turbines** using cost-benefit analysis
4. **Optimizing routes** with early termination capability
5. **Filtering uneconomical repairs** using configurable thresholds

## Current Status: MVP Stage 2 - Enhanced User Experience ✅

### Features Implemented
- ✅ **Enhanced Data Structure**: Realistic offshore wind farm data with component specifications
- ✅ **Cost Calculation Engine**: Multi-factor cost analysis framework
- ✅ **Priority Scoring System**: Repair urgency based on opportunity cost
- ✅ **Interactive Visualization**: Overview map with click-to-inspect nodes
- ✅ **Route Optimization**: Modified TSP with cost-benefit weighting
- ✅ **Threshold Filtering**: Configurable repair worthiness criteria (default: 0.52 benefit/cost ratio)
- ✅ **GUI Data Generator**: Integrated popup interface for creating custom wind farm data
- ✅ **Seamless Workflow**: Automatic data source detection and loading indicators
- ✅ **Future Predictions**: Date-based maintenance forecasting with validation

### Technical Implementation
- **Component Health Assessment**: Calculates degradation and failure probability
- **Multi-Cost Analysis**: Real, projected, and opportunity cost calculations
- **Spatial Clustering**: Realistic wind farm layouts across multiple regions
- **Interactive Interface**: Click-to-inspect nodes, interactive input fields, pathway generation
- **User Experience**: Startup instructions, loading indicators, seamless data generation workflow

## Cost Analysis Framework

| **Cost Type** | **Category** | **Cost Item** | **Calculation Method** | **Example/Estimate** |
|---------------|--------------|---------------|------------------------|----------------------|
| **Real/Capital** | Direct | New component costs | Step/Binary (buy/no buy) | Gearbox: $500K, Blade set: $200K, Generator: $300K |
| **Real/Capital** | Direct | Component transportation | Discrete step by vessel type | Small parts: $2K, Large components: $50K |
| **Real/Capital** | Direct | Crew costs | Linear by time | Technician crew: $2K/day, Specialist: $5K/day |
| **Real/Capital** | Direct | Vessel charter | Linear by time + fixed mobilization | CTV: $5K/day, SOV: $25K/day, HLV: $100K/day |
| **Real/Capital** | Direct | Fuel costs | Linear by distance | $2/nautical mile |
| **Projected** | Depreciation | Component depreciation | Linear by remaining lifetime | (Original_cost - Salvage) × (Days_used/Total_days) |
| **Opportunity** | Revenue Loss | Energy production loss | Linear by downtime | 3MW × $50/MWh × 24hrs = $3,600/day |
| **Opportunity** | Timing | Weather window penalty | Step cost (miss = delay weeks) | Missing window: +$50K vessel standby |
| **Opportunity** | Efficiency | Route inefficiency | Linear by extra distance | Additional travel: $5/unit distance |
| **Missing - Operational** | Storage | Inventory holding | Linear by time and value | 2% annual holding cost of component value |
| **Missing - Risk** | Insurance | Offshore operation premium | Percentage of operation value | 3-5% of total operation cost |
| **Missing - Regulatory** | Compliance | Environmental permits | Fixed per operation | $10K per major repair operation |
| **Missing - Regulatory** | Safety | Safety inspections | Fixed per vessel mobilization | $5K per vessel deployment |
| **Missing - Risk** | Contingency | Weather delay buffer | Percentage of planned costs | 15-20% of base operation cost |
| **Missing - Operational** | Logistics | Port/base facility | Fixed daily rate | $1K/day port charges |

## Getting Started

### Prerequisites
- Python 3.7+
- Required packages: `matplotlib`, `numpy`, `csv`, `datetime`

### Quick Start

#### Option 1: Using Existing Data
```bash
# Run with existing data file
python main.py nodes_data.csv
```

#### Option 2: Generate New Data (Recommended)
```bash
# Launch with integrated data generator
python main.py
```

The application will:
1. **Show startup instructions** with clear guidance
2. **Detect existing data sources** or offer to generate new ones
3. **Launch GUI data generator** if no data exists
4. **Display loading indicator** during map generation
5. **Present interactive visualization** ready for analysis

### User Interface Features

#### Startup Experience
- **Welcome Dialog**: Clear instructions and data source status
- **Data Generation**: Integrated GUI for creating custom wind farm scenarios
- **Loading Indicators**: Visual feedback during data processing
- **Seamless Workflow**: No need to restart application after generating data

#### Main Interface
- **Interactive Map**: Click any turbine to see detailed component information
- **Dynamic Controls**: Adjust prediction date, repair threshold, and cost parameters
- **Real-time Updates**: All calculations update automatically when parameters change
- **Visual Feedback**: Selected nodes highlighted in red, clusters color-coded
- **Pathway Generation**: Click "Generate Pathway" to run full optimization analysis
- **Map Controls**: Reset map view, zoom, and pan functionality

#### Data Generator Features
- **Comprehensive Input Fields**: Customize all component lifetimes and costs
- **Validation**: Built-in checks for valid inputs and file naming
- **File Management**: Automatic overwrite warnings and file existence checks
- **Default Values**: Sensible defaults based on industry standards
- **Instant Feedback**: Clear error messages and success confirmations

### Understanding the Output

#### Visual Elements
- **Node Colors**: Each wind farm cluster has a distinct color
- **Selected Nodes**: Highlighted in red when clicked
- **Optimized Route**: Red line connecting turbines in optimal sequence
- **Route Markers**: Green star (start), red X (end point)
- **Legend**: Shows cluster names and selected node indicator

#### Interactive Controls
- **Prediction Date**: Set future date for maintenance forecasting (validates against current date)
- **Repair Threshold Ratio**: Minimum benefit/cost ratio for repair consideration
- **Cost Per Distance**: Transportation cost multiplier for route optimization

#### Console Output
- **Priority Scores**: Higher scores indicate better cost-benefit ratios
- **Filtering Results**: Number of nodes meeting repair threshold criteria
- **Route Summary**: Total estimated benefits, costs, and overall benefit/cost ratio
- **Detailed Analysis**: Component-by-component breakdown for each turbine

#### Component Information Panel
- **Node Details**: ID, cluster, priority score, power rating
- **Component Status**: Health scores, failure probabilities, criticality levels
- **Cost Analysis**: Repair costs, opportunity costs, and replacement values

## Next Steps: MVP Development Roadmap

### **Stage 3: Financial Cost Model** (Next Priority)
**Objective**: Complete economic decision-making capability

**Required Implementations**:
- [ ] **Weather Window Integration**: Seasonal accessibility and delay costs
- [ ] **Advanced Depreciation Models**: Non-linear degradation curves
- [ ] **Dynamic Pricing**: Real-time energy market integration
- [ ] **Multi-Component Interactions**: Cascading failure analysis
- [ ] **Inventory Management**: Optimal spare parts positioning
- [ ] **Risk Assessment**: Weather delay probabilities and costs

**Key Functions to Enhance**:
- `calculate_opportunity_cost()`: Add weather window penalties
- `calculate_repair_costs()`: Include inventory and logistics costs
- `calculate_repair_priority()`: Multi-component failure scenarios
- `filter_repair_worthy_nodes()`: Dynamic threshold adjustment

### **Stage 4: Route Optimization** (Medium Priority)
**Objective**: Advanced pathway optimization

**Required Implementations**:
- [ ] **Multi-Objective Optimization**: Genetic algorithm or simulated annealing
- [ ] **Time Window Constraints**: Weather-dependent scheduling
- [ ] **Vessel Capacity Planning**: Component size and weight limitations
- [ ] **Return Journey Optimization**: Fuel capacity and base return requirements
- [ ] **Multi-Trip Scenarios**: Large repair programs over multiple voyages

### **Stage 5: Operational Constraints** (Future)
**Objective**: Real-world operational integration

**Required Implementations**:
- [ ] **Fleet Management**: Multiple vessel coordination
- [ ] **Weather Forecasting**: API integration for real-time conditions
- [ ] **Regulatory Compliance**: Environmental and safety requirement tracking
- [ ] **Performance Monitoring**: Historical repair effectiveness analysis

### **Stage 6: Advanced Analytics** (Future)
**Objective**: Strategic maintenance planning

**Required Implementations**:
- [ ] **Predictive Maintenance**: Machine learning failure prediction
- [ ] **Seasonal Optimization**: Annual maintenance program planning
- [ ] **Portfolio Management**: Multi-farm optimization across regions
- [ ] **ROI Dashboard**: Financial performance tracking and reporting

## Data Structure

### Node (Wind Turbine)
```python
{
    'node_id': 'WTG_01',
    'latitude': 54.52,
    'longitude': 2.15,
    'water_depth': 25.3,
    'power_rating': 3.0,      # MW
    'current_output': 2.7,    # MW (accounting for issues)
    'energy_price_mwh': 52.0, # $/MWh
    'cluster_name': 'North Sea Alpha'
}
```

### Component
```python
{
    'name': 'Gearbox',
    'replacement_cost': 500000,
    'salvage_value': 50000,
    'criticality_level': 'critical',
    'power_impact_factor': 1.0,  # 100% power loss if failed
    'repair_hours': 72,
    'health_score': 0.65,        # Calculated
    'failure_probability': 0.58   # Calculated
}
```

## Configuration

### Interactive Parameters (Adjustable via GUI)
- **Repair Threshold Ratio**: `0.52` (default minimum benefit/cost ratio)
- **Transportation Cost**: `$5/unit distance` (adjustable in interface)
- **Prediction Date**: Current date (can be set to future dates for forecasting)

### System Parameters
- **Base Vessel Cost**: `$5,000/day`
- **Base Crew Cost**: `$2,000/day`
- **Default Component Lifetimes**: Blade (20y), Gearbox (15y), Generator (18y), etc.

### Customization Options
1. **Via GUI**: Use the interactive input fields in the main interface
2. **Via Data Generator**: Customize component costs and lifetimes when creating data
3. **Via Code**: Modify default values in `Map.__init__()` and `DataMakerGUI.default_values`

### Runtime Environment
For Nix users, run with proper package environment:
```bash
nix-shell -p python3 python3Packages.matplotlib python3Packages.numpy python3Packages.tkinter --run "python main.py"
```

## For AI Assistants: Development Guidance

### Immediate Tasks (Stage 3 Focus)
1. **Weather Integration**: Add seasonal accessibility windows to node data
2. **Advanced Costing**: Implement non-linear depreciation and cascading failure costs
3. **Dynamic Thresholds**: Make repair thresholds adaptive based on market conditions
4. **Inventory Optimization**: Add spare parts logistics to cost calculations

### Code Enhancement Priorities
1. **CostCalculator Class**: Expand with weather delay and inventory holding costs
2. **Component Health**: Add predictive failure modeling beyond simple lifetime
3. **Route Optimization**: Replace greedy algorithm with genetic algorithm or A*
4. **Data Validation**: Add comprehensive error handling and data validation

### Testing Strategy
- **Unit Tests**: Each cost calculation function
- **Integration Tests**: Full pathway generation pipeline
- **Performance Tests**: Large-scale wind farm scenarios (100+ turbines)
- **Validation Tests**: Compare with actual maintenance records

### Architecture Considerations
- **Modularity**: Separate concerns (data, calculations, visualization, optimization)
- **Scalability**: Design for 500+ turbine wind farms
- **Extensibility**: Plugin architecture for new cost factors and optimization algorithms
- **Data Sources**: Prepare for real-time API integrations (weather, energy prices)

## Recent Improvements

### Version 2.1 - Enhanced User Experience
- **Integrated Data Generator**: Seamless workflow from data creation to visualization
- **Loading Indicators**: Clear feedback during data processing and map generation
- **Input Validation**: Date validation with future prediction capabilities
- **Window Management**: Proper GUI window lifecycle and closing behavior
- **Error Handling**: Comprehensive validation and user-friendly error messages

### Version 2.0 - Interactive Interface
- **Dynamic Parameters**: Real-time adjustment of prediction date, thresholds, and costs
- **Visual Enhancements**: Improved node selection, color coding, and route visualization
- **Component Details**: Detailed component information panel with health metrics
- **Future Predictions**: Date-based forecasting for maintenance planning

## Contributing

### Development Environment Setup
1. Clone the repository
2. Install dependencies: `matplotlib`, `numpy`, `tkinter`
3. For Nix users: Use the provided nix-shell command
4. Run tests: `python -m pytest` (when implemented)

### Code Structure
- `main.py`: Core application with GUI and optimization logic
- `datamaker.py`: Data generation utility with GUI interface
- `nodes_data.csv`: Sample wind farm data (auto-generated)

---

This project represents a sophisticated approach to offshore wind farm maintenance optimization, combining financial modeling, operational research, and practical engineering constraints into an actionable decision-support system with an intuitive user interface.