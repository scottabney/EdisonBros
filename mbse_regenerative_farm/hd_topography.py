"""
HD Topography Integration Module

Manages high-definition terrain data including 3D coordinates, slope aspects,
and elevation gradients for precise modeling of water runoff, solar gain,
and erosion risk.
"""

import numpy as np
from dataclasses import dataclass
from typing import Tuple, Optional, Dict
from enum import Enum


class AspectDirection(Enum):
    """Cardinal and ordinal directions for slope aspect"""
    N = "North"
    NE = "Northeast"
    E = "East"
    SE = "Southeast"
    S = "South"
    SW = "Southwest"
    W = "West"
    NW = "Northwest"
    FLAT = "Flat"


@dataclass
class Coordinate3D:
    """3D coordinate with x, y, z position"""
    x: float  # Easting (meters)
    y: float  # Northing (meters)
    z: float  # Elevation (meters above reference)
    
    def distance_to(self, other: 'Coordinate3D') -> float:
        """Calculate 3D distance to another coordinate"""
        return np.sqrt(
            (self.x - other.x)**2 + 
            (self.y - other.y)**2 + 
            (self.z - other.z)**2
        )
    
    def horizontal_distance_to(self, other: 'Coordinate3D') -> float:
        """Calculate horizontal (2D) distance to another coordinate"""
        return np.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)


@dataclass
class TopographicPoint:
    """
    Represents a point in the HD topography with all relevant attributes
    """
    coordinate: Coordinate3D
    slope: float  # Slope gradient (degrees)
    aspect: float  # Aspect angle (degrees, 0=N, 90=E, 180=S, 270=W)
    elevation: float  # Elevation (meters)
    curvature: float = 0.0  # Surface curvature (1/m)
    
    @property
    def aspect_direction(self) -> AspectDirection:
        """Get cardinal direction of aspect"""
        if self.slope < 2.0:  # Nearly flat
            return AspectDirection.FLAT
        
        # Convert aspect to cardinal direction
        aspect_normalized = self.aspect % 360
        if aspect_normalized < 22.5 or aspect_normalized >= 337.5:
            return AspectDirection.N
        elif 22.5 <= aspect_normalized < 67.5:
            return AspectDirection.NE
        elif 67.5 <= aspect_normalized < 112.5:
            return AspectDirection.E
        elif 112.5 <= aspect_normalized < 157.5:
            return AspectDirection.SE
        elif 157.5 <= aspect_normalized < 202.5:
            return AspectDirection.S
        elif 202.5 <= aspect_normalized < 247.5:
            return AspectDirection.SW
        elif 247.5 <= aspect_normalized < 292.5:
            return AspectDirection.W
        else:  # 292.5 <= aspect_normalized < 337.5
            return AspectDirection.NW
    
    def solar_gain_factor(self, latitude: float, day_of_year: int) -> float:
        """
        Calculate relative solar gain based on aspect and slope.
        Returns a factor from 0 to 1+ where 1 is horizontal surface.
        
        Args:
            latitude: Site latitude in degrees
            day_of_year: Day of year (1-365)
        """
        # Simplified solar gain calculation
        # In reality, this would involve solar position calculations
        
        if self.slope < 2.0:
            return 1.0  # Flat surface
        
        # Solar declination (simplified)
        declination = 23.45 * np.sin(np.radians((360/365) * (day_of_year - 81)))
        
        # Adjust for aspect - south-facing slopes get more sun in northern hemisphere
        aspect_factor = np.cos(np.radians(self.aspect - 180))  # Max at 180° (south)
        
        # Adjust for slope
        slope_rad = np.radians(self.slope)
        
        # Combined factor
        if latitude >= 0:  # Northern hemisphere
            gain_factor = 1.0 + 0.3 * aspect_factor * np.sin(slope_rad)
        else:  # Southern hemisphere
            gain_factor = 1.0 - 0.3 * aspect_factor * np.sin(slope_rad)
        
        return max(0.5, min(1.5, gain_factor))
    
    def erosion_risk_factor(self) -> float:
        """
        Calculate erosion risk based on slope.
        Returns a risk factor from 0 (no risk) to 1 (high risk).
        """
        # USLE slope factor approximation
        if self.slope < 5:
            return 0.1
        elif self.slope < 10:
            return 0.3
        elif self.slope < 15:
            return 0.5
        elif self.slope < 20:
            return 0.7
        else:
            return 0.9


