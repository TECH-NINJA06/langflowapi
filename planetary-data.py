from flask import Flask, request, jsonify
import swisseph as swe
from datetime import datetime
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim
import pytz

app = Flask(__name__)

def get_planetary_data(dob, tob, place):
    geolocator = Nominatim(user_agent="astro_locator")
    location = geolocator.geocode(place)
    if not location:
        raise ValueError("Invalid place. Please check the spelling or try a nearby location.")
    
    latitude = location.latitude
    longitude = location.longitude

    tf = TimezoneFinder()
    timezone_str = tf.timezone_at(lng=longitude, lat=latitude)
    if not timezone_str:
        raise ValueError("Timezone not found for the given location.")
    
    local_tz = pytz.timezone(timezone_str)
    dob_datetime = datetime.strptime(f"{dob} {tob}", "%Y-%m-%d %H:%M")
    utc_datetime = local_tz.localize(dob_datetime).astimezone(pytz.utc)

    julian_day = swe.julday(
        utc_datetime.year,
        utc_datetime.month,
        utc_datetime.day,
        utc_datetime.hour + utc_datetime.minute / 60 + utc_datetime.second / 3600
    )

    planets = {
        "Sun": swe.SUN,
        "Moon": swe.MOON,
        "Mercury": swe.MERCURY,
        "Venus": swe.VENUS,
        "Mars": swe.MARS,
        "Jupiter": swe.JUPITER,
        "Saturn": swe.SATURN,
        "Uranus": swe.URANUS,
        "Neptune": swe.NEPTUNE,
        "Pluto": swe.PLUTO
    }

    planetary_positions = {}
    for planet, planet_id in planets.items():
        position, _ = swe.calc(julian_day, planet_id)
        planetary_positions[planet] = position[0]

    return {
        "latitude": latitude,
        "longitude": longitude,
        "timezone": timezone_str,
        "planetary_positions": planetary_positions
    }

@app.route('/get_planetary_data', methods=['POST'])
def planetary_data():
    data = request.json
    dob = data.get('dob')
    tob = data.get('tob')
    place = data.get('place')

    if not dob or not tob or not place:
        return jsonify({"error": "Missing required parameters"}), 400

    try:
        result = get_planetary_data(dob, tob, place)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
    app.run(host='0.0.0.0', port=5000)