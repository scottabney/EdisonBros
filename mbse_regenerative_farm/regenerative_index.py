"""
Regenerative Index Calculator

Calculates a comprehensive "Regenerative Index" that quantifies the net positive
impact on the ecosystem over time. This index integrates multiple dimensions:
- Soil health and carbon sequestration
- Water management efficiency
- Biodiversity enhancement
- Ecosystem service provision
"""

import numpy as np
from typing import Dict, List, Optional


def calculate_regenerative_index(current_state: Dict, 
                                 state_history: List[Dict]) -> Dict[str, float]:
    """
    Calculate the Regenerative Index for the farm system.
    
    The index ranges from 0-100, where:
    - 0-40: Degradative (net negative impact)
    - 40-60: Neutral (maintaining status quo)
    - 60-80: Regenerative (net positive impact)
    - 80-100: Highly regenerative (strong positive impact)
    
    Args:
        current_state: Current system state
        state_history: Historical states for trend analysis
    
    Returns:
        Dictionary with overall index and component scores
    """
    
    # Extract current state values
    pedosphere = current_state.get('pedosphere', {})
    hydrosphere = current_state.get('hydrosphere', {})
    biosphere = current_state.get('biosphere', {})
    
    # 1. SOIL HEALTH SCORE (0-100)
    soil_health_score = calculate_soil_health_score(pedosphere, state_history)
    
    # 2. WATER MANAGEMENT SCORE (0-100)
    water_score = calculate_water_management_score(hydrosphere, state_history)
    
    # 3. BIODIVERSITY SCORE (0-100)
    biodiversity_score = calculate_biodiversity_score(biosphere, state_history)
    
    # 4. CARBON SEQUESTRATION SCORE (0-100)
    carbon_score = calculate_carbon_sequestration_score(
        pedosphere, biosphere, current_state.get('cumulative_carbon_sequestration', 0)
    )
    
    # 5. NUTRIENT CYCLING SCORE (0-100)
    nutrient_score = calculate_nutrient_cycling_score(pedosphere, biosphere)
    
    # 6. ECOSYSTEM RESILIENCE SCORE (0-100)
    resilience_score = calculate_resilience_score(current_state, state_history)
    
    # Calculate weighted overall index
    weights = {
        'soil_health': 0.25,
        'water': 0.20,
        'biodiversity': 0.20,
        'carbon': 0.20,
        'nutrients': 0.10,
        'resilience': 0.05,
    }
    
    overall_index = (
        soil_health_score * weights['soil_health'] +
        water_score * weights['water'] +
        biodiversity_score * weights['biodiversity'] +
        carbon_score * weights['carbon'] +
        nutrient_score * weights['nutrients'] +
        resilience_score * weights['resilience']
    )
    
    # Calculate trend (improvement over time)
    trend = calculate_trend(state_history)
    
    # Determine classification
    if overall_index >= 80:
        classification = "Highly Regenerative"
    elif overall_index >= 60:
        classification = "Regenerative"
    elif overall_index >= 40:
        classification = "Neutral"
    else:
        classification = "Degradative"
    
    return {
        'overall_index': overall_index,
        'classification': classification,
        'soil_health_score': soil_health_score,
        'water_score': water_score,
        'biodiversity_score': biodiversity_score,
        'carbon_score': carbon_score,
        'nutrient_score': nutrient_score,
        'resilience_score': resilience_score,
        'trend': trend,
        'components': {
            'soil_health': soil_health_score,
            'water_management': water_score,
            'biodiversity': biodiversity_score,
            'carbon_sequestration': carbon_score,
            'nutrient_cycling': nutrient_score,
            'ecosystem_resilience': resilience_score,
        }
    }


