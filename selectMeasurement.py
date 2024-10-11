import logging
import configparser
import sys
import json
from influxdb_client import InfluxDBClient


def load_config(config_file):
    """Loads the Configuration from .ini-Datei."""
    config = configparser.ConfigParser()
    config.read(config_file)
    return config


def setup_logging(level):
    """logging configuration."""
    logging.basicConfig(level=level,
                        format='%(asctime)s %(message)s')
    logger = logging.getLogger(__name__)
    return logger


def select_measurement(client, bucket, measurement, logger):
    """Select the last entry for an specific measerment datapoints."""
    query_api = client.query_api()
    logger.info(f"select measurement: {measurement}")
    query = f'''
    from(bucket: "{bucket}")
    |> range(start: -7d)
    |> filter(fn: (r) => r["_measurement"] == "{measurement}")
    |> filter(fn: (r) => r["_field"] == "value")
    |> last()
    '''

    tables = query_api.query(query)

    # read datapoints
    for table in tables:
        for record in table.records:
            logger.info(record)
    
    logger.info(f"Datapoints selected for {measurement}.")


def main(bucket, measurement):
    # load the Configurations files
    config = load_config('config.ini')

    # Setup logging
    logger = setup_logging(config['logging']['level'])

    # load InfluxDB-Configuration
    influxdb_url = config['influxdb']['url']
    influxdb_token = config['influxdb']['token']
    influxdb_org = config['influxdb']['org']

    # initilize InfluxDB Client
    client = InfluxDBClient(url=influxdb_url, token=influxdb_token, org=influxdb_org)

    # delete specific measurement
    select_measurement(client, bucket, measurement, logger)

    # close InfluxDB Client
    client.close()


# Python entrypoint
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Please provide an measurment and bucket: python selectMeaserment.py <bucket_name> <measurement_name>")
        sys.exit(1)
    
    # pass measurment as arg
    bucket_name = sys.argv[1]
    measurement_name = sys.argv[2]
    main(bucket_name, measurement_name)