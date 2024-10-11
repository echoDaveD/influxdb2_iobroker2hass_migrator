import logging
import configparser
import sys
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


def delete_measurement(client, bucket, org, measurement, start_time, stop_time, logger):
    """Delete an specific measerment datapoints in provided timespan."""
    delete_api = client.delete_api()
    
    logger.info(f"delete measurement: {measurement} in timespan from {start_time} to {stop_time}")
    
    # deletze the specific measurement
    delete_api.delete(
        start=start_time,
        stop=stop_time,
        predicate=f'_measurement="{measurement}"',
        bucket=bucket,
        org=org
    )
    
    logger.info(f"Datapoints for {measurement} deleted.")


def main(bucket, measurement, start, stop):
    # load the Configurations files
    config = load_config('config.ini')

    # Setup logging
    logger = setup_logging(config['logging']['level'])

    # load InfluxDB-Configuration
    influxdb_url = config['influxdb']['url']
    influxdb_token = config['influxdb']['token']
    influxdb_org = config['influxdb']['org']
    influxdb_bucket = bucket

    # initilize InfluxDB Client
    client = InfluxDBClient(url=influxdb_url, token=influxdb_token, org=influxdb_org)

    # define the timespan
    start_time = start#"1970-01-01T00:00:00.000Z"  # oldes possible timestamp (Unix-Epoch)
    stop_time = stop #"2024-10-09T00:00:00.000Z"  # end ts you want (sample)

    # delete specific measurement
    delete_measurement(client, influxdb_bucket, influxdb_org, measurement, start_time, stop_time, logger)

    # close InfluxDB Client
    client.close()


# Python entrypoint
if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Please provide an measurment: python deleteMeasermentData.py <bucket_name> <measurement_name> <start_time> <stop_time>")
        sys.exit(1)
    
    # pass measurment as arg
    bucket_name = sys.argv[1]
    measurement_name = sys.argv[2]
    start_time = sys.argv[2]
    stop_time = sys.argv[2]
    main(bucket_name, measurement_name, start_time, stop_time)