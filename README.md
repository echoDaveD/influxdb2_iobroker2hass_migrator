# influxdb2_iobroker2hass_migrator
This is a very simple script to migrate Datapoints from ioBroker bucket to a Home Assistant bucket.

The requierement for this is Influxdb v2.
The measurement naming in Home Assistant can variate it depends on `measurement_attr` attribute in the configuration.yaml.
This script is assuming you are using `measurement_attr: entity_id`. If your Configuration is different, feel free to use this as tamplate and modify this until it fit your purpose.

# Installtion
1. Install python and pip for your platform.
2. Install the requirements
    `pip install -r requirements.txt`

# Configuration
Create an `config.ini` file.
This file should be structured as followed:

```
[influxdb]
url = <influxdb2_host>:8086
token = <yout token>
org = <your orgnaisation>
bucket_iobroker = <iobroker bucket>
bucket_ha = <home assistant bucket>

[time_range]
start = <start timestamp your want to migrate from: 2024-05-01T00:00:00.000Z>
stop = <end timestamp your want to migrate to: 2024-10-06T19:00:59.974Z>

[logging]
level = INFO
```

# Analyse your Datapoints
First at all you should analyse your Datapoints structure.
This is very important because ioBroker and Home Assistant are logging very different, even the units can be different (watt <-> kilo watts for example)

To see the current structure just select the ioBroker measurement and then the Home Assistant measurement and compere those two.

For this purpose ist the `selectMeasurement.py` Script.

Just call it with:
```python
python selectMeaserment.py <bucket_name> <measurement_name>
```

# Migrate the Data Points
To Migrate the Datapoints it is important that the Home Assistant already created the measurement in influxdb2 for us, this script only copy the value datapoints from ioBroker to Home Asisstant format.

Ccreate the `measurement_mapping.json` with the Names of the Datapoints you want to migrate. All Datapoints in one run should have the same units/value structure.
```json
{
    "<iobroker_namingscheme>": "hass_namingscheme",
    "shelly.0.data.point.value": "sensor.shelly_data_point_value",
    "shelly.0.data.point.value2": "sensor.shelly_data_point_value2",
    "shelly.0.data.point.value3": "sensor.shelly_data_point_value3",
    "shelly.0.data.point.value4": "sensor.shelly_data_point_value4",
}
```

Then configure the timespan you want to migrate in the `config.ini`.
For test reasons i strongly recommend to use an very short timespan in the past where no data in target Home Assistant measurment exists, so you can better delete it from there if something is wrong. 
```
[time_range]
start = 2024-05-01T00:00:00.000Z
stop = 2024-10-06T19:00:59.974Z
```

**Attention!**
Your results from the analysis step should be persist in `migrate.py` just search for `#TODO` and change the next line so it fits your purpose. 
For exemple: Shelly Energy Datapoints are stored in watts in ioBroker and in kilo watts in Home Assistant so, you have to devide the ioBroker value by 1000 for Home Assistant.

```python
"value": record["_value"] / 1000  # Example: transfer Values from watts to kilowatts (hasss store sin different unit as iobroker)
```

To run the migrate just execute the `migrator.py`

```python
python migrator.py
```

# Delete Datapoints
It is very possible that use mess up within the first tries, because it happend to me i wrote the delete script `deleteMeasermentData.py`. Thats why it is recommendet to migrate short timespan for test reasons, so you can better delete it in case you messed it up.

```cmd
python deleteMeasermentData.py <bucket_name> <measurement_name> <start_time> <stop_time>
```

Time format is `1970-01-01T00:00:00.000Z`.