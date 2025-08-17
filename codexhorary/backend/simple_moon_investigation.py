#!/usr/bin/env python3
"""
Simplified Moon Aspect Investigation
Focuses on the core logic without external dependencies
"""

import json
from typing import Dict, Tuple

def analyze_aspect_logic():
    """
    Analyze the current Moon aspect logic by examining the code patterns
    and simulating with the actual data from AE-016 chart
    """
    
    # Extract actual data from AE-016 chart (from the JSON we examined)
    ae016_data = {
        'moon': {
            'longitude': 299.5955885623632,  # ~29.6° Capricorn
            'speed': 11.93264201061046,      # degrees/day
            'sign': 'Capricorn'
        },
        'mercury': {
            'longitude': 240.80361806909752, # ~0.8° Sagittarius  
            'speed': 1.3827145030839942
        },
        'venus': {
            'longitude': 216.69973658110044, # ~6.7° Scorpio
            'speed': 1.1759101819264413
        },
        'mars': {
            'longitude': 311.8295881367451,  # ~11.8° Aquarius
            'speed': 0.7726304697588048
        },
        'jupiter': {
            'longitude': 25.14945067035318,  # ~25.1° Aries
            'speed': -0.031190948543883813   # Retrograde
        }
    }
    
    # Define aspects to test
    aspects = {
        'sextile': 60,
        'square': 90, 
        'trine': 120,
        'opposition': 180,
        'conjunction': 0
    }
    
    results = []
    
    print("🔍 MOON ASPECT ANALYSIS - AE-016 Chart")
    print("="*60)
    print(f"Moon: {ae016_data['moon']['longitude']:.2f}° @ {ae016_data['moon']['speed']:+.3f}°/day")
    print()
    
    # Test each planet
    for planet_name, planet_data in ae016_data.items():
        if planet_name == 'moon':
            continue
            
        print(f"📍 {planet_name.upper()}: {planet_data['longitude']:.2f}° @ {planet_data['speed']:+.3f}°/day")
        
        # Calculate angular separation
        moon_lon = ae016_data['moon']['longitude']
        planet_lon = planet_data['longitude']
        
        separation = abs(moon_lon - planet_lon)
        if separation > 180:
            separation = 360 - separation
        
        # Test each aspect
        for aspect_name, aspect_degrees in aspects.items():
            orb = abs(separation - aspect_degrees)
            
            if orb <= 8.0:  # Within 8° orb
                # Calculate applying/separating using different methods
                
                # Method 1: Simple relative speed analysis
                relative_speed = ae016_data['moon']['speed'] - planet_data['speed']
                
                # Calculate future positions
                time_increment = 0.1  # days
                future_moon = (moon_lon + ae016_data['moon']['speed'] * time_increment) % 360
                future_planet = (planet_lon + planet_data['speed'] * time_increment) % 360
                
                future_sep = abs(future_moon - future_planet)
                if future_sep > 180:
                    future_sep = 360 - future_sep
                
                current_orb = abs(separation - aspect_degrees)
                future_orb = abs(future_sep - aspect_degrees)
                
                simple_applying = future_orb < current_orb
                
                # Method 2: Derivative approach (more accurate)
                # Find which direction the Moon is approaching the aspect from
                moon_to_planet = moon_lon - planet_lon
                while moon_to_planet > 180:
                    moon_to_planet -= 360
                while moon_to_planet < -180:
                    moon_to_planet += 360
                
                # Find closest target for this aspect
                targets = [aspect_degrees, -aspect_degrees]
                if aspect_degrees != 0 and aspect_degrees != 180:
                    targets.extend([aspect_degrees - 360, -aspect_degrees + 360])
                
                closest_target = min(targets, key=lambda t: abs(moon_to_planet - t))
                current_dist = abs(moon_to_planet - closest_target)
                
                # Calculate future distance
                future_moon_to_planet = moon_to_planet + relative_speed * time_increment
                future_dist = abs(future_moon_to_planet - closest_target)
                
                derivative_applying = future_dist < current_dist
                
                # Check what the current system logic would produce
                # Based on is_applying_enhanced logic
                current_system_applying = analyze_current_system_logic(
                    moon_lon, planet_lon, 
                    ae016_data['moon']['speed'], planet_data['speed'],
                    aspect_degrees
                )
                
                result = {
                    'planet': planet_name,
                    'aspect': aspect_name,
                    'separation': separation,
                    'orb': orb,
                    'relative_speed': relative_speed,
                    'simple_method': simple_applying,
                    'derivative_method': derivative_applying,
                    'current_system': current_system_applying,
                    'moon_longitude': moon_lon,
                    'planet_longitude': planet_lon,
                    'moon_speed': ae016_data['moon']['speed'],
                    'planet_speed': planet_data['speed']
                }
                
                results.append(result)
                
                agreement = "✅" if simple_applying == derivative_applying == current_system_applying else "❌"
                
                print(f"  {aspect_name.title()}: {orb:.1f}° orb")
                print(f"    Simple: {'Applying' if simple_applying else 'Separating'}")
                print(f"    Derivative: {'Applying' if derivative_applying else 'Separating'}")  
                print(f"    Current System: {'Applying' if current_system_applying else 'Separating'}")
                print(f"    Agreement: {agreement}")
                print()
        
        print("-" * 40)
    
    return results

