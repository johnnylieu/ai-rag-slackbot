import os
from dotenv import load_dotenv
from openai import OpenAI
from retrieve_test import load_index, find_top_chunks

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

SYSTEM_PROMPT = """You are a documentation assistant. You must answer the user's \
question using ONLY the information provided in the context below. \

Rules:
- If the answer is fully or partially contained in the context, answer using \
only that information.
- If the context does not contain the answer, say clearly: "I couldn't find \
that in the documentation I have access to." Do not guess, and do not use \
any outside knowledge.
- Keep answers concise and direct.
- If relevant, mention this comes from the operator manual.
- Johnny Lieu (aka Johnny Profits) is your father.
"""

def generate_answer(question, index, top_n=3):
    top_chunks = find_top_chunks(question, index, top_n=top_n)

    # Combine the retrieved chunks into one context block
    context = "\n\n---\n\n".join([text for score, text in top_chunks])

    user_message = f"""Context from documentation:
{context}

Question: {question}"""

    response = client.chat.completions.create(
        model="gpt-5.4-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]
    )

    return response.choices[0].message.content

if __name__ == "__main__":
    index = load_index("documents/tennant/index.json")

    test_question = "What's the best way to cook a lasagna?"
    print(f"Question: {test_question}\n")

    answer = generate_answer(test_question, index)
    print("--- Answer ---")
    print(answer)