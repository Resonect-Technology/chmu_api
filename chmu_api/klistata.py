import matplotlib.pyplot as plt
from PIL import Image
import requests
from io import BytesIO
from enum import Enum
import math
import logging

logging.basicConfig(level=logging.INFO)

class Severity(Enum):
    NO_WARNING = "#fffbd8"
    LOW = "#fee397"
    MODERATE = "#feac47"
    HIGH = "#df6e23"
    VERY_HIGH = "#9a451e"

class MapKlistataAnalyzer:
    def __init__(self, image_url, lat_min, lat_max, lon_min, lon_max, border_left, border_right, border_top, border_bottom):
        self.image_url = image_url
        self.lat_min = lat_min
        self.lat_max = lat_max
        self.lon_min = lon_min
        self.lon_max = lon_max
        self.border_left = border_left
        self.border_right = border_right
        self.border_top = border_top
        self.border_bottom = border_bottom
        
        # Load the map image
        self.map_image = self.load_image(image_url)
        self.image_width, self.image_height = self.map_image.size
        
    def load_image(self, url):
        response = requests.get(url)
        return Image.open(BytesIO(response.content))
    
    def geo_to_pixel(self, lat, lon):
        x = self.border_left + (lon - self.lon_min) / (self.lon_max - self.lon_min) * (self.image_width - self.border_left - self.border_right)
        y = self.border_top + (1 - (lat - self.lat_min) / (self.lat_max - self.lat_min)) * (self.image_height - self.border_top - self.border_bottom)
        return int(x), int(y)
    
    def color_to_hex(self, rgb_color):
        return '#{:02x}{:02x}{:02x}'.format(*rgb_color)
    
    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def get_severity_from_hex(self, hex_color, tolerance=20):
        # Define a helper function to calculate the Euclidean distance between two RGB colors
        def color_distance(c1, c2):
            return math.sqrt(sum((a - b) ** 2 for a, b in zip(c1, c2)))
        
        # Iterate over all severities to find the closest match
        rgb_color = self.hex_to_rgb(hex_color)
        for severity in Severity:
            severity_rgb = self.hex_to_rgb(severity.value)
            if color_distance(rgb_color, severity_rgb) < tolerance:
                return severity
        return None
    
    def get_severity_message(self, severity):
        match severity:
            case Severity.NO_WARNING:
                return ("1", "Nepatrná")
            case Severity.LOW:
                return ("2", "Mírná")
            case Severity.MODERATE:
                return ("3", "Střední")
            case Severity.HIGH:
                return ("4", "Vysoká")
            case Severity.VERY_HIGH:
                return ("5", "Mimořádná")
            case _:
                return ("0", "Neznámá")
    
    def analyze(self, latitude, longitude):
        pixel_x, pixel_y = self.geo_to_pixel(latitude, longitude)
        rgb_color = self.map_image.getpixel((pixel_x, pixel_y))
        hex_color = self.color_to_hex(rgb_color)
        
        severity = self.get_severity_from_hex(hex_color)
        severity_message = self.get_severity_message(severity)
        
        return {
            "latitude": latitude,
            "longitude": longitude,
            "severity_id": severity_message[0],
            "severity_message": severity_message[1]
        }

# Usage example
if __name__ == "__main__":
    image_url = "https://info.chmi.cz/bio/maps/kliste_1.png"
    lat_min, lat_max = 48.55, 51.05
    lon_min, lon_max = 12.09, 18.87
    border_left, border_right = 150, 170
    border_top, border_bottom = 270, 300

    analyzer = MapKlistataAnalyzer(image_url, lat_min, lat_max, lon_min, lon_max, border_left, border_right, border_top, border_bottom)
    latitude = 50.07926370796739
    longitude = 14.430981701794192

    response = analyzer.analyze(latitude, longitude)
    print(response)
