#!/usr/bin/env python3
"""
Investigation of Moon aspects marked as "Separating" in actual chart
"""

import json
from typing import Dict, Tuple

def analyze_separating_moon_chart():
    """
    Analyze the chart where Moon aspects were marked as separating
    """
    
    # Extract actual data from the chart where Moon aspects show as separating
    chart_data = {
        'moon': {
            'longitude': 71.57313760021185,  # ~11.6° Gemini
            'speed': 14.126580400828198,     # degrees/day
            'sign': 'Gemini'
        },
        'mercury': {
            'longitude': 126.49531162844104, # ~6.5° Leo
            'speed': 0.730625313029497
        },
        'mars': {
            'longitude': 186.5997697338033,  # ~6.6° Libra  
            'speed': 0.6337295642879655
        },
        'jupiter': {
            'longitude': 105.12094523832012, # ~15.1° Cancer
            'speed': 0.19864062305988348
        }
    }
    
    # Expected aspects from the JSON:
    # Moon ☍ Mercury: applying=false, orb=5.08° (Sextile)
    # Moon △ Mars: applying=false, orb=4.97° (Trine) 
    
    print("🔍 SEPARATING MOON ANALYSIS")
    print("="*60)
    print(f"Moon: {chart_data['moon']['longitude']:.2f}° @ {chart_data['moon']['speed']:+.3f}°/day")
    print()
    
    results = []
    
    # Test the specific aspects that were marked as separating
    test_cases = [
        ('mercury', 'sextile', 60),
        ('mars', 'trine', 120)
    ]
    
    for planet_name, aspect_name, aspect_degrees in test_cases:
        planet_data = chart_data[planet_name]
        
        print(f"📍 {planet_name.upper()}: {planet_data['longitude']:.2f}° @ {planet_data['speed']:+.3f}°/day")
        
        # Calculate angular separation
        moon_lon = chart_data['moon']['longitude']
        planet_lon = planet_data['longitude']
        
        separation = abs(moon_lon - planet_lon)
        if separation > 180:
            separation = 360 - separation
        
        orb = abs(separation - aspect_degrees)
        
        print(f"  {aspect_name.title()}: {orb:.1f}° orb, {separation:.1f}° separation")
        
        # Method 1: Simple future calculation
        relative_speed = chart_data['moon']['speed'] - planet_data['speed']
        
        time_increment = 0.1  # days
        future_moon = (moon_lon + chart_data['moon']['speed'] * time_increment) % 360
        future_planet = (planet_lon + planet_data['speed'] * time_increment) % 360
        
        future_sep = abs(future_moon - future_planet)
        if future_sep > 180:
            future_sep = 360 - future_sep
        
        current_orb = abs(separation - aspect_degrees)
        future_orb = abs(future_sep - aspect_degrees)
        
        simple_applying = future_orb < current_orb
        
        # Method 2: Analyze the current system's logic more carefully
        # Based on is_applying_enhanced from aspects.py
        
        # Faster planet applies to slower
        if abs(chart_data['moon']['speed']) > abs(planet_data['speed']):
            faster_lon, slower_lon = moon_lon, planet_lon
            faster_speed, slower_speed = chart_data['moon']['speed'], planet_data['speed']
            faster_name, slower_name = 'Moon', planet_name
        else:
            faster_lon, slower_lon = planet_lon, moon_lon
            faster_speed, slower_speed = planet_data['speed'], chart_data['moon']['speed']
            faster_name, slower_name = planet_name, 'Moon'
        
        # Calculate separation as faster - slower (signed)
        separation_signed = faster_lon - slower_lon
        
        # Normalize to -180 to +180
        while separation_signed > 180:
            separation_signed -= 360
        while separation_signed < -180:
            separation_signed += 360
        
        # Target separations for this aspect
        targets = [aspect_degrees, -aspect_degrees]
        if aspect_degrees != 0 and aspect_degrees != 180:
            targets.extend([aspect_degrees - 360, -aspect_degrees + 360])
        
        # Find closest target
        closest_target = min(targets, key=lambda t: abs(separation_signed - t))
        current_orb_enhanced = abs(separation_signed - closest_target)
        
        # Calculate future separation
        future_separation_signed = separation_signed + (faster_speed - slower_speed) * time_increment
        
        # Normalize future separation
        while future_separation_signed > 180:
            future_separation_signed -= 360
        while future_separation_signed < -180:
            future_separation_signed += 360
        
        future_orb_enhanced = abs(future_separation_signed - closest_target)
        
        enhanced_applying = future_orb_enhanced < current_orb_enhanced
        
        # Method 3: Direct derivative calculation
        # The rate of change of distance to exact aspect
        orb_rate_of_change = (future_orb - current_orb) / time_increment
        derivative_applying = orb_rate_of_change < 0  # Orb decreasing = applying
        
        print(f"    Faster planet: {faster_name} ({faster_speed:+.3f}°/day)")
        print(f"    Slower planet: {slower_name} ({slower_speed:+.3f}°/day)")
        print(f"    Relative speed: {relative_speed:+.3f}°/day")
        print(f"    Signed separation: {separation_signed:+.2f}°")
        print(f"    Closest target: {closest_target:+.0f}°")
        print(f"    Current orb: {current_orb:.3f}°")
        print(f"    Future orb: {future_orb:.3f}°")
        print(f"    Orb change rate: {orb_rate_of_change:+.4f}°/day")
        print()
        print(f"    Simple method: {'Applying' if simple_applying else 'Separating'}")
        print(f"    Enhanced method: {'Applying' if enhanced_applying else 'Separating'}")
        print(f"    Derivative method: {'Applying' if derivative_applying else 'Separating'}")
        print(f"    Chart says: Separating (applying=false)")
        
        # Check agreement
        methods_agree = simple_applying == enhanced_applying == derivative_applying
        chart_correct = not simple_applying  # Chart says separating, so applying should be False
        
        print(f"    Methods agree: {'✅' if methods_agree else '❌'}")
        print(f"    Chart correct: {'✅' if chart_correct else '❌'}")
        
        result = {
            'planet': planet_name,
            'aspect': aspect_name,
            'separation': separation,
            'orb': orb,
            'relative_speed': relative_speed,
            'orb_change_rate': orb_rate_of_change,
            'simple_applying': simple_applying,
            'enhanced_applying': enhanced_applying,
            'derivative_applying': derivative_applying,
            'chart_says_separating': True,
            'methods_agree': methods_agree,
            'chart_correct': chart_correct
        }
        
        results.append(result)
        print("-" * 40)
    
    return results

def main():
    """Run the investigation"""
    print("Starting investigation of Moon aspects marked as separating...")
    
    results = analyze_separating_moon_chart()
    
    print("\n📊 SUMMARY")
    print("="*60)
    
    total = len(results)
    methods_agree_count = sum(1 for r in results if r['methods_agree'])
    chart_correct_count = sum(1 for r in results if r['chart_correct'])
    
    print(f"Total aspects analyzed: {total}")
    print(f"Methods agree with each other: {methods_agree_count}/{total}")
    print(f"Chart marking is correct: {chart_correct_count}/{total}")
    
    if chart_correct_count < total:
        print(f"\n❌ POTENTIAL ISSUES FOUND:")
        for r in results:
            if not r['chart_correct']:
                print(f"  {r['planet'].title()} {r['aspect'].title()}: Chart says separating, but analysis says applying")
                print(f"    Orb change rate: {r['orb_change_rate']:+.4f}°/day (negative = applying)")
    
    # Save results
    with open('separating_moon_analysis.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to separating_moon_analysis.json")

if __name__ == "__main__":
    main()