# MBSE Regenerative Farm System

A comprehensive Model-Based Systems Engineering (MBSE) framework for regenerative agriculture, capable of simulating ecosystem services, carbon sequestration, and nutrient cycling.

## Overview

This framework provides a digital twin of a regenerative farm system that integrates:

- **Structural Definition (Ontology)**: System hierarchy with four main subsystems
- **HD Topography Integration**: High-definition terrain modeling for spatial-explicit simulations
- **Variable Dictionary**: Comprehensive catalog of input, state, and flow/process variables
- **Functional Requirements**: AMP grazing, no-till cover cropping, and feedback loops
- **Regenerative Index**: Quantifies net positive ecosystem impact over time

## System Architecture

### Subsystems

1. **Pedosphere (Soil System)**
   - Soil organic carbon dynamics
   - Nutrient cycling (N, P, K)
   - Water holding capacity
   - Soil health indicators

2. **Hydrosphere (Water System)**
   - Water balance modeling
   - Green-Ampt infiltration model
   - Penman-Monteith evapotranspiration
   - Runoff and drainage calculations

3. **Biosphere (Flora/Fauna System)**
   - Plant growth modeling
   - Biodiversity tracking (Shannon-Wiener index)
   - Grazing dynamics
   - Carbon sequestration from biomass

4. **Anthroposphere (Human Management)**
   - Adaptive Multi-Paddock (AMP) grazing
   - No-till cover cropping
   - Irrigation decision support
   - Monitoring and adaptive management

### HD Topography Integration

The system incorporates high-definition terrain data including:
- 3D coordinates (x, y, z)
- Slope gradients and aspects
- Elevation-based microclimate adjustments
- Water runoff direction and contributing areas
- Solar gain factors based on slope and aspect
- Erosion risk assessment

### Variable Dictionary

Comprehensive variable catalog with three categories:

**Input Variables:**
- Precipitation (P)
- Solar radiation (R_s)
- Initial soil organic carbon (SOC_0)
- Bulk density (ρ_b)
- Microbial biomass carbon (MBC)
- Temperature (T)

**State Variables:**
- Soil moisture content (θ)
- NPK levels (N, P, K)
- Soil organic carbon (SOC)
- Water holding capacity (WHC)
- Biodiversity index (BI)
- Plant biomass (B_p)

**Flow/Process Variables:**
- Carbon sequestration rate (C_seq)
- Infiltration rate (I) - Green-Ampt logic
- Evapotranspiration (ET_0) - Penman-Monteith
- Surface runoff (Q)
- Nutrient mineralization (N_min)
- Decomposition rate (k_d)

## Key Features

### Feedback Loops

The system implements critical feedback loops:

1. **SOC → WHC → Irrigation**: Increased soil organic carbon improves water holding capacity, reducing irrigation requirements
2. **Biomass → Infiltration**: Higher plant biomass increases soil infiltration capacity
3. **Biodiversity → Resilience**: Greater biodiversity enhances system resilience
4. **Grazing → Growth**: Moderate grazing stimulates plant regrowth

### Spatial-Explicit Modeling

Every coordinate influences local behavior:
- Microclimate variations based on topography
- Water flow patterns following terrain
- Solar gain adjusted for slope and aspect
- Drainage behavior varies by elevation gradient

### Regenerative Index

The Regenerative Index (0-100) quantifies net positive ecosystem impact:
- **0-40**: Degradative (net negative)
- **40-60**: Neutral (status quo)
- **60-80**: Regenerative (net positive)
- **80-100**: Highly regenerative (strong positive)

Components:
- Soil health (25%)
- Water management (20%)
- Biodiversity (20%)
- Carbon sequestration (20%)
- Nutrient cycling (10%)
- Ecosystem resilience (5%)

## Installation

```bash
# Clone the repository
git clone https://github.com/scottabney/EdisonBros.git
cd EdisonBros

# Install dependencies
pip install numpy
```

## Quick Start

```python
from mbse_regenerative_farm import RegenerativeFarmSystem

# Initialize the farm system
farm = RegenerativeFarmSystem(
    total_area=100.0,      # 100 hectares
    num_paddocks=10,       # 10 paddocks for rotation
    latitude=40.0,         # 40°N latitude
    grid_resolution=10.0   # 10m grid resolution
)

# Add grazing animals
farm.biosphere.add_grazing_animal("cattle", count=50)

# Simulate one day
result = farm.simulate_time_step(
    precipitation=5.0,      # 5mm rainfall
    temperature=20.0,       # 20°C
    solar_radiation=20.0,   # 20 MJ/m²/day
    day_of_year=180        # Mid-summer
)

# View results
print(f"Soil Moisture: {result['pedosphere']['moisture']:.2f}%")
print(f"Total Biomass: {result['biosphere']['total_biomass']:.2f} t/ha")
```

## Usage Examples

### Seasonal Simulation

```python
# Simulate a full growing season (120 days)
results = farm.simulate_season(
    days=120,
    avg_precipitation=3.0,
    avg_temperature=22.0,
    avg_solar_radiation=22.0,
    start_day_of_year=120
)

# Compare initial and final states
print(f"SOC Change: {results[-1]['pedosphere']['soil_organic_carbon'] - results[0]['pedosphere']['soil_organic_carbon']:.2f} t/ha")
```

