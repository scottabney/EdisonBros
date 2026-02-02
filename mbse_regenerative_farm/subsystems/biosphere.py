"""
Biosphere Subsystem - Flora and Fauna System

Manages plant growth, biodiversity, grazing dynamics, and biomass production.
"""

import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class PlantType(Enum):
    """Types of plants in the system"""
    GRASS = "grass"
    LEGUME = "legume"
    FORB = "forb"
    COVER_CROP = "cover_crop"
    TREE = "tree"


@dataclass
class PlantSpecies:
    """Represents a plant species"""
    name: str
    type: PlantType
    biomass: float = 0.0  # t/ha above-ground
    root_biomass: float = 0.0  # t/ha below-ground
    nitrogen_fixation: float = 0.0  # kg N/ha/year (for legumes)
    carbon_content: float = 0.45  # fraction of dry matter
    
    @property
    def total_biomass(self) -> float:
        """Total biomass (above + below ground)"""
        return self.biomass + self.root_biomass
    
    @property
    def carbon_stored(self) -> float:
        """Carbon stored in biomass (t C/ha)"""
        return self.total_biomass * self.carbon_content


@dataclass
class GrazingAnimal:
    """Represents grazing animals"""
    species: str
    count: int
    daily_intake: float = 15.0  # kg DM/animal/day
    manure_production: float = 10.0  # kg/animal/day
    n_content_manure: float = 0.5  # % N in manure
    
    @property
    def total_daily_intake(self) -> float:
        """Total herd intake (kg DM/day)"""
        return self.count * self.daily_intake
    
    @property
    def nitrogen_excretion(self) -> float:
        """Daily N excretion (kg N/day)"""
        return self.count * self.manure_production * (self.n_content_manure / 100.0)


