import requests
import json
import pandas as pd
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime


# Remove # Below - and change directory location
#file_link = "[insert file path to]/property_urls.csv"
#output_file = "[insert file path to]/complete_portfolio.csv"

df = pd.read_csv(file_link, dtype=str, low_memory=False)
df = df.dropna(how='all')

# Remove duplicate header rows
df = df[df['state'] != 'state']

# States (where AVB has apartment complexes)
valid_states = {"California", "Colorado", "Florida", "Maryland", "Massachusetts",
                "New Jersey", "New York", "North Carolina", "Texas", "Virginia",
                "Washington", "District Of Columbia"}

def scrape_avalon_apartments(sightmap_url, city="", state=""):


    # Block-ID
    block_id = sightmap_url.split('/')[-1]

    try:
        response = requests.get(sightmap_url, timeout=10)
        response.raise_for_status()
        data = response.json()['data']
    except Exception as e:
        print(f"ERROR: {city}, {state} - {str(e)[:50]}")
        return None
    
    apt_complex = data['asset']['name']
    
    # Floor plan lookup (for bed/bath counts)
    floor_plan_lookup = {}
    for fp in data['floor_plans']:
        floor_plan_lookup[fp['id']] = {
            'bedroom_count': fp['bedroom_count'],
            'bathroom_count': fp['bathroom_count']
        }
    
    # Floor lookup
    floor_lookup = {}
    for floor in data['floors']:
        floor_lookup[floor['id']] = floor['filter_short_label']
    
    # All units
    all_apartments = []
    units = data.get('units', [])

    for unit in units:
        display_unit = unit.get('display_unit_number', '')
        if not (display_unit.startswith('APT') or display_unit.startswith('HOME')):
            continue
        
        # Floor plan
        floor_plan_id = unit.get('floor_plan_id')
        floor_plan_info = floor_plan_lookup.get(floor_plan_id, {})
        
        # Floor number
        floor_id = unit.get('floor_id')
        floor_number = floor_lookup.get(floor_id, '')
        
        # Sqft
        sqft = unit.get('area', '')
        
        apartment_data = {
            'state': state,
            'city': city,
            'apt_complex': apt_complex,
            'block_id': block_id,
            'apt_id': unit.get('id', ''),
            'apt_name': display_unit,
            'bed_count': floor_plan_info.get('bedroom_count', ''),
            'bath_count': floor_plan_info.get('bathroom_count', ''),
            'sqft': sqft,
            'floor': floor_number,
            'floor_plan_id': floor_plan_id,
            'unit_number': unit.get('unit_number', ''),
            'web_url': sightmap_url,
            'price': '',
            'adjusted_price': '',
            'date_scraped': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        all_apartments.append(apartment_data)
    
    # Create DataFrame
    result_df = pd.DataFrame(all_apartments)

    # Only sort if we have data
    if len(result_df) > 0:
        result_df = result_df.sort_values('apt_name').reset_index(drop=True)

    return result_df if len(result_df) > 0 else None

def add_binary_variables(df):
    """
    Add binary variables for states and cities
    """
    # State binary variables
    states = ['california', 'colorado', 'district_of_columbia', 'florida', 'maryland',
              'massachusetts', 'new_jersey', 'new_york', 'north_carolina', 'texas',
              'virginia', 'washington']

    # Create all state binary columns at once using dict comprehension
    state_columns = {}
    for state in states:
        state_display = state.replace('_', ' ').title()
        if state == 'district_of_columbia':
            state_display = 'District Of Columbia'
        state_columns[f'binary_{state}'] = (df['state'].str.lower().str.replace(' ', '_') == state).astype(int)

    # City binary variables
    cities = ['Acton', 'Addison', 'Agoura_Hills', 'Alexandria', 'Allen', 'Annapolis', 'Arlington',
              'Artesia', 'Aurora', 'Austin', 'Baltimore', 'Bedford', 'Bellevue', 'Benbrook',
              'Bloomfield', 'Bloomingdale', 'Boca_Raton', 'Boonton', 'Boston', 'Bothell', 'Brea',
              'Brighton', 'Brooklyn', 'Burbank', 'Burlington', 'Calabasas', 'Camarillo', 'Cambridge',
              'Canoga_Park', 'Carrollton', 'Castle_Rock', 'Charlotte', 'Chestnut_Hill', 'Chino_Hills',
              'Coconut_Creek', 'Columbia', 'Costa_Mesa', 'Dallas', 'Denver', 'Doral', 'Dublin',
              'Durham', 'Edgewater', 'Emeryville', 'Encino', 'Englewood', 'Fairfax_County',
              'Falls_Church', 'Florham_Park', 'Flower_Mound', 'Fort_Lauderdale', 'Foster_City',
              'Framingham', 'Fremont', 'Frisco', 'Garden_City', 'Georgetown', 'Glendale', 'Glendora',
              'Great_Neck', 'Harrison', 'Herndon', 'Hialeah', 'Hingham', 'Hoboken', 'Hunt_Valley',
              'Huntington_Beach', 'Huntington_Station', 'Irvine', 'Jersey_City', 'La_Mesa', 'Lafayette',
              'Lake_Forest', 'Lakewood', 'Laurel', 'Lewisville', 'Lexington', 'Linthicum_Heights',
              'Littleton', 'Long_Island', 'Long_Island_City', 'Los_Angeles', 'Lynnwood', 'Maplewood',
              'Margate', 'Marlborough', 'Melville', 'Merrifield', 'Miami', 'Milford', 'Miramar',
              'Monrovia', 'Montville', 'Mooresville', 'Morrisville', 'Mountain_View', 'Natick',
              'Newcastle', 'New_York_City', 'North_Andover', 'North_Bergen', 'North_Bethesda',
              'North_Potomac', 'Northborough', 'Norwood', 'Old_Bridge', 'Owings_Mills', 'Pacifica',
              'Parker', 'Parsippany', 'Pasadena', 'Peabody', 'Pflugerville', 'Piscataway', 'Pleasanton',
              'Plymouth', 'Pomona', 'Princeton', 'Quincy', 'Rancho_Santa_Margarita', 'Redmond', 'Reston',
              'Rockville', 'Rockville_Centre', 'Roseland', 'San_Bruno', 'San_Diego', 'San_Dimas',
              'San_Francisco', 'San_Jose', 'San_Marcos', 'Santa_Monica', 'Saugus', 'Seal_Beach',
              'Seattle', 'Silver_Spring', 'Smithtown', 'Somers', 'Somerville', 'Studio_City', 'Sudbury',
              'Sunnyvale', 'Teaneck', 'Thousand_Oaks', 'Towson', 'Tysons_Corner', 'Union', 'Union_City',
              'Vista', 'Walnut_Creek', 'Waltham', 'Washington', 'Wayne', 'West_Hollywood',
              'West_Palm_Beach', 'West_Windsor', 'Westbury', 'Westminster', 'Wharton', 'Wheaton',
              'White_Plains', 'Wilmington', 'Woburn', 'Woodland_Hills', 'Yonkers']

    # Create all city binary columns at once using dict comprehension
    city_columns = {}
    for city in cities:
        city_normalized = city.replace('_', ' ')
        city_columns[f'binary_{city}'] = (df['city'].str.replace(' ', '_').str.lower() == city.lower()).astype(int)

    # Concatenate all binary columns at once (much faster than adding one at a time)
    binary_df = pd.DataFrame({**state_columns, **city_columns}, index=df.index)
    df = pd.concat([df, binary_df], axis=1)

    return df

def save_to_downloads(df, filename='{apt_complex}.csv'):
    """Save DataFrame to Downloads folder"""
    # Get Downloads folder path
    downloads_path = str(Path.home() / "Downloads")
    filepath = os.path.join(downloads_path, filename)

    # Save to CSV
    df.to_csv(filepath, index=False)
    print(f"\n✓ Data saved to: {filepath}")
    return filepath

if __name__ == "__main__":
    # Build list of tasks to scrape
    tasks = []
    skipped = 0
    for index, row in df.iterrows():
        state = row['state']
        city = row['city']
        sitemap_url = row['Sitemap Url']

        # Skip if no valid sightmap URL
        if pd.isna(sitemap_url) or sitemap_url == "Nothing" or sitemap_url == "":
            skipped += 1
            continue
        if not str(sitemap_url).startswith("https://sightmap.com/app/api"):
            print(f"⚠ Skipped {city}, {state} - Invalid URL format: {sitemap_url}")
            skipped += 1
            continue

        tasks.append({
            'url': sitemap_url,
            'city': city,
            'state': state
        })

    print(f"Found {len(tasks)} valid sightmap URLs (skipped {skipped})")
    print(f"Scraping {len(tasks)} locations concurrently...\n")

    # Scrape URLs
    all_results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_task = {
            executor.submit(scrape_avalon_apartments, task['url'], task['city'], task['state']): task
            for task in tasks
        }

        for future in as_completed(future_to_task):
            task = future_to_task[future]
            result = future.result()

            if result is not None:
                print(f"✓ {task['city']}, {task['state']} → {len(result)} units")
                all_results.append(result)
            else:
                print(f"✗ {task['city']}, {task['state']} → failed")

    # Combined
    if all_results:
        new_data = pd.concat(all_results, ignore_index=True)

        # Read CSV
        try:
            existing_df = pd.read_csv(output_file, dtype=str, low_memory=False)
            existing_df = existing_df.dropna(how='all')
        except FileNotFoundError:
            existing_df = pd.DataFrame()

        # Filter out duplicates based on apt_id, apt_complex, and block_id
        if len(existing_df) > 0 and all(col in existing_df.columns for col in ['apt_id', 'apt_complex', 'block_id']):
            # Create composite key for duplicate checking
            existing_keys = existing_df['apt_id'].astype(str) + '|' + existing_df['apt_complex'].astype(str) + '|' + existing_df['block_id'].astype(str)
            new_keys = new_data['apt_id'].astype(str) + '|' + new_data['apt_complex'].astype(str) + '|' + new_data['block_id'].astype(str)
            new_apartments = new_data[~new_keys.isin(existing_keys)]
        else:
            new_apartments = new_data

        if len(new_apartments) > 0:
            # Add binary variables to ONLY new apartments
            print(f"\nAdding binary variables to {len(new_apartments)} new apartments...")
            new_apartments = add_binary_variables(new_apartments)

            # Append new apartments to existing data
            updated_df = pd.concat([existing_df, new_apartments], ignore_index=True)
            updated_df = updated_df.dropna(how='all')

            # Save to CSV
            updated_df.to_csv(output_file, index=False)
            print(f"\n✓ Saved {len(new_apartments)} new apartments to {output_file}")
            print(f"   (skipped {len(new_data) - len(new_apartments)} duplicates)")
            print(f"   Total apartments in file: {len(updated_df)}")
        else:
            print(f"\n⚠ All {len(new_data)} apartments already exist in {output_file}")
    else:
        print("\n✗ No data scraped")
