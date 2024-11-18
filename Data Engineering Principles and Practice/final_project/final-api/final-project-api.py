# Import necessary libraries
from flask import Flask, jsonify
import psycopg2
import pandas as pd

# Initialize a Flask application
app = Flask(__name__)

# Database connection parameters
DB_NAME = "final_db"
DB_USER = "group"
DB_PASS = "project"
DB_HOST = "host.docker.internal"
DB_PORT = "5432"

topics_data = {}

@app.route("/", methods=['GET', 'POST'])
def index():
    # Attempt-connect-the PostgreSQL database
    try:
        _ = psycopg2.connect(
            database=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
        )
        json_response = {
            "Connection": "Database connected successfully",
            "Host": DB_HOST,
            "DB Name": DB_NAME,
            "User": DB_USER,
            "Port": DB_PORT
        }
    except psycopg2.DatabaseError as e:
        json_response = {
            "Connection": "Database NOT connected successfully",
            "Host": DB_HOST,
            "DB Name": DB_NAME,
            "User": DB_USER,
            "Port": DB_PORT,
            "Error": str(e)
        }

    return jsonify(json_response)

# Route-check stored topic data in memory
@app.route("/api/check_data", methods=["GET"])
def check_data():

    try:
        conn = psycopg2.connect(
            database=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
        )
        # Define your queries
        queries = {
            "census": "SELECT * FROM covid19.census LIMIT 5;",
            "census_total": "SELECT * FROM covid19.census_total LIMIT 5;",
            "vaccinations_total": "SELECT * FROM covid19.vaccinations_total LIMIT 5;",
            "vaccination_daily": "SELECT * FROM covid19.vaccination_daily LIMIT 5;",
            "covid_death_monthly": "SELECT * FROM covid19.covid_death_monthly LIMIT 5;",
            "covid_death_total": "SELECT * FROM covid19.covid_death_total LIMIT 5;",
        }

        # Execute queries and collect results
        json_response = {}
        for key, query in queries.items():
            df = pd.read_sql_query(query, conn)
            json_response[key] = df.to_dict(orient="records")

        # # Optional: Serialize the response as JSON (for verification or further use)
        # json_response = json.dumps({"items": response}, ensure_ascii=False)

    except pd.errors.DatabaseError as e:
        json_response = {"Error": str(e)}

    return jsonify(json_response)

# Route-check stored topic data in memory
@app.route("/api/deaths_per_age_group", methods=["GET"])
def age_group_data():
    try:
        conn = psycopg2.connect(
            database=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
        )
        # Define your queries
        # small_query = "SELECT DISTINCT 'Age Group' FROM covid19.covid_death_total"
        # df_ages = pd.read_sql_query(small_query, conn)
        # print(df_ages)

        # Execute queries and collect results
        json_response = {}
        age_group = [
            "25-34 years",
            "35-44 years",
            "45-54 years",
            "65-74 years",
            "75-84 years",
        ]
        for i in age_group:
            main_query = f"""
            SELECT
                t1.state,
                SUM(t2."COVID-19 Deaths") AS total_deaths,
                SUM(t1.population) AS total_population,
                (SUM(t2."COVID-19 Deaths") * 1.0 / SUM(t1.population)) * 100 AS percentage
            FROM
                covid19.census t1
            JOIN
                covid19.covid_death_total t2
            ON
                t1.state = t2.state AND t1.grouping = t2."Age Group"
            WHERE
                t1.grouping = '{i}' AND t2.sex = 'All Sexes'
            GROUP BY
                t1.state,
                t1.grouping
            ORDER BY
                percentage DESC
            LIMIT 1;
            
            """
            df = pd.read_sql_query(main_query, conn)
            json_response[i] = df.to_dict(orient="records")

    except pd.errors.DatabaseError as e:
        json_response = {"Error": str(e)}

    return jsonify(json_response)


# Route-check stored topic data in memory
@app.route("/api/vaccine_ratio_death_rate", methods=["GET"])
def vaccine_ratio_death_rate():
    try:
        conn = psycopg2.connect(
            database=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
        )
        main_query = """
        WITH VaccinationData AS (
            SELECT
                location AS state,
                people_vaccinated
            FROM covid19.vaccinations_total
        ),
        PopulationData AS (
            SELECT
                state,
                population AS total_population
            FROM covid19.census_total
        ),
        CovidDeaths AS (
            SELECT
                state,
                SUM("COVID-19 Deaths") AS total_covid_deaths
            FROM covid19.covid_death_total
            GROUP BY state
        ),
        CalculatedData AS (
            SELECT
                v.state,
                v.people_vaccinated,
                p.total_population,
                COALESCE(cd.total_covid_deaths, 0) AS total_covid_deaths,
                CASE 
                    WHEN p.total_population > 0 THEN (v.people_vaccinated::FLOAT / p.total_population)
                    ELSE NULL
                END AS vaccination_to_population_ratio,
                CASE 
                    WHEN p.total_population > 0 THEN (COALESCE(cd.total_covid_deaths, 0)::FLOAT / p.total_population) * 100
                    ELSE NULL
                END AS death_rate
            FROM VaccinationData v
            INNER JOIN PopulationData p ON v.state = p.state
            LEFT JOIN CovidDeaths cd ON v.state = cd.state
        )
        SELECT
            state,
            vaccination_to_population_ratio,
            death_rate
        FROM CalculatedData
        WHERE vaccination_to_population_ratio IS NOT NULL
        AND death_rate IS NOT NULL
        ORDER BY vaccination_to_population_ratio DESC;
        
        """
        df = pd.read_sql_query(main_query, conn)
        json_response = df.to_dict(orient="records")

    except pd.errors.DatabaseError as e:
        json_response = {"Error": str(e)}

    return jsonify(json_response)

# Run the Flask application
if __name__ == "__main__":
    PORT = 8001
    app.run(host="0.0.0.0", port=PORT)