def calculate_soil_health_score(pedosphere: Dict, history: List[Dict]) -> float:
    """
    Calculate soil health score based on multiple indicators.
    
    Args:
        pedosphere: Current pedosphere state
        history: State history for trend analysis
    
    Returns:
        Score from 0-100
    """
    score = 0.0
    
    # Soil Organic Carbon (35% of score)
    soc = pedosphere.get('soil_organic_carbon', 50.0)
    soc_score = min(100, (soc / 80.0) * 100)  # Target: 80 t/ha
    score += soc_score * 0.35
    
    # Organic Matter (25% of score)
    om = pedosphere.get('organic_matter', 3.0)
    om_score = min(100, (om / 5.0) * 100)  # Target: 5%
    score += om_score * 0.25
    
    # Nutrient levels (20% of score)
    n = pedosphere.get('nitrogen', 100.0)
    p = pedosphere.get('phosphorus', 30.0)
    k = pedosphere.get('potassium', 200.0)
    
    n_score = min(100, (n / 150.0) * 100)
    p_score = min(100, (p / 40.0) * 100)
    k_score = min(100, (k / 250.0) * 100)
    nutrient_score = (n_score + p_score + k_score) / 3.0
    score += nutrient_score * 0.20
    
    # Water holding capacity (10% of score)
    whc = pedosphere.get('water_holding_capacity', 150.0)
    whc_score = min(100, (whc / 200.0) * 100)  # Target: 200mm
    score += whc_score * 0.10
    
    # Trend bonus (10% of score)
    if len(history) > 10:
        soc_trend = calculate_trend_for_metric(history, 'pedosphere.soil_organic_carbon')
        trend_bonus = max(0, min(100, 50 + soc_trend * 500))  # Positive trend increases score
        score += trend_bonus * 0.10
    else:
        score += 50 * 0.10  # Neutral if insufficient history
    
    return min(100, max(0, score))


def calculate_water_management_score(hydrosphere: Dict, history: List[Dict]) -> float:
    """
    Calculate water management efficiency score.
    
    Args:
        hydrosphere: Current hydrosphere state
        history: State history
    
    Returns:
        Score from 0-100
    """
    score = 0.0
    
    # Soil moisture (30% of score) - optimal range 40-70%
    moisture = hydrosphere.get('soil_moisture', 30.0)
    if 40 <= moisture <= 70:
        moisture_score = 100
    elif moisture < 40:
        moisture_score = (moisture / 40.0) * 100
    else:  # > 70
        moisture_score = max(0, 100 - (moisture - 70) * 2)
    score += moisture_score * 0.30
    
    # Infiltration efficiency (30% of score)
    infiltration = hydrosphere.get('infiltration', 0.0)
    precipitation = hydrosphere.get('precipitation', 1.0)
    if precipitation > 0:
        infiltration_ratio = infiltration / precipitation
        infiltration_score = min(100, infiltration_ratio * 100)
    else:
        infiltration_score = 100
    score += infiltration_score * 0.30
    
    # Runoff minimization (20% of score) - less runoff is better
    runoff = hydrosphere.get('runoff', 0.0)
    if precipitation > 0:
        runoff_ratio = runoff / precipitation
        runoff_score = max(0, 100 - runoff_ratio * 200)  # Penalize high runoff
    else:
        runoff_score = 100
    score += runoff_score * 0.20
    
    # Irrigation efficiency (20% of score) - lower irrigation need is better
    irrigation = hydrosphere.get('irrigation_required', 0.0)
    et = hydrosphere.get('evapotranspiration', 4.0)
    if et > 0:
        irrigation_efficiency = max(0, 100 - (irrigation / et) * 100)
    else:
        irrigation_efficiency = 100
    score += irrigation_efficiency * 0.20
    
    return min(100, max(0, score))


