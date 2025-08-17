#!/usr/bin/env python3
"""
Moon Aspect Investigation Script
Analyzes the current logic for determining applying vs separating aspects
and compares against authoritative calculations.
"""

import sys
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import traceback
import swisseph as swe

# Import the horary engine modules
from horary_engine.aspects import is_applying_enhanced, is_moon_applying_to_aspect, is_moon_separating_from_aspect
from horary_engine.models import Planet, Aspect, PlanetPosition
from horary_engine.utils import degrees_to_sign
from horary_config import cfg

def calculate_raw_moon_aspect_status(moon_pos: PlanetPosition, planet_pos: PlanetPosition, aspect_type: Aspect) -> Dict:
    """Calculate applying/separating status using different methods for comparison"""
    
    # Method 1: Current system's enhanced logic
    current_applying = is_applying_enhanced(moon_pos, planet_pos, aspect_type, 0.0)
    
    # Method 2: Moon-specific logic
    moon_applying = is_moon_applying_to_aspect(moon_pos, planet_pos, aspect_type, moon_pos.speed)
    moon_separating = is_moon_separating_from_aspect(moon_pos, planet_pos, aspect_type, moon_pos.speed)
    
    # Method 3: Authoritative calculation (derivative method)
    auth_applying = calculate_authoritative_applying(moon_pos, planet_pos, aspect_type)
    
    # Calculate current angular separation
    current_separation = abs(moon_pos.longitude - planet_pos.longitude)
    if current_separation > 180:
        current_separation = 360 - current_separation
    
    # Calculate degrees from exact aspect
    orb_from_exact = abs(current_separation - aspect_type.degrees)
    
    return {
        'aspect_type': aspect_type.name,
        'aspect_degrees': aspect_type.degrees,
        'moon_longitude': moon_pos.longitude,
        'planet_longitude': planet_pos.longitude,
        'moon_speed': moon_pos.speed,
        'planet_speed': planet_pos.speed,
        'moon_retrograde': moon_pos.retrograde,
        'planet_retrograde': planet_pos.retrograde,
        'current_separation': current_separation,
        'orb_from_exact': orb_from_exact,
        'current_system_applying': current_applying,
        'moon_specific_applying': moon_applying,
        'moon_specific_separating': moon_separating,
        'authoritative_applying': auth_applying,
        'relative_speed': moon_pos.speed - planet_pos.speed,
        'will_perfect_in_future': auth_applying
    }

def calculate_authoritative_applying(moon_pos: PlanetPosition, planet_pos: PlanetPosition, aspect_type: Aspect) -> bool:
    """
    Authoritative calculation based on derivative method:
    Applying = angular distance to exact aspect is decreasing
    """
    # Current angular separation
    current_sep = moon_pos.longitude - planet_pos.longitude
    
    # Normalize to -180 to +180
    while current_sep > 180:
        current_sep -= 360
    while current_sep < -180:
        current_sep += 360
    
    # Target separations for this aspect (consider both directions)
    targets = [aspect_type.degrees, -aspect_type.degrees]
    if aspect_type.degrees != 0 and aspect_type.degrees != 180:
        targets.extend([aspect_type.degrees - 360, -aspect_type.degrees + 360])
    
    # Find closest target
    closest_target = min(targets, key=lambda t: abs(current_sep - t))
    current_orb = abs(current_sep - closest_target)
    
    # Calculate how orb changes with time (derivative)
    relative_speed = moon_pos.speed - planet_pos.speed
    
    # Future separation after small time increment
    future_sep = current_sep + relative_speed * 0.1  # 0.1 days forward
    
    # Normalize future separation
    while future_sep > 180:
        future_sep -= 360
    while future_sep < -180:
        future_sep += 360
    
    future_orb = abs(future_sep - closest_target)
    
    # Applying if orb is decreasing
    return future_orb < current_orb

def test_scenario(jd: float, description: str) -> List[Dict]:
    """Test Moon aspects for a specific Julian Day"""
    results = []
    
    try:
        # Calculate planetary positions
        planets = {}
        for planet in Planet:
            if planet == Planet.NORTH_NODE or planet == Planet.SOUTH_NODE:
                continue
            
            swe_planet = getattr(swe, planet.value.upper())
            lon, lat, dist, speed_lon, speed_lat, speed_dist = swe.calc_ut(jd, swe_planet, swe.FLG_SPEED)
            
            planets[planet] = PlanetPosition(
                longitude=lon,
                latitude=lat,
                speed=speed_lon,
                retrograde=(speed_lon < 0 and planet != Planet.MOON),
                house=1,  # Placeholder
                sign=degrees_to_sign(lon),
                degree_in_sign=lon % 30,
                dignity_score=0  # Placeholder
            )
        
        moon_pos = planets[Planet.MOON]
        
        # Test Moon aspects to each planet
        for planet, planet_pos in planets.items():
            if planet == Planet.MOON:
                continue
                
            # Test each major aspect
            for aspect_type in [Aspect.CONJUNCTION, Aspect.SEXTILE, Aspect.SQUARE, Aspect.TRINE, Aspect.OPPOSITION]:
                # Calculate current angular separation
                current_separation = abs(moon_pos.longitude - planet_pos.longitude)
                if current_separation > 180:
                    current_separation = 360 - current_separation
                
                # Check if aspect is within orb (use 8 degrees for all)
                orb_from_exact = abs(current_separation - aspect_type.degrees)
                if orb_from_exact <= 8.0:  # Within orb
                    result = calculate_raw_moon_aspect_status(moon_pos, planet_pos, aspect_type)
                    result['scenario'] = description
                    result['planet'] = planet.value
                    result['julian_day'] = jd
                    result['date_utc'] = swe.julday_to_utc(jd, 0)[1:6]  # year, month, day, hour, minute
                    results.append(result)
    
    except Exception as e:
        print(f"Error in scenario {description}: {e}")
        traceback.print_exc()
    
    return results

