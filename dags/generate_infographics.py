from airflow import DAG
from airflow.operators.python import PythonOperator, PythonVirtualenvOperator
from airflow.operators.bash import BashOperator
from airflow.decorators import task
from airflow.models import Variable
from airflow.exceptions import AirflowSkipException

import os
import paramiko
import stat
import logging
logger = logging.getLogger(__name__)

from datetime import datetime

SFTP_ROOT = Variable.get("sftp_root")
ALLOWED_DATA_FILENAMES = ["datos_entidades.csv", "datos_autonomas.csv"]

def get_sftp_client():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(Variable.get("sftp_host"), Variable.get("sftp_port"),
                Variable.get("sftp_user"), Variable.get("sftp_password"))
    return ssh.open_sftp()

def begin(ti, logical_date):
    dt = logical_date.in_tz("Europe/Madrid").format("YYYY-MM-DD_HH-mm-ss")
    tmp_dir = os.path.join(os.sep, "tmp", "infografias", dt)
    os.makedirs(tmp_dir, exist_ok=True)
    logger.info(f"Created tempdir at {tmp_dir}")
    ti.xcom_push(key="execution_datetime", value=dt)
    ti.xcom_push(key="tmp_dir", value=tmp_dir)
    sftp_client = get_sftp_client()

    files = sftp_client.listdir(SFTP_ROOT)
    data_files = [file for file in files if file in ALLOWED_DATA_FILENAMES]

    if not data_files:
        raise AirflowSkipException

    move_dirs_to_historic(sftp_client)

    for file in data_files:
        sftp_client.get(os.path.join(SFTP_ROOT, file), os.path.join(tmp_dir, file))

def move_dirs_to_historic(sftp_client):
    # Move previous runs directories to historic folder
    historic_dir = "historico"
    historic_dir_path = os.path.join(SFTP_ROOT, historic_dir)
    try:
        sftp_client.stat(historic_dir_path)
    except FileNotFoundError:
        # Create dir if not exists
        sftp_client.mkdir(historic_dir_path)

    for filename in sftp_client.listdir(SFTP_ROOT):
        logger.info(f"Trying to move '{filename}' to historic dir.")
        file_abs_path = os.path.join(SFTP_ROOT, filename)
        if stat.S_ISDIR(sftp_client.stat(file_abs_path).st_mode) and filename != historic_dir:
            # Move all directories inside the historic_dir
            logger.info(f"Moving directory {filename} to directory '{historic_dir}'")
            sftp_client.rename(file_abs_path, os.path.join(historic_dir_path, filename))

def geninfo(tmp_dir_name, allowed_data_filenames):
    # Running inside virtualenv.
    import os
    from airflow.models import Variable

    selenium_host = Variable.get("selenium_host")
    selenium_port = Variable.get("selenium_port")

    from geninfografia import generar_infografias
    for file in os.listdir(tmp_dir_name):
        if file in allowed_data_filenames:
            generar_infografias.run(os.path.join(tmp_dir_name, file), tmp_dir_name, regenerate=True, selenium_host=selenium_host, selenium_port=selenium_port)

def end(ti):
    execution_datetime = ti.xcom_pull(key="execution_datetime")
    execution_dir = os.path.join(SFTP_ROOT, execution_datetime)
    sftp_client = get_sftp_client()
    sftp_client.mkdir(execution_dir)

    tmp_dir = ti.xcom_pull(key="tmp_dir")
    for (root, dirs, files) in os.walk(tmp_dir, topdown=True):
        parent_dir = os.path.join(execution_dir, os.path.relpath(root, tmp_dir))
        for dir in dirs:
            logger.info(f"Creating directory at [{os.path.join(parent_dir, dir)}]")
            sftp_client.mkdir(os.path.join(parent_dir, dir))

        for file in files:
            local_path = os.path.join(root, file)
            remote_path = os.path.join(parent_dir, file)
            logger.info(f"Sending file from [{local_path}] to [{remote_path}]")
            sftp_client.put(local_path, remote_path)

    # Cleanup
    cleanup(sftp_client, SFTP_ROOT)

def cleanup(sftp_client, remote_root):
    # Delete root .csv files. As they have been moved to the specific execution directory
    for file in sftp_client.listdir(remote_root):
        extension = file.split(".")[-1]
        if extension == "csv":
            sftp_client.remove(os.path.join(remote_root, file))


with DAG("generate_infographics",
         start_date=datetime(2021, 1, 1),
         schedule_interval="0 6 * * *",
         catchup=False) as dag:

    begin = PythonOperator(
        task_id="begin",
        python_callable=begin,
        email_on_failure=True,
        email=Variable.get("mail_zulip"),
    )

    generar_infografias = PythonVirtualenvOperator(
        task_id="generar_infografias",
        python_callable=geninfo,
        op_kwargs = {
            "tmp_dir_name": "{{ ti.xcom_pull(key='tmp_dir') }}",
            "allowed_data_filenames": ALLOWED_DATA_FILENAMES
        },
        requirements=(lambda: open("/opt/airflow/dags/geninfografia/requirements.txt").readlines())(),
        email_on_failure=True,
        email=Variable.get("mail_zulip"),
    )

    end = PythonOperator(
        task_id="end",
        python_callable=end,
        email_on_failure=True,
        email=Variable.get("mail_zulip"),
    )

    begin >> generar_infografias >> end

