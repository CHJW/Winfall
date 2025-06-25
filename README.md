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

## Current Status: MVP Stage 2 - Realistic Data Foundation ✅

### Features Implemented
- ✅ **Enhanced Data Structure**: Realistic offshore wind farm data with component specifications
- ✅ **Cost Calculation Engine**: Multi-factor cost analysis framework
- ✅ **Priority Scoring System**: Repair urgency based on opportunity cost
- ✅ **Interactive Visualization**: Overview map with regional zoom views
- ✅ **Route Optimization**: Modified TSP with cost-benefit weighting
- ✅ **Threshold Filtering**: Configurable repair worthiness criteria (default: 3:1 benefit/cost ratio)

### Technical Implementation
- **Component Health Assessment**: Calculates degradation and failure probability
- **Multi-Cost Analysis**: Real, projected, and opportunity cost calculations
- **Spatial Clustering**: Realistic wind farm layouts across multiple regions
- **Interactive Interface**: Click-to-inspect nodes, zoomable maps, pathway generation

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
1. **Generate Test Data**:
   ```bash
   python datamaker.py
   ```
   This creates `nodes_data.csv` with 25 offshore wind turbines across 3 realistic wind farm clusters.

2. **Run Analysis**:
   ```bash
   python main.py nodes_data.csv
   ```

3. **Interact with Interface**:
   - **Overview Map**: Shows all turbines color-coded by repair priority
   - **Regional Views**: Detailed views of individual wind farm clusters
   - **Zoom**: Use mouse wheel or toolbar to zoom in/out on overview map
   - **Inspect Nodes**: Click any turbine to see detailed component information
   - **Generate Pathway**: Click button to run full optimization analysis

### Understanding the Output
The system provides:
- **Priority Scores**: Higher scores indicate better cost-benefit ratios
- **Optimized Route**: Red line showing recommended maintenance sequence
- **Console Analysis**: Detailed cost breakdowns and filtering results
- **Visual Indicators**: Green square (start), red X (end), color-coded priorities

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

### Key Parameters
- **Repair Threshold Ratio**: `3.0` (3:1 benefit-to-cost ratio)
- **Transportation Cost**: `$5/unit distance`
- **Base Vessel Cost**: `$5,000/day`
- **Base Crew Cost**: `$2,000/day`

### Customization
Modify these parameters in `Map.__init__()`:
```python
self.repair_threshold_ratio = 3.0  # Adjust repair worthiness threshold
self.cost_calculator.cost_per_distance_unit = 5.0  # Adjust transport costs
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

This project represents a sophisticated approach to offshore wind farm maintenance optimization, combining financial modeling, operational research, and practical engineering constraints into an actionable decision-support system.