from etl.transform_load import read_json, load_to_db, embed_table_rows, load_config
import yaml
import pandas as pd



config = load_config()
df = read_json(config)
load_to_db(df, config)
embed_table_rows(config)