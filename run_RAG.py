import openai
import psycopg2
import yaml
from etl.transform_load import load_config

config = load_config()

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

# 1. Get question from user
user_question = input("Please enter your question: ")

# 2. Get answer from user
user_answer = input("Your answer: ")

# 3. Generate embedding for user's answer
response = openai.embeddings.create(
    input=user_question,
    model="text-embedding-ada-002"
)
question_embedding = response.data[0].embedding
embedding_str = str(question_embedding)

# 4. Similarity search using user's question embedding, retrieving question and answer columns
cur.execute(
    f"""
    SELECT "Question", "Answer" FROM {TABLE_NAME}
    ORDER BY embedding <-> %s
    LIMIT %s;
    """,
    (embedding_str, 3)
)
results = cur.fetchall()

# 5. Build context from similar questions and answers
context = ""
for idx, (q, a) in enumerate(results, 1):
    context += f"Similar QA Pair {idx}:\nQ: {q}\nA: {a}\n\n"

# 6. Ask GPT-4.1 to evaluate the user's answer
eval_prompt = (
    f"You are an expert evaluator. Here is a user's question, their answer, and some similar question-answer pairs from a database.\n\n"
    f"User's Question: {user_question}\n"
    f"User's Answer: {user_answer}\n\n"
    f"Similar QA Context:\n{context}"
    f"Is the user's answer correct for their question? Reply with 'Correct' or 'Incorrect' and a brief explanation based on the context provided."
)


eval_response = openai.chat.completions.create(
    model="gpt-4-1106-preview",
    messages=[{"role": "user", "content": eval_prompt}]
)
print("Evaluation Result:")
print(eval_response.choices[0].message.content)
# Clean up
cur.close()
conn.close()

