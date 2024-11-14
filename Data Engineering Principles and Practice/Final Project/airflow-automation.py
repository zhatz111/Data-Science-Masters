
from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
import pandas as pd
import numpy as np
import os

# Define paths inside Docker container
DATA_DIR = "/opt/airflow/data"  # This is where data files are shared
DATASET_PATHS = [f"{DATA_DIR}/dataset1.csv", f"{DATA_DIR}/dataset2.csv", f"{DATA_DIR}/dataset3.csv"]

def clean_census_data(file_path):
    census_data = pd.read_csv(file_path)
    labels_to_keep = [
        "Male",
        "Female",
        "Under 5 years",
        "5 to 9 years",
        "10 to 14 years",
        "15 to 19 years",
        "20 to 24 years",
        "25 to 34 years",
        "35 to 44 years",
        "45 to 54 years",
        "55 to 59 years",
        "60 to 64 years",
        "65 to 74 years",
        "75 to 84 years",
        "85 years and over",
        "White",
        "Black or African American",
        "American Indian and Alaska Native",
        "Asian",
        "Native Hawaiian and Other Pacific Islander",
        "Some other race",
        "White and Black or African American",
        "White and American Indian and Alaska Native",
        "White and Asian",
        "Black or African American and American Indian and Alaska Native",
    ]
    column_selection = [census_data.columns[0]] + list(census_data.filter(like="Estimate").columns)
    row_labels = [i.strip() for i in census_data["Label (Grouping)"]]
    census_data["Label (Grouping)"] = row_labels
    census_data_filtered = census_data.drop_duplicates(subset="Label (Grouping)")
    census_data_filtered = census_data_filtered.loc[census_data_filtered.isin(labels_to_keep).iloc[:,0]]
    census_data_melted = census_data_filtered.melt(id_vars="Label (Grouping)", var_name="State", value_name="Population")
    stripped = [i.replace("!!Estimate", "") for i in census_data_melted["State"]]
    census_data_melted["State"] = stripped
    census_data_melted = census_data_melted[~census_data_melted["State"].str.contains("Percent")].reset_index(drop=True)
    census_ages_to_combine = [
        ("5 to 9 years", "10 to 14 years", "5 to 14 years"),
        ("15 to 19 years", "20 to 24 years", "15 to 24 years"),
        ("55 to 59 years", "60 to 64 years", "55 to 64 years"),
    ]
    for count, i in enumerate(census_data_melted["Label (Grouping)"]):
        for j in census_ages_to_combine:
            if j[0] == i:
                census_data_melted.loc[count, "Label (Grouping)"] = j[2]
            if j[1] == i:
                census_data_melted.loc[count, "Label (Grouping)"] = j[2]

    # Specify the columns to group by (all columns except 'value')
    group_by_columns = [col for col in census_data_melted.columns if col != 'Population']
    census_data_melted['Population'] = census_data_melted['Population'].str.replace(',', '').astype(int)

    # Group by the specified columns and sum the 'value' column
    census_result = census_data_melted.groupby(group_by_columns, as_index=False)['Population'].agg("sum")
    census = census_result.rename(columns={"Label (Grouping)": "Grouping"})
    return census

def clean_vaccination(file_path):
    vaccination_data = pd.read_csv(file_path)
    vaccination_data["date"] = pd.to_datetime(vaccination_data["date"])
    vaccination_data["year"] = [i.year for i in vaccination_data["date"]]
    vaccination_data["month"] = [i.month for i in vaccination_data["date"]]
    vaccination_data["day"] = [i.day for i in vaccination_data["date"]]
    vaccination_data = vaccination_data.loc[vaccination_data["year"]==2021,:].reset_index(drop=True)
    
    vaccines_totals_columns = [
        "location",
        "total_vaccinations",
        "total_distributed",
        "people_vaccinated",
        "people_fully_vaccinated"
    ]

    vaccines_daily_columns = [
        "day",
        "month",
        "location",
        "daily_vaccinations",
        "daily_vaccinations_per_million",
        "people_vaccinated",
        "share_doses_used"
    ]

    vaccinations_total = vaccination_data[vaccines_totals_columns].groupby("location").agg("sum").reset_index()
    vaccination_daily = vaccination_data[vaccines_daily_columns]

    return vaccinations_total, vaccination_daily

def clean_covid_death(file_path):
    death_data = pd.read_csv(file_path)

    ages_to_discard = [
        '0-17 years',
        '18-29 years',
        '30-39 years',
        '40-49 years',
        '50-64 years',
    ]

    death_ages_to_combine = [
        ('Under 1 year', '1-4 years', 'Under 5 years'),
    ]

    death_columns = [
        "Year",
        "Month",
        "State",
        "Sex",
        "Age Group",
        "COVID-19 Deaths",
    ]
    death_data = death_data[death_columns]
    death_data_2021 = death_data[death_data["Year"]==2021.0]
    death_data_2021 = death_data_2021.dropna(subset=["Year", "Month"]).drop("Year", axis=1)
    death_data_2021 = death_data_2021[~death_data_2021['Age Group'].isin(ages_to_discard)].reset_index(drop=True)
    
    for count, i in enumerate(death_data_2021["Age Group"]):
        for j in death_ages_to_combine:
            if j[0] == i:
                death_data_2021.loc[count, "Age Group"] = j[2]
            if j[1] == i:
                death_data_2021.loc[count, "Age Group"] = j[2]
    
    # Group by the specified columns and sum the 'value' column
    group_by_columns_death = [col for col in death_data_2021.columns if col != 'COVID-19 Deaths']
    covid_death_monthly = death_data_2021.groupby(group_by_columns_death, as_index=False)['COVID-19 Deaths'].agg("sum")
    covid_death_total = covid_death_monthly.groupby(["State", "Sex", "Age Group"], as_index=False)['COVID-19 Deaths'].agg("sum")

    return covid_death_monthly, covid_death_total


