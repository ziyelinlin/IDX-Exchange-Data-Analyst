"""
Week 2 Dataset Structuring and Validation

This script summarizes the combined MLS sold and listing datasets, filters both
datasets to Residential properties, creates missing-value reports, reviews key
numeric distributions, saves plots, and answers the suggested EDA questions.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


# ---------------------------------------------------------------------------
# File paths
# ---------------------------------------------------------------------------

data_path = Path("/Users/lindsey/Desktop/IDX/data")
reports_path = Path("/Users/lindsey/Desktop/IDX/reports/week2_reports")
plots_path = reports_path / "plots"

reports_path.mkdir(parents=True, exist_ok=True)
plots_path.mkdir(parents=True, exist_ok=True)

sold_file = data_path / "sold_combined.csv"
listings_file = data_path / "listings_combined.csv"

sold_residential_file = data_path / "week2_sold_residential.csv"
listings_residential_file = data_path / "week2_listings_residential.csv"


# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------

sold = pd.read_csv(sold_file, low_memory=False)
listings = pd.read_csv(listings_file, low_memory=False)

print("Sold dataset shape:", sold.shape)
print("Listings dataset shape:", listings.shape)


# ---------------------------------------------------------------------------
# Dataset understanding: columns, data types, and field groups
# ---------------------------------------------------------------------------

sold_structure = pd.DataFrame({
    "column": sold.columns,
    "data_type": sold.dtypes.astype(str).values
})

listings_structure = pd.DataFrame({
    "column": listings.columns,
    "data_type": listings.dtypes.astype(str).values
})

sold_structure.to_csv(reports_path / "sold_structure.csv", index=False)
listings_structure.to_csv(reports_path / "listings_structure.csv", index=False)

market_analysis_fields = [
    "ClosePrice",
    "ListPrice",
    "OriginalListPrice",
    "LivingArea",
    "LotSizeAcres",
    "BedroomsTotal",
    "BathroomsTotalInteger",
    "DaysOnMarket",
    "YearBuilt",
    "CloseDate",
    "ListingContractDate",
    "PurchaseContractDate",
    "PropertyType",
    "PropertySubType",
    "MlsStatus",
    "CountyOrParish",
    "City",
    "PostalCode",
    "Latitude",
    "Longitude",
]

sold_field_groups = pd.DataFrame({
    "column": sold.columns,
    "field_group": [
        "market_analysis" if column in market_analysis_fields else "metadata"
        for column in sold.columns
    ],
})

listings_field_groups = pd.DataFrame({
    "column": listings.columns,
    "field_group": [
        "market_analysis" if column in market_analysis_fields else "metadata"
        for column in listings.columns
    ],
})

sold_field_groups.to_csv(reports_path / "sold_field_groups.csv", index=False)
listings_field_groups.to_csv(reports_path / "listings_field_groups.csv", index=False)


# ---------------------------------------------------------------------------
# Unique property types and Residential filtering
# ---------------------------------------------------------------------------

sold_property_type_counts = sold["PropertyType"].value_counts(dropna=False).reset_index()
sold_property_type_counts.columns = ["PropertyType", "row_count"]
sold_property_type_counts["percent_of_rows"] = (
    sold_property_type_counts["row_count"] / len(sold) * 100
)

listings_property_type_counts = listings["PropertyType"].value_counts(dropna=False).reset_index()
listings_property_type_counts.columns = ["PropertyType", "row_count"]
listings_property_type_counts["percent_of_rows"] = (
    listings_property_type_counts["row_count"] / len(listings) * 100
)

sold_property_type_counts.to_csv(
    reports_path / "sold_property_type_counts.csv",
    index=False,
)
listings_property_type_counts.to_csv(
    reports_path / "listings_property_type_counts.csv",
    index=False,
)

# Filtering logic: keep only records where PropertyType is Residential after
# trimming extra spaces.
sold_res = sold[sold["PropertyType"].astype("string").str.strip() == "Residential"].copy()
listings_res = listings[
    listings["PropertyType"].astype("string").str.strip() == "Residential"
].copy()

print("Sold rows before Residential filter:", len(sold))
print("Sold rows after Residential filter:", len(sold_res))
print("Listings rows before Residential filter:", len(listings))
print("Listings rows after Residential filter:", len(listings_res))

sold_res.to_csv(sold_residential_file, index=False)
listings_res.to_csv(listings_residential_file, index=False)


# ---------------------------------------------------------------------------
# Missing value analysis
# ---------------------------------------------------------------------------

# Core fields are kept for analysis even when partially missing.
core_fields = [
    "ListingKey",
    "ListingId",
    "PropertyType",
    "PropertySubType",
    "MlsStatus",
    "CloseDate",
    "PurchaseContractDate",
    "ListingContractDate",
    "ClosePrice",
    "ListPrice",
    "OriginalListPrice",
    "LivingArea",
    "LotSizeAcres",
    "BedroomsTotal",
    "BathroomsTotalInteger",
    "DaysOnMarket",
    "YearBuilt",
    "CountyOrParish",
    "City",
    "PostalCode",
    "Latitude",
    "Longitude",
]

sold_missing_report = pd.DataFrame({
    "column": sold_res.columns,
    "missing_count": sold_res.isnull().sum().values,
    "missing_percent": sold_res.isnull().mean().values * 100,
})
sold_missing_report["above_90_percent_missing"] = (
    sold_missing_report["missing_percent"] > 90
)
sold_missing_report["recommended_action"] = "retain"
sold_missing_report.loc[
    sold_missing_report["above_90_percent_missing"],
    "recommended_action",
] = "review_for_drop"
sold_missing_report.loc[
    sold_missing_report["column"].isin(core_fields),
    "recommended_action",
] = "retain_core_field"
sold_missing_report = sold_missing_report.sort_values(
    by="missing_percent",
    ascending=False,
)

listings_missing_report = pd.DataFrame({
    "column": listings_res.columns,
    "missing_count": listings_res.isnull().sum().values,
    "missing_percent": listings_res.isnull().mean().values * 100,
})
listings_missing_report["above_90_percent_missing"] = (
    listings_missing_report["missing_percent"] > 90
)
listings_missing_report["recommended_action"] = "retain"
listings_missing_report.loc[
    listings_missing_report["above_90_percent_missing"],
    "recommended_action",
] = "review_for_drop"
listings_missing_report.loc[
    listings_missing_report["column"].isin(core_fields),
    "recommended_action",
] = "retain_core_field"
listings_missing_report = listings_missing_report.sort_values(
    by="missing_percent",
    ascending=False,
)

sold_columns_above_90_missing = sold_missing_report[
    sold_missing_report["above_90_percent_missing"]
]
listings_columns_above_90_missing = listings_missing_report[
    listings_missing_report["above_90_percent_missing"]
]

sold_missing_report.to_csv(reports_path / "sold_missing_value_report.csv", index=False)
listings_missing_report.to_csv(
    reports_path / "listings_missing_value_report.csv",
    index=False,
)
sold_columns_above_90_missing.to_csv(
    reports_path / "sold_columns_above_90_missing.csv",
    index=False,
)
listings_columns_above_90_missing.to_csv(
    reports_path / "listings_columns_above_90_missing.csv",
    index=False,
)


# ---------------------------------------------------------------------------
# Numeric distribution review
# ---------------------------------------------------------------------------

numeric_fields = [
    "ClosePrice",
    "ListPrice",
    "OriginalListPrice",
    "LivingArea",
    "LotSizeAcres",
    "BedroomsTotal",
    "BathroomsTotalInteger",
    "DaysOnMarket",
    "YearBuilt",
]

summary_fields = ["ClosePrice", "LivingArea", "DaysOnMarket"]

sold_numeric = sold_res[numeric_fields].apply(pd.to_numeric, errors="coerce")
listings_numeric = listings_res[numeric_fields].apply(pd.to_numeric, errors="coerce")

sold_numeric_summary = sold_numeric.describe(
    percentiles=[0.01, 0.05, 0.25, 0.50, 0.75, 0.95, 0.99]
).T
listings_numeric_summary = listings_numeric.describe(
    percentiles=[0.01, 0.05, 0.25, 0.50, 0.75, 0.95, 0.99]
).T

sold_deliverable_numeric_summary = sold_numeric[summary_fields].describe(
    percentiles=[0.01, 0.05, 0.25, 0.50, 0.75, 0.95, 0.99]
).T
listings_deliverable_numeric_summary = listings_numeric[summary_fields].describe(
    percentiles=[0.01, 0.05, 0.25, 0.50, 0.75, 0.95, 0.99]
).T

sold_numeric_summary.to_csv(reports_path / "sold_numeric_distribution_summary.csv")
listings_numeric_summary.to_csv(
    reports_path / "listings_numeric_distribution_summary.csv"
)
sold_deliverable_numeric_summary.to_csv(
    reports_path / "sold_deliverable_numeric_summary.csv"
)
listings_deliverable_numeric_summary.to_csv(
    reports_path / "listings_deliverable_numeric_summary.csv"
)

sold_outlier_rows = []
listings_outlier_rows = []

for field in numeric_fields:
    sold_series = sold_numeric[field].dropna()
    sold_q1 = sold_series.quantile(0.25)
    sold_q3 = sold_series.quantile(0.75)
    sold_iqr = sold_q3 - sold_q1
    sold_lower_bound = sold_q1 - 1.5 * sold_iqr
    sold_upper_bound = sold_q3 + 1.5 * sold_iqr
    sold_outlier_count = (
        (sold_series < sold_lower_bound) | (sold_series > sold_upper_bound)
    ).sum()

    sold_outlier_rows.append({
        "field": field,
        "lower_bound": sold_lower_bound,
        "upper_bound": sold_upper_bound,
        "outlier_count": sold_outlier_count,
        "outlier_percent": sold_outlier_count / len(sold_series) * 100,
    })

    listings_series = listings_numeric[field].dropna()
    listings_q1 = listings_series.quantile(0.25)
    listings_q3 = listings_series.quantile(0.75)
    listings_iqr = listings_q3 - listings_q1
    listings_lower_bound = listings_q1 - 1.5 * listings_iqr
    listings_upper_bound = listings_q3 + 1.5 * listings_iqr
    listings_outlier_count = (
        (listings_series < listings_lower_bound)
        | (listings_series > listings_upper_bound)
    ).sum()

    listings_outlier_rows.append({
        "field": field,
        "lower_bound": listings_lower_bound,
        "upper_bound": listings_upper_bound,
        "outlier_count": listings_outlier_count,
        "outlier_percent": listings_outlier_count / len(listings_series) * 100,
    })

sold_outlier_report = pd.DataFrame(sold_outlier_rows)
listings_outlier_report = pd.DataFrame(listings_outlier_rows)

sold_outlier_report.to_csv(reports_path / "sold_numeric_outlier_report.csv", index=False)
listings_outlier_report.to_csv(
    reports_path / "listings_numeric_outlier_report.csv",
    index=False,
)

for field in numeric_fields:
    sold_series = sold_numeric[field].dropna()
    fig, axes = plt.subplots(1, 2, figsize=(10, 3))
    axes[0].hist(sold_series, bins=50)
    axes[0].set_title(f"Sold {field} Histogram")
    axes[0].set_xlabel(field)
    axes[0].set_ylabel("Count")
    axes[1].boxplot(sold_series, vert=True)
    axes[1].set_title(f"Sold {field} Boxplot")
    axes[1].set_ylabel(field)
    plt.tight_layout()
    plt.savefig(plots_path / f"sold_{field}_histogram_boxplot.png")
    plt.close()

    listings_series = listings_numeric[field].dropna()
    fig, axes = plt.subplots(1, 2, figsize=(10, 3))
    axes[0].hist(listings_series, bins=50)
    axes[0].set_title(f"Listings {field} Histogram")
    axes[0].set_xlabel(field)
    axes[0].set_ylabel("Count")
    axes[1].boxplot(listings_series, vert=True)
    axes[1].set_title(f"Listings {field} Boxplot")
    axes[1].set_ylabel(field)
    plt.tight_layout()
    plt.savefig(plots_path / f"listings_{field}_histogram_boxplot.png")
    plt.close()


# ---------------------------------------------------------------------------
# Suggested intern questions
# ---------------------------------------------------------------------------

sold_residential_share = (
    sold["PropertyType"].astype("string").str.strip() == "Residential"
).mean() * 100
listings_residential_share = (
    listings["PropertyType"].astype("string").str.strip() == "Residential"
).mean() * 100

sold_res["ClosePrice"] = pd.to_numeric(sold_res["ClosePrice"], errors="coerce")
sold_res["ListPrice"] = pd.to_numeric(sold_res["ListPrice"], errors="coerce")
sold_res["DaysOnMarket"] = pd.to_numeric(sold_res["DaysOnMarket"], errors="coerce")

average_close_price = sold_res["ClosePrice"].mean()
median_close_price = sold_res["ClosePrice"].median()

valid_price_rows = sold_res[
    sold_res["ClosePrice"].notna()
    & sold_res["ListPrice"].notna()
    & (sold_res["ListPrice"] > 0)
].copy()

sold_above_list_percent = (
    valid_price_rows["ClosePrice"] > valid_price_rows["ListPrice"]
).mean() * 100
sold_below_list_percent = (
    valid_price_rows["ClosePrice"] < valid_price_rows["ListPrice"]
).mean() * 100
sold_at_list_percent = (
    valid_price_rows["ClosePrice"] == valid_price_rows["ListPrice"]
).mean() * 100

sold_res["CloseDate"] = pd.to_datetime(sold_res["CloseDate"], errors="coerce")
sold_res["ListingContractDate"] = pd.to_datetime(
    sold_res["ListingContractDate"],
    errors="coerce",
)

valid_date_rows = sold_res[
    sold_res["CloseDate"].notna()
    & sold_res["ListingContractDate"].notna()
].copy()
date_issue_rows = valid_date_rows[
    valid_date_rows["CloseDate"] < valid_date_rows["ListingContractDate"]
]
date_issue_count = len(date_issue_rows)
date_issue_percent = date_issue_count / len(valid_date_rows) * 100

county_price_summary = (
    sold_res
    .dropna(subset=["CountyOrParish", "ClosePrice"])
    .groupby("CountyOrParish")
    .agg(
        sale_count=("ClosePrice", "size"),
        median_close_price=("ClosePrice", "median"),
        average_close_price=("ClosePrice", "mean"),
    )
    .sort_values("median_close_price", ascending=False)
    .reset_index()
)

county_price_summary_100_plus = county_price_summary[
    county_price_summary["sale_count"] >= 100
]

intern_question_answers = pd.DataFrame([
    {"question": "Sold Residential share", "answer": sold_residential_share},
    {"question": "Listings Residential share", "answer": listings_residential_share},
    {"question": "Average close price", "answer": average_close_price},
    {"question": "Median close price", "answer": median_close_price},
    {"question": "Sold above list price percent", "answer": sold_above_list_percent},
    {"question": "Sold below list price percent", "answer": sold_below_list_percent},
    {"question": "Sold at list price percent", "answer": sold_at_list_percent},
    {"question": "Close date before listing date count", "answer": date_issue_count},
    {
        "question": "Close date before listing date percent",
        "answer": date_issue_percent,
    },
])

intern_question_answers.to_csv(
    reports_path / "intern_question_answers.csv",
    index=False,
)
county_price_summary.to_csv(
    reports_path / "sold_county_price_summary.csv",
    index=False,
)
county_price_summary_100_plus.to_csv(
    reports_path / "sold_county_price_summary_100_plus.csv",
    index=False,
)


# ---------------------------------------------------------------------------
# Final summary
# ---------------------------------------------------------------------------

print("\nWeek 2 EDA complete.")
print("Filtered sold Residential dataset:", sold_residential_file)
print("Filtered listings Residential dataset:", listings_residential_file)
print("Reports folder:", reports_path)
print("Plots folder:", plots_path)
