import logging
import pandas as pd
from sqlalchemy import create_engine
import yaml
import json
import logging
import psycopg2
from psycopg2.extras import execute_values
import openai

#load config data
def load_config():
    with open('/Users/ayushupadhyay/Documents/GitHub/RAG-RETRIEVAL/config/config.yaml') as f:
        return yaml.safe_load(f)

def read_json(config):
    path = config['data_loc']
    logging.info(f"Reading JSON data from {path}")
    with open(path, 'r') as f:
        data = json.load(f)
    # Extract the 'Data' list
    records = data["Data"]

    # Create a list of dicts containing only the fields you want
    rows = []
    for item in records:
        question = item["Question"]
        question_id = item["QuestionId"]
        question_source = item["QuestionSource"]
        answer_alias = item["Answer"]["Aliases"]
        normalized_alias = item["Answer"]["NormalizedAliases"]
        answer = item["Answer"]["Value"]

        rows.append({
            "Question": question,
            "QuestionId": question_id,
            "QuestionSource": question_source,
            "Answer": answer,
            "NormalizedAliases": normalized_alias,
            "Aliases": answer_alias,
            
        })

    # Convert to DataFrame
    df = pd.DataFrame(rows)
    return df

def load_to_db(df, config):
    pg = config['postgres']
    dbname = pg['dbname']
    user = pg['user']
    host = pg['host']
    port = pg['port']
    table = pg['table']

    logging.info(f"Inserting DataFrame into PostgreSQL table: {table}")

    try:
        # Establish connection (no password)
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            host=host,
            port=port
        )
        cursor = conn.cursor()

        # Dynamically build CREATE TABLE statement with all TEXT columns
        create_cols = ', '.join([f'"{col}" TEXT' for col in df.columns])
        create_query = f'CREATE TABLE IF NOT EXISTS "{table}" ({create_cols});'
        cursor.execute(create_query)

                # Build column string separately
        columns = ', '.join([f'"{col}"' for col in df.columns])

        # Safe insert query
        insert_query = f'INSERT INTO "{table}" ({columns}) VALUES %s'


        # Convert DataFrame to list of tuples
        data_tuples = [tuple(map(str, row)) for row in df.to_numpy()]

        # Use psycopg2.extras.execute_values for efficient bulk insert
        execute_values(cursor, insert_query, data_tuples)

        # Commit and close
        conn.commit()
        cursor.close()
        conn.close()

        logging.info(f"Successfully inserted {len(df)} rows into {table}")

    except Exception as e:
        logging.exception("Failed to load data to PostgreSQL via psycopg2")
        raise

def embed_table_rows(config):
    """Ensure embedding column exists, then generate and store embeddings for all rows missing them."""
    openai.api_key = config["api_key"]
    pg = config["postgres"]
    DB_CONN = (
        f"host={pg['host']} "
        f"port={pg['port']} "
        f"dbname={pg['dbname']} "
        f"user={pg['user']} "
        f"password={pg['password']}"
    )
    TABLE_NAME = pg["table"]

    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()

    # 1. Ensure embedding column exists
    cur.execute(f"""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = %s AND column_name = 'embedding';
    """, (TABLE_NAME,))
    if not cur.fetchone():
        # Add the embedding column if it doesn't exist
        cur.execute(f"ALTER TABLE {TABLE_NAME} ADD COLUMN embedding vector(1536);")
        conn.commit()

    # 2. Generate and store embeddings for rows missing them
    cur.execute(f"""SELECT "QuestionId", "Question" FROM {TABLE_NAME} WHERE embedding IS NULL;""")
    rows = cur.fetchall()
    for row_id, text in rows:
        print(row_id, text)
        response = openai.embeddings.create(
            input=text,
            model="text-embedding-ada-002"
        )
        embedding = response.data[0].embedding
        cur.execute(f"""UPDATE {TABLE_NAME} SET "embedding" = %s WHERE "QuestionId" = %s;""", (embedding, row_id))
        conn.commit()
    cur.close()
    conn.close()
