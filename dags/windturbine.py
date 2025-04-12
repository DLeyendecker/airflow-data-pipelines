from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.email import EmailOperator
from airflow.sensors.filesystem import FileSensor
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.models import Variable
from airflow.utils.task_group import TaskGroup
from datetime import datetime, timedelta
import json
import os

default_args = {
    'depends_on_past': False,
    'email': ['aws@evoluth.com.br'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(seconds=10)
}

with DAG(
    'windturbine',
    description='Dados da Turbina',
    schedule_interval=None,
    start_date=datetime(2023, 3, 5),
    catchup=False,
    default_args=default_args,
    default_view='graph',
    doc_md="## Dag para registrar dados de turbina eólica"
) as dag:

    file_sensor_task = FileSensor(
        task_id='file_sensor_task',
        filepath=Variable.get('path_file'),
        fs_conn_id='fs_default',
        poke_interval=10
    )

    def process_file(**kwargs):
        with open(Variable.get('path_file')) as f:
            data = json.load(f)
            kwargs['ti'].xcom_push(key='idtemp', value=data['idtemp'])
            kwargs['ti'].xcom_push(key='powerfactor', value=data['powerfactor'])
            kwargs['ti'].xcom_push(key='hydraulicpressure', value=data['hydraulicpressure'])
            kwargs['ti'].xcom_push(key='temperature', value=data['temperature'])
            kwargs['ti'].xcom_push(key='timestamp', value=data['timestamp'])
        os.remove(Variable.get('path_file'))

    get_data = PythonOperator(
        task_id='get_data',
        python_callable=process_file
    )

    # GROUP 1: Checagem de Temperatura
    with TaskGroup("group_check_temp", tooltip="Verifica Temperatura") as group_check_temp:

        def avalia_temp(**context):
            temp = float(context['ti'].xcom_pull(task_ids='get_data', key='temperature'))
            if temp >= 24:
                return 'group_check_temp.send_email_alert'
            else:
                return 'group_check_temp.send_email_normal'

        check_temp_branch = BranchPythonOperator(
            task_id='check_temp_branch',
            python_callable=avalia_temp
        )

        send_email_alert = EmailOperator(
            task_id='send_email_alert',
            to='d.leyendecker@ymail.com',
            subject='Alerta de Temperatura - Airflow',
            html_content='<h3>Temperatura acima do limite.</h3><p>Dag: windturbine</p>'
        )

        send_email_normal = EmailOperator(
            task_id='send_email_normal',
            to='d.leyendecker@ymail.com',
            subject='Temperatura Normal - Airflow',
            html_content='<h3>Temperatura dentro do esperado.</h3><p>Dag: windturbine</p>'
        )

        check_temp_branch >> [send_email_alert, send_email_normal]

    # GROUP 2: Banco de Dados
    with TaskGroup("group_database", tooltip="Processa e grava dados") as group_database:

        create_table = PostgresOperator(
            task_id="create_table",
            postgres_conn_id='postgres',
            sql='''
                CREATE TABLE IF NOT EXISTS sensors (
                    idtemp VARCHAR,
                    powerfactor VARCHAR,
                    hydraulicpressure VARCHAR,
                    temperature VARCHAR,
                    timestamp VARCHAR
                );
            '''
        )

        insert_data = PostgresOperator(
            task_id='insert_data',
            postgres_conn_id='postgres',
            parameters=(
                '{{ ti.xcom_pull(task_ids="get_data", key="idtemp") }}',
                '{{ ti.xcom_pull(task_ids="get_data", key="powerfactor") }}',
                '{{ ti.xcom_pull(task_ids="get_data", key="hydraulicpressure") }}',
                '{{ ti.xcom_pull(task_ids="get_data", key="temperature") }}',
                '{{ ti.xcom_pull(task_ids="get_data", key="timestamp") }}'
            ),
            sql='''
                INSERT INTO sensors (
                    idtemp, powerfactor, hydraulicpressure, temperature, timestamp
                ) VALUES (%s, %s, %s, %s, %s);
            '''
        )

        create_table >> insert_data

    # Dependências finais
    file_sensor_task >> get_data
    get_data >> group_check_temp
    get_data >> group_database