def calculate_biodiversity_score(biosphere: Dict, history: List[Dict]) -> float:
    """
    Calculate biodiversity and ecosystem health score.
    
    Args:
        biosphere: Current biosphere state
        history: State history
    
    Returns:
        Score from 0-100
    """
    score = 0.0
    
    # Shannon diversity index (40% of score)
    diversity_index = biosphere.get('biodiversity_index', 2.0)
    # Shannon index typically ranges 0-3.5, with 2.5+ being high diversity
    diversity_score = min(100, (diversity_index / 3.0) * 100)
    score += diversity_score * 0.40
    
    # Species richness (20% of score)
    species_count = biosphere.get('plant_species_count', 3)
    richness_score = min(100, (species_count / 10.0) * 100)  # Target: 10+ species
    score += richness_score * 0.20
    
    # Biomass productivity (20% of score)
    biomass = biosphere.get('total_biomass', 5.0)
    biomass_score = min(100, (biomass / 10.0) * 100)  # Target: 10 t/ha
    score += biomass_score * 0.20
    
    # Pollinator abundance (10% of score)
    pollinator = biosphere.get('pollinator_abundance', 50.0)
    pollinator_score = min(100, pollinator)
    score += pollinator_score * 0.10
    
    # Nitrogen fixation (10% of score)
    n_fixation = biosphere.get('nitrogen_fixation_rate', 0.0)
    n_fix_score = min(100, (n_fixation / 200.0) * 100)  # Target: 200 kg N/ha/year
    score += n_fix_score * 0.10
    
    return min(100, max(0, score))


def calculate_carbon_sequestration_score(pedosphere: Dict, biosphere: Dict,
                                        cumulative_carbon: float) -> float:
    """
    Calculate carbon sequestration and climate impact score.
    
    Args:
        pedosphere: Pedosphere state
        biosphere: Biosphere state
        cumulative_carbon: Cumulative carbon sequestered
    
    Returns:
        Score from 0-100
    """
    score = 0.0
    
    # Soil organic carbon stock (40% of score)
    soc = pedosphere.get('soil_organic_carbon', 50.0)
    soc_score = min(100, (soc / 100.0) * 100)  # Target: 100 t/ha
    score += soc_score * 0.40
    
    # Carbon in biomass (20% of score)
    biomass_carbon = biosphere.get('carbon_in_biomass', 0.0)
    biomass_c_score = min(100, (biomass_carbon / 5.0) * 100)  # Target: 5 t C/ha
    score += biomass_c_score * 0.20
    
    # Cumulative sequestration rate (40% of score)
    # Target: 2 t C/ha/year (ambitious regenerative target)
    if cumulative_carbon > 0:
        # Assume 1 year = 1 t C/ha is good
        seq_score = min(100, (cumulative_carbon / 2.0) * 100)
    else:
        seq_score = 0
    score += seq_score * 0.40
    
    return min(100, max(0, score))


def calculate_nutrient_cycling_score(pedosphere: Dict, biosphere: Dict) -> float:
    """
    Calculate nutrient cycling efficiency score.
    
    Args:
        pedosphere: Pedosphere state
        biosphere: Biosphere state
    
    Returns:
        Score from 0-100
    """
    score = 0.0
    
    # Nitrogen cycling (40% of score)
    n_level = pedosphere.get('nitrogen', 100.0)
    n_fixation = biosphere.get('nitrogen_fixation_rate', 0.0)
    n_score = min(100, ((n_level / 150.0) * 50 + (n_fixation / 200.0) * 50))
    score += n_score * 0.40
    
    # Phosphorus availability (30% of score)
    p_level = pedosphere.get('phosphorus', 30.0)
    p_score = min(100, (p_level / 40.0) * 100)
    score += p_score * 0.30
    
    # Potassium availability (30% of score)
    k_level = pedosphere.get('potassium', 200.0)
    k_score = min(100, (k_level / 250.0) * 100)
    score += k_score * 0.30
    
    return min(100, max(0, score))


