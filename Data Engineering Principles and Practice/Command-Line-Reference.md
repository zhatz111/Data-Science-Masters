## List of Useful Command Line Tools For Data Engineering

### Useful Postgre Commands
```Shell
psql -U jhu -d jhu # Log into specific postgre database with your username
psql -U jhu -d jhu -f "ZHatzenbeller-module6.sql" # Run an SQL file on the postgre Server in Powershell
psql -U jhu -d jhu < "ZHatzenbeller-module6.sql" # Run an SQL file on the postgre Server in CMD
```

### Useful Docker Commands
```Shell
docker ps -a #see a list of all containers
docker run jhu_docker-airflow-jupyter # run a specific container based on Image name
docker exec -it 63f7865e3d67 airflow webserver # start Airflow webserver
docker exec -it 63f7865e3d67 airflow scheduler # start Airflow scheduler
```