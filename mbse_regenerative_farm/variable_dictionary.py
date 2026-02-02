"""
Variable Dictionary for MBSE Regenerative Farm System

Comprehensive catalog of all system variables categorized by type:
- Input Variables: External forcing variables
- State Variables: System state descriptors
- Flow/Process Variables: Dynamic processes and rates
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from enum import Enum


class VariableCategory(Enum):
    """Categories of variables in the system"""
    INPUT = "input"
    STATE = "state"
    FLOW_PROCESS = "flow_process"


class VariableUnit(Enum):
    """Standard units for variables"""
    # Precipitation and water
    MM = "mm"  # millimeters
    MM_PER_DAY = "mm/day"
    M3 = "m³"  # cubic meters
    PERCENT = "%"
    
    # Energy
    MJ_PER_M2_DAY = "MJ/m²/day"  # Megajoules per square meter per day
    W_PER_M2 = "W/m²"  # Watts per square meter
    
    # Soil and carbon
    KG_PER_M2 = "kg/m²"
    KG_PER_HA = "kg/ha"
    T_PER_HA = "t/ha"  # tonnes per hectare
    G_PER_CM3 = "g/cm³"  # bulk density
    MG_C_PER_KG_SOIL = "mg C/kg soil"  # microbial biomass
    
    # Nutrients
    KG_N_PER_HA = "kg N/ha"
    KG_P_PER_HA = "kg P/ha"
    KG_K_PER_HA = "kg K/ha"
    PPM = "ppm"  # parts per million
    
    # Spatial
    METERS = "m"
    DEGREES = "degrees"
    
    # Biodiversity
    INDEX = "index"  # dimensionless
    COUNT = "count"
    
    # Rates
    T_C_PER_HA_YEAR = "t C/ha/year"  # carbon sequestration rate
    MM_PER_HOUR = "mm/hour"  # infiltration rate
    
    # Dimensionless
    DIMENSIONLESS = "dimensionless"


@dataclass
class Variable:
    """Represents a single variable in the system"""
    name: str
    symbol: str
    category: VariableCategory
    unit: VariableUnit
    description: str
    default_value: Optional[float] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    spatial_explicit: bool = False  # Whether variable varies by location


class VariableDictionary:
    """
    Comprehensive variable dictionary for the regenerative farm system.
    Manages all input, state, and flow/process variables.
    """
    
    def __init__(self):
        self.variables: Dict[str, Variable] = {}
        self._initialize_variables()
    
    def _initialize_variables(self):
        """Initialize all system variables"""
        
        # =================
        # INPUT VARIABLES
        # =================
        
        # Precipitation
        self.add_variable(Variable(
            name="precipitation",
            symbol="P",
            category=VariableCategory.INPUT,
            unit=VariableUnit.MM_PER_DAY,
            description="Daily precipitation input",
            default_value=0.0,
            min_value=0.0,
            spatial_explicit=True
        ))
        
        # Solar Radiation
        self.add_variable(Variable(
            name="solar_radiation",
            symbol="R_s",
            category=VariableCategory.INPUT,
            unit=VariableUnit.MJ_PER_M2_DAY,
            description="Solar radiation at surface",
            default_value=20.0,
            min_value=0.0,
            spatial_explicit=True
        ))
        
        # Initial Soil Organic Carbon
        self.add_variable(Variable(
            name="initial_soc",
            symbol="SOC_0",
            category=VariableCategory.INPUT,
            unit=VariableUnit.T_PER_HA,
            description="Initial soil organic carbon content",
            default_value=50.0,
            min_value=0.0,
            spatial_explicit=True
        ))
        
        # Bulk Density
        self.add_variable(Variable(
            name="bulk_density",
            symbol="ρ_b",
            category=VariableCategory.INPUT,
            unit=VariableUnit.G_PER_CM3,
            description="Soil bulk density",
            default_value=1.3,
            min_value=0.8,
            max_value=2.0,
            spatial_explicit=True
        ))
        
        # Microbial Biomass Carbon
        self.add_variable(Variable(
            name="microbial_biomass",
            symbol="MBC",
            category=VariableCategory.INPUT,
            unit=VariableUnit.MG_C_PER_KG_SOIL,
            description="Microbial biomass carbon",
            default_value=300.0,
            min_value=0.0,
            spatial_explicit=True
        ))
        
        # Ambient Temperature
        self.add_variable(Variable(
            name="temperature",
            symbol="T",
            category=VariableCategory.INPUT,
            unit=VariableUnit.DEGREES,
            description="Ambient air temperature (Celsius)",
            default_value=20.0,
            spatial_explicit=True
        ))
        
        # =================
        # STATE VARIABLES
        # =================
        
        # Soil Moisture Content
        self.add_variable(Variable(
            name="soil_moisture",
            symbol="θ",
            category=VariableCategory.STATE,
            unit=VariableUnit.PERCENT,
            description="Volumetric soil moisture content",
            default_value=30.0,
            min_value=0.0,
            max_value=100.0,
            spatial_explicit=True
        ))
        
        # Nitrogen Content
        self.add_variable(Variable(
            name="nitrogen_level",
            symbol="N",
            category=VariableCategory.STATE,
            unit=VariableUnit.KG_N_PER_HA,
            description="Available nitrogen in soil",
            default_value=100.0,
            min_value=0.0,
            spatial_explicit=True
        ))
        
        # Phosphorus Content
        self.add_variable(Variable(
            name="phosphorus_level",
            symbol="P",
            category=VariableCategory.STATE,
            unit=VariableUnit.KG_P_PER_HA,
            description="Available phosphorus in soil",
            default_value=30.0,
            min_value=0.0,
            spatial_explicit=True
        ))
        
        # Potassium Content
        self.add_variable(Variable(
            name="potassium_level",
            symbol="K",
            category=VariableCategory.STATE,
            unit=VariableUnit.KG_K_PER_HA,
            description="Available potassium in soil",
            default_value=200.0,
            min_value=0.0,
            spatial_explicit=True
        ))
        
        # Soil Organic Carbon (state)
        self.add_variable(Variable(
            name="soil_organic_carbon",
            symbol="SOC",
            category=VariableCategory.STATE,
            unit=VariableUnit.T_PER_HA,
            description="Current soil organic carbon content",
            default_value=50.0,
            min_value=0.0,
            spatial_explicit=True
        ))
        
        # Water Holding Capacity
        self.add_variable(Variable(
            name="water_holding_capacity",
            symbol="WHC",
            category=VariableCategory.STATE,
            unit=VariableUnit.MM,
            description="Soil water holding capacity",
            default_value=150.0,
            min_value=0.0,
            spatial_explicit=True
        ))
        
        # Biodiversity Index
        self.add_variable(Variable(
            name="biodiversity_index",
            symbol="BI",
            category=VariableCategory.STATE,
            unit=VariableUnit.INDEX,
            description="Shannon-Wiener biodiversity index",
            default_value=2.0,
            min_value=0.0,
            spatial_explicit=True
        ))
        
        # Plant Biomass
        self.add_variable(Variable(
            name="plant_biomass",
            symbol="B_p",
            category=VariableCategory.STATE,
            unit=VariableUnit.T_PER_HA,
            description="Above-ground plant biomass",
            default_value=5.0,
            min_value=0.0,
            spatial_explicit=True
        ))
        
        # =================
        # FLOW/PROCESS VARIABLES
        # =================
        
        # Carbon Sequestration Rate
        self.add_variable(Variable(
            name="carbon_sequestration_rate",
            symbol="C_seq",
            category=VariableCategory.FLOW_PROCESS,
            unit=VariableUnit.T_C_PER_HA_YEAR,
            description="Rate of carbon sequestration",
            default_value=0.0,
            spatial_explicit=True
        ))
        
        # Infiltration Rate (Green-Ampt)
        self.add_variable(Variable(
            name="infiltration_rate",
            symbol="I",
            category=VariableCategory.FLOW_PROCESS,
            unit=VariableUnit.MM_PER_HOUR,
            description="Water infiltration rate (Green-Ampt model)",
            default_value=10.0,
            min_value=0.0,
            spatial_explicit=True
        ))
        
        # Reference Evapotranspiration
        self.add_variable(Variable(
            name="evapotranspiration",
            symbol="ET_0",
            category=VariableCategory.FLOW_PROCESS,
            unit=VariableUnit.MM_PER_DAY,
            description="Reference evapotranspiration rate",
            default_value=4.0,
            min_value=0.0,
            spatial_explicit=True
        ))
        
        # Surface Runoff
        self.add_variable(Variable(
            name="surface_runoff",
            symbol="Q",
            category=VariableCategory.FLOW_PROCESS,
            unit=VariableUnit.MM_PER_DAY,
            description="Surface water runoff",
            default_value=0.0,
            min_value=0.0,
            spatial_explicit=True
        ))
        
        # Nutrient Mineralization Rate
        self.add_variable(Variable(
            name="n_mineralization_rate",
            symbol="N_min",
            category=VariableCategory.FLOW_PROCESS,
            unit=VariableUnit.KG_N_PER_HA,
            description="Nitrogen mineralization rate",
            default_value=2.0,
            min_value=0.0,
            spatial_explicit=True
        ))
        
        # Decomposition Rate
        self.add_variable(Variable(
            name="decomposition_rate",
            symbol="k_d",
            category=VariableCategory.FLOW_PROCESS,
            unit=VariableUnit.DIMENSIONLESS,
            description="Organic matter decomposition rate constant",
            default_value=0.02,
            min_value=0.0,
            spatial_explicit=True
        ))
        
        # Grazing Impact
        self.add_variable(Variable(
            name="grazing_impact",
            symbol="G",
            category=VariableCategory.FLOW_PROCESS,
            unit=VariableUnit.DIMENSIONLESS,
            description="Grazing impact on biomass (0-1)",
            default_value=0.0,
            min_value=0.0,
            max_value=1.0,
            spatial_explicit=True
        ))
    
    def add_variable(self, variable: Variable):
        """Add a variable to the dictionary"""
        self.variables[variable.symbol] = variable
    
    def get_variable(self, symbol: str) -> Optional[Variable]:
        """Get a variable by its symbol"""
        return self.variables.get(symbol)
    
    def get_variables_by_category(self, category: VariableCategory) -> Dict[str, Variable]:
        """Get all variables in a specific category"""
        return {
            symbol: var for symbol, var in self.variables.items()
            if var.category == category
        }
    
    def get_spatial_variables(self) -> Dict[str, Variable]:
        """Get all spatially explicit variables"""
        return {
            symbol: var for symbol, var in self.variables.items()
            if var.spatial_explicit
        }
    
    def summary(self) -> str:
        """Generate a summary of the variable dictionary"""
        lines = ["Variable Dictionary Summary", "=" * 50, ""]
        
        for category in VariableCategory:
            vars_in_cat = self.get_variables_by_category(category)
            lines.append(f"\n{category.value.upper()} VARIABLES ({len(vars_in_cat)}):")
            lines.append("-" * 50)
            
            for symbol, var in vars_in_cat.items():
                lines.append(f"  {symbol:10} | {var.name:30} | {var.unit.value}")
        
        return "\n".join(lines)
