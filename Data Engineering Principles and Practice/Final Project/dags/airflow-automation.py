
from airflow import DAG
from airflow.operators.python import PythonOperator
import pendulum
import pandas as pd
from pathlib import Path
import psycopg2

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
    # column_selection = [census_data.columns[0]] + list(census_data.filter(like="Estimate").columns)
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


def load_data_postgre(dataset_paths: list):

    census = clean_census_data(dataset_paths[0])
    vaccinations_total, vaccination_daily = clean_vaccination(dataset_paths[1])
    covid_death_monthly, covid_death_total = clean_covid_death(dataset_paths[2])

    # Connect to PostgreSQL
    connection = psycopg2.connect(
        host="postgres",
        database="final_db",
        user="group",
        password="project",
        port="5432"
    )

    # Create a cursor
    cursor = connection.cursor()

    # Drop existing tables if they already exist
    cursor.execute("DROP TABLE IF EXISTS vaccinations_total, vaccination_daily, covid_death_monthly, covid_death_total, census CASCADE;")
    connection.commit()

    # Define SQL to create each table with primary keys and foreign keys
    create_census_table = """
    CREATE TABLE IF NOT EXISTS census (
        state VARCHAR(100) PRIMARY KEY,
        grouping VARCHAR(100),
        population INTEGER
    );
    """

    create_vaccinations_total_table = """
    CREATE TABLE IF NOT EXISTS vaccinations_total (
        location VARCHAR(100) PRIMARY KEY,
        total_vaccinations BIGINT,
        total_distributed BIGINT,
        people_vaccinated BIGINT,
        people_fully_vaccinated BIGINT,
        FOREIGN KEY (location) REFERENCES census(state)
    );
    """

    create_vaccination_daily_table = """
    CREATE TABLE IF NOT EXISTS vaccination_daily (
        day INTEGER,
        month INTEGER,
        location VARCHAR(100),
        daily_vaccinations NUMERIC,
        daily_vaccinations_per_million NUMERIC,
        people_vaccinated NUMERIC,
        share_doses_used FLOAT,
        PRIMARY KEY (day, month, location),
        FOREIGN KEY (location) REFERENCES census(state)
    );
    """

    create_covid_death_monthly_table = """
    CREATE TABLE IF NOT EXISTS covid_death_monthly (
        month INTEGER,
        State VARCHAR(100),
        Sex VARCHAR(10),
        "Age Group" VARCHAR(50),
        "COVID-19 Deaths" INTEGER,
        PRIMARY KEY (month, State, "Age Group"),
        FOREIGN KEY (State) REFERENCES census(state)
    );
    """

    create_covid_death_total_table = """
    CREATE TABLE IF NOT EXISTS covid_death_total (
        State VARCHAR(100),
        Sex VARCHAR(10),
        "Age Group" VARCHAR(50),
        "COVID-19 Deaths" INTEGER,
        PRIMARY KEY (State, Sex, "Age Group"),
        FOREIGN KEY (State) REFERENCES census(state)
    );
    """

    # Execute each table creation
    cursor.execute(create_census_table)
    cursor.execute(create_vaccinations_total_table)
    cursor.execute(create_vaccination_daily_table)
    cursor.execute(create_covid_death_monthly_table)
    cursor.execute(create_covid_death_total_table)
    connection.commit()

    # Insert data into the census table
    for _, row in census.iterrows():
        cursor.execute("""
            INSERT INTO census (state, grouping, population)
            VALUES (%s, %s, %s)
            ON CONFLICT DO NOTHING;
        """, (row['State'], row['Grouping'], row['Population']))
    connection.commit()

    # Identify missing locations in `vaccinations_total`
    missing_locations = set(vaccinations_total['location']) - set(census['State'])

    # Insert missing locations into `census` table with default values
    for location in missing_locations:
        #print(f"Inserting missing location '{location}' into census")
        cursor.execute("""
            INSERT INTO census (state, grouping, population)
            VALUES (%s, 'Unknown Group', 0)
            ON CONFLICT DO NOTHING;
        """, (location,))
    connection.commit()

    # Identify missing states in `covid_death_monthly` and `covid_death_total`
    missing_states_monthly = set(covid_death_monthly['State']) - set(census['State'])
    missing_states_total = set(covid_death_total['State']) - set(census['State'])

    # Combine all missing states into a single set
    missing_states = missing_states_monthly | missing_states_total

    # Insert missing states into `census` table with default values
    for state in missing_states:
        #print(f"Inserting missing state '{state}' into census")
        cursor.execute("""
            INSERT INTO census (state, grouping, population)
            VALUES (%s, 'Unknown Group', 0)
            ON CONFLICT DO NOTHING;
        """, (state,))
    connection.commit()

    # Insert data into the vaccinations_total table
    for _, row in vaccinations_total.iterrows():
        cursor.execute("""
            INSERT INTO vaccinations_total (location, total_vaccinations, total_distributed, people_vaccinated, people_fully_vaccinated)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING;
        """, (row['location'], row['total_vaccinations'], row['total_distributed'], row['people_vaccinated'], row['people_fully_vaccinated']))
    connection.commit()

    # Insert data into the vaccination_daily table
    for _, row in vaccination_daily.iterrows():
        cursor.execute("""
            INSERT INTO vaccination_daily (day, month, location, daily_vaccinations, daily_vaccinations_per_million, people_vaccinated, share_doses_used)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING;
        """, (row['day'], row['month'], row['location'], row['daily_vaccinations'], row['daily_vaccinations_per_million'], row['people_vaccinated'], row['share_doses_used']))
    connection.commit()

    # Insert data into the covid_death_monthly table
    for _, row in covid_death_monthly.iterrows():
        cursor.execute("""
            INSERT INTO covid_death_monthly (month, State, Sex, "Age Group", "COVID-19 Deaths")
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING;
        """, (row['Month'], row['State'], row['Sex'], row['Age Group'], row['COVID-19 Deaths']))
    connection.commit()

    # Insert data into the covid_death_total table
    for _, row in covid_death_total.iterrows():
        cursor.execute("""
            INSERT INTO covid_death_total (State, Sex, "Age Group", "COVID-19 Deaths")
            VALUES (%s, %s, %s, %s)
            ON CONFLICT DO NOTHING;
        """, (row['State'], row['Sex'], row['Age Group'], row['COVID-19 Deaths']))
    connection.commit()

    # Verify data insertion by counting rows in each table
    print("\nRow counts after data insertion:")
    for table in ["census", "vaccinations_total", "vaccination_daily", "covid_death_monthly", "covid_death_total"]:
        query = f"SELECT COUNT(*) FROM {table};"
        count = pd.read_sql_query(query, connection)
        print(f"{table} Table Row Count:", count.iloc[0, 0])

    # Close the cursor and connection
    cursor.close()
    connection.close()


