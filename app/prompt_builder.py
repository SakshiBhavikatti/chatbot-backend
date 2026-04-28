def build_faq_prompt(user_msg, faq):
    return f"""
You are a helpful support assistant.

User question:
{user_msg}

Relevant FAQ:
Question: {faq.question}
Answer: {faq.answer}

Use the FAQ context and generate a clear helpful answer.
"""

def build_direct_prompt(user_msg):
    return f"""
You are a helpful support assistant.

Answer this user query clearly and professionally:

{user_msg}
"""