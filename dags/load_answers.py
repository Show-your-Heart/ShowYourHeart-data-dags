from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable

from datetime import datetime

from loadanswers import loadanswers

def load_answers():
    loadanswers.loadanswers(campaign = None)

with DAG("DAG_load_answers", start_date=datetime(2021, 1, 1), schedule_interval=None, catchup=False) as dag:
    la = PythonOperator(
        task_id="load_answers",
        python_callable=load_answers,
        email_on_failure=True,
        email=Variable.get("mail_zulip")
    )

    la
