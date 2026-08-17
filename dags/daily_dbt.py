from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.models import Variable
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

from datetime import datetime, timedelta


with DAG("DAG_daily_dbt", start_date=datetime(2021, 1, 1), schedule_interval="30 2 * * *", catchup=False) as dag:
    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command='/home/airflow/projdbt/.venv/bin/dbt run --project-dir=/home/airflow/dbt/daily ',
        email_on_failure=True,
        execution_timeout=timedelta(seconds=3600),
        email=Variable.get("mail_zulip"),
        dag=dag
    )

    dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command='/home/airflow/projdbt/.venv/bin/dbt test --project-dir=/home/airflow/dbt/daily',
        email_on_failure=True,
        email=Variable.get("mail_zulip"),
        dag=dag
    )

    load_answers = TriggerDagRunOperator(
        task_id="load_answers",
        trigger_dag_id="DAG_load_answers",
        conf={"message": "Triggered DAG_load_answers"}
    )



    dbt_run >> dbt_test >> load_answers
