import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

# Remove # Below, and edit directory path
#all_properties_path = "/[file path directory]/complete_portfolio.csv"
#predictions_path = "/[file_path_directory]/missing_properties_predictions.csv"

def add_binary_variables(df):
    states = ['california', 'colorado', 'district_of_columbia', 'florida', 'maryland',
              'massachusetts', 'new_jersey', 'new_york', 'north_carolina', 'texas',
              'virginia', 'washington']

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

    # Create state binary columns
    for state in states:
        df[f'binary_{state}'] = (df['state'].str.lower().str.replace(' ', '_') == state).astype(int)

    # Create city binary columns
    for city in cities:
        df[f'binary_{city}'] = (df['city'].str.replace(' ', '_').str.lower() == city.lower()).astype(int)

    return df

# Load data
print("Loading data...")
all_properties = pd.read_csv(all_properties_path)
predictions_df = pd.read_csv(predictions_path)

print(f"All Properties: {len(all_properties)} units")
print(f"Properties to predict: {len(predictions_df)} properties\n")

# Add binary variables to predictions dataframe
predictions_df = add_binary_variables(predictions_df)

# Define features
binary_features = [col for col in all_properties.columns if col.startswith('binary_')]
features = ['bed_count', 'bath_count', 'sqft', 'floor'] + binary_features

# Train model
print("Training model...")
train_data = all_properties[all_properties['price'].notna()].copy()
X_train, X_test, y_train, y_test = train_test_split(
    train_data[features], train_data['price'], test_size=0.2, random_state=1
)

model = RandomForestRegressor(n_estimators=100, random_state=1, n_jobs=-1)
model.fit(X_train, y_train)

# Evaluate
mae = mean_absolute_error(y_test, model.predict(X_test))
r2 = r2_score(y_test, model.predict(X_test))
print(f"MAE: ${mae:.2f}, R²: {r2:.4f}\n")

# Calculate state averages for bed/bath/sqft/floor by bedroom type
print("Calculating state averages...")
state_averages = train_data.groupby(['state', 'bed_count']).agg({
    'bath_count': 'mean',
    'sqft': 'mean',
    'floor': 'mean'
}).reset_index()

# Calculate unit mix by state (distribution of bedroom types)
state_unit_mix = train_data.groupby(['state', 'bed_count']).size().reset_index(name='count')
state_totals = train_data.groupby('state').size().reset_index(name='total')
state_unit_mix = state_unit_mix.merge(state_totals, on='state')
state_unit_mix['percentage'] = state_unit_mix['count'] / state_unit_mix['total']

# Update predictions for each property
print("Updating predictions...\n")

for idx, prop in predictions_df.iterrows():
    total_units = int(prop['unit_count'])
    state_mix = state_unit_mix[state_unit_mix['state'] == prop['state']]

    if len(state_mix) == 0:
        continue

    total_revenue = 0

    # For each bedroom type in this state's mix
    for _, mix in state_mix.iterrows():
        bed_count = mix['bed_count']
        num_units = int(np.round(total_units * mix['percentage']))

        if num_units == 0:
            continue

        # Get state averages for this bedroom type
        avg = state_averages[(state_averages['state'] == prop['state']) &
                             (state_averages['bed_count'] == bed_count)]

        if len(avg) == 0:
            continue

        # Create feature vector and predict
        feature_dict = {
            'bed_count': bed_count,
            'bath_count': avg['bath_count'].values[0],
            'sqft': avg['sqft'].values[0],
            'floor': avg['floor'].values[0]
        }

        # Add binary features from property
        for col in binary_features:
            feature_dict[col] = prop[col]

        predicted_rent = model.predict(pd.DataFrame([feature_dict])[features])[0]
        total_revenue += predicted_rent * num_units

    # Update revenue columns
    predictions_df.loc[idx, 'avg_rent'] = total_revenue / total_units if total_units > 0 else 0
    predictions_df.loc[idx, 'monthly_revenue'] = total_revenue
    predictions_df.loc[idx, 'annual_revenue'] = total_revenue * 12

# Save updated predictions
predictions_df = predictions_df.sort_values('annual_revenue', ascending=False)
predictions_df.to_csv(predictions_path, index=False)

# Summary
total_revenue = predictions_df['annual_revenue'].sum()
total_units = predictions_df['unit_count'].sum()

print(f"Results saved to: {predictions_path}")
print(f"Total properties: {len(predictions_df)}")
print(f"Total units: {int(total_units):,}")
print(f"Total annual revenue: ${total_revenue:,.2f}")
