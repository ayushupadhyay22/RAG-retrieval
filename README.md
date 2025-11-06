# RAG-retrieval
## Overview
This project implements an end-to-end ETL pipeline for the [TriviaQA of Joshi et al., (2017)](https://nlp.cs.washington.edu/triviaqa/) using Python and PostgreSQL.
The project also builds a RAG pipeline, to identify if a user answered a question correctly based on the Trivia data loaded

---

## About the data

[TriviaQA of Joshi et al., (2017)](https://nlp.cs.washington.edu/triviaqa/) is a reading comprehension dataset with over 650,000 question-answer-evidence sets. It includes 95,000 question-answer pairs created by trivia fans, with six evidence documents per question on average. TriviaQA stands out because it has complex questions, varied language between questions and evidence, and requires reasoning across multiple sentences to find answers.
We have used the **unfiltered-web-dev.json** for this project

---

## Project Structure

- **config/**: Configuration files (YAML)
- **etl/**: ETL modules (`transform_load.py`)
- **data/**: Raw JSON file (Sample data for the repo, download the "unfiltered-web-dev.json" from the website)
- **README.md**: Project documentation
- **requirements.txt**: Python dependencies
- **run_ETL.py**: ETL pipeline: loads data, stores in DB, generates embeddings
- **run_RAG.py**: Main RAG script: user Q&A, similarity search, answer evaluation
---

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd end_to_end_ETL
   ```

2. **Create and activate a virtual environment (optional but recommended)**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install other dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure your settings**
   - Edit `config/config.yaml` as needed (see below for details).

5. **Set up PostgreSQL locally**
   - See "Setting up PostgreSQL" below for instructions on installing and configuring PostgreSQL and creating a database.
     ```

---

## Running the Pipeline

You can run the ETL pipeline to load the raw data as below:

```bash
   python3 run_ETL.py
   ```
To run RAG pipeline you can run the command below

```bash
python3 run_RAG.py
```

---

## Configuration

Edit `config/config.yaml` to match your environment. Example:

```yaml
data_loc: "<local data path>"
api_key: "<OpenAI API key>"
postgres:
  user: "" #Add username
  password: ""         # Add your password if needed
  host: "localhost"
  port: 5432
  dbname: "" #database name of your postgres
  table: "" #table name 
```

**Field explanations:**
- `data_loc`: Local path for the dataset.
- `api_key`: API key for OpenAI model.
- `postgres`: Connection details for your local PostgreSQL instance.

---

## ETL Flow

- **Extract**: Loads the dataset from the provided location.
- **Transform**: Cleans and processes the raw data.
- **Load**: Loads the cleaned data into a PostgreSQL table.

Each step is implemented in the `etl/` directory as a separate Python module.

---

## Setting up PostgreSQL

1. **Install PostgreSQL** (if not already installed)
   - [Download pgAdmin](https://www.pgadmin.org/download/) for a GUI.

2. **Create a new server in pgAdmin**
   - Open pgAdmin.
   - Right-click "Servers" → Create → Server...
   - **General Tab**: Name your server (e.g., "Local Postgres").
   - **Connection Tab**:  
     - Host: `localhost`  
     - Port: `5432`  
     - Username: your local username  
     - Password: (leave blank if not set, or enter your password)

3. **Create a new database**
   - In pgAdmin, expand:  
     `Servers > Local Postgres > Databases`
   - Right-click "Databases" → Create → Database...
   - Enter a name (e.g., `your_db`) and owner (your username).
   - Click Save.

4. **Update `config/config.yaml`** with your database details.

---

## Setting up PostgreSQL as Vector database

1. **Clone the pgvector GitHub repository:** 
```bash
git clone https://github.com/pgvector/pgvector.git
```

2. **Build and install the pgvector extension:**
```bash
cd pgvector
make
sudo make install
```

3. **Connect to your PostgreSQL database:**

4. **After connecting to your PostgreSQL database, create the extension:**
```bash
CREATE EXTENSION vector;
```
---

## Troubleshooting

- **Database connection errors**: Double-check your `config.yaml` and that PostgreSQL is running.
- **Permission denied**: Ensure your user has the right permissions in PostgreSQL.

---
