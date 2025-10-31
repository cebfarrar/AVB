<img width="66" height="17" alt="image" src="https://github.com/user-attachments/assets/a3f8d594-43fb-4c28-a4c3-7b110f19504a" />

# AvalonBay Communities Rental Pricing Model

Predictive modeling of apartment rental prices across AvalonBay's US portfolio using web-scraped data and machine learning.

<div align="center" style="text-align: center">
    <img width="400" height="400" alt="5382f508a8c09c894de6c5d439c023d5" src="https://github.com/user-attachments/assets/26ab5bd7-c356-4b31-90ec-e3c0edb809ce" />
</div>

- [Project Overview](#project-overview)
- [Results](#results)
- [Methodology](#methodology)
- [Data Coverage Notes](#data-coverage-notes)
- [Revenue Prediction & Forecast](#revenue-prediction--forecast)
- [Repository Structure](#repository-structure)
- [Future Improvements](#future-improvements)
- [Learning Resources](#learning-resources)
- [Learning Resources](#notes)
- [Sample Output](#sample-output)
- [Workflow](#workflow)
- [Technical Stack](#technical-stack)
- [Contact](#contact)


---
## Project Overview

**Goal**: Predict rental prices for AvalonBay Communities' apartment portfolio using property characteristics and location data.

**Approach**: Random Forest regression model trained on currently listed apartments, then applied to predict prices across the entire portfolio.

## Results

### Model Performance (on held-out test set)
```
Mean Absolute Error: $124.80
R² Score: 0.944
Adjusted R² Score: 0.935
MAE as % of average rent: 4.2%
Average rent: ~$2,933
```

### Dataset Summary

- **Total apartments scraped**: 76,545 across 273 properties
- **Currently listed** (known prices): 6,578 apartments
- **Unlisted** (predicted prices): 69,967 apartments
- **Train/Test split**: 80% train (5,262) / 20% test (1,316)
- **Geographic coverage**: 12 US states, 165 cities
- **Portfolio coverage**: 86% of AvalonBay's operational units (per SEC filings)

### What the results mean

The model achieves **R² = 0.944**, meaning it explains 94.4% of rental price variation. The **MAE of $124.80** means predictions are typically within ±$125 of actual market prices - **4.25% error** relative to average rent.

Validation was performed on 1,316 apartments completely withheld from training, ensuring the model generalises to unseen data.

---

# Methodology

### 1. Data Collection

**Web scraping** using Python (BeautifulSoup, Selenium):
- Scraped AvalonBay's public website for all listed properties
- Used browser DevTools to identify the API endpoint behind AvalonBay's interactive property map, containing all currently available properties
- Collected apartment-level features (bed, bath, sqft, floor) and current rental prices
- Total: 76,545 apartments across 229 properties

**Property coverage note**: AvalonBay reports 276 properties in SEC filings. My dataset includes 229 (82.9% coverage). The 48 missing properties consist of 3 properties opening in 2026 and 45 properties without interactive maps on the website, making API-based scraping impossible.

**Data Sources**:
- Primary: AvalonBay public listings
- Validation: SEC 10-K and 10-Q filings

### 2. Feature Engineering

**Apartment-level features**:
- `bed_count`: Number of bedrooms (0-4)
- `bath_count`: Number of bathrooms (1-3)
- `sqft`: Square footage (400-2,500 sqft)
- `floor`: Floor number within building

**Location features** (binary encoding):
- 12 state-level indicators (California, New York, Texas, etc.)
- 165 city-level indicators (Boston, Seattle, Denver, etc.)

Total features: 181 (4 continuous + 177 binary location indicators)

### 3. Model Selection & Training

**Algorithm**: Random Forest Regressor (scikit-learn)
- Ensemble of 100 decision trees
- Each tree trained on random subset of data and features
- Final prediction: average across all trees

**Why Random Forest?**
- Handles non-linear relationships between features and price
- Resistant to overfitting through ensemble averaging
- No feature scaling required
- Naturally handles binary encoded location data

**Training process**:
```python
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

# Split data: 80% train, 20% test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=1
)

# Train model
model = RandomForestRegressor(n_estimators=100, random_state=1, n_jobs=-1)
model.fit(X_train, y_train)

# Evaluate on held-out test set
predictions = model.predict(X_test)
```

### 4. Validation Strategy

**Train/test split approach**:
- Train on 5,262 apartments (80%)
- Test on 1,316 apartments (20%)
- Test set completely withheld during training
- Prevents overfitting and ensures generalisation

**Metrics**:
- **R² Score**: Proportion of variance explained (0 = no better than mean, 1 = perfect)
- **MAE**: Average absolute prediction error in dollars
- **Adjusted R²**: R² adjusted for number of features (penalises model complexity)

---

## Data Coverage Notes

### Why 76,545 apartments vs. AvalonBay's reported figures?

**Official AvalonBay figures**:
- Website: 97,212 apartment homes
- SEC filings (Q2 2025): 88,669 operational units

**My dataset (76,545) includes only**:
- Publicly listed properties on AvalonBay's website
- Currently operational and move-in ready apartments
- Properties with complete feature data

**The ~12,000 unit gap (88,669 - 76,545) likely includes**:
- Properties under development (2026+ deliveries)
- Partial ownership/joint ventures
- Off-market corporate housing
- Recently sold properties (reporting lag)

**Coverage**: 76,545 / 88,669 = **86% of operational portfolio** ✓

---

## Revenue Prediction & Forecast

**Using the model to test real-world predictive power**: With comprehensive portfolio coverage and October earnings release approaching, I'm using the model to forecast Q3 2025 revenues as a validation exercise.
**AvalonBay's Q3 2025 Earnings Release: October 29, 2025**

### Model-Based Revenue Estimate

The model predicts Q3 2025 revenues from the following sources (monthly):
```
Rent revenue from properties with interactive map (API access): $224,558,605
Rent revenue from properties without interactive map (no API access): $38,677,245.51
Less: Rent not utilized (property on market as of October 27, 2025): $21,432,498
```

**Quarterly calculation:**
```
Monthly rental income:
  Net Monthly: $224,558,605 + $38,677,245.51 - $21,432,498 = $241,803,352.51

Quarterly income (3 months):
  $241,803,352.51 × 3 = $725,410,057.53

Furnishing adjustment (10% furnished @ 41% premium):
  $725,410,057.53 × 1.041 = $755,151,869.89
```

**Q3 2025 Estimated Revenue: $755.2M**

---

### Prediction vs. Consensus

**Result will be known on October 29, 2025.** 

This model estimates AvalonBay will report approximately $755M for Q3 2025, compared to the Zacks consensus of $772M.
The Zacks consensus ($772M) sits comfortably within the model's conservative range ($728M - $782M), meaning both estimates are effectively consistent with each other given the statistical uncertainty involved.

The prediction carries statistical uncertainty from the MAE of $124.80 per apartment (4.2% of average rent):

- **Conservative range**: $728M - $782M (±$27M)
- **95% confidence interval**: $704M - $806M (±$51M)

Edit from 31 October 2025:
## Post-Earnings Update (October 29, 2025)

**Actual Q3 2025 Revenue**: $764.9M  
**Model Prediction**: $755.2M  
**Difference**: -$9.7M (-1.3%)
<img width="493" height="169" alt="Screenshot 2025-10-31 at 23 01 09" src="https://github.com/user-attachments/assets/107e894e-e95c-4872-831a-f57593450d39" />

### Analysis

The model underestimated revenue by 1.3%, which is **significantly better than the expected error rate of 4.2%** and well within the conservative prediction range ($728M-$782M).

**Why the prediction was low**: As anticipated in the limitations section, the snapshot methodology introduced downward bias. The model assumed all apartments listed on October 27 had been vacant for the entire quarter, when in reality many were only recently vacated. This caused the model to subtract $21.4M in "lost rent" that was actually collected earlier in Q3.

**Key takeaway**: The 1.3% error validates the model's core pricing predictions while confirming that tracking listing duration over time (now implemented via daily scraping) is essential for accurate occupancy modeling. The prediction's accuracy despite this known limitation suggests the apartment-level pricing model (R² = 0.944) is robust.

**Q4 2025 forecast improvement**: With daily scraping now active since October 28, the Q4 prediction will incorporate actual listing duration data, eliminating the snapshot bias that affected Q3.

---

### Known Limitations

This forecast has several important limitations. Most significantly, the prediction is based on a single snapshot taken on October 27, 2025, without any historical tracking of listing duration. The model assumes all apartments currently on the market have been vacant for the entire Q3 period, which likely introduces downward bias. In reality, many of these apartments were probably occupied for most of the quarter and only recently became available. This creates data corruption because recent move-outs are incorrectly counted as full-quarter vacancies. Without a backlog of previously scraped data showing how long each apartment has been listed, the model cannot distinguish between a unit vacant all quarter versus one that just hit the market yesterday.

Additional limitations include 48 properties (14% of portfolio) that lack interactive maps and rely on estimated revenues, potential underrepresentation of properties under development or in lease-up phase, and incomplete capture of joint ventures and partial ownership structures.

---

**Result will be known on October 29, 2025**

---


## Repository Structure
```
avalonbay-rental-pricing/
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   ├── property_urls.csv              (INPUT - included)
│   ├── complete_portfolio.csv         (generated by script 1)
│   ├── currently_available.csv        (generated by script 2)
│   └── missing_properties_predictions.csv (generated by script 5)
└── scripts/
    ├── 1_scrape_complete_portfolio.py
    ├── 2_currently_available.py
    ├── 3_available_to_complete_portfolio.py
    ├── 4_scikit.py
    └── 5_scikit_missing.py
```

---

## Future Improvements

**Model enhancements**:
- Incorporate temporal features (seasonality, market trends)
- Add property-level amenities (pool, gym, parking, pet policy)
- Feature importance analysis to identify key price drivers

**Data expansion**:
- Historical price tracking over time
- Neighborhood demographic data
- Proximity to transit, schools, employment centers
- Competitor pricing (other REITs in same markets)

**Deployment**:
- Interactive dashboard for price predictions
- API endpoint for real-time predictions
- Automated monthly retraining pipeline

**Continual Scraping**:
- To overcome the snapshot limitations described above, the scraping scripts now run daily to capture real-time market data. This creates a historical backlog showing which apartments are listed and for how long, enabling the model to accurately distinguish between properties vacant all quarter versus recent listings. This continuous monitoring will hopefully improve occupancy modeling and revenue predictions for Q4 2025 results.

---

## Learning Resources

This project was developed using techniques from:
- [Kaggle's Intro to Machine Learning](https://www.kaggle.com/learn/intro-to-machine-learning)
- scikit-learn documentation
- Web scraping tutorials (BeautifulSoup, Selenium)
- Boot.dev: Learn to code in Python, Build a Bookbot in Python, Learn Object Oriented Programming in Python, Learn Functional Programming in Python

---

## Notes

- **Independent academic project** - not affiliated with AvalonBay Communities
- Data scraped from publicly available sources
- Created for portfolio demonstration and learning purposes
- October 2025

---


## Sample Output
```
=== Model Performance (on held-out test set) ===
Mean Absolute Error: $124.80
R² Score: 0.9440
Adjusted R² Score: 0.9350

=== Dataset Summary ===
Total apartments: 76,545
Listed (known prices): 6,578
Unlisted (predicted): 69,967
Training set: 5,262
Test set: 1,316
Properties: 229
Coverage: 86% of operational portfolio
```

---

# Workflow

### Step 1: Scrape Complete Portfolio
```
python scripts/1_scrape_complete_portfolio.py

- **Input**: `data/property_urls.csv` (Sightmap URLs)
- **Output**: `data/complete_portfolio.csv` (76,346 apartments with property characteristics)
- **Purpose**: Extracts all apartment details (beds, baths, sqft, floor, location) from Sightmap API
```
### Step 2: Scrape Current Listings
```
python scripts/2_currently_available.py

- **Input**: `data/property_urls.csv` (communityID)
- **Output**: `data/currently_available.csv` (~6,000 currently available apartments with prices)
- **Purpose**: Gets current rental prices for available units from AvalonBay API
```
### Step 3: Match Prices to Portfolio
```
python scripts/3_available_to_complete_portfolio.py

- **Input**: `data/complete_portfolio.csv` + `data/currently_available.csv`
- **Output**: Updates `data/complete_portfolio.csv` with matched prices
- **Purpose**: Matches current listing prices to corresponding units in complete portfolio
```
### Step 4: Train Price Prediction Model
```
python scripts/4_scikit.py

- **Input**: `data/complete_portfolio.csv` (with matched prices)
- **Output**: Predictions for all 76,346 properties in complete_portfolio.csv
- **Model**: Random Forest (R² = 0.938, MAE = 4.5%)
- **Purpose**: Trains on ~6,000 priced units, predicts rent for all units
```
### Step 5: Predict Missing Properties
```
python scripts/5_scikit_missing.py

- **Input**: Properties in `property_urls.csv` missing from `complete_portfolio.csv`
- **Output**: `data/missing_properties_predictions.csv`
- **Purpose**: Estimates rent for properties without detailed Sightmap data
```
---

## Technical Stack
```
Python 3.x
├── pandas: Data manipulation and analysis
├── scikit-learn: Machine learning (Random Forest)
├── BeautifulSoup: HTML parsing for web scraping
├── Selenium: Dynamic content scraping
└── numpy: Numerical computations
```

**Requirements**:
```
pandas==2.0.3
scikit-learn==1.3.0
beautifulsoup4==4.12.2
selenium==4.10.0
numpy==1.24.3
```

---

# Contact
**Contact**: charlie.farrar@icloud.com  
**GitHub**: github.com/cebfarrar

---
