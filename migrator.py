import logging
import configparser
import json
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS


def load_config(config_file):
    """Loads the Configuration from .ini-Datei."""
    config = configparser.ConfigParser()
    config.read(config_file)
    return config


def load_measurement_mapping(mapping_file):
    """Loads measurement mapping from JSON file."""
    with open(mapping_file, 'r') as f:
        return json.load(f)


def setup_logging(level):
    """logging configuration."""
    logging.basicConfig(level=level,
                        format='%(asctime)s %(message)s')
    logger = logging.getLogger(__name__)
    return logger


def migrate_measurement(query_api, write_api, influxdb_bucket_iobroker, influxdb_bucket_ha, influxdb_org, iobroker_measurement, ha_measurement, start_time, stop_time, logger):
    """migrate a single measurement from ioBroker to Home Assistant."""
    logger.info(f"migrate measurement: {iobroker_measurement} -> {ha_measurement}")
    parts = ha_measurement.split(".")
    domain = parts[0]
    entity_id = parts[1]

    # Query for the ioBroker measurement
    query = f'''
    from(bucket: "{influxdb_bucket_iobroker}")
    |> range(start: {start_time}, stop: {stop_time})
    |> filter(fn: (r) => r["_measurement"] == "{iobroker_measurement}")
    |> filter(fn: (r) => r["_field"] == "value")
    '''
    
    tables = query_api.query(query)
    
    counter = 0
    for table in tables:
        for record in table.records:
            if counter % 10000 == 0:
                logger.info(f"    -> processed datapoints: {counter}")
            
            # create the new datapoint for Home Assistant
            json_body = [
                {
                    "measurement": ha_measurement,
                    "tags": {
                        "entity_id": entity_id,
                        "domain": domain
                    },
                    "time": record["_time"],
                    "fields": {
                        #TODO persist your results from analysis
                        "value": record["_value"] / 1000  # Example: transfer Values from watts to kilowatts (hasss store sin different unit as iobroker)
                    }
                }
            ]
            
            # write to Home Assistant bucket 
            write_api.write(bucket=influxdb_bucket_ha, org=influxdb_org, record=json_body)
            counter += 1
    
    logger.info(f"Migration completed for {iobroker_measurement}. Datapoints: {counter}")


def main():
    # load the Configurations files
    config = load_config('config.ini')
    measurement_mapping = load_measurement_mapping('measurement_mapping.json')

    # Setup logging
    logger = setup_logging(config['logging']['level'])

    # load InfluxDB-Configuration
    influxdb_url = config['influxdb']['url']
    influxdb_token = config['influxdb']['token']
    influxdb_org = config['influxdb']['org']
    influxdb_bucket_iobroker = config['influxdb']['bucket_iobroker']
    influxdb_bucket_ha = config['influxdb']['bucket_ha']

    # get timespan from config
    start_time = config['time_range']['start']
    stop_time = config['time_range']['stop']

    # initilize InfluxDB Client
    client = InfluxDBClient(url=influxdb_url, token=influxdb_token, org=influxdb_org)
    query_api = client.query_api()
    write_api = client.write_api(write_options=SYNCHRONOUS)

    # Migrate all measurements from the mapping
    for iobroker_measurement, ha_measurement in measurement_mapping.items():
        migrate_measurement(
            query_api=query_api,
            write_api=write_api,
            influxdb_bucket_iobroker=influxdb_bucket_iobroker,
            influxdb_bucket_ha=influxdb_bucket_ha,
            influxdb_org=influxdb_org,
            iobroker_measurement=iobroker_measurement,
            ha_measurement=ha_measurement,
            start_time=start_time,
            stop_time=stop_time,
            logger=logger
        )

    logger.info("Migration of all Measurements completed!")


# Python entrypoint
if __name__ == "__main__":
    main()
