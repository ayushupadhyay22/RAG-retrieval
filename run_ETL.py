from etl.transform_load import read_json, load_to_db, embed_table_rows, load_config
import yaml
import pandas as pd

config = load_config()
# Load data from JSON
df = read_json(config)
# Transform and load data into Postgres
load_to_db(df, config)
# Embed table rows
embed_table_rows(config)