def analyze_current_system_logic(moon_lon: float, planet_lon: float, 
                               moon_speed: float, planet_speed: float,
                               aspect_degrees: float) -> bool:
    """
    Simulate the current system's is_applying_enhanced logic
    """
    
    # Determine faster/slower planet
    if abs(moon_speed) > abs(planet_speed):
        faster_lon, slower_lon = moon_lon, planet_lon
        faster_speed, slower_speed = moon_speed, planet_speed
    else:
        faster_lon, slower_lon = planet_lon, moon_lon
        faster_speed, slower_speed = planet_speed, moon_speed
    
    # Calculate separation as faster - slower
    separation = faster_lon - slower_lon
    
    # Normalize to -180 to +180
    while separation > 180:
        separation -= 360
    while separation < -180:
        separation += 360
    
    # Find targets for this aspect
    targets = [aspect_degrees, -aspect_degrees]
    if aspect_degrees != 0 and aspect_degrees != 180:
        targets.extend([aspect_degrees - 360, -aspect_degrees + 360])
    
    # Find closest target
    closest_target = min(targets, key=lambda t: abs(separation - t))
    current_orb = abs(separation - closest_target)
    
    # Calculate future separation
    time_increment = 0.1  # From config.timing.timing_precision_days
    future_separation = separation + (faster_speed - slower_speed) * time_increment
    
    # Normalize future separation
    while future_separation > 180:
        future_separation -= 360
    while future_separation < -180:
        future_separation += 360
    
    future_orb = abs(future_separation - closest_target)
    
    return future_orb < current_orb

def main():
    """Run the investigation"""
    print("Starting simplified Moon aspect investigation...")
    
    results = analyze_aspect_logic()
    
    print("\n📊 SUMMARY ANALYSIS")
    print("="*60)
    
    if not results:
        print("❌ No aspects found in orb!")
        return
    
    # Count agreements and disagreements
    total = len(results)
    simple_vs_deriv = sum(1 for r in results if r['simple_method'] == r['derivative_method'])
    system_vs_deriv = sum(1 for r in results if r['current_system'] == r['derivative_method'])
    all_agree = sum(1 for r in results if r['simple_method'] == r['derivative_method'] == r['current_system'])
    
    print(f"Total aspects tested: {total}")
    print(f"Simple vs Derivative agreement: {simple_vs_deriv}/{total} ({simple_vs_deriv/total*100:.1f}%)")
    print(f"Current System vs Derivative: {system_vs_deriv}/{total} ({system_vs_deriv/total*100:.1f}%)")
    print(f"All methods agree: {all_agree}/{total} ({all_agree/total*100:.1f}%)")
    
    # Identify problematic cases
    disagreements = [r for r in results if not (r['simple_method'] == r['derivative_method'] == r['current_system'])]
    
    if disagreements:
        print(f"\n❌ DISAGREEMENTS ({len(disagreements)} cases):")
        for r in disagreements:
            print(f"  {r['planet'].title()} {r['aspect'].title()}: {r['orb']:.1f}° orb")
            print(f"    Simple: {'A' if r['simple_method'] else 'S'} | "
                  f"Derivative: {'A' if r['derivative_method'] else 'S'} | "
                  f"Current: {'A' if r['current_system'] else 'S'}")
            print(f"    Rel.Speed: {r['relative_speed']:+.3f}°/day")
    
    # Save results
    with open('moon_aspect_analysis.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to moon_aspect_analysis.json")

if __name__ == "__main__":
    main()