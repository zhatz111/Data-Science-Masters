# MODULE 8 - 100 points total

import os
import json
from airflow import DAG
from airflow.operators.python_operator import PythonOperator, BranchPythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.utils.trigger_rule import TriggerRule
from datetime import datetime, timedelta, date

# define the default arguments
default_args = {
    'owner': 'data_engineer',
    'start_date': datetime(2023, 4, 6),
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

# define the DAG
with DAG('process_student_data', default_args=default_args, schedule_interval='@daily', catchup=False) as dag:

    def load_data():
        with open(os.path.join('/home/jhu/airflow/dags/data/input.json')) as f:
            data = json.load(f)
        f.close()
        return data

    def process_data():
        data = load_data()
        students = data['students']
        courses = data['courses']
        # Nothing required here for submission - this function is complete
 

    def check_weekday():
        #**context
        # execution_date = context['ds']
        
        # QUESTION #1 (20 points)
        # Extract the day (number) of the week
        weekday = date.today().weekday()

        if weekday < 5:  # weekday is 0-based, with 0=Monday and 4=Friday
            return 'store_data_weekday'
        else:
            return 'store_data_weekend'

    def store_data_weekday():
        data = load_data()
        students = data['students']
        courses = data['courses']

        # QUESTION #2 (20 points)
        # Loop through the students and find each course and description
        # Save this data to the 'data/weekday_data.txt' file as follows:
        # '<LASTNAME, FIRSTNAME> took <COURSE> (<COURSE_DESCRIPTION>) on a weekday'
        # Example: 'Mosko, Scott took ENG101 (Data Engineering) on a weekday'
        # 
        # Each entry should be on a new line
        # This function is only run on weekdays (due to the check_weekday function)
        course_list = []
        for student in students:
            first_name = student["name"].split()[0]
            last_name = student["name"].split()[1]
            for s_course in student["courses"]:
                descrip = ""
                for course in courses:
                    if s_course == course["name"]:
                        descrip = course["description"]
                course_str = f"{last_name}, {first_name} took {s_course} ({descrip}) on a weekday"
                course_list.append(course_str)
        
        with open('/home/jhu/airflow/dags/data/weekday_data.txt', 'w') as f:
            for line in course_list:
                f.write(f"{line}\n")

 

    def store_data_weekend():
        data = load_data()
        students = data['students']
        courses = data['courses']
        
        
        # QUESTION #3 (20 points)
        # Loop through the students and find each course and description
        # Save this data to the 'data/weekend_data.txt' file as follows:
        # '<LASTNAME, FIRSTNAME> took <COURSE> (<COURSE_DESCRIPTION>) on a weekend'
        # Example: 'Mosko, Scott took ENG101 (Data Engineering) on a weekend'
        # 
        # Each entry should be on a new line
        # This function is only run on weekends (due to the check_weekdend function)
        course_list = []
        for student in students:
            first_name = student["name"].split()[0]
            last_name = student["name"].split()[1]
            for s_course in student["courses"]:
                descrip = ""
                for course in courses:
                    if s_course == course["name"]:
                        descrip = course["description"]
                course_str = f"{last_name}, {first_name} took {s_course} ({descrip}) on a weekend"
                course_list.append(course_str)
        
        with open('/home/jhu/airflow/dags/data/weekend_data.txt', 'w') as f:
            for line in course_list:
                f.write(f"{line}\n")


    # QUESTION #4
    load_data_task = PythonOperator(
        task_id = "load_data",
        python_callable = load_data
    )
    process_data_task = PythonOperator(
        task_id = "process_data",
        python_callable = process_data
    )
    check_weekday_task = BranchPythonOperator(
        task_id = "check_weekday",
        python_callable = check_weekday
    )
    store_data_weekday_task = PythonOperator(
        task_id = "store_data_weekday",
        python_callable = store_data_weekday
    )
    store_data_weekend_task = PythonOperator(
        task_id = "store_data_weekend",
        python_callable = store_data_weekend
    )
    end_task = DummyOperator(
        task_id='end',
        trigger_rule=TriggerRule.ALL_DONE  # This allows the task to run even if one of the branches is skipped.
    )
        
        # TODO (10 points)
        # Note that end_task will be tricky. There is a way to make it complete even though
        # only one of the branches finishes successfully and the other is skipped. Normally
        # this would cause anything following the branch to be skipped.

    # QUESTION #5 (20 points)
    # Create the flow for the DAG to match the provided diagram.
    load_data_task >> process_data_task >> check_weekday_task >> [store_data_weekday_task, store_data_weekend_task]
    [store_data_weekday_task, store_data_weekend_task] >> end_task

    # PLEASE NOTE: See Instruction document for files to turn in.