# Define the DAG
default_args = {
    "owner": "airflow",
    "retries": 1,
}
with DAG(
    "data_cleaning_and_loading",
    default_args=default_args,
    description="Clean and load datasets into PostgreSQL",
    schedule="@daily",
    start_date=pendulum.today('UTC').add(days=-2),
    catchup=False,
) as dag:
    
    # Define paths inside Docker container
    DATA_DIR = "/home/jovyan/data" # This is where data files are shared
    print(DATA_DIR)
    DATASET_PATHS = [
        f"{DATA_DIR}/demographic_data.csv",
       f"{DATA_DIR}/us_state_vaccinations_data.csv",
        f"{DATA_DIR}/covid19_death_data.csv",
    ]

    # Task to load each cleaned dataset into PostgreSQL
    census_task = PythonOperator(
            task_id="clean_census_data",
            python_callable=clean_census_data,
            op_args=DATASET_PATHS[0],
        )
    vaccines_task = PythonOperator(
            task_id="clean_vaccines_data",
            python_callable=clean_vaccination,
            op_args=DATASET_PATHS[1],
        )
    death_task = PythonOperator(
            task_id="clean_covid_death_data",
            python_callable=clean_covid_death,
            op_args=DATASET_PATHS[2],
        )
    postgre_task = PythonOperator(
        task_id="clean_and_load_data",
        python_callable=load_data_postgre,
        op_args=DATASET_PATHS,
    )

    # Set up task dependencies: clean -> load
    census_task >> vaccines_task >> death_task >> postgre_task
