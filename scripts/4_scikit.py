from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
import pandas as pd

#DecisionTreeRegressor option
#AVB_model = DecisionTreeRegressor(random_state=1)

AVB_model = RandomForestRegressor(n_estimators=100, random_state=1,n_jobs=-1)
#file_path = "[insert directory path]/complete_portfolio.csv"
AVB_data = pd.read_csv(file_path)

print(AVB_data.columns)
train_data = AVB_data[AVB_data['price'].notna()]
y = train_data.price
AVB_features = ['bed_count', 'bath_count', 'sqft', 'floor',
                'binary_california', 'binary_colorado', 'binary_district_of_columbia', 'binary_florida',
                'binary_maryland', 'binary_massachusetts', 'binary_new_jersey', 'binary_new_york',
                'binary_north_carolina', 'binary_texas', 'binary_virginia', 'binary_washington',
                'binary_Acton', 'binary_Addison', 'binary_Agoura_Hills', 'binary_Alexandria',
                'binary_Allen', 'binary_Annapolis', 'binary_Arlington', 'binary_Artesia',
                'binary_Aurora', 'binary_Austin', 'binary_Baltimore', 'binary_Bedford',
                'binary_Bellevue', 'binary_Benbrook', 'binary_Bloomfield', 'binary_Bloomingdale',
                'binary_Boca_Raton', 'binary_Boonton', 'binary_Boston', 'binary_Bothell',
                'binary_Brea', 'binary_Brighton', 'binary_Brooklyn', 'binary_Burbank',
                'binary_Burlington', 'binary_Calabasas', 'binary_Camarillo', 'binary_Cambridge',
                'binary_Canoga_Park', 'binary_Carrollton', 'binary_Castle_Rock', 'binary_Charlotte',
                'binary_Chestnut_Hill', 'binary_Chino_Hills', 'binary_Coconut_Creek', 'binary_Columbia',
                'binary_Costa_Mesa', 'binary_Dallas', 'binary_Denver', 'binary_Doral',
                'binary_Dublin', 'binary_Durham', 'binary_Edgewater', 'binary_Emeryville',
                'binary_Encino', 'binary_Englewood', 'binary_Fairfax_County', 'binary_Falls_Church',
                'binary_Florham_Park', 'binary_Flower_Mound', 'binary_Fort_Lauderdale', 'binary_Foster_City',
                'binary_Framingham', 'binary_Fremont', 'binary_Frisco', 'binary_Garden_City',
                'binary_Georgetown', 'binary_Glendale', 'binary_Glendora', 'binary_Great_Neck',
                'binary_Harrison', 'binary_Herndon', 'binary_Hialeah', 'binary_Hingham',
                'binary_Hoboken', 'binary_Hunt_Valley', 'binary_Huntington_Beach', 'binary_Huntington_Station',
                'binary_Irvine', 'binary_Jersey_City', 'binary_La_Mesa', 'binary_Lafayette',
                'binary_Lake_Forest', 'binary_Lakewood', 'binary_Laurel', 'binary_Lewisville',
                'binary_Lexington', 'binary_Linthicum_Heights', 'binary_Littleton', 'binary_Long_Island',
                'binary_Long_Island_City', 'binary_Los_Angeles', 'binary_Lynnwood', 'binary_Maplewood',
                'binary_Margate', 'binary_Marlborough', 'binary_Melville', 'binary_Merrifield',
                'binary_Miami', 'binary_Milford', 'binary_Miramar', 'binary_Monrovia',
                'binary_Montville', 'binary_Mooresville', 'binary_Morrisville', 'binary_Mountain_View',
                'binary_Natick', 'binary_Newcastle', 'binary_New_York_City', 'binary_North_Andover',
                'binary_North_Bergen', 'binary_North_Bethesda', 'binary_North_Potomac', 'binary_Northborough',
                'binary_Norwood', 'binary_Old_Bridge', 'binary_Owings_Mills', 'binary_Pacifica',
                'binary_Parker', 'binary_Parsippany', 'binary_Pasadena', 'binary_Peabody',
                'binary_Pflugerville', 'binary_Piscataway', 'binary_Pleasanton', 'binary_Plymouth',
                'binary_Pomona', 'binary_Princeton', 'binary_Quincy', 'binary_Rancho_Santa_Margarita',
                'binary_Redmond', 'binary_Reston', 'binary_Rockville', 'binary_Rockville_Centre',
                'binary_Roseland', 'binary_San_Bruno', 'binary_San_Diego', 'binary_San_Dimas',
                'binary_San_Francisco', 'binary_San_Jose', 'binary_San_Marcos', 'binary_Santa_Monica',
                'binary_Saugus', 'binary_Seal_Beach', 'binary_Seattle', 'binary_Silver_Spring',
                'binary_Smithtown', 'binary_Somers', 'binary_Somerville', 'binary_Studio_City',
                'binary_Sudbury', 'binary_Sunnyvale', 'binary_Teaneck', 'binary_Thousand_Oaks',
                'binary_Towson', 'binary_Tysons_Corner', 'binary_Union', 'binary_Union_City',
                'binary_Vista', 'binary_Walnut_Creek', 'binary_Waltham', 'binary_Washington',
                'binary_Wayne', 'binary_West_Hollywood', 'binary_West_Palm_Beach', 'binary_West_Windsor',
                'binary_Westbury', 'binary_Westminster', 'binary_Wharton', 'binary_Wheaton',
                'binary_White_Plains', 'binary_Wilmington', 'binary_Woburn', 'binary_Woodland_Hills',
                'binary_Yonkers']

X_all = AVB_data[AVB_features]
X_train, X_test, y_train, y_test = train_test_split(
    train_data[AVB_features], y, test_size=0.2, random_state=1
)
AVB_model.fit(X_train, y_train)
predicted_test = AVB_model.predict(X_test)
mae = mean_absolute_error(y_test, predicted_test)
r2 = r2_score(y_test, predicted_test)
n = len(y_test)
p = X_train.shape[1]
adj_r2 = 1 - (1 - r2) * (n - 1) / (n - p - 1)
print(f"\nModel Performance:")
print(f"  Mean Absolute Error: ${mae:.2f}")
print(f"  R² Score: {r2:.4f}")
print(f"Adjusted R² Score: {adj_r2:.4f}")

#Edit 2 lines below in/out depending on need. Include if using scikitlearn to predict. Exclude to just get the R2 & MAE
#AVB_data['adjusted_price'] = AVB_model.predict(X_all)
#AVB_data.to_csv(file_path, index=False)
print(f"Total rows: {len(AVB_data)}")
print(f"Trained on {len(train_data)} rows with known prices")
print(f"Predicted for all {len(AVB_data)} rows")