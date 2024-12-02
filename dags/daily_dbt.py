from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.models import Variable

from datetime import datetime, timedelta


with DAG("DAG_daily_dbt", start_date=datetime(2021, 1, 1), schedule_interval="30 2 * * *", catchup=False) as dag:
    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command='dbt run --project-dir=/home/airflow/dbt/daily ',
        email_on_failure=True,
        execution_timeout=timedelta(seconds=3600),
        email=Variable.get("mail_zulip"),
        dag=dag
    )

    dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command='dbt test --project-dir=/home/airflow/dbt/daily',
        email_on_failure=True,
        email=Variable.get("mail_zulip"),
        dag=dag
    )

    dbt_run >> dbt_test
