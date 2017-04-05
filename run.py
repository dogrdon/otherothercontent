#!/usr/bin/env python
# -*- coding: utf-8 -*-

# import the main script
from theothercontent import theothercontent as toc


# airflow imports
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

default_args = {
	'owner':'airflow',
	'depends_on_past': True,
	'start_date': datetime.now(),
	'email':['drew@subtxt.in'],
	'email_on_failure': True,
	'email_on_retry': False,
	'retries': 2,
	'retry_delay': timedelta(minutes=10)
}

dag = DAG('run', default_args=default_args)

t1 = PythonOperator(
	task_id='get_articles',
	python_callable=toc.getArticles,
	dag=dag
	)

# t2

# t3

# t4

# t5