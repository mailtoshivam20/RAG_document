import os
import glob
from dotenv import load_dotenv
from pathlib import Path
import gradio as gr
from openai import OpenAI

load_dotenv(override=True)

MODEL = "gpt-4.1-nano"

openai = OpenAI()

knowledge = {}

LOG_FILE = "chat_logs.txt"


def save_log(user_input, ai_output):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"USER: {user_input}\n")
        f.write(f"AI: {ai_output}\n")
        f.write("-" * 80 + "\n")



# Load employee documents
filenames = glob.glob(
    r"D:\Shivam\Project\knowledge-base\employees\*"
)

for filename in filenames:
    name = Path(filename).stem.lower()

    with open(filename, "r", encoding="utf-8") as f:
        knowledge[name] = f.read()

print(knowledge.keys())



SYSTEM_PREFIX = """
You represent Insurellm, the Insurance Tech company.

You are an expert in answering questions about Insurellm, its employees and its products.

Answer the user's question using the provided context.

If the information is present in the context, give the answer directly.

If the information is not present in the context, say:
"I don't have that information in the provided documents."

Do not make up information.

Relevant context:
"""


def get_relevant_context_simple(message):

    message = message.lower()

    relevant_context = []

    for name, content in knowledge.items():

        name_words = name.split()

        if all(word in message for word in name_words):
            relevant_context.append(content)

    return relevant_context


def additional_context(message):

    relevant_context = get_relevant_context_simple(message)

    if not relevant_context:
        return "No relevant employee document was found."

    return (
        "The following employee document is relevant:\n\n"
        + "\n\n".join(relevant_context)
    )


def chat(message, history):

    context = additional_context(message)

    print("\nUSER:", message)
    print("\nRETRIEVED CONTEXT:")
    print(context)

    system_message = SYSTEM_PREFIX + context

    messages = [
        {"role": "system", "content": system_message}
    ]

    messages += history
    messages.append(
        {"role": "user", "content": message}
    )

    response = openai.chat.completions.create(
        model=MODEL,
        messages=messages
    )

    output = response.choices[0].message.content

    save_log(message, output)

    return output


gr.ChatInterface(chat).launch(inbrowser=True)