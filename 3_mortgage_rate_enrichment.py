import pandas as pd
from pathlib import Path

data_path = Path("/Users/lindsey/Desktop/IDX/data")

sold_file = data_path / "sold_residential.csv"
listings_file = data_path / "listings_residential.csv"

sold = pd.read_csv(sold_file, low_memory=False)
listings = pd.read_csv(listings_file, low_memory=False)

# 1. Fetch the mortgage rate data from FRED
url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US"
mortgage = pd.read_csv(url, parse_dates=['observation_date'])
mortgage.columns = ['date', 'rate_30yr_fixed']

# 2. Resample weekly rates to monthly averages
mortgage['year_month'] = mortgage['date'].dt.to_period('M')
mortgage_monthly = mortgage.groupby(
    'year_month')['rate_30yr_fixed'].mean().reset_index()

# 3. Create a matching year_month key on the MLS datasets

# Sold dataset — key off CloseDate
sold['year_month'] = pd.to_datetime(sold['CloseDate']).dt.to_period('M')

# Listings dataset — key off ListingContractDate
listings['year_month'] = pd.to_datetime(
    listings['ListingContractDate']).dt.to_period('M')

# 4. Merge
sold_with_rates = sold.merge(mortgage_monthly, on='year_month', how='left')
listings_with_rates = listings.merge(
    mortgage_monthly, on='year_month', how='left')

# 5. Validate the merge
# Check for any unmatched rows (rate should not be null)
print(sold_with_rates['rate_30yr_fixed'].isnull().sum())
print(listings_with_rates['rate_30yr_fixed'].isnull().sum())

print(sold_with_rates[['CloseDate', 'year_month',
      'ClosePrice', 'rate_30yr_fixed']].head())

print(listings_with_rates[['ListingContractDate',
      'year_month', 'ListPrice', 'rate_30yr_fixed']].head())

# 6. Save the merged datasets to CSV files
sold_with_rates.to_csv(data_path / "sold_with_rates.csv", index=False)
listings_with_rates.to_csv(data_path / "listings_with_rates.csv", index=False)