def calculate_resilience_score(current_state: Dict, history: List[Dict]) -> float:
    """
    Calculate ecosystem resilience score based on stability and recovery capacity.
    
    Args:
        current_state: Current system state
        history: State history
    
    Returns:
        Score from 0-100
    """
    if len(history) < 10:
        return 50.0  # Neutral score if insufficient data
    
    score = 0.0
    
    # Stability score (50% of resilience) - low variance in key metrics
    soc_variance = calculate_variance_for_metric(history, 'pedosphere.soil_organic_carbon')
    moisture_variance = calculate_variance_for_metric(history, 'hydrosphere.soil_moisture')
    
    # Lower variance = higher stability
    soc_stability = max(0, 100 - soc_variance * 10)
    moisture_stability = max(0, 100 - moisture_variance * 2)
    
    stability_score = (soc_stability + moisture_stability) / 2.0
    score += stability_score * 0.50
    
    # Recovery capacity (50% of resilience) - positive trends
    soc_trend = calculate_trend_for_metric(history, 'pedosphere.soil_organic_carbon')
    biodiv_trend = calculate_trend_for_metric(history, 'biosphere.biodiversity_index')
    
    recovery_score = max(0, min(100, 50 + (soc_trend + biodiv_trend) * 250))
    score += recovery_score * 0.50
    
    return min(100, max(0, score))


def calculate_trend(history: List[Dict], window: int = 30) -> float:
    """
    Calculate overall trend across all metrics.
    
    Args:
        history: State history
        window: Number of recent records to analyze
    
    Returns:
        Trend value (positive = improving, negative = degrading)
    """
    if len(history) < 2:
        return 0.0
    
    recent_history = history[-window:] if len(history) > window else history
    
    trends = []
    
    # Calculate trends for key metrics
    trends.append(calculate_trend_for_metric(recent_history, 'pedosphere.soil_organic_carbon'))
    trends.append(calculate_trend_for_metric(recent_history, 'biosphere.biodiversity_index'))
    trends.append(calculate_trend_for_metric(recent_history, 'biosphere.total_biomass'))
    
    return np.mean(trends)


def calculate_trend_for_metric(history: List[Dict], metric_path: str) -> float:
    """
    Calculate trend for a specific metric using linear regression.
    
    Args:
        history: State history
        metric_path: Dot-notation path to metric (e.g., 'pedosphere.soil_organic_carbon')
    
    Returns:
        Slope of trend line
    """
    if len(history) < 2:
        return 0.0
    
    values = []
    for state in history:
        value = get_nested_value(state, metric_path)
        if value is not None:
            values.append(value)
    
    if len(values) < 2:
        return 0.0
    
    # Simple linear regression
    x = np.arange(len(values))
    y = np.array(values)
    
    # Calculate slope
    slope = np.polyfit(x, y, 1)[0]
    
    # Normalize by mean value to get relative trend
    mean_value = np.mean(y)
    if mean_value != 0:
        normalized_slope = slope / mean_value
    else:
        normalized_slope = 0.0
    
    return normalized_slope


def calculate_variance_for_metric(history: List[Dict], metric_path: str) -> float:
    """
    Calculate variance for a specific metric.
    
    Args:
        history: State history
        metric_path: Dot-notation path to metric
    
    Returns:
        Coefficient of variation (std / mean)
    """
    if len(history) < 2:
        return 0.0
    
    values = []
    for state in history:
        value = get_nested_value(state, metric_path)
        if value is not None:
            values.append(value)
    
    if len(values) < 2:
        return 0.0
    
    mean_value = np.mean(values)
    if mean_value == 0:
        return 0.0
    
    std_value = np.std(values)
    cv = std_value / mean_value  # Coefficient of variation
    
    return cv


def get_nested_value(data: Dict, path: str) -> Optional[float]:
    """
    Get value from nested dictionary using dot notation.
    
    Args:
        data: Nested dictionary
        path: Dot-separated path (e.g., 'pedosphere.soil_organic_carbon')
    
    Returns:
        Value if found, None otherwise
    """
    keys = path.split('.')
    current = data
    
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return None
    
    return current if isinstance(current, (int, float)) else None
