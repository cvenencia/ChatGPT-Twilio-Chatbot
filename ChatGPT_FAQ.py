from os import getenv
from dotenv import load_dotenv
import openai
import tiktoken
import numpy as np
import pandas as pd

load_dotenv()

COMPLETIONS_MODEL = "text-davinci-003"
MAX_SECTION_LEN = 500
SEPARATOR = "\n* "
ENCODING = "cl100k_base"
encoding = tiktoken.get_encoding(ENCODING)
separator_len = len(encoding.encode(SEPARATOR))
df = pd.read_csv(
    'https://raw.githubusercontent.com/DAR-DatenanalyseRehberg/import/main/QatarWorldCup.csv')
df = df.set_index(["title", "heading"])

openai.api_key = getenv('CHATGPT_API_KEY')

EMBEDDING_MODEL = "text-embedding-ada-002"
COMPLETIONS_API_PARAMS = {
    "temperature": 0.0,
    "max_tokens": 300,
    "model": COMPLETIONS_MODEL,
}


def get_embedding(text: str, model: str = EMBEDDING_MODEL):
    result = openai.Embedding.create(
        model=model,
        input=text
    )
    return result["data"][0]["embedding"]


def compute_doc_embeddings(df):
    return {
        idx: get_embedding(r.content) for idx, r in df.iterrows()
    }


document_embeddings = compute_doc_embeddings(df)


def vector_similarity(x, y):
    return np.dot(np.array(x), np.array(y))


def order_document_sections_by_query_similarity(query, contexts):
    query_embedding = get_embedding(query)
    document_similarities = sorted([
        (vector_similarity(query_embedding, doc_embedding), doc_index) for doc_index, doc_embedding in contexts.items()
    ], reverse=True)
    return document_similarities


def construct_prompt(question: str, context_embeddings: dict, df: pd.DataFrame) -> str:
    most_relevant_document_sections = order_document_sections_by_query_similarity(
        question, context_embeddings)
    chosen_sections = []
    chosen_sections_len = 0
    chosen_sections_indexes = []

    for _, section_index in most_relevant_document_sections:
        # Add contexts until we run out of space.
        document_section = df.loc[section_index]

        chosen_sections_len += document_section.tokens + separator_len
        if chosen_sections_len > MAX_SECTION_LEN:
            break

        chosen_sections.append(
            SEPARATOR + document_section.content.replace("\n", " "))
        chosen_sections_indexes.append(str(section_index))

    header = """Answer the question as truthfully as possible using the provided context, and if the answer is not contained within the text below, say "I don't know."\n\nContext:\n"""

    return header + "".join(chosen_sections) + "\n\n Q: " + question + "\n A:"


def answer_query_with_context(query):
    prompt = construct_prompt(
        query,
        document_embeddings,
        df
    )

    response = openai.Completion.create(
        prompt=prompt,
        **COMPLETIONS_API_PARAMS
    )
    return response["choices"][0]["text"].strip(" \n")


if __name__ == "__main__":
    prompt = input('Question: ')
    print(answer_query_with_context(prompt))