def main():
    """Run the investigation"""
    print("🔍 Moon Aspect Investigation Starting...")
    print("="*60)
    
    # Initialize Swiss Ephemeris
    swe.set_ephe_path(".")  # Use current directory for ephemeris files
    
    all_results = []
    
    # Test scenarios
    scenarios = [
        # Original chart scenario (Moon ≈ 29.6° Capricorn)
        (swe.julday(1999, 12, 11, 16.166667, swe.GREG_CAL), "AE-016 Original Chart"),
        
        # Edge cases
        (swe.julday(2024, 1, 1, 12, swe.GREG_CAL), "New Year 2024"),
        (swe.julday(2024, 6, 15, 12, swe.GREG_CAL), "Mid-year 2024"),
        (swe.julday(2024, 12, 25, 12, swe.GREG_CAL), "Christmas 2024"),
        
        # Multiple times for the original chart date (hourly sampling)
    ]
    
    # Add hourly sampling for original chart date
    base_jd = swe.julday(1999, 12, 11, 16.166667, swe.GREG_CAL)
    for hours in range(-12, 13):  # 24 hours around the original time
        jd = base_jd + hours/24.0
        scenarios.append((jd, f"AE-016 + {hours:+d}h"))
    
    # Run all scenarios
    for jd, description in scenarios:
        print(f"\n📊 Testing scenario: {description}")
        scenario_results = test_scenario(jd, description)
        all_results.extend(scenario_results)
        print(f"   Found {len(scenario_results)} aspects in orb")
    
    # Analysis
    print(f"\n📈 ANALYSIS RESULTS")
    print("="*60)
    print(f"Total aspects tested: {len(all_results)}")
    
    if not all_results:
        print("❌ No aspects found in any scenarios!")
        return
    
    # Agreement analysis
    agreements = 0
    disagreements = []
    
    for result in all_results:
        current_vs_auth = result['current_system_applying'] == result['authoritative_applying']
        if current_vs_auth:
            agreements += 1
        else:
            disagreements.append(result)
    
    accuracy = (agreements / len(all_results)) * 100
    
    print(f"✅ Agreement between current system and authoritative: {agreements}/{len(all_results)} ({accuracy:.1f}%)")
    
    if disagreements:
        print(f"\n❌ DISAGREEMENTS ({len(disagreements)} cases):")
        print("-"*60)
        
        for i, result in enumerate(disagreements[:10]):  # Show first 10 disagreements
            date_str = f"{result['date_utc'][0]:04d}-{result['date_utc'][1]:02d}-{result['date_utc'][2]:02d} {result['date_utc'][3]:02d}:{result['date_utc'][4]:02d}"
            print(f"{i+1:2d}. {result['scenario']} | {date_str}")
            print(f"    Moon {result['aspect_type']} {result['planet']}")
            print(f"    Current: {'Applying' if result['current_system_applying'] else 'Separating'}")
            print(f"    Authoritative: {'Applying' if result['authoritative_applying'] else 'Separating'}")
            print(f"    Moon: {result['moon_longitude']:.2f}° @ {result['moon_speed']:+.3f}°/day")
            print(f"    {result['planet']}: {result['planet_longitude']:.2f}° @ {result['planet_speed']:+.3f}°/day")
            print(f"    Relative speed: {result['relative_speed']:+.3f}°/day")
            print(f"    Orb: {result['orb_from_exact']:.2f}°")
            print()
    
    # Systematic bias analysis
    print(f"\n🔍 SYSTEMATIC BIAS ANALYSIS:")
    print("-"*40)
    
    # Count by type
    total_applying_auth = sum(1 for r in all_results if r['authoritative_applying'])
    total_separating_auth = sum(1 for r in all_results if not r['authoritative_applying'])
    
    current_says_applying = sum(1 for r in all_results if r['current_system_applying'])
    current_says_separating = sum(1 for r in all_results if not r['current_system_applying'])
    
    print(f"Authoritative: {total_applying_auth} applying, {total_separating_auth} separating")
    print(f"Current system: {current_says_applying} applying, {current_says_separating} separating")
    
    # Check for specific biases
    retrograde_issues = sum(1 for r in disagreements if r['planet_retrograde'])
    sign_boundary_issues = sum(1 for r in disagreements if (r['moon_longitude'] % 30) > 25 or (r['moon_longitude'] % 30) < 5)
    
    print(f"Disagreements involving retrograde planets: {retrograde_issues}/{len(disagreements)}")
    print(f"Disagreements near sign boundaries: {sign_boundary_issues}/{len(disagreements)}")
    
    # Save detailed results
    output_file = "moon_aspect_investigation_results.json"
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: {output_file}")
    print(f"🎯 Investigation complete! Accuracy: {accuracy:.1f}%")

if __name__ == "__main__":
    main()