"""
Hydrosphere Subsystem - Water System

Manages water balance, infiltration, runoff, evapotranspiration,
and irrigation requirements using Green-Ampt infiltration model.
"""

import numpy as np
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class WaterBalance:
    """Tracks water balance components"""
    precipitation: float = 0.0  # mm
    infiltration: float = 0.0  # mm
    runoff: float = 0.0  # mm
    evapotranspiration: float = 0.0  # mm
    drainage: float = 0.0  # mm
    irrigation: float = 0.0  # mm
    
    @property
    def total_input(self) -> float:
        """Total water input"""
        return self.precipitation + self.irrigation
    
    @property
    def total_output(self) -> float:
        """Total water output"""
        return self.runoff + self.evapotranspiration + self.drainage
    
    @property
    def storage_change(self) -> float:
        """Change in water storage"""
        return self.total_input + self.infiltration - self.total_output


class Hydrosphere:
    """
    Hydrosphere subsystem - manages all water-related processes.
    """
    
    def __init__(self):
        """Initialize Hydrosphere"""
        self.water_balance = WaterBalance()
        self.soil_moisture = 30.0  # % volumetric
        self.water_table_depth = 200.0  # cm below surface
        self.cumulative_infiltration = 0.0  # mm
        
        # Green-Ampt parameters
        self.hydraulic_conductivity = 10.0  # mm/hr (saturated)
        self.wetting_front_suction = 100.0  # mm
        self.porosity = 0.45  # fraction
        self.initial_moisture = 0.20  # fraction
    
    def calculate_green_ampt_infiltration(self, rainfall_intensity: float,
                                         time_step: float = 1.0) -> Dict[str, float]:
        """
        Calculate infiltration using Green-Ampt model.
        
        Args:
            rainfall_intensity: Rainfall intensity (mm/hr)
            time_step: Time step (hours)
        
        Returns:
            Dictionary with infiltration and runoff (mm)
        """
        # Green-Ampt infiltration model
        # f = K * (1 + (ψ * Δθ) / F)
        # where:
        # f = infiltration rate (mm/hr)
        # K = hydraulic conductivity (mm/hr)
        # ψ = wetting front suction head (mm)
        # Δθ = moisture deficit (porosity - initial moisture)
        # F = cumulative infiltration (mm)
        
        moisture_deficit = self.porosity - self.initial_moisture
        
        if moisture_deficit <= 0:
            # Soil is saturated
            infiltration_rate = self.hydraulic_conductivity
        else:
            # Calculate potential infiltration rate
            if self.cumulative_infiltration <= 0:
                infiltration_rate = rainfall_intensity
            else:
                infiltration_rate = self.hydraulic_conductivity * (
                    1 + (self.wetting_front_suction * moisture_deficit) / 
                    self.cumulative_infiltration
                )
        
        # Actual infiltration limited by rainfall intensity
        actual_infiltration_rate = min(infiltration_rate, rainfall_intensity)
        
        # Calculate amounts for time step
        infiltration = actual_infiltration_rate * time_step
        total_rainfall = rainfall_intensity * time_step
        runoff = max(0, total_rainfall - infiltration)
        
        # Update cumulative infiltration
        self.cumulative_infiltration += infiltration
        
        return {
            'infiltration': infiltration,
            'runoff': runoff,
            'infiltration_rate': actual_infiltration_rate
        }
    
    def calculate_evapotranspiration(self, 
                                    temperature: float,
                                    solar_radiation: float,
                                    wind_speed: float = 2.0,
                                    relative_humidity: float = 50.0,
                                    crop_coefficient: float = 1.0) -> float:
        """
        Calculate reference evapotranspiration (ET₀) using simplified Penman-Monteith.
        
        Args:
            temperature: Air temperature (°C)
            solar_radiation: Solar radiation (MJ/m²/day)
            wind_speed: Wind speed at 2m height (m/s)
            relative_humidity: Relative humidity (%)
            crop_coefficient: Crop coefficient (Kc)
        
        Returns:
            Evapotranspiration (mm/day)
        """
        # Simplified FAO Penman-Monteith equation
        
        # Saturation vapor pressure (kPa)
        es = 0.6108 * np.exp((17.27 * temperature) / (temperature + 237.3))
        
        # Actual vapor pressure (kPa)
        ea = es * (relative_humidity / 100.0)
        
        # Vapor pressure deficit (kPa)
        vpd = es - ea
        
        # Slope of saturation vapor pressure curve (kPa/°C)
        delta = (4098 * es) / ((temperature + 237.3) ** 2)
        
        # Psychrometric constant (kPa/°C)
        gamma = 0.665e-3 * 101.3  # at sea level
        
        # Net radiation (simplified, assuming 60% of solar radiation)
        rn = solar_radiation * 0.6
        
        # Soil heat flux (assumed negligible for daily calculation)
        g = 0.0
        
        # Reference ET₀ (mm/day)
        numerator = 0.408 * delta * (rn - g) + gamma * (900 / (temperature + 273)) * wind_speed * vpd
        denominator = delta + gamma * (1 + 0.34 * wind_speed)
        
        et0 = max(0, numerator / denominator)
        
        # Actual ET with crop coefficient
        etc = et0 * crop_coefficient
        
        return etc
    
    def calculate_runoff_curve_number(self, precipitation: float,
                                     curve_number: int = 70) -> float:
        """
        Calculate runoff using SCS Curve Number method.
        
        Args:
            precipitation: Rainfall amount (mm)
            curve_number: SCS curve number (0-100)
        
        Returns:
            Runoff amount (mm)
        """
        # Curve Number method
        # Q = (P - 0.2*S)² / (P + 0.8*S)
        # S = (25400 / CN) - 254
        
        if precipitation <= 0:
            return 0.0
        
        # Maximum retention (mm)
        s = (25400 / curve_number) - 254
        
        # Initial abstraction (mm)
        ia = 0.2 * s
        
        if precipitation <= ia:
            return 0.0
        
        # Runoff (mm)
        runoff = ((precipitation - ia) ** 2) / (precipitation - ia + s)
        
        return runoff
    
    def calculate_irrigation_requirement(self, et: float, 
                                        effective_rainfall: float,
                                        target_moisture: float = 70.0) -> float:
        """
        Calculate irrigation water requirement.
        
        Args:
            et: Evapotranspiration (mm)
            effective_rainfall: Effective rainfall (mm)
            target_moisture: Target soil moisture (%)
        
        Returns:
            Irrigation requirement (mm)
        """
        # Current moisture deficit
        current_deficit = target_moisture - self.soil_moisture
        
        # Water needed to meet ET demand
        et_demand = et - effective_rainfall
        
        # Total irrigation need
        irrigation = max(0, et_demand + (current_deficit * 0.5))
        
        return irrigation
    
    def update_water_balance(self, precipitation: float, temperature: float,
                            solar_radiation: float, soil_whc: float,
                            slope_factor: float = 1.0, 
                            cover_factor: float = 1.0) -> Dict[str, float]:
        """
        Update complete water balance for a time step.
        
        Args:
            precipitation: Rainfall (mm/day)
            temperature: Air temperature (°C)
            solar_radiation: Solar radiation (MJ/m²/day)
            soil_whc: Soil water holding capacity (mm)
            slope_factor: Slope factor affecting runoff
            cover_factor: Vegetation cover factor
        
        Returns:
            Dictionary with water balance components
        """
        # Calculate infiltration and runoff
        infiltration_result = self.calculate_green_ampt_infiltration(
            rainfall_intensity=precipitation,
            time_step=1.0
        )
        
        infiltration = infiltration_result['infiltration']
        runoff = infiltration_result['runoff'] * slope_factor
        
        # Calculate evapotranspiration
        et = self.calculate_evapotranspiration(
            temperature=temperature,
            solar_radiation=solar_radiation,
            crop_coefficient=cover_factor
        )
        
        # Calculate drainage (excess water below field capacity)
        current_water = (self.soil_moisture / 100.0) * soil_whc
        potential_water = current_water + infiltration
        
        if potential_water > soil_whc:
            drainage = potential_water - soil_whc
            available_water = soil_whc
        else:
            drainage = 0.0
            available_water = potential_water
        
        # Update soil moisture
        available_water = max(0, available_water - et)
        self.soil_moisture = (available_water / soil_whc) * 100.0
        
        # Calculate irrigation requirement
        irrigation = self.calculate_irrigation_requirement(et, infiltration)
        
        # Update water balance
        self.water_balance = WaterBalance(
            precipitation=precipitation,
            infiltration=infiltration,
            runoff=runoff,
            evapotranspiration=et,
            drainage=drainage,
            irrigation=irrigation
        )
        
        return {
            'precipitation': precipitation,
            'infiltration': infiltration,
            'runoff': runoff,
            'evapotranspiration': et,
            'drainage': drainage,
            'irrigation_required': irrigation,
            'soil_moisture': self.soil_moisture
        }
    
    def calculate_water_use_efficiency(self, biomass_production: float) -> float:
        """
        Calculate water use efficiency.
        
        Args:
            biomass_production: Biomass produced (kg/ha)
        
        Returns:
            Water use efficiency (kg/m³)
        """
        total_water_used = self.water_balance.total_input - self.water_balance.runoff
        
        if total_water_used <= 0:
            return 0.0
        
        # Convert mm to m³/ha (1 mm = 10 m³/ha)
        water_m3 = total_water_used * 10
        
        wue = biomass_production / water_m3
        
        return wue
    
    def get_state(self) -> Dict:
        """Get current state of hydrosphere"""
        return {
            'soil_moisture': self.soil_moisture,
            'water_table_depth': self.water_table_depth,
            'cumulative_infiltration': self.cumulative_infiltration,
            'precipitation': self.water_balance.precipitation,
            'infiltration': self.water_balance.infiltration,
            'runoff': self.water_balance.runoff,
            'evapotranspiration': self.water_balance.evapotranspiration,
            'drainage': self.water_balance.drainage,
            'irrigation_required': self.water_balance.irrigation,
        }
