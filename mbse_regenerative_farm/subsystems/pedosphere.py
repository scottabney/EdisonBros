"""
Pedosphere Subsystem - Soil System

Manages soil properties, organic carbon dynamics, nutrient cycling,
and soil health indicators.
"""

import numpy as np
from typing import Dict, Optional
from dataclasses import dataclass, field


@dataclass
class SoilProperties:
    """Physical and chemical properties of soil"""
    # Physical properties
    bulk_density: float = 1.3  # g/cm³
    porosity: float = 0.5  # fraction
    sand_fraction: float = 0.4  # fraction
    silt_fraction: float = 0.4  # fraction
    clay_fraction: float = 0.2  # fraction
    
    # Chemical properties
    pH: float = 6.5
    cation_exchange_capacity: float = 15.0  # cmol/kg
    
    # Organic matter
    organic_matter: float = 3.0  # %
    soil_organic_carbon: float = 50.0  # t/ha
    microbial_biomass_carbon: float = 300.0  # mg C/kg soil
    
    # Nutrients
    nitrogen: float = 100.0  # kg N/ha
    phosphorus: float = 30.0  # kg P/ha
    potassium: float = 200.0  # kg K/ha
    
    # Derived properties
    @property
    def water_holding_capacity(self) -> float:
        """Calculate water holding capacity based on soil properties"""
        # WHC increases with clay content and organic matter
        base_whc = 100.0  # mm
        clay_factor = 1.0 + (self.clay_fraction * 0.5)
        om_factor = 1.0 + (self.organic_matter / 100.0 * 2.0)
        return base_whc * clay_factor * om_factor
    
    @property
    def infiltration_capacity(self) -> float:
        """Calculate infiltration capacity (mm/hr)"""
        # Higher sand content = higher infiltration
        base_infiltration = 10.0  # mm/hr
        sand_factor = 1.0 + self.sand_fraction
        structure_factor = 1.0 + (self.organic_matter / 100.0)
        return base_infiltration * sand_factor * structure_factor


