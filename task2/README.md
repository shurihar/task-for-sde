# Task2
Airflow pipeline that performs a full ETL process for currency exchange rates.

## Requirements
- [Docker Desktop](https://docs.docker.com/get-started/get-docker/)

## Installation and use
Run database migrations and create the first user account:
```
docker compose up airflow-init
```

After initialization is complete, you should see a message like this:
```
airflow-init-1 exited with code 0
```

The account created has the login `airflow` and the password `airflow`.

Now you can start all services:
```
docker compose up -d
```

Check the condition of the containers and make sure that no containers are in an unhealthy condition:
```
$ docker ps
CONTAINER ID   IMAGE                  COMMAND                  CREATED        STATUS                 PORTS                                         NAMES
48b5f8230825   apache/airflow:3.1.5   "/usr/bin/dumb-init …"   18 hours ago   Up 4 hours (healthy)   8080/tcp                                      task2-airflow-worker-1
8cb7a9468252   postgres:16            "docker-entrypoint.s…"   18 hours ago   Up 4 hours (healthy)   0.0.0.0:5433->5432/tcp, [::]:5433->5432/tcp   task2-postgres-data-1
40f4b00c00da   apache/airflow:3.1.5   "/usr/bin/dumb-init …"   18 hours ago   Up 4 hours (healthy)   0.0.0.0:8080->8080/tcp, [::]:8080->8080/tcp   task2-airflow-apiserver-1
463c15f1ef58   apache/airflow:3.1.5   "/usr/bin/dumb-init …"   18 hours ago   Up 4 hours (healthy)   8080/tcp                                      task2-airflow-scheduler-1
7891f0c553bb   apache/airflow:3.1.5   "/usr/bin/dumb-init …"   18 hours ago   Up 4 hours (healthy)   8080/tcp                                      task2-airflow-triggerer-1
745c004ae49f   apache/airflow:3.1.5   "/usr/bin/dumb-init …"   18 hours ago   Up 4 hours (healthy)   8080/tcp                                      task2-airflow-dag-processor-1
385db682942a   postgres:16            "docker-entrypoint.s…"   18 hours ago   Up 4 hours (healthy)   5432/tcp                                      task2-postgres-1
0d83cb5756d5   redis:7.2-bookworm     "docker-entrypoint.s…"   18 hours ago   Up 4 hours (healthy)   6379/tcp                                      task2-redis-1
```

Import connections from the connections.json file:
```
docker exec task2-airflow-apiserver-1 airflow connections import --overwrite /opt/airflow/config/connections.json
```

Log in to the web interface at `http://localhost:8080`. 
The default account has the login `airflow` and the password `airflow`.

## Links
- [Running Airflow in Docker](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html)