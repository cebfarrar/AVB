import pandas as pd
import requests
import time
from datetime import datetime

# Remove # Below - and change directory locations
#file_path = "[insert directory path]/property_urls.csv"
#output_file = "[insert directory path]/currently_available.csv"

def fetch_units_from_api(api_url):
    try:
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"    ❌ API returned status {response.status_code}")
            return None
            
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return None

def parse_units(json_data, state, city, property_name, block_id):
    """
    Parse units from JSON response
    Returns: List of dicts with unit data
    """
    units_list = []

    # Check if response has units
    if not json_data or 'units' not in json_data:
        return units_list

    # Parse each unit
    for unit in json_data['units']:
        try:
            # Extract price from nested structure
            price = None
            if 'startingAtPricesUnfurnished' in unit and unit['startingAtPricesUnfurnished']:
                prices_obj = unit['startingAtPricesUnfurnished'].get('prices', {})
                price = prices_obj.get('price')

            # Convert numeric fields to proper types (int or None)
            bed_count = unit.get('bedroomNumber')
            bath_count = unit.get('bathroomNumber')
            sqft = unit.get('squareFeet')

            current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            unit_dict = {
                'state': state,
                'city': city,
                'apt_complex': property_name,
                'block_id': block_id,
                'apt_id': unit.get('unitId', ''),
                'apt_name': unit.get('unitName', ''),
                'bed_count': int(bed_count) if bed_count is not None else '',
                'bath_count': int(bath_count) if bath_count is not None else '',
                'sqft': int(sqft) if sqft is not None else '',
                'floor': str(unit.get('floorNumber', '')),
                'floor_plan_id': '',
                'unit_number': unit.get('unitId', ''),
                'web_url': unit.get('url', ''),
                'price': int(price) if price is not None else '',
                'adjusted_price': '',
                'first_seen': current_timestamp,
                'last_seen': current_timestamp
            }

            units_list.append(unit_dict)

        except Exception as e:
            print(f"    ⚠️  Error parsing unit: {e}")
            continue

    return units_list

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

def main():
    # Load CSV
    print("Loading CSV...")
    df = pd.read_csv(file_path)

    # Drop duplicates based on communityID to ensure one row per property
    df = df.drop_duplicates(subset=['communityID'], keep='first')

    # Filter out rows with missing communityID
    df = df[df['communityID'].notna()]

    print(f"Loaded {len(df)} properties\n")

    # Read existing CSV if it exists
    try:
        existing_df = pd.read_csv(output_file, dtype=str, low_memory=False)
        existing_df = existing_df.dropna(how='all')

        # Migration: if old format with 'date_scraped', rename to 'first_seen' and add 'last_seen'
        if 'date_scraped' in existing_df.columns and 'first_seen' not in existing_df.columns:
            print("Migrating old format: date_scraped -> first_seen/last_seen")
            existing_df = existing_df.rename(columns={'date_scraped': 'first_seen'})
            existing_df['last_seen'] = existing_df['first_seen']

        print(f"Found existing file with {len(existing_df)} units\n")
    except FileNotFoundError:
        existing_df = pd.DataFrame()
        print("No existing file found, will create new one\n")

    all_results = []

    # Process each property
    for idx, row in df.iterrows():
        state = row['state']
        city = row['city']
        property_name = row['Unnamed: 4']  # Property name in AvalonMaster.csv
        api_url = row['communityID']
        block_id = api_url.split('/')[-1] if isinstance(api_url, str) else ''

        print(f"[{idx+1}/{len(df)}] {property_name} ({city}, {state})")

        # Fetch from API
        print(f"    → Fetching units from API...")
        json_data = fetch_units_from_api(api_url)

        if not json_data:
            print(f"    ✗ No data returned\n")
            continue

        # Parse units
        units = parse_units(json_data, state, city, property_name, block_id)

        if len(units) == 0:
            print(f"    ✗ No units found\n")
            continue

        print(f"    → Found {len(units)} units")

        # Convert to DataFrame
        df_units = pd.DataFrame(units)
        all_results.append(df_units)

        print()

        # Be polite to server
        time.sleep(0.5)

    # Combine all results
    if all_results:
        new_data = pd.concat(all_results, ignore_index=True)

        # Update existing apartments or add new ones
        if len(existing_df) > 0 and all(col in existing_df.columns for col in ['apt_id', 'apt_complex', 'apt_name']):
            # Create composite key for matching (apt_complex, apt_name, apt_id)
            existing_df['_temp_key'] = existing_df['apt_complex'].astype(str) + '|' + existing_df['apt_name'].astype(str) + '|' + existing_df['apt_id'].astype(str)
            new_data['_temp_key'] = new_data['apt_complex'].astype(str) + '|' + new_data['apt_name'].astype(str) + '|' + new_data['apt_id'].astype(str)

            # Separate new apartments from updates
            new_apartments = new_data[~new_data['_temp_key'].isin(existing_df['_temp_key'])].copy()
            apartments_to_update = new_data[new_data['_temp_key'].isin(existing_df['_temp_key'])].copy()

            # Update existing apartments' price and last_seen (keep first_seen unchanged)
            updated_count = 0
            if len(apartments_to_update) > 0:
                for _, apt in apartments_to_update.iterrows():
                    mask = existing_df['_temp_key'] == apt['_temp_key']
                    existing_df.loc[mask, 'price'] = apt['price']
                    existing_df.loc[mask, 'last_seen'] = apt['last_seen']
                    # first_seen stays unchanged - it's the original date the unit was first scraped
                    updated_count += 1

            # Remove temporary key column
            existing_df = existing_df.drop(columns=['_temp_key'])
            new_apartments = new_apartments.drop(columns=['_temp_key']) if len(new_apartments) > 0 else new_apartments
        else:
            new_apartments = new_data
            updated_count = 0

        if len(new_apartments) > 0:
            # Add binary variables to ONLY the new apartments
            print("Adding binary variables to new apartments...")
            new_apartments = add_binary_variables(new_apartments)

            # Append new apartments to existing data
            updated_df = pd.concat([existing_df, new_apartments], ignore_index=True)
            updated_df = updated_df.dropna(how='all')
        else:
            updated_df = existing_df.dropna(how='all')

        # Calculate days_on_market before saving
        if 'first_seen' in updated_df.columns and 'last_seen' in updated_df.columns:
            updated_df['first_seen_dt'] = pd.to_datetime(updated_df['first_seen'], errors='coerce')
            updated_df['last_seen_dt'] = pd.to_datetime(updated_df['last_seen'], errors='coerce')
            updated_df['days_on_market'] = (updated_df['last_seen_dt'] - updated_df['first_seen_dt']).dt.days
            # Drop temporary datetime columns
            updated_df = updated_df.drop(columns=['first_seen_dt', 'last_seen_dt'])

        updated_df.to_csv(output_file, index=False)
        print(f"\n✓ Saved {len(new_apartments)} new apartments to {output_file}")
        print(f"   Updated {updated_count} existing apartments with new price and last_seen")
        print(f"   Total apartments in file: {len(updated_df)}")
    else:
        print("\n✗ No data scraped")

    print("="*60)
    print(f"✓ COMPLETE!")
    print(f"Output file: {output_file}")

if __name__ == "__main__":
    main()