"""
Anthroposphere Subsystem - Human Management System

Manages human decision-making, adaptive multi-paddock grazing,
management practices, and monitoring.
"""

import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta


class ManagementStrategy(Enum):
    """Types of management strategies"""
    AMP_GRAZING = "adaptive_multi_paddock_grazing"
    NO_TILL = "no_till_cover_cropping"
    HOLISTIC_PLANNED = "holistic_planned_grazing"
    REGENERATIVE_ANNUAL = "regenerative_annual_cropping"
    AGROFORESTRY = "agroforestry"


@dataclass
class GrazingPaddock:
    """Represents a grazing paddock in AMP system"""
    id: int
    area: float  # hectares
    current_biomass: float = 5.0  # t/ha
    rest_days: int = 0
    last_grazed: Optional[datetime] = None
    target_residual: float = 1500.0  # kg/ha minimum residual
    
    @property
    def available_forage(self) -> float:
        """Available forage for grazing (kg/ha)"""
        return max(0, self.current_biomass * 1000 - self.target_residual)
    
    @property
    def is_ready_for_grazing(self) -> bool:
        """Check if paddock has recovered sufficiently"""
        return self.rest_days >= 30 and self.current_biomass >= 3.0


@dataclass
class ManagementEvent:
    """Records a management action"""
    date: datetime
    event_type: str
    paddock_id: Optional[int] = None
    details: Dict = field(default_factory=dict)