class Pedosphere:
    """
    Pedosphere subsystem - manages all soil-related processes and state.
    """
    
    def __init__(self, soil_depth: float = 30.0):
        """
        Initialize Pedosphere.
        
        Args:
            soil_depth: Active soil depth in cm
        """
        self.soil_depth = soil_depth
        self.properties = SoilProperties()
        self.temperature = 15.0  # °C
        self.moisture = 30.0  # % volumetric
        
    def update_soil_organic_carbon(self, carbon_input: float, 
                                   decomposition_rate: float, 
                                   time_step: float = 1.0) -> float:
        """
        Update SOC based on inputs and decomposition.
        
        Args:
            carbon_input: Carbon added (t C/ha/year)
            decomposition_rate: Decomposition rate constant (1/year)
            time_step: Time step (years)
        
        Returns:
            Carbon sequestration rate (t C/ha/year)
        """
        # Simple carbon balance model
        decomposition = self.properties.soil_organic_carbon * decomposition_rate * time_step
        net_change = carbon_input * time_step - decomposition
        
        self.properties.soil_organic_carbon += net_change
        
        # Update organic matter (SOC is ~58% of OM)
        self.properties.organic_matter = (self.properties.soil_organic_carbon / 
                                         (self.soil_depth * self.properties.bulk_density * 100)) * 58
        
        return net_change / time_step
    
    def calculate_mineralization_rate(self) -> float:
        """
        Calculate nitrogen mineralization rate from organic matter.
        
        Returns:
            N mineralization rate (kg N/ha/day)
        """
        # Temperature factor
        if self.temperature < 0:
            temp_factor = 0.0
        else:
            temp_factor = np.exp(0.1 * (self.temperature - 20))
        
        # Moisture factor (optimal around 50-70% WHC)
        moisture_fraction = self.moisture / 100.0
        if moisture_fraction < 0.3:
            moisture_factor = moisture_fraction / 0.3
        elif moisture_fraction > 0.8:
            moisture_factor = (1.0 - moisture_fraction) / 0.2
        else:
            moisture_factor = 1.0
        
        # Base mineralization rate (function of SOC)
        base_rate = self.properties.soil_organic_carbon * 0.02 / 365.0  # kg N/ha/day
        
        return base_rate * temp_factor * moisture_factor
    
    def update_nutrients(self, n_input: float = 0.0, p_input: float = 0.0, 
                        k_input: float = 0.0, plant_uptake_factor: float = 0.1):
        """
        Update nutrient levels accounting for mineralization, inputs, and uptake.
        
        Args:
            n_input: External N input (kg/ha)
            p_input: External P input (kg/ha)
            k_input: External K input (kg/ha)
            plant_uptake_factor: Fraction of available nutrients taken up by plants
        """
        # Nitrogen dynamics
        mineralization = self.calculate_mineralization_rate()
        self.properties.nitrogen += mineralization + n_input
        self.properties.nitrogen *= (1 - plant_uptake_factor)
        self.properties.nitrogen = max(0, self.properties.nitrogen)
        
        # Phosphorus
        self.properties.phosphorus += p_input
        self.properties.phosphorus *= (1 - plant_uptake_factor * 0.5)  # Lower uptake rate
        self.properties.phosphorus = max(0, self.properties.phosphorus)
        
        # Potassium
        self.properties.potassium += k_input
        self.properties.potassium *= (1 - plant_uptake_factor * 0.7)
        self.properties.potassium = max(0, self.properties.potassium)
    
    def calculate_erosion_loss(self, rainfall_energy: float, 
                              slope_factor: float, 
                              cover_factor: float = 1.0) -> float:
        """
        Calculate soil erosion using simplified USLE.
        
        Args:
            rainfall_energy: Rainfall erosivity (MJ mm/ha/hr)
            slope_factor: Slope length and steepness factor
            cover_factor: Cover management factor (0=full cover, 1=bare)
        
        Returns:
            Soil loss (t/ha)
        """
        # Simplified Universal Soil Loss Equation (USLE)
        # A = R * K * LS * C * P
        
        # Soil erodibility factor (function of soil texture)
        k_factor = 0.3 * (1 - self.properties.sand_fraction) + 0.1
        
        # Support practice factor (assume conservation practices)
        p_factor = 0.5
        
        soil_loss = rainfall_energy * k_factor * slope_factor * cover_factor * p_factor
        
        return max(0, soil_loss)
    
    def update_soil_moisture(self, infiltration: float, et: float, 
                            drainage: float = 0.0) -> float:
        """
        Update soil moisture content.
        
        Args:
            infiltration: Water infiltrating into soil (mm)
            et: Evapotranspiration loss (mm)
            drainage: Deep drainage loss (mm)
        
        Returns:
            Updated soil moisture (%)
        """
        # Convert to volumetric content
        whc = self.properties.water_holding_capacity
        
        # Water balance
        moisture_mm = (self.moisture / 100.0) * whc
        moisture_mm += infiltration - et - drainage
        
        # Limit to field capacity
        moisture_mm = max(0, min(whc, moisture_mm))
        
        self.moisture = (moisture_mm / whc) * 100.0
        
        return self.moisture
    
    def calculate_soil_health_index(self) -> float:
        """
        Calculate overall soil health index (0-100).
        Considers SOC, nutrients, pH, and biological activity.
        """
        # SOC score (optimal > 3%)
        soc_score = min(100, (self.properties.organic_matter / 3.0) * 100)
        
        # Nutrient score (based on sufficiency)
        n_score = min(100, (self.properties.nitrogen / 150.0) * 100)
        p_score = min(100, (self.properties.phosphorus / 40.0) * 100)
        k_score = min(100, (self.properties.potassium / 250.0) * 100)
        nutrient_score = (n_score + p_score + k_score) / 3.0
        
        # pH score (optimal 6.0-7.0)
        if 6.0 <= self.properties.pH <= 7.0:
            ph_score = 100
        else:
            ph_score = max(0, 100 - abs(self.properties.pH - 6.5) * 20)
        
        # Biological activity score
        bio_score = min(100, (self.properties.microbial_biomass_carbon / 400.0) * 100)
        
        # Weighted average
        health_index = (
            soc_score * 0.35 +
            nutrient_score * 0.25 +
            ph_score * 0.20 +
            bio_score * 0.20
        )
        
        return health_index
    
    def get_state(self) -> Dict:
        """Get current state of pedosphere"""
        return {
            'soil_organic_carbon': self.properties.soil_organic_carbon,
            'organic_matter': self.properties.organic_matter,
            'nitrogen': self.properties.nitrogen,
            'phosphorus': self.properties.phosphorus,
            'potassium': self.properties.potassium,
            'moisture': self.moisture,
            'temperature': self.temperature,
            'water_holding_capacity': self.properties.water_holding_capacity,
            'infiltration_capacity': self.properties.infiltration_capacity,
            'health_index': self.calculate_soil_health_index(),
        }
