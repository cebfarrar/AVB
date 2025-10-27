# AvalonBay Communities Rental Pricing Model

Predictive modeling of apartment rental prices across AvalonBay's US portfolio using web-scraped data and machine learning.
<div align="center" style="text-align: center">
    <img width="400" height="400" alt="5382f508a8c09c894de6c5d439c023d5" src="https://github.com/user-attachments/assets/26ab5bd7-c356-4b31-90ec-e3c0edb809ce" />
</div>
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
Average rent: ~$2,976
```

### Dataset Summary

- **Total apartments scraped**: 76,545 across 273 properties
- **Currently listed** (known prices): 6,578 apartments
- **Unlisted** (predicted prices): 69,967 apartments
- **Train/Test split**: 80% train (5,262) / 20% test (1,316)
- **Geographic coverage**: 12 US states, 165 cities
- **Portfolio coverage**: 86% of AvalonBay's operational units (per SEC filings)

### What the results mean

The model achieves **R² = 0.944**, meaning it explains 94.4% of rental price variation. The **MAE of $124.80** means predictions are typically within ±$125 of actual market prices - **4.2% error** relative to average rent.

Validation was performed on 1,316 apartments completely withheld from training, ensuring the model generalizes to unseen data.

---

## Methodology

### 1. Data Collection

**Web scraping** using Python (BeautifulSoup, Selenium):
- Scraped AvalonBay's public website for all listed properties - Used browser DevTools to identify the API endpoint behind AvalonBay's interactive property map, containing all currently available properties.
- Collected apartment-level features (bed, bath, sqft, floor) and current rental prices
- Total: 76,545 apartments across 273 properties

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
- 165+ city-level indicators (Boston, Seattle, Denver, etc.)

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
- Prevents overfitting and ensures generalization

**Metrics**:
- **R² Score**: Proportion of variance explained (0 = no better than mean, 1 = perfect)
- **MAE**: Average absolute prediction error in dollars
- **Adjusted R²**: R² adjusted for number of features (penalizes model complexity)

---

## Data Coverage Notes

### Why 76,545 apartments vs. AvalonBay's reported figures?

**Official AvalonBay figures (Q3 2025)**:
- Website: 97,212 apartment homes
- SEC filings: 88,669 operational units

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

## Repository Structure
```
/avalonbay-rental-pricing/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── train_model.py                     # Model training script
├── scrape_current_listings.py         # Scraper for listed apartments
├── scrape_total_portfolio.py          # Scraper for all properties
├── /data/
│   ├── sample_data.csv                # Sample (10 rows, anonymized)
│   └── data_dictionary.md             # Feature descriptions
└── /results/
    └── model_performance.txt          # Detailed results
```

---

## Future Improvements

**Model enhancements**:
- Incorporate temporal features (seasonality, market trends)
- Add property-level amenities (pool, gym, parking, pet policy)
- Experiment with gradient boosting (XGBoost, LightGBM)
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

---

## Learning Resources

This project was developed using techniques from:
- [Kaggle's Intro to Machine Learning](https://www.kaggle.com/learn/intro-to-machine-learning)
- scikit-learn documentation
- Web scraping tutorials (BeautifulSoup, Selenium)

---

## Notes

- **Independent academic project** - not affiliated with AvalonBay Communities
- Data scraped from publicly available sources
- Created for portfolio demonstration and learning purposes
- October 2025

---

**Contact**: charlie.farrar@icloud.com  
**GitHub**: github.com/charliefarrar

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
Properties: 273
Coverage: 86% of operational portfolio

=== Geographic Distribution ===
Top 5 cities by apartment count:
1. New York City: 8,234 apartments
2. Los Angeles: 6,891 apartments
3. Boston: 5,432 apartments
4. Seattle: 4,567 apartments
5. San Francisco: 3,876 apartments
```
