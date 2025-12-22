import logging
from datetime import date, timedelta
from decimal import *

import pendulum
from airflow.sdk import dag, task, Param
from airflow.exceptions import AirflowException
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator, SQLInsertRowsOperator
from airflow.providers.http.operators.http import HttpOperator
from airflow.providers.standard.operators.python import PythonOperator


@dag(
    dag_id="process_currency_exchange_rates",
    default_args={
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
    },
    schedule="0 2 * * 5",
    start_date=pendulum.datetime(2025, 12, 20, tz="UTC"),
    catchup=False,
    params={
        "base_currency": Param("EUR", type="string", enum=["EUR", "USD"]),
        "exchange_date": Param(f"{date.today() - timedelta(days=1)}", type="string", format="date")
    }
)
def process_currency_exchange_rates():

    @task(retries=0)
    def get_previous_day(**kwargs):
        exchange_date = date.fromisoformat(kwargs["params"]["exchange_date"])
        if exchange_date > date.today():
            raise AirflowException("Parameter 'exchange_date' must not be a future date")
        return str(exchange_date - timedelta(days=1))

    previous_day = get_previous_day()

    create_table = SQLExecuteQueryOperator(
        task_id="create_table",
        conn_id="postgres_db",
        sql="sql/create_table.sql"
    )

    fetch_exchange_rates = HttpOperator(
        task_id="fetch_exchange_rates",
        http_conn_id="frankfurter_api",
        method="GET",
        endpoint="{{ params.exchange_date }}",
        data={"base": "{{ params.base_currency }}"},
        response_filter=lambda response: response.json()["rates"]
    )

    get_previous_rates = HttpOperator(
        task_id="get_previous_rates",
        http_conn_id="frankfurter_api",
        method="GET",
        endpoint=previous_day,
        data={"base": "{{ params.base_currency }}"},
        response_filter=lambda response: response.json()["rates"]
    )

    @task
    def calculate_percentage_change(**kwargs):
        logger = logging.getLogger("airflow.task")
        params = kwargs["params"]
        base_currency = params["base_currency"]
        exchange_date = params["exchange_date"]
        logger.info("Base currency: %s", base_currency)
        logger.info("Exchange date: %s", exchange_date)
        ti = kwargs["ti"]
        rates = ti.xcom_pull(task_ids="fetch_exchange_rates")
        previous_rates = ti.xcom_pull(task_ids="get_previous_rates")
        rows = []
        for currency, rate in previous_rates.items():
            if currency not in rates:
                logger.warning(
                    "Latest exchange rate for currency %s is missing. Defaulting to previous exchange rate.",
                    currency
                )
                rates[currency] = rate
        getcontext().prec = 4
        for currency, rate in rates.items():
            if currency not in previous_rates:
                logger.warning(
                    "Previous exchange rate for currency %s is missing. Defaulting to latest exchange rate.",
                    currency
                )
                previous_rates[currency] = rate
            logger.info("Calculating percentage change for currency: %s", currency)
            logger.info("Exchange rate: %s", rate)
            previous_rate = Decimal(str(previous_rates[currency]))
            logger.info("Previous exchange rate: %s", previous_rate)
            diff = Decimal(str(rate)) - previous_rate
            percentage_change = diff / previous_rate * 100
            logger.info("Difference: %s", diff)
            logger.info("Percentage change: %s", percentage_change)
            rows.append((base_currency, currency, exchange_date, rate, previous_rate, percentage_change))
        return rows

    results = calculate_percentage_change()

    save_results = SQLInsertRowsOperator(
        task_id="save_results",
        table_name="public.exchange_rates",
        conn_id="postgres_db",
        columns=[
            "base_currency",
            "relative_currency",
            "exchange_date",
            "exchange_rate",
            "previous_exchange_rate",
            "percentage_change"
        ],
        rows=results,
        insert_args={
            "executemany": True,
            "replace": True,
            "replace_index": ["base_currency", "relative_currency", "exchange_date"],
        }
    )

    previous_day >> create_table >> [fetch_exchange_rates, get_previous_rates] >> results >> save_results


process_currency_exchange_rates()