class Biosphere:
    """
    Biosphere subsystem - manages all biological processes including
    flora and fauna dynamics.
    """
    
    def __init__(self):
        """Initialize Biosphere"""
        self.plant_species: List[PlantSpecies] = []
        self.grazing_animals: List[GrazingAnimal] = []
        self.biodiversity_index = 2.0  # Shannon-Wiener index
        self.total_biomass = 5.0  # t/ha
        self.pollinator_abundance = 50.0  # index
        
        # Initialize with default grassland
        self._initialize_default_vegetation()
    
    def _initialize_default_vegetation(self):
        """Initialize with typical grassland vegetation"""
        self.plant_species = [
            PlantSpecies(name="Perennial Ryegrass", type=PlantType.GRASS, 
                        biomass=3.0, root_biomass=2.0),
            PlantSpecies(name="White Clover", type=PlantType.LEGUME, 
                        biomass=1.5, root_biomass=1.0, nitrogen_fixation=150.0),
            PlantSpecies(name="Mixed Forbs", type=PlantType.FORB, 
                        biomass=0.5, root_biomass=0.3),
        ]
        self._update_total_biomass()
    
    def _update_total_biomass(self):
        """Update total biomass from all species"""
        self.total_biomass = sum(species.total_biomass for species in self.plant_species)
    
    def calculate_shannon_diversity(self) -> float:
        """
        Calculate Shannon-Wiener biodiversity index.
        H' = -Σ(pi * ln(pi))
        where pi is the proportion of biomass of species i
        """
        if self.total_biomass <= 0:
            return 0.0
        
        diversity = 0.0
        for species in self.plant_species:
            if species.total_biomass > 0:
                proportion = species.total_biomass / self.total_biomass
                diversity -= proportion * np.log(proportion)
        
        self.biodiversity_index = diversity
        return diversity
    
    def calculate_plant_growth(self, temperature: float, solar_radiation: float,
                              soil_moisture: float, nitrogen_availability: float,
                              day_of_year: int) -> float:
        """
        Calculate daily plant growth rate using simple production model.
        
        Args:
            temperature: Air temperature (°C)
            solar_radiation: Solar radiation (MJ/m²/day)
            soil_moisture: Soil moisture (%)
            nitrogen_availability: Available N (kg/ha)
            day_of_year: Day of year (1-365)
        
        Returns:
            Growth rate (t/ha/day)
        """
        # Temperature factor (optimal 15-25°C)
        if temperature < 5:
            temp_factor = 0.1
        elif temperature < 15:
            temp_factor = (temperature - 5) / 10
        elif temperature <= 25:
            temp_factor = 1.0
        else:
            temp_factor = max(0.5, 1.0 - (temperature - 25) / 15)
        
        # Light factor (radiation use efficiency)
        rue = 3.0  # g DM/MJ (radiation use efficiency)
        light_limited_growth = solar_radiation * rue / 1000.0  # Convert g to kg, then to t
        
        # Water stress factor
        if soil_moisture < 30:
            water_factor = soil_moisture / 30
        elif soil_moisture > 80:
            water_factor = 0.9
        else:
            water_factor = 1.0
        
        # Nitrogen factor
        n_optimal = 150.0  # kg N/ha
        n_factor = min(1.0, nitrogen_availability / n_optimal)
        
        # Seasonal factor
        season_factor = 0.5 + 0.5 * np.sin(2 * np.pi * (day_of_year - 80) / 365)
        
        # Combined growth rate
        growth_rate = light_limited_growth * temp_factor * water_factor * n_factor * season_factor
        
        return max(0, growth_rate)
    
    def update_plant_growth(self, temperature: float, solar_radiation: float,
                           soil_moisture: float, nitrogen_availability: float,
                           day_of_year: int = 180):
        """
        Update biomass of all plant species.
        """
        growth_rate = self.calculate_plant_growth(
            temperature, solar_radiation, soil_moisture,
            nitrogen_availability, day_of_year
        )
        
        # Distribute growth proportionally to existing biomass
        if self.total_biomass > 0:
            for species in self.plant_species:
                proportion = species.total_biomass / self.total_biomass
                species_growth = growth_rate * proportion
                species.biomass += species_growth * 0.7  # 70% above ground
                species.root_biomass += species_growth * 0.3  # 30% below ground
        
        self._update_total_biomass()
    
    def apply_grazing(self, grazing_intensity: float = 0.5, 
                     grazing_duration: float = 1.0) -> Dict[str, float]:
        """
        Apply grazing impact on vegetation (AMP Grazing model).
        
        Args:
            grazing_intensity: Fraction of biomass removed (0-1)
            grazing_duration: Duration of grazing (days)
        
        Returns:
            Dictionary with grazing impacts
        """
        # Calculate total intake requirement
        total_intake = sum(animal.total_daily_intake for animal in self.grazing_animals)
        total_intake_kg_ha = (total_intake * grazing_duration) / 1.0  # Assume 1 ha paddock
        
        # Available forage (only 50% of biomass is accessible)
        available_forage = self.total_biomass * 1000 * 0.5  # Convert t/ha to kg/ha
        
        # Actual intake limited by availability
        actual_intake = min(total_intake_kg_ha, available_forage * grazing_intensity)
        
        # Remove biomass
        removal_fraction = actual_intake / (self.total_biomass * 1000)
        
        for species in self.plant_species:
            species.biomass *= (1 - removal_fraction)
        
        self._update_total_biomass()
        
        # Calculate nutrient return through manure
        total_n_return = sum(animal.nitrogen_excretion for animal in self.grazing_animals) * grazing_duration
        
        # Trampling and soil stimulation effect
        trampling_benefit = 0.05  # 5% increase in decomposition from trampling
        
        return {
            'biomass_removed': actual_intake / 1000.0,  # t/ha
            'nitrogen_returned': total_n_return,  # kg N
            'trampling_effect': trampling_benefit,
            'utilization_rate': removal_fraction,
        }
    
    def apply_cover_cropping(self, cover_crop_type: str = "mixed",
                            termination_method: str = "roller_crimp") -> Dict[str, float]:
        """
        Model no-till cover cropping impacts.
        
        Args:
            cover_crop_type: Type of cover crop
            termination_method: How cover crop is terminated
        
        Returns:
            Dictionary with cover cropping benefits
        """
        # Add cover crop to species list if not present
        cover_crop_biomass = 4.0  # t/ha typical
        
        cover_crop = PlantSpecies(
            name=f"Cover Crop - {cover_crop_type}",
            type=PlantType.COVER_CROP,
            biomass=cover_crop_biomass * 0.6,
            root_biomass=cover_crop_biomass * 0.4,
            nitrogen_fixation=100.0 if "legume" in cover_crop_type.lower() else 0.0
        )
        
        # Carbon input to soil (when terminated)
        carbon_input = cover_crop.carbon_stored
        
        # Nitrogen contribution
        n_contribution = cover_crop.nitrogen_fixation / 365.0  # Daily rate
        
        # Soil protection benefit
        erosion_reduction = 0.8  # 80% erosion reduction
        
        # Weed suppression
        weed_suppression = 0.7  # 70% weed suppression
        
        return {
            'carbon_input': carbon_input,  # t C/ha
            'nitrogen_contribution': n_contribution,  # kg N/ha
            'erosion_reduction': erosion_reduction,
            'weed_suppression': weed_suppression,
            'biomass_added': cover_crop_biomass,
        }
    
    def calculate_carbon_sequestration_from_biomass(self) -> float:
        """
        Calculate carbon sequestration from biomass production.
        
        Returns:
            Carbon sequestration rate (t C/ha/year)
        """
        # Carbon sequestered in plant biomass
        total_carbon = sum(species.carbon_stored for species in self.plant_species)
        
        # Root exudates and rhizodeposition (20-40% of photosynthate)
        root_carbon = total_carbon * 0.3
        
        # Total carbon input to soil system
        total_c_input = total_carbon * 0.4 + root_carbon  # 40% of above-ground becomes soil C
        
        return total_c_input
    
    def calculate_nitrogen_fixation(self) -> float:
        """
        Calculate total biological nitrogen fixation.
        
        Returns:
            N fixation rate (kg N/ha/year)
        """
        total_n_fixation = sum(
            species.nitrogen_fixation 
            for species in self.plant_species 
            if species.type == PlantType.LEGUME
        )
        
        return total_n_fixation
    
    def add_grazing_animal(self, species: str, count: int):
        """Add grazing animals to the system"""
        animal = GrazingAnimal(species=species, count=count)
        self.grazing_animals.append(animal)
    
    def get_state(self) -> Dict:
        """Get current state of biosphere"""
        return {
            'total_biomass': self.total_biomass,
            'biodiversity_index': self.biodiversity_index,
            'plant_species_count': len(self.plant_species),
            'carbon_in_biomass': sum(s.carbon_stored for s in self.plant_species),
            'nitrogen_fixation_rate': self.calculate_nitrogen_fixation(),
            'pollinator_abundance': self.pollinator_abundance,
            'grazing_animal_count': sum(a.count for a in self.grazing_animals),
        }
