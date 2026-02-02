# EdisonBros - MBSE Regenerative Farm System

[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive **Model-Based Systems Engineering (MBSE)** framework for **regenerative agriculture**, capable of simulating ecosystem services, carbon sequestration, and nutrient cycling through a digital twin approach.

## 🌱 Overview

This framework provides a complete MBSE system for modeling regenerative farms, integrating:

- **Four Subsystems**: Pedosphere (Soil), Hydrosphere (Water), Biosphere (Flora/Fauna), Anthroposphere (Human Management)
- **HD Topography**: High-definition terrain modeling with 3D coordinates, slope, aspect, and elevation
- **Variable Dictionary**: Comprehensive catalog of 25+ system variables
- **AMP Grazing**: Adaptive Multi-Paddock grazing management
- **No-Till Cover Cropping**: Regenerative cropping practices
- **Regenerative Index**: Quantifies net positive ecosystem impact (0-100 scale)

## 🚀 Quick Start

```python
from mbse_regenerative_farm import RegenerativeFarmSystem

# Initialize farm system
farm = RegenerativeFarmSystem(
    total_area=100.0,      # 100 hectares
    num_paddocks=10,       # 10 paddocks
    latitude=40.0          # 40°N
)

# Add livestock
farm.biosphere.add_grazing_animal("cattle", count=50)

# Simulate a season
results = farm.simulate_season(
    days=120,
    avg_precipitation=3.0,
    avg_temperature=22.0,
    avg_solar_radiation=20.0
)

# Calculate Regenerative Index
regen_index = farm.get_regenerative_index()
print(f"Regenerative Index: {regen_index['overall_index']:.2f}/100")
print(f"Classification: {regen_index['classification']}")
```

## 📋 Features

### System Architecture

**Pedosphere (Soil System)**
- Soil organic carbon dynamics
- Nutrient cycling (N, P, K)
- Water holding capacity
- Mineralization and decomposition

**Hydrosphere (Water System)**
- Green-Ampt infiltration model
- Penman-Monteith evapotranspiration
- Water balance and runoff
- Irrigation requirement calculation

**Biosphere (Flora/Fauna)**
- Plant growth modeling
- Shannon-Wiener biodiversity index
- AMP grazing dynamics
- Cover cropping benefits

**Anthroposphere (Management)**
- Adaptive Multi-Paddock grazing
- No-till cover crop rotation
- Irrigation decision support
- Monitoring and recommendations

### Feedback Loops

Critical system feedback loops:
1. **SOC → WHC → Irrigation**: Higher soil carbon = better water retention = less irrigation
2. **Biomass → Infiltration**: More plants = better infiltration
3. **Biodiversity → Resilience**: More diversity = greater stability
4. **Grazing → Growth**: Optimal grazing stimulates regrowth

### Spatial-Explicit Modeling

- Every coordinate influences local microclimate
- Topography affects water runoff and solar gain
- Elevation gradients impact drainage
- Slope and aspect determine erosion risk

## 📊 Regenerative Index

Comprehensive metric (0-100) evaluating:
- **Soil Health** (25%): SOC, nutrients, WHC
- **Water Management** (20%): Infiltration, runoff, efficiency
- **Biodiversity** (20%): Species diversity, pollinator abundance
- **Carbon Sequestration** (20%): SOC accumulation, biomass carbon
- **Nutrient Cycling** (10%): NPK availability, N fixation
- **Ecosystem Resilience** (5%): Stability, recovery capacity

**Scale:**
- 80-100: Highly Regenerative
- 60-80: Regenerative
- 40-60: Neutral
- 0-40: Degradative

## 📚 Documentation

For complete documentation, see [DOCUMENTATION.md](DOCUMENTATION.md)

## 🎯 Examples

Run the demo script to see all features:

```bash
cd examples
python demo.py
```

Examples include:
1. Basic simulation
2. Seasonal modeling
3. AMP grazing management
4. HD topography integration
5. Regenerative Index calculation
6. Complete system reports

## 🛠️ Installation

```bash
# Clone repository
git clone https://github.com/scottabney/EdisonBros.git
cd EdisonBros

# Install dependencies
pip install -r requirements.txt

# Run demo
python examples/demo.py
```

## 📦 Requirements

- Python 3.7+
- NumPy

## 🔬 Scientific Models

Implements established scientific models:
- **Green-Ampt**: Infiltration modeling
- **Penman-Monteith**: Evapotranspiration (FAO-56)
- **USLE**: Soil erosion prediction
- **RothC**: Carbon dynamics (simplified)
- **Shannon-Wiener**: Biodiversity index
- **RUE**: Radiation use efficiency for growth

## 🎓 Applications

- Farm design and planning
- Management decision support
- Education and training
- Research on ecosystem services
- Carbon accounting and credits
- Policy development

## 🤝 Contributing

Contributions welcome! Please submit pull requests or open issues.

## 📄 License

MIT License - See LICENSE file

## 👥 Authors

Edison Bros Systems Engineering Team

## 🙏 Acknowledgments

Synthesizes knowledge from:
- Regenerative agriculture practices
- Systems ecology principles
- Model-Based Systems Engineering (MBSE)
- Soil science and hydrology
- Agroecology research
