# IoT-system
## fake-agent 
This app emulates gathering data from IoT devices and sends it to the MQTT to visualize

## store-api
This app implements CRUD operations for IoT data to store in DB(Postgres)

## hub
This app implements caching strategy for IoT data

## edge
This app implements filtering functions for IoT data

## Running

Refer to `Makefile` for configuring environment

Development mode: use `Makefile`

Production mode: `docker compose up --build` in the docker dir within the app