class HDTopography:
    """
    High-Definition Topography manager for spatial explicit modeling.
    Handles terrain data and spatial calculations.
    """
    
    def __init__(self, resolution: float = 1.0):
        """
        Initialize HD Topography system.
        
        Args:
            resolution: Grid resolution in meters
        """
        self.resolution = resolution
        self.points: Dict[Tuple[float, float], TopographicPoint] = {}
        self.latitude = 0.0  # Will be set during initialization
    
    def add_point(self, x: float, y: float, z: float, 
                  slope: float = 0.0, aspect: float = 0.0):
        """
        Add a topographic point to the system.
        
        Args:
            x, y, z: 3D coordinates
            slope: Slope gradient in degrees
            aspect: Aspect angle in degrees (0=N, 90=E, 180=S, 270=W)
        """
        coord = Coordinate3D(x, y, z)
        point = TopographicPoint(
            coordinate=coord,
            slope=slope,
            aspect=aspect,
            elevation=z
        )
        self.points[(x, y)] = point
    
    def get_point(self, x: float, y: float) -> Optional[TopographicPoint]:
        """Get topographic point at specific coordinates"""
        return self.points.get((x, y))
    
    def calculate_slope(self, x: float, y: float, dem: np.ndarray, 
                       cell_size: float) -> float:
        """
        Calculate slope at a point using finite differences.
        
        Args:
            x, y: Coordinates
            dem: Digital Elevation Model as 2D array
            cell_size: Size of DEM cells in meters
        """
        # Get indices
        i, j = int(y / cell_size), int(x / cell_size)
        
        if i <= 0 or i >= dem.shape[0]-1 or j <= 0 or j >= dem.shape[1]-1:
            return 0.0
        
        # Calculate slope using Horn's method
        dz_dx = ((dem[i-1, j+1] + 2*dem[i, j+1] + dem[i+1, j+1]) - 
                 (dem[i-1, j-1] + 2*dem[i, j-1] + dem[i+1, j-1])) / (8 * cell_size)
        
        dz_dy = ((dem[i+1, j-1] + 2*dem[i+1, j] + dem[i+1, j+1]) - 
                 (dem[i-1, j-1] + 2*dem[i-1, j] + dem[i-1, j+1])) / (8 * cell_size)
        
        slope_rad = np.arctan(np.sqrt(dz_dx**2 + dz_dy**2))
        return np.degrees(slope_rad)
    
    def calculate_aspect(self, x: float, y: float, dem: np.ndarray, 
                        cell_size: float) -> float:
        """
        Calculate aspect at a point using finite differences.
        
        Args:
            x, y: Coordinates
            dem: Digital Elevation Model as 2D array
            cell_size: Size of DEM cells in meters
        """
        # Get indices
        i, j = int(y / cell_size), int(x / cell_size)
        
        if i <= 0 or i >= dem.shape[0]-1 or j <= 0 or j >= dem.shape[1]-1:
            return 0.0
        
        # Calculate aspect using Horn's method
        dz_dx = ((dem[i-1, j+1] + 2*dem[i, j+1] + dem[i+1, j+1]) - 
                 (dem[i-1, j-1] + 2*dem[i, j-1] + dem[i+1, j-1])) / (8 * cell_size)
        
        dz_dy = ((dem[i+1, j-1] + 2*dem[i+1, j] + dem[i+1, j+1]) - 
                 (dem[i-1, j-1] + 2*dem[i-1, j] + dem[i-1, j+1])) / (8 * cell_size)
        
        # Calculate aspect
        aspect_rad = np.arctan2(dz_dy, -dz_dx)
        aspect_deg = np.degrees(aspect_rad)
        
        # Convert to 0-360 range with 0 = North
        aspect_deg = 90 - aspect_deg
        if aspect_deg < 0:
            aspect_deg += 360
        
        return aspect_deg % 360
    
    def load_from_dem(self, dem: np.ndarray, cell_size: float, 
                     origin_x: float = 0.0, origin_y: float = 0.0):
        """
        Load topography from a Digital Elevation Model.
        
        Args:
            dem: 2D numpy array with elevation values
            cell_size: Size of each cell in meters
            origin_x, origin_y: Origin coordinates
        """
        rows, cols = dem.shape
        
        for i in range(rows):
            for j in range(cols):
                x = origin_x + j * cell_size
                y = origin_y + i * cell_size
                z = dem[i, j]
                
                slope = self.calculate_slope(x, y, dem, cell_size)
                aspect = self.calculate_aspect(x, y, dem, cell_size)
                
                self.add_point(x, y, z, slope, aspect)
    
    def calculate_runoff_direction(self, x: float, y: float) -> Optional[Tuple[float, float]]:
        """
        Calculate runoff direction at a point (downhill direction).
        Returns (dx, dy) unit vector.
        """
        point = self.get_point(x, y)
        if not point:
            return None
        
        # Runoff flows in direction of steepest descent
        aspect_rad = np.radians(point.aspect)
        
        # Convert aspect to downhill direction
        # Aspect 0° = North, water flows south (180°)
        flow_direction = (aspect_rad + np.pi) % (2 * np.pi)
        
        dx = np.sin(flow_direction)
        dy = np.cos(flow_direction)
        
        return (dx, dy)
    
    def get_contributing_area(self, x: float, y: float, radius: float = 10.0) -> float:
        """
        Calculate contributing drainage area for a point.
        Simplified calculation based on surrounding slopes.
        
        Args:
            x, y: Target point coordinates
            radius: Search radius in meters
        """
        point = self.get_point(x, y)
        if not point:
            return 0.0
        
        contributing_area = 0.0
        
        # Check surrounding points
        for (px, py), p in self.points.items():
            distance = np.sqrt((px - x)**2 + (py - y)**2)
            
            if 0 < distance <= radius:
                # Check if water would flow toward target point
                flow_dir = self.calculate_runoff_direction(px, py)
                if flow_dir:
                    dx, dy = flow_dir
                    target_dx = x - px
                    target_dy = y - py
                    
                    # Normalize
                    target_dist = np.sqrt(target_dx**2 + target_dy**2)
                    if target_dist > 0:
                        target_dx /= target_dist
                        target_dy /= target_dist
                        
                        # Dot product to check if flow is toward target
                        alignment = dx * target_dx + dy * target_dy
                        
                        if alignment > 0.5:  # Flow toward target
                            contributing_area += self.resolution ** 2
        
        return contributing_area
    
    def calculate_microclimate_factor(self, x: float, y: float, 
                                     day_of_year: int = 180) -> Dict[str, float]:
        """
        Calculate microclimate factors for a specific location.
        
        Returns:
            Dictionary with factors: solar_gain, wind_exposure, cold_air_drainage
        """
        point = self.get_point(x, y)
        if not point:
            return {
                'solar_gain': 1.0,
                'wind_exposure': 1.0,
                'cold_air_drainage': 0.0
            }
        
        # Solar gain based on aspect and slope
        solar_gain = point.solar_gain_factor(self.latitude, day_of_year)
        
        # Wind exposure based on elevation and exposure
        # Higher elevations = more wind exposure
        wind_exposure = 1.0 + 0.1 * (point.slope / 45.0)
        
        # Cold air drainage - valleys collect cold air
        cold_air_drainage = 1.0 if point.slope < 5 else 0.0
        
        return {
            'solar_gain': solar_gain,
            'wind_exposure': min(2.0, wind_exposure),
            'cold_air_drainage': cold_air_drainage
        }
