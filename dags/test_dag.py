from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import os


def save_test_text():
    """10분마다 '테스트' 텍스트를 파일에 저장"""
    output_dir = '/opt/airflow/logs'
    output_file = os.path.join(output_dir, 'test_output.txt')

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message = f"[{timestamp}] 테스트\n"

    with open(output_file, 'a', encoding='utf-8') as f:
        f.write(message)

    print(f"테스트 텍스트 저장 완료: {message.strip()}")


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

with DAG(
    'test_every_10min',
    default_args=default_args,
    description='10분마다 테스트 텍스트를 저장하는 DAG',
    schedule='*/10 * * * *',  # 10분마다 실행
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=['test'],
) as dag:

    save_task = PythonOperator(
        task_id='save_test_text',
        python_callable=save_test_text,
    )
