from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.models import Variable

from datetime import datetime


with DAG("DAG_dynamic_packages_dbt", start_date=datetime(2021, 1, 1), schedule_interval=None, catchup=False) as dag:
    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command='dbt run --project-dir=/home/airflow/dbt/daily --select ' +
                     Variable.get("packages_dbt")+ ' '+Variable.get("full-refresh"),
        email_on_failure=True,
        email=Variable.get("mail_zulip"),
        dag=dag
    )

    dbt_run