### HD Topography Integration

```python
import numpy as np

# Create or load Digital Elevation Model (DEM)
dem = np.loadtxt('terrain_data.csv')  # Or create synthetic DEM

# Load into system
farm.load_topography(
    dem=dem,
    cell_size=10.0,  # 10m resolution
    origin_x=0.0,
    origin_y=0.0
)

# Query topographic properties at specific locations
point = farm.topography.get_point(50, 50)
print(f"Elevation: {point.elevation:.1f}m")
print(f"Slope: {point.slope:.1f}°")
print(f"Aspect: {point.aspect_direction.value}")

# Get microclimate factors
microclimate = farm.calculate_microclimate_adjustment(50, 50, day_of_year=180)
print(f"Solar gain: {microclimate['radiation_factor']:.2f}")
```

### AMP Grazing Management

```python
# Set up intensive rotational grazing
farm = RegenerativeFarmSystem(
    total_area=50.0,
    num_paddocks=20,  # More paddocks = shorter grazing, longer rest
    latitude=35.0
)

farm.biosphere.add_grazing_animal("cattle", count=30)

# Simulate and monitor paddock rotation
results = farm.simulate_season(days=60)

# Check paddock recovery status
for paddock in farm.anthroposphere.paddocks:
    print(f"Paddock {paddock.id}: Biomass={paddock.current_biomass:.2f} t/ha, "
          f"Rest={paddock.rest_days} days, Ready={paddock.is_ready_for_grazing}")
```

### Regenerative Index Calculation

```python
# Run simulation
farm.simulate_season(days=365)

# Calculate Regenerative Index
regen_index = farm.get_regenerative_index()

print(f"Overall Index: {regen_index['overall_index']:.2f}")
print(f"Classification: {regen_index['classification']}")
print(f"Soil Health: {regen_index['soil_health_score']:.2f}")
print(f"Carbon Sequestration: {regen_index['carbon_score']:.2f}")
```

### Complete System Report

```python
# Generate comprehensive report
report = farm.generate_report()
print(report)
```

## Module Documentation

### RegenerativeFarmSystem

Main integration class that coordinates all subsystems.

**Key Methods:**
- `simulate_time_step()`: Simulate one time step (typically 1 day)
- `simulate_season()`: Simulate multiple days with automated inputs
- `load_topography()`: Load HD terrain data
- `get_regenerative_index()`: Calculate regenerative performance
- `generate_report()`: Generate comprehensive system report

### Subsystems

#### Pedosphere
Manages soil properties and processes.
- `update_soil_organic_carbon()`: Carbon balance modeling
- `calculate_mineralization_rate()`: N mineralization
- `update_nutrients()`: Nutrient cycling
- `calculate_soil_health_index()`: Overall soil health (0-100)

#### Hydrosphere
Manages water balance and flow.
- `calculate_green_ampt_infiltration()`: Infiltration modeling
- `calculate_evapotranspiration()`: ET calculation (Penman-Monteith)
- `calculate_irrigation_requirement()`: Irrigation decision support
- `update_water_balance()`: Complete water balance update

#### Biosphere
Manages biological components.
- `calculate_plant_growth()`: Growth rate calculation
- `apply_grazing()`: AMP grazing impact
- `apply_cover_cropping()`: Cover crop benefits
- `calculate_shannon_diversity()`: Biodiversity index

#### Anthroposphere
Manages human decision-making.
- `plan_amp_grazing()`: Adaptive grazing rotation planning
- `plan_cover_crop_rotation()`: Seasonal cover crop planning
- `make_irrigation_decision()`: Adaptive irrigation decisions
- `monitor_and_adapt()`: System monitoring and recommendations

### HD Topography

High-definition terrain modeling.
- `load_from_dem()`: Load Digital Elevation Model
- `calculate_slope()`: Calculate slope using finite differences
- `calculate_aspect()`: Calculate aspect (direction of slope)
- `calculate_runoff_direction()`: Downhill flow direction
- `calculate_microclimate_factor()`: Microclimate adjustments

## Scientific Basis

The framework implements established scientific models:

- **Green-Ampt Infiltration**: Physically-based infiltration model
- **Penman-Monteith ET**: FAO-56 reference evapotranspiration
- **USLE**: Universal Soil Loss Equation for erosion
- **RothC Carbon Model**: Simplified carbon dynamics
- **Shannon-Wiener Index**: Biodiversity measurement
- **Radiation Use Efficiency**: Crop growth modeling

## Applications

This framework can be used for:

1. **Farm Planning**: Design regenerative farm systems
2. **Decision Support**: Optimize management practices
3. **Education**: Teach regenerative agriculture principles
4. **Research**: Study ecosystem service provision
5. **Carbon Accounting**: Quantify carbon sequestration
6. **Policy Development**: Evaluate regenerative practices

## Requirements

- Python 3.7+
- NumPy

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please submit pull requests or open issues on GitHub.

## Authors

Edison Bros Systems Engineering Team

## Acknowledgments

This framework synthesizes knowledge from regenerative agriculture, systems ecology, and MBSE principles.
