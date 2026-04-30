def build_faq_prompt(user_description, faq):
    return f"""
You are a support assistant.

Customer issue:
{user_description}

Relevant FAQ:
Question: {faq.Question}
Answer: {faq.Answer}

Instructions:
Answer ONLY using the FAQ answer above.
Do not use outside knowledge.
If the user asks only part of the FAQ, answer only that relevant part.
Rephrase only for clarity.
"""

def build_direct_prompt(user_description):
    return f"""
You are a support assistant.

Customer issue:
{user_description}

Provide a clear support response.
"""