# REST service for RDBMS

## Instructions to run
1. Install docker
2. Make sure you are in the main directory of the project
3. Open the terminal and run **docker-compose build**
4. Run **docker-compose up**
5. Make sure the DB is created and the admin is added. Make sure API is running (from the containers logs)
6. Access API on **localhost/docs** (It is on port 80, default for HTTP)
7. If you want to stop the containers, run **docker-compose down**

## Instructions to delete database (This will remove all data!)
1. Stop the docker containers using **docker-compose down -v** (the **-v** is vital to delete all volumes)
2. Navigate to REST-MySQL/mysql and run **rm -R data** to remove the created data by the database.