class Anthroposphere:
    """
    Anthroposphere subsystem - manages human decision-making and
    adaptive management practices.
    """
    
    def __init__(self, total_area: float = 100.0, num_paddocks: int = 10):
        """
        Initialize Anthroposphere.
        
        Args:
            total_area: Total farm area (hectares)
            num_paddocks: Number of paddocks for rotational grazing
        """
        self.total_area = total_area
        self.num_paddocks = num_paddocks
        self.paddock_area = total_area / num_paddocks
        
        # Initialize paddocks
        self.paddocks: List[GrazingPaddock] = [
            GrazingPaddock(id=i, area=self.paddock_area)
            for i in range(num_paddocks)
        ]
        
        self.current_paddock_index = 0
        self.management_events: List[ManagementEvent] = []
        self.active_strategies: List[ManagementStrategy] = [
            ManagementStrategy.AMP_GRAZING,
            ManagementStrategy.NO_TILL
        ]
        
        # Monitoring data
        self.monitoring_data = {
            'soil_health_trend': [],
            'biodiversity_trend': [],
            'productivity_trend': [],
            'financial_trend': [],
        }
    
    def plan_amp_grazing(self, total_animal_demand: float,
                        growth_rate: float) -> Dict[str, any]:
        """
        Plan Adaptive Multi-Paddock (AMP) grazing rotation.
        
        Args:
            total_animal_demand: Total daily forage demand (kg DM/day)
            growth_rate: Current pasture growth rate (kg/ha/day)
        
        Returns:
            Dictionary with grazing plan
        """
        # Calculate days in each paddock
        current_paddock = self.paddocks[self.current_paddock_index]
        
        # Available forage in current paddock
        available_forage_total = current_paddock.available_forage * current_paddock.area
        
        # Days of grazing possible
        if total_animal_demand > 0:
            days_in_paddock = available_forage_total / total_animal_demand
        else:
            days_in_paddock = 0
        
        # Calculate required rest period based on growth rate
        # Need enough time for regrowth to target biomass
        target_regrowth = 2.0  # t/ha regrowth target
        if growth_rate > 0:
            required_rest_days = (target_regrowth * 1000) / growth_rate
        else:
            required_rest_days = 60  # Default minimum
        
        # Adjust paddock count if needed
        optimal_paddocks = max(self.num_paddocks, int(required_rest_days / days_in_paddock) + 1)
        
        return {
            'current_paddock': self.current_paddock_index,
            'days_in_paddock': min(days_in_paddock, 3),  # Max 3 days per paddock
            'required_rest_days': required_rest_days,
            'optimal_paddock_count': optimal_paddocks,
            'available_forage': available_forage_total,
            'rotation_complete': self.current_paddock_index == self.num_paddocks - 1,
        }
    
    def execute_paddock_move(self, biomass_removed: float, 
                           nitrogen_returned: float) -> bool:
        """
        Execute movement to next paddock.
        
        Args:
            biomass_removed: Biomass removed from current paddock (t/ha)
            nitrogen_returned: N returned through manure (kg N/ha)
        
        Returns:
            True if move was successful
        """
        current_paddock = self.paddocks[self.current_paddock_index]
        
        # Update current paddock
        current_paddock.current_biomass -= biomass_removed
        current_paddock.last_grazed = datetime.now()
        current_paddock.rest_days = 0
        
        # Record event
        event = ManagementEvent(
            date=datetime.now(),
            event_type="paddock_grazed",
            paddock_id=self.current_paddock_index,
            details={
                'biomass_removed': biomass_removed,
                'nitrogen_returned': nitrogen_returned,
            }
        )
        self.management_events.append(event)
        
        # Move to next paddock
        self.current_paddock_index = (self.current_paddock_index + 1) % self.num_paddocks
        
        return True
    
    def update_paddock_recovery(self, paddock_id: int, growth_rate: float):
        """
        Update paddock biomass during rest period.
        
        Args:
            paddock_id: Paddock to update
            growth_rate: Current growth rate (t/ha/day)
        """
        if 0 <= paddock_id < len(self.paddocks):
            paddock = self.paddocks[paddock_id]
            paddock.current_biomass += growth_rate
            paddock.rest_days += 1
    
    def plan_cover_crop_rotation(self, current_date: datetime,
                                climate_zone: str = "temperate") -> Dict[str, str]:
        """
        Plan no-till cover crop rotation based on season.
        
        Args:
            current_date: Current date
            climate_zone: Climate classification
        
        Returns:
            Cover crop recommendation
        """
        month = current_date.month
        
        # Temperate climate cover crop calendar
        if climate_zone == "temperate":
            if month in [3, 4, 5]:  # Spring
                return {
                    'season': 'spring',
                    'cover_crop': 'oats_peas_radish',
                    'termination_timing': '60_days',
                    'termination_method': 'roller_crimp',
                    'benefits': 'nitrogen_fixation,soil_building,weed_suppression'
                }
            elif month in [6, 7, 8]:  # Summer
                return {
                    'season': 'summer',
                    'cover_crop': 'sorghum_sudangrass_cowpea',
                    'termination_timing': '90_days',
                    'termination_method': 'roller_crimp',
                    'benefits': 'carbon_input,deep_roots,biomass_production'
                }
            elif month in [9, 10, 11]:  # Fall
                return {
                    'season': 'fall',
                    'cover_crop': 'cereal_rye_crimson_clover',
                    'termination_timing': 'overwinter',
                    'termination_method': 'roller_crimp_spring',
                    'benefits': 'erosion_control,nitrogen_fixation,organic_matter'
                }
            else:  # Winter
                return {
                    'season': 'winter',
                    'cover_crop': 'winter_rye_hairy_vetch',
                    'termination_timing': 'spring',
                    'termination_method': 'roller_crimp',
                    'benefits': 'soil_protection,nitrogen_fixation,early_spring_growth'
                }
        
        return {
            'season': 'unknown',
            'cover_crop': 'mixed_species',
            'termination_timing': 'adaptive',
            'termination_method': 'roller_crimp',
            'benefits': 'general_soil_health'
        }
    
    def make_irrigation_decision(self, soil_moisture: float,
                                crop_stage: str,
                                forecast_rainfall: float,
                                water_cost: float = 1.0) -> Dict[str, any]:
        """
        Adaptive irrigation decision based on multiple factors.
        
        Args:
            soil_moisture: Current soil moisture (%)
            crop_stage: Current crop development stage
            forecast_rainfall: Expected rainfall in next 7 days (mm)
            water_cost: Cost of irrigation ($/mm)
        
        Returns:
            Irrigation decision
        """
        # Critical thresholds by crop stage
        critical_thresholds = {
            'establishment': 50.0,
            'vegetative': 45.0,
            'reproductive': 55.0,
            'maturity': 40.0,
        }
        
        threshold = critical_thresholds.get(crop_stage, 45.0)
        
        # Decision logic
        if soil_moisture < threshold:
            if forecast_rainfall < 10.0:  # Insufficient forecast rain
                amount = threshold - soil_moisture
                decision = 'irrigate'
            else:
                amount = 0.0
                decision = 'wait_for_rain'
        else:
            amount = 0.0
            decision = 'no_irrigation_needed'
        
        return {
            'decision': decision,
            'amount': amount,
            'cost': amount * water_cost,
            'reasoning': f"Moisture {soil_moisture:.1f}% vs threshold {threshold}%, forecast {forecast_rainfall}mm"
        }
    
    def monitor_and_adapt(self, system_state: Dict) -> List[str]:
        """
        Monitor system state and generate adaptive recommendations.
        
        Args:
            system_state: Current state of all subsystems
        
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Check soil health
        if 'soil_health' in system_state:
            if system_state['soil_health'] < 60:
                recommendations.append(
                    "CRITICAL: Soil health below 60. Consider increasing cover crop diversity "
                    "and reducing tillage intensity."
                )
        
        # Check biodiversity
        if 'biodiversity_index' in system_state:
            if system_state['biodiversity_index'] < 1.5:
                recommendations.append(
                    "WARNING: Low biodiversity. Add more plant species to rotation "
                    "and consider establishing pollinator habitats."
                )
        
        # Check water use efficiency
        if 'water_use_efficiency' in system_state:
            if system_state['water_use_efficiency'] < 10:
                recommendations.append(
                    "INFO: Low water use efficiency. Review irrigation timing and "
                    "consider increasing soil organic matter for better water retention."
                )
        
        # Check carbon sequestration
        if 'carbon_sequestration_rate' in system_state:
            if system_state['carbon_sequestration_rate'] < 1.0:
                recommendations.append(
                    "OPPORTUNITY: Carbon sequestration below 1 t C/ha/year. "
                    "Increase plant diversity, optimize grazing, and maintain ground cover."
                )
        
        return recommendations
    
    def record_monitoring_data(self, category: str, value: float):
        """Record monitoring data for trend analysis"""
        if category in self.monitoring_data:
            self.monitoring_data[category].append({
                'date': datetime.now(),
                'value': value
            })
    
    def calculate_financial_metrics(self, production_value: float,
                                   input_costs: float,
                                   ecosystem_service_value: float = 0.0) -> Dict[str, float]:
        """
        Calculate financial performance including ecosystem service values.
        
        Args:
            production_value: Value of products sold ($)
            input_costs: Cost of inputs ($)
            ecosystem_service_value: Value of ecosystem services ($)
        
        Returns:
            Financial metrics
        """
        gross_margin = production_value - input_costs
        total_value = gross_margin + ecosystem_service_value
        roi = (total_value / input_costs * 100) if input_costs > 0 else 0
        
        return {
            'gross_margin': gross_margin,
            'input_costs': input_costs,
            'ecosystem_service_value': ecosystem_service_value,
            'total_value': total_value,
            'roi': roi,
        }
    
    def get_state(self) -> Dict:
        """Get current state of anthroposphere"""
        return {
            'total_area': self.total_area,
            'num_paddocks': self.num_paddocks,
            'current_paddock': self.current_paddock_index,
            'active_strategies': [s.value for s in self.active_strategies],
            'management_events_count': len(self.management_events),
            'paddock_states': [
                {
                    'id': p.id,
                    'biomass': p.current_biomass,
                    'rest_days': p.rest_days,
                    'ready': p.is_ready_for_grazing
                }
                for p in self.paddocks
            ]
        }
