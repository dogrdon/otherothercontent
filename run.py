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
	'email_on_retry': True,
	'retries': 3,
	'retry_delay': timedelta(minutes=8)
}

dag = DAG('run', default_args=default_args)

t1 = PythonOperator(
	task_id='get_articles',
	python_callable=toc.getArticles,
	dag=dag
	)

t2 = PythonOperator(
	task_id='enrich_targets',
	python_callable=toc.enrichTargets,
	params={'articleResults':None, 'targets':None}
	dag=dag
	)

t3 = PythonOperator(
	task_id='article_data',
	python_callable=toc.getArticleData,
	params={'enrichedTargets':None}
	dag=dag
	)


t4 = PythonOperator(
	task_id='clear_dupes',
	python_callable=toc.clearDupes,
	params={'contentResutls':None}
	dag=dag
	)


t5 = PythonOperator(
	task_id='download_images',
	python_callable=toc.downloadImages,
	params={'contentResutls':None}
	dag=dag
	)


t5 = PythonOperator(
	task_id='finalize_records',
	python_callable=toc.finalizeRecords,
	params={'withImages':None}
	dag=dag
	)



t2.set_upstream(t1)
t3.set_upstream(t2)
t4.set_upstream(t3)
t5.set_upstream(t4)