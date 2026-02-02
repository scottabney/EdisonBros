"""
Example Usage of MBSE Regenerative Farm System

Demonstrates how to use the regenerative farm system framework
for modeling and simulation.
"""

import numpy as np
from mbse_regenerative_farm import RegenerativeFarmSystem

def basic_example():
    """Basic example of system initialization and simulation"""
    print("=" * 70)
    print("BASIC EXAMPLE: Single Day Simulation")
    print("=" * 70)
    
    # Initialize the farm system
    farm = RegenerativeFarmSystem(
        total_area=100.0,  # 100 hectares
        num_paddocks=10,   # 10 paddocks for rotation
        latitude=40.0,     # 40°N latitude
        grid_resolution=10.0  # 10m grid resolution
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
    
    print("\nSingle Day Results:")
    print(f"  Soil Moisture: {result['pedosphere']['moisture']:.2f}%")
    print(f"  SOC: {result['pedosphere']['soil_organic_carbon']:.2f} t/ha")
    print(f"  Total Biomass: {result['biosphere']['total_biomass']:.2f} t/ha")
    print(f"  Biodiversity Index: {result['biosphere']['biodiversity_index']:.2f}")
    print()


def seasonal_simulation():
    """Simulate a full growing season"""
    print("=" * 70)
    print("SEASONAL SIMULATION: 120 Day Growing Season")
    print("=" * 70)
    
    # Initialize system
    farm = RegenerativeFarmSystem(
        total_area=100.0,
        num_paddocks=12,
        latitude=40.0
    )
    
    # Add grazing animals
    farm.biosphere.add_grazing_animal("cattle", count=40)
    
    # Simulate growing season (120 days)
    results = farm.simulate_season(
        days=120,
        avg_precipitation=3.0,      # 3mm/day average
        avg_temperature=22.0,       # 22°C average
        avg_solar_radiation=22.0,   # 22 MJ/m²/day average
        start_day_of_year=120      # Start in late spring
    )
    
    print(f"\nSimulated {len(results)} days")
    
    # Show initial and final state
    initial = results[0]
    final = results[-1]
    
    print("\nInitial State:")
    print(f"  SOC: {initial['pedosphere']['soil_organic_carbon']:.2f} t/ha")
    print(f"  Biomass: {initial['biosphere']['total_biomass']:.2f} t/ha")
    print(f"  Biodiversity: {initial['biosphere']['biodiversity_index']:.2f}")
    
    print("\nFinal State:")
    print(f"  SOC: {final['pedosphere']['soil_organic_carbon']:.2f} t/ha")
    print(f"  Biomass: {final['biosphere']['total_biomass']:.2f} t/ha")
    print(f"  Biodiversity: {final['biosphere']['biodiversity_index']:.2f}")
    
    print("\nChanges:")
    soc_change = final['pedosphere']['soil_organic_carbon'] - initial['pedosphere']['soil_organic_carbon']
    print(f"  SOC Change: {soc_change:+.2f} t/ha")
    print(f"  Cumulative C Sequestration: {final['cumulative_carbon_sequestration']:.2f} t C/ha")
    print()


def amp_grazing_example():
    """Demonstrate Adaptive Multi-Paddock (AMP) grazing management"""
    print("=" * 70)
    print("AMP GRAZING EXAMPLE")
    print("=" * 70)
    
    # Initialize system with more paddocks for intensive rotation
    farm = RegenerativeFarmSystem(
        total_area=50.0,
        num_paddocks=20,  # More paddocks = shorter grazing, longer rest
        latitude=35.0
    )
    
    # Add livestock
    farm.biosphere.add_grazing_animal("cattle", count=30)
    
    print(f"\nFarm Setup:")
    print(f"  Total Area: {farm.total_area} ha")
    print(f"  Number of Paddocks: {farm.anthroposphere.num_paddocks}")
    print(f"  Paddock Size: {farm.anthroposphere.paddock_area:.2f} ha")
    print(f"  Herd Size: 30 cattle")
    
    # Simulate 60 days to show paddock rotation
    results = farm.simulate_season(
        days=60,
        avg_precipitation=2.5,
        avg_temperature=20.0,
        avg_solar_radiation=20.0
    )
    
    print(f"\nSimulation Complete: {len(results)} days")
    
    # Show paddock states
    final_state = results[-1]
    print("\nPaddock Status:")
    for paddock_info in final_state['anthroposphere']['paddock_states'][:5]:  # Show first 5
        print(f"  Paddock {paddock_info['id']}: "
              f"Biomass={paddock_info['biomass']:.2f} t/ha, "
              f"Rest={paddock_info['rest_days']} days, "
              f"Ready={paddock_info['ready']}")
    
    print()


def topography_integration():
    """Demonstrate HD topography integration"""
    print("=" * 70)
    print("HD TOPOGRAPHY INTEGRATION")
    print("=" * 70)
    
    # Create synthetic DEM (Digital Elevation Model)
    # Simulate a hillside with varying slopes
    dem_size = 50  # 50x50 grid
    x = np.linspace(0, 100, dem_size)
    y = np.linspace(0, 100, dem_size)
    X, Y = np.meshgrid(x, y)
    
    # Create elevation pattern: gradual slope with some variation
    Z = 100 + 0.5 * X + 0.3 * Y + 5 * np.sin(X / 10) * np.cos(Y / 10)
    
    # Initialize system
    farm = RegenerativeFarmSystem(
        total_area=100.0,
        num_paddocks=8,
        latitude=40.0,
        grid_resolution=2.0  # 2m resolution
    )
    
    # Load topography
    farm.load_topography(Z, cell_size=2.0, origin_x=0.0, origin_y=0.0)
    
    print(f"\nTopography Loaded:")
    print(f"  Grid Size: {dem_size} x {dem_size}")
    print(f"  Resolution: {farm.grid_resolution} m")
    print(f"  Number of Points: {len(farm.topography.points)}")
    
    # Sample a few points
    print("\nSample Topographic Points:")
    sample_coords = [(10, 10), (50, 50), (90, 90)]
    for x, y in sample_coords:
        point = farm.topography.get_point(x, y)
        if point:
            print(f"  ({x}, {y}): Elevation={point.elevation:.1f}m, "
                  f"Slope={point.slope:.1f}°, "
                  f"Aspect={point.aspect_direction.value}")
            
            microclimate = farm.calculate_microclimate_adjustment(x, y, day_of_year=180)
            print(f"    Solar gain factor: {microclimate['radiation_factor']:.2f}")
            print(f"    Temp adjustment: {microclimate['temperature_adjustment']:.2f}°C")
    
    print()


def regenerative_index_example():
    """Demonstrate Regenerative Index calculation"""
    print("=" * 70)
    print("REGENERATIVE INDEX CALCULATION")
    print("=" * 70)
    
    # Initialize and run simulation
    farm = RegenerativeFarmSystem(total_area=100.0, num_paddocks=10)
    farm.biosphere.add_grazing_animal("cattle", count=50)
    
    # Simulate a year
    results = farm.simulate_season(
        days=365,
        avg_precipitation=2.5,
        avg_temperature=18.0,
        avg_solar_radiation=18.0
    )
    
    # Calculate Regenerative Index
    regen_index = farm.get_regenerative_index()
    
    print("\nREGENERATIVE INDEX REPORT")
    print("-" * 70)
    print(f"Overall Index: {regen_index['overall_index']:.2f} / 100")
    print(f"Classification: {regen_index['classification']}")
    print(f"Trend: {regen_index['trend']:.4f}")
    print()
    
    print("Component Scores:")
    for component, score in regen_index['components'].items():
        print(f"  {component.replace('_', ' ').title()}: {score:.2f}")
    
    print()


def complete_system_report():
    """Generate a complete system report"""
    print("=" * 70)
    print("COMPLETE SYSTEM REPORT")
    print("=" * 70)
    
    # Initialize system
    farm = RegenerativeFarmSystem(
        total_area=150.0,
        num_paddocks=15,
        latitude=42.0
    )
    
    # Add animals
    farm.biosphere.add_grazing_animal("cattle", count=60)
    
    # Run simulation
    farm.simulate_season(
        days=180,  # Half year
        avg_precipitation=3.0,
        avg_temperature=20.0,
        avg_solar_radiation=20.0
    )
    
    # Generate and print report
    report = farm.generate_report()
    print(report)


def main():
    """Run all examples"""
    examples = [
        ("Basic Example", basic_example),
        ("Seasonal Simulation", seasonal_simulation),
        ("AMP Grazing", amp_grazing_example),
        ("Topography Integration", topography_integration),
        ("Regenerative Index", regenerative_index_example),
        ("Complete Report", complete_system_report),
    ]
    
    print("\n")
    print("*" * 70)
    print("MBSE REGENERATIVE FARM SYSTEM - EXAMPLES")
    print("*" * 70)
    print("\n")
    
    for i, (name, func) in enumerate(examples, 1):
        print(f"\n{'='*70}")
        print(f"Example {i}/{len(examples)}: {name}")
        print(f"{'='*70}\n")
        
        try:
            func()
        except Exception as e:
            print(f"Error in {name}: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n")
    
    print("*" * 70)
    print("ALL EXAMPLES COMPLETE")
    print("*" * 70)


if __name__ == "__main__":
    main()
