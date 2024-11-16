from airflow import DAG
from airflow.operators.python_operator import PythonOperator, BranchPythonOperator
from airflow.operators.dummy_operator import DummyOperator
from datetime import datetime, timedelta
import pandas as pd
import os
import psycopg2

default_args = {
    'owner': 'data_engineer',
    'start_date': datetime(2024, 11, 13),
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

with DAG(
    'extract_transform_load', 
    default_args=default_args, 
    schedule_interval='@daily',
    is_paused_upon_creation=False,
    catchup=True,
) as dag:

    def fetch_vaccination_data():
        file_path = '/opt/airflow/data/us_state_vaccinations_data.csv'
        data = pd.read_csv(file_path)
        return data

    def fetch_death_data():
        file_path = '/opt/airflow/data/covid19_death_data.csv'
        data = pd.read_csv(file_path)
        return data

    def fetch_census_data():
        file_path = '/opt/airflow/data/demographic_data.csv'
        data = pd.read_csv(file_path)
        return data

    def clean_census_data(census_data):
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

        census_total = census.groupby("State")["Population"].agg("sum").reset_index()

        census.to_csv("/opt/airflow/data/cleaned/census.csv")
        census_total.to_csv("/opt/airflow/data/cleaned/census_total.csv")

        return census, census_total


    def clean_vaccination_data(vaccination_data):

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

        vaccination_daily.to_csv("/opt/airflow/data/cleaned/vaccination_daily.csv")
        vaccinations_total.to_csv("/opt/airflow/data/cleaned/vaccinations_total.csv")

        return vaccinations_total, vaccination_daily

    def clean_death_data(death_data):
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

        covid_death_monthly.to_csv("/opt/airflow/data/cleaned/covid_death_monthly.csv")
        covid_death_total.to_csv("/opt/airflow/data/cleaned/covid_death_total.csv")

        return covid_death_monthly, covid_death_total

    def create_db():
        connection = psycopg2.connect(
            host="host.docker.internal",
            database="final_db",
            user="group",
            password="project",
            port="5432"
        )

        newpath = "/opt/airflow/data/cleaned" 
        if not os.path.exists(newpath):
            os.makedirs(newpath)

        # Create a cursor
        cursor = connection.cursor()

        # Drop existing tables if they already exist
        cursor.execute("""
            DROP TABLE IF EXISTS covid19.vaccinations_total, covid19.vaccination_daily, covid19.covid_death_monthly, covid19.covid_death_total, covid19.census, covid19.census_total;
            DROP SCHEMA IF EXISTS covid19;

            CREATE SCHEMA IF NOT EXISTS covid19;

        """)
        connection.commit()

        # Define SQL to create each table with primary keys and foreign keys
        create_census_total_table = """
        CREATE TABLE IF NOT EXISTS covid19.census_total (
            state VARCHAR(100) PRIMARY KEY,
            population INTEGER
        );
        """

        # Define SQL to create each table with primary keys and foreign keys
        create_census_table = """
        CREATE TABLE IF NOT EXISTS covid19.census (
            state VARCHAR(100) NOT NULL,
            grouping VARCHAR(100) NOT NULL,
            population INTEGER,
            PRIMARY KEY (state, grouping),
            FOREIGN KEY (state) REFERENCES covid19.census_total(state)
        );
        """

        create_vaccinations_total_table = """
        CREATE TABLE IF NOT EXISTS covid19.vaccinations_total (
            location VARCHAR(100) PRIMARY KEY,
            total_vaccinations BIGINT,
            total_distributed BIGINT,
            people_vaccinated BIGINT,
            people_fully_vaccinated BIGINT,
            FOREIGN KEY (location) REFERENCES covid19.census_total(state)
        );
        """

        create_vaccination_daily_table = """
        CREATE TABLE IF NOT EXISTS covid19.vaccination_daily (
            day INTEGER,
            month INTEGER,
            location VARCHAR(100),
            daily_vaccinations NUMERIC,
            daily_vaccinations_per_million NUMERIC,
            people_vaccinated NUMERIC,
            share_doses_used FLOAT,
            PRIMARY KEY (day, month, location),
            FOREIGN KEY (location) REFERENCES covid19.census_total(state)
        );
        """

        create_covid_death_monthly_table = """
        CREATE TABLE IF NOT EXISTS covid19.covid_death_monthly (
            month INTEGER,
            State VARCHAR(100),
            Sex VARCHAR(10),
            "Age Group" VARCHAR(50),
            "COVID-19 Deaths" INTEGER,
            PRIMARY KEY (month, State, "Age Group"),
            FOREIGN KEY (State) REFERENCES covid19.census_total(state)
        );
        """

        create_covid_death_total_table = """
        CREATE TABLE IF NOT EXISTS covid19.covid_death_total (
            State VARCHAR(100),
            Sex VARCHAR(10),
            "Age Group" VARCHAR(50),
            "COVID-19 Deaths" INTEGER,
            PRIMARY KEY (State, Sex, "Age Group"),
            FOREIGN KEY (State) REFERENCES covid19.census_total(state)
        );
        """

        # Execute each table creation
        cursor.execute(create_census_total_table)
        cursor.execute(create_census_table)
        cursor.execute(create_vaccinations_total_table)
        cursor.execute(create_vaccination_daily_table)
        cursor.execute(create_covid_death_monthly_table)
        cursor.execute(create_covid_death_total_table)
        connection.commit()

        # Close the cursor and connection
        cursor.close()
        connection.close()

    def insert_data():
        connection = psycopg2.connect(
            host="host.docker.internal",
            database="final_db",
            user="group",
            password="project",
            port="5432"
        )
        cursor = connection.cursor()

        file_path = '/opt/airflow/data/cleaned'
        census = pd.read_csv(f"{file_path}/census.csv")
        census_total = pd.read_csv(f"{file_path}/census_total.csv")
        vaccination_daily = pd.read_csv(f"{file_path}/vaccination_daily.csv")
        vaccinations_total = pd.read_csv(f"{file_path}/vaccinations_total.csv")
        covid_death_monthly = pd.read_csv(f"{file_path}/covid_death_monthly.csv")
        covid_death_total = pd.read_csv(f"{file_path}/covid_death_total.csv")

        # raw_census_data = fetch_census_data()
        # census = clean_census_data(raw_census_data)

        # raw_vaccination_data = fetch_vaccination_data()
        # vaccination_daily, vaccinations_total = clean_vaccination_data(raw_vaccination_data)

        # raw_death_data = fetch_death_data()
        # covid_death_monthly, covid_death_total = clean_death_data(raw_death_data)

        # Insert data into the census_total table
        for _, row in census_total.iterrows():
            cursor.execute("""
                INSERT INTO covid19.census_total (state, population)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING;
            """, (row['State'], row['Population']))

        # Insert data into the census table
        for _, row in census.iterrows():
            cursor.execute("""
                INSERT INTO covid19.census (state, grouping, population)
                VALUES (%s, %s, %s)
                ON CONFLICT DO NOTHING;
            """, (row['State'], row['Grouping'], row['Population']))

        # Identify missing locations in `vaccinations_total`
        missing_locations = set(vaccinations_total['location']) - set(census['State'])

        # Insert missing locations into both `census` and `census_total` tables with default values
        for location in missing_locations:
            cursor.execute("""
                INSERT INTO covid19.census_total (state, population)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING;
            """, (location, 0))

            cursor.execute("""
                INSERT INTO covid19.census (state, grouping, population)
                VALUES (%s, %s, %s)
                ON CONFLICT DO NOTHING;
            """, (location, 'Unknown', 0))

        # Identify missing states in `covid_death_monthly` and `covid_death_total`
        missing_states_monthly = set(covid_death_monthly['State']) - set(census['State'])
        missing_states_total = set(covid_death_total['State']) - set(census['State'])

        # Combine all missing states into a single set
        missing_states = missing_states_monthly | missing_states_total

        # Insert missing states into both `census` and `census_total` tables with default values
        for state in missing_states:
            cursor.execute("""
                INSERT INTO covid19.census_total (state, population)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING;
            """, (state, 0))

            cursor.execute("""
                INSERT INTO covid19.census (state, grouping, population)
                VALUES (%s, %s, %s)
                ON CONFLICT DO NOTHING;
            """, (state, 'Unknown', 0))


        # Commit the transaction after all insertions
        connection.commit()

        # Insert data into the vaccinations_total table
        for _, row in vaccinations_total.iterrows():
            cursor.execute("""
                INSERT INTO covid19.vaccinations_total (location, total_vaccinations, total_distributed, people_vaccinated, people_fully_vaccinated)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING;
            """, (row['location'], row['total_vaccinations'], row['total_distributed'], row['people_vaccinated'], row['people_fully_vaccinated']))
        connection.commit()

        # Insert data into the vaccination_daily table
        for _, row in vaccination_daily.iterrows():
            cursor.execute("""
                INSERT INTO covid19.vaccination_daily (day, month, location, daily_vaccinations, daily_vaccinations_per_million, people_vaccinated, share_doses_used)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING;
            """, (row['day'], row['month'], row['location'], row['daily_vaccinations'], row['daily_vaccinations_per_million'], row['people_vaccinated'], row['share_doses_used']))
        connection.commit()

        # Insert data into the covid_death_monthly table
        for _, row in covid_death_monthly.iterrows():
            cursor.execute("""
                INSERT INTO covid19.covid_death_monthly (month, State, Sex, "Age Group", "COVID-19 Deaths")
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING;
            """, (row['Month'], row['State'], row['Sex'], row['Age Group'], row['COVID-19 Deaths']))
        connection.commit()

        # Insert data into the covid_death_total table
        for _, row in covid_death_total.iterrows():
            cursor.execute("""
                INSERT INTO covid19.covid_death_total (State, Sex, "Age Group", "COVID-19 Deaths")
                VALUES (%s, %s, %s, %s)
                ON CONFLICT DO NOTHING;
            """, (row['State'], row['Sex'], row['Age Group'], row['COVID-19 Deaths']))
        connection.commit()

        # Close the cursor and connection
        cursor.close()
        connection.close()
    
    create_database = PythonOperator(
        task_id='create_db',
        python_callable=create_db,
    )

    load_vaccination_data = PythonOperator(
        task_id='load_vaccination_data',
        python_callable=fetch_vaccination_data
    )

    load_death_data = PythonOperator(
        task_id='load_death_data',
        python_callable=fetch_death_data
    )

    load_census_data = PythonOperator(
        task_id='load_census_data',
        python_callable=fetch_census_data
    )

    clean_census = PythonOperator(
        task_id='clean_census_data',
        python_callable=lambda: clean_census_data(fetch_census_data())
    )

    clean_vaccination = PythonOperator(
        task_id='clean_vaccination_data',
        python_callable=lambda: clean_vaccination_data(fetch_vaccination_data())[0]
    )

    clean_death = PythonOperator(
        task_id='clean_death_data',
        python_callable=lambda: clean_death_data(fetch_death_data())[0]
    )

    insert_data_task = PythonOperator(
        task_id='insert_data',
        python_callable=insert_data,
        execution_timeout=timedelta(minutes=10)
    )

    end = DummyOperator(task_id='end')

    create_database >> [load_vaccination_data, load_death_data, load_census_data]
    [load_vaccination_data >> clean_vaccination, load_death_data >> clean_death, load_census_data >> clean_census] >> insert_data_task >> end
