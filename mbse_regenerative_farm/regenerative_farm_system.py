"""
Regenerative Farm System - Main Integration Module

Integrates all subsystems (Pedosphere, Hydrosphere, Biosphere, Anthroposphere)
with HD Topography for comprehensive farm system modeling.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

from .subsystems import Pedosphere, Hydrosphere, Biosphere, Anthroposphere
from .hd_topography import HDTopography, TopographicPoint
from .variable_dictionary import VariableDictionary


class RegenerativeFarmSystem:
    """
    Main system class integrating all subsystems for regenerative farm modeling.
    Implements feedback loops and spatial-explicit modeling.
    """
    
    def __init__(self, 
                 total_area: float = 100.0,
                 num_paddocks: int = 10,
                 latitude: float = 40.0,
                 grid_resolution: float = 10.0):
        """
        Initialize the complete regenerative farm system.
        
        Args:
            total_area: Total farm area (hectares)
            num_paddocks: Number of grazing paddocks
            latitude: Site latitude (degrees)
            grid_resolution: Spatial grid resolution (meters)
        """
        # System metadata
        self.total_area = total_area
        self.latitude = latitude
        self.simulation_start = datetime.now()
        self.current_time = self.simulation_start
        self.time_step = 1  # days
        
        # Initialize subsystems
        self.pedosphere = Pedosphere()
        self.hydrosphere = Hydrosphere()
        self.biosphere = Biosphere()
        self.anthroposphere = Anthroposphere(total_area, num_paddocks)
        
        # Initialize topography
        self.topography = HDTopography(resolution=grid_resolution)
        self.topography.latitude = latitude
        
        # Initialize variable dictionary
        self.variable_dict = VariableDictionary()
        
        # Spatial data (grid-based)
        self.grid_resolution = grid_resolution
        self.spatial_data: Dict[Tuple[float, float], Dict] = {}
        
        # System state history
        self.state_history: List[Dict] = []
        
        # Performance metrics
        self.cumulative_carbon_sequestration = 0.0
        self.cumulative_water_use = 0.0
        
    def load_topography(self, dem: np.ndarray, cell_size: float,
                       origin_x: float = 0.0, origin_y: float = 0.0):
        """
        Load HD topography from Digital Elevation Model.
        
        Args:
            dem: 2D array of elevation values
            cell_size: DEM cell size (meters)
            origin_x, origin_y: Origin coordinates
        """
        self.topography.load_from_dem(dem, cell_size, origin_x, origin_y)
        self._initialize_spatial_data()
    
    def _initialize_spatial_data(self):
        """Initialize spatial data for each grid cell"""
        for (x, y), topo_point in self.topography.points.items():
            self.spatial_data[(x, y)] = {
                'soil_moisture': self.pedosphere.moisture,
                'soil_organic_carbon': self.pedosphere.properties.soil_organic_carbon,
                'biomass': self.biosphere.total_biomass,
                'slope': topo_point.slope,
                'aspect': topo_point.aspect,
                'elevation': topo_point.elevation,
            }
    
    def calculate_microclimate_adjustment(self, x: float, y: float, 
                                         day_of_year: int) -> Dict[str, float]:
        """
        Calculate microclimate adjustments based on topography.
        
        Args:
            x, y: Coordinates
            day_of_year: Day of year
        
        Returns:
            Adjusted climate factors
        """
        microclimate = self.topography.calculate_microclimate_factor(x, y, day_of_year)
        
        # Get topographic point
        point = self.topography.get_point(x, y)
        
        if point:
            # Temperature adjustment (decreases with elevation)
            temp_adjustment = -0.006 * point.elevation  # -0.6°C per 100m
            
            # Radiation adjustment based on slope and aspect
            radiation_factor = microclimate['solar_gain']
            
            # Wind adjustment
            wind_factor = microclimate['wind_exposure']
            
            return {
                'temperature_adjustment': temp_adjustment,
                'radiation_factor': radiation_factor,
                'wind_factor': wind_factor,
                'cold_air_drainage': microclimate['cold_air_drainage'],
            }
        
        return {
            'temperature_adjustment': 0.0,
            'radiation_factor': 1.0,
            'wind_factor': 1.0,
            'cold_air_drainage': 0.0,
        }
    
    def update_feedback_loops(self):
        """
        Update system feedback loops.
        Key loop: SOC -> WHC -> Irrigation Requirements
        """
        # Feedback: SOC increases WHC
        base_whc = self.pedosphere.properties.water_holding_capacity
        soc_factor = 1.0 + (self.pedosphere.properties.soil_organic_carbon / 50.0) * 0.5
        improved_whc = base_whc * soc_factor
        
        # Update pedosphere WHC
        # (This happens automatically through the SoilProperties property)
        
        # Feedback: Improved WHC reduces irrigation
        # (Handled in hydrosphere irrigation calculation)
        
        # Feedback: Biodiversity increases system resilience
        biodiversity_factor = min(1.5, self.biosphere.biodiversity_index / 2.0)
        
        # Feedback: Plant biomass increases infiltration
        biomass_factor = 1.0 + (self.biosphere.total_biomass / 10.0) * 0.3
        self.hydrosphere.hydraulic_conductivity = 10.0 * biomass_factor
        
        # Feedback: Grazing stimulates plant growth (moderate grazing)
        # (Handled in anthroposphere grazing management)
        
        return {
            'soc_whc_factor': soc_factor,
            'biodiversity_resilience': biodiversity_factor,
            'biomass_infiltration_factor': biomass_factor,
        }
    
    def simulate_time_step(self, 
                          precipitation: float,
                          temperature: float,
                          solar_radiation: float,
                          day_of_year: int = 180) -> Dict:
        """
        Simulate one time step (typically 1 day) of the system.
        
        Args:
            precipitation: Daily precipitation (mm)
            temperature: Air temperature (°C)
            solar_radiation: Solar radiation (MJ/m²/day)
            day_of_year: Day of year (1-365)
        
        Returns:
            Dictionary with time step results
        """
        # Update feedback loops
        feedback = self.update_feedback_loops()
        
        # 1. HYDROSPHERE - Water balance
        water_balance = self.hydrosphere.update_water_balance(
            precipitation=precipitation,
            temperature=temperature,
            solar_radiation=solar_radiation,
            soil_whc=self.pedosphere.properties.water_holding_capacity,
            slope_factor=1.0,  # Average across farm
            cover_factor=min(1.0, self.biosphere.total_biomass / 5.0)
        )
        
        # 2. PEDOSPHERE - Update soil moisture
        self.pedosphere.update_soil_moisture(
            infiltration=water_balance['infiltration'],
            et=water_balance['evapotranspiration'],
            drainage=water_balance['drainage']
        )
        
        # Sync moisture between systems
        self.hydrosphere.soil_moisture = self.pedosphere.moisture
        
        # 3. BIOSPHERE - Plant growth
        self.biosphere.update_plant_growth(
            temperature=temperature,
            solar_radiation=solar_radiation,
            soil_moisture=self.pedosphere.moisture,
            nitrogen_availability=self.pedosphere.properties.nitrogen,
            day_of_year=day_of_year
        )
        
        # 4. PEDOSPHERE - Nutrient cycling
        n_mineralization = self.pedosphere.calculate_mineralization_rate()
        self.pedosphere.update_nutrients(
            plant_uptake_factor=0.05  # Daily uptake fraction
        )
        
        # 5. PEDOSPHERE - Carbon dynamics
        # Carbon input from biomass turnover
        carbon_input = self.biosphere.calculate_carbon_sequestration_from_biomass() / 365.0
        decomposition_rate = 0.02 * (1 + (temperature - 15) / 20)  # Temperature-dependent
        
        carbon_seq_rate = self.pedosphere.update_soil_organic_carbon(
            carbon_input=carbon_input,
            decomposition_rate=decomposition_rate,
            time_step=1.0 / 365.0  # Daily time step
        )
        
        self.cumulative_carbon_sequestration += carbon_seq_rate / 365.0
        
        # 6. BIOSPHERE - Nitrogen fixation
        n_fixation = self.biosphere.calculate_nitrogen_fixation() / 365.0
        self.pedosphere.properties.nitrogen += n_fixation
        
        # 7. ANTHROPOSPHERE - Management decisions
        # Check if grazing is scheduled
        if self.biosphere.grazing_animals:
            grazing_plan = self.anthroposphere.plan_amp_grazing(
                total_animal_demand=sum(a.total_daily_intake for a in self.biosphere.grazing_animals),
                growth_rate=self.biosphere.calculate_plant_growth(
                    temperature, solar_radiation, self.pedosphere.moisture,
                    self.pedosphere.properties.nitrogen, day_of_year
                ) * 1000  # Convert to kg/ha/day
            )
            
            # Execute grazing if in paddock
            if grazing_plan['days_in_paddock'] > 0:
                grazing_result = self.biosphere.apply_grazing(grazing_intensity=0.5)
                
                # Return nutrients to soil
                self.pedosphere.properties.nitrogen += grazing_result['nitrogen_returned']
        
        # Update time
        self.current_time = self.current_time + timedelta(days=self.time_step)
        
        # Record state
        current_state = self.get_system_state()
        self.state_history.append(current_state)
        
        return current_state
    
    def simulate_season(self, 
                       days: int,
                       avg_precipitation: float = 3.0,
                       avg_temperature: float = 20.0,
                       avg_solar_radiation: float = 20.0,
                       start_day_of_year: int = 1) -> List[Dict]:
        """
        Simulate a full season (multiple days).
        
        Args:
            days: Number of days to simulate
            avg_precipitation: Average daily precipitation (mm)
            avg_temperature: Average temperature (°C)
            avg_solar_radiation: Average solar radiation (MJ/m²/day)
            start_day_of_year: Starting day of year
        
        Returns:
            List of daily states
        """
        results = []
        
        for day in range(days):
            # Add variability to inputs
            precipitation = max(0, np.random.normal(avg_precipitation, avg_precipitation * 0.5))
            temperature = np.random.normal(avg_temperature, 3.0)
            solar_radiation = max(0, np.random.normal(avg_solar_radiation, avg_solar_radiation * 0.2))
            
            day_of_year = (start_day_of_year + day) % 365 + 1
            
            state = self.simulate_time_step(
                precipitation=precipitation,
                temperature=temperature,
                solar_radiation=solar_radiation,
                day_of_year=day_of_year
            )
            
            results.append(state)
        
        return results
    
    def get_system_state(self) -> Dict:
        """Get complete system state across all subsystems"""
        state = {
            'timestamp': self.current_time,
            'pedosphere': self.pedosphere.get_state(),
            'hydrosphere': self.hydrosphere.get_state(),
            'biosphere': self.biosphere.get_state(),
            'anthroposphere': self.anthroposphere.get_state(),
            'cumulative_carbon_sequestration': self.cumulative_carbon_sequestration,
        }
        return state
    
    def get_regenerative_index(self) -> Dict[str, float]:
        """
        Calculate comprehensive Regenerative Index.
        See regenerative_index.py for detailed calculation.
        """
        from .regenerative_index import calculate_regenerative_index
        
        system_state = self.get_system_state()
        return calculate_regenerative_index(system_state, self.state_history)
    
    def generate_report(self) -> str:
        """Generate comprehensive system report"""
        state = self.get_system_state()
        regen_index = self.get_regenerative_index()
        
        report = []
        report.append("=" * 70)
        report.append("REGENERATIVE FARM SYSTEM REPORT")
        report.append("=" * 70)
        report.append(f"Report Generated: {datetime.now()}")
        report.append(f"Simulation Time: {self.current_time}")
        report.append("")
        
        report.append("REGENERATIVE INDEX")
        report.append("-" * 70)
        report.append(f"Overall Index: {regen_index['overall_index']:.2f} / 100")
        report.append(f"  - Soil Health: {regen_index['soil_health_score']:.2f}")
        report.append(f"  - Water Management: {regen_index['water_score']:.2f}")
        report.append(f"  - Biodiversity: {regen_index['biodiversity_score']:.2f}")
        report.append(f"  - Carbon Sequestration: {regen_index['carbon_score']:.2f}")
        report.append("")
        
        report.append("PEDOSPHERE (SOIL)")
        report.append("-" * 70)
        for key, value in state['pedosphere'].items():
            report.append(f"  {key}: {value:.2f}")
        report.append("")
        
        report.append("HYDROSPHERE (WATER)")
        report.append("-" * 70)
        for key, value in state['hydrosphere'].items():
            report.append(f"  {key}: {value:.2f}")
        report.append("")
        
        report.append("BIOSPHERE (BIOLOGY)")
        report.append("-" * 70)
        for key, value in state['biosphere'].items():
            report.append(f"  {key}: {value:.2f}")
        report.append("")
        
        report.append("ANTHROPOSPHERE (MANAGEMENT)")
        report.append("-" * 70)
        anthro_state = state['anthroposphere']
        report.append(f"  Total Area: {anthro_state['total_area']} ha")
        report.append(f"  Number of Paddocks: {anthro_state['num_paddocks']}")
        report.append(f"  Current Paddock: {anthro_state['current_paddock']}")
        report.append(f"  Active Strategies: {', '.join(anthro_state['active_strategies'])}")
        report.append("")
        
        report.append("=" * 70)
        
        return "\n".join(report)
