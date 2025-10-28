import pandas as pd

# Configuration - edit file path
#currently_available = "/[file path]/currently_available.csv"
#output_path = "/[file path]/complete_portfolio.csv"

def normalize_text(text):
    """
    Normalize text for comparison (lowercase, strip spaces, remove common prefixes)
    """
    if pd.isna(text):
        return ""
    
    text = str(text).lower().strip()
    
    # Remove common prefixes/variations
    text = text.replace('ava ', '').replace('avalon ', '').replace('avalon at ', '')
    
    # Remove extra spaces
    text = ' '.join(text.split())
    
    return text

def normalize_city(city):
    """
    Normalize city names for comparison
    """
    if pd.isna(city):
        return ""
    
    city = str(city).lower().strip()
    
    # Handle common variations
    city = city.replace('-apartments', '').replace(' apartments', '')
    city = city.replace('-', ' ')
    
    return ' '.join(city.split())

def match_and_update(df_properties, df_available):
    """
    Match properties with available units using apt_complex, city, and unit_number
    """
    # Normalize columns in available units for matching
    df_available['city_norm'] = df_available['city'].apply(normalize_city)
    df_available['property_norm'] = df_available['apt_complex'].apply(normalize_text)
    df_available['unit_norm'] = df_available['unit_number'].astype(str).str.strip()

    matches = 0
    no_matches = []

    for idx, row in df_properties.iterrows():
        # Normalize property data
        city_norm = normalize_city(row['city'])
        property_norm = normalize_text(row['apt_complex'])
        unit_number = str(row['unit_number']).strip()

        # Find match in available units (Property Name + City + Unit Number)
        # Try exact match first
        match = df_available[
            (df_available['city_norm'] == city_norm) &
            (df_available['property_norm'] == property_norm) &
            (df_available['unit_norm'] == unit_number)
        ]

        # If no exact match, try matching on unit suffix (e.g., "001-101" matches "AVB-CA097-001-101")
        if len(match) == 0:
            match = df_available[
                (df_available['city_norm'] == city_norm) &
                (df_available['property_norm'] == property_norm) &
                (df_available['unit_norm'].str.endswith(unit_number))
            ]

        if len(match) > 0:
            # Match found!
            matched_unit = match.iloc[0]

            # Update price only if:
            # Current price is empty/null, OR
            # Currently_available has a non-null price
            current_price = row['price']
            available_price = matched_unit['price']

            if pd.isna(current_price) or pd.notna(available_price):
                df_properties.at[idx, 'price'] = available_price

            # Always update scraped_date if available
            if pd.notna(matched_unit['date_scraped']):
                df_properties.at[idx, 'scraped_date'] = matched_unit['date_scraped']

            matches += 1

            if matches % 100 == 0:
                print(f"  ✓ Matched {matches} units so far...")
        else:
            # Track non-matches for debugging
            no_matches.append({
                'city': row['city'],
                'property': row['apt_complex'],
                'unit': unit_number
            })

    return df_properties, matches, no_matches

def main():
    print("Loading All_Properties.csv...")
    df_properties = pd.read_csv(output_path)
    print(f"Loaded {len(df_properties)} properties\n")

    print("Loading currently_available.csv...")
    df_available = pd.read_csv(currently_available)
    print(f"Loaded {len(df_available)} available units\n")

    if len(df_available) == 0:
        print("\nNo available units found. Exiting.")
        return

    print("\nMatching properties with available units...")
    print("Matching on: City + Property Name (apt_complex) + Unit Number\n")
    df_updated, match_count, no_matches = match_and_update(df_properties, df_available)
    
    print(f"\n{'='*60}")
    print(f"✓ Matched {match_count} out of {len(df_properties)} properties")
    print(f"  Match rate: {match_count/len(df_properties)*100:.1f}%")
    print(f"  Not matched: {len(no_matches)}")
    
    # Save updated CSV
    df_updated.to_csv(output_path, index=False)
    print(f"\n✓ Saved updated file to: {output_path}")
    
    # Show sample of matched data
    matched_rows = df_updated[df_updated['price'].notna()]
    if len(matched_rows) > 0:
        print("\nSample of matched data:")
        print(matched_rows[['state', 'city', 'apt_complex', 'unit_number', 'price', 'scraped_date']].head(10))
    
    # Show some non-matches for debugging
    if len(no_matches) > 0 and len(no_matches) < 50:
        print(f"\nFirst {min(10, len(no_matches))} non-matched properties:")
        for i, nm in enumerate(no_matches[:10]):
            print(f"  {i+1}. {nm['city']} | {nm['property']} | Unit: {nm['unit']}")

        # Check if any properties in All_Properties aren't in currently_available at all
        csv_properties = set(df_properties.apply(
            lambda x: f"{normalize_city(x['city'])}|{normalize_text(x['apt_complex'])}",
            axis=1
        ))

        available_properties = set(df_available.apply(
            lambda x: f"{x['city_norm']}|{x['property_norm']}",
            axis=1
        ))

        missing_properties = csv_properties - available_properties
        if len(missing_properties) > 0:
            print(f"\n⚠️  {len(missing_properties)} properties in All_Properties are not in currently_available")
            print("This means those properties have NO available units currently")

if __name__ == "__main__":
    main()