def build_faq_prompt(user_description, faq):
    return f"""
You are a support assistant.

Customer issue:
{user_description}

Relevant FAQ:
Question: {faq.Question}
Answer: {faq.Answer}

Generate a helpful support response.
"""

def build_direct_prompt(user_description):
    return f"""
You are a support assistant.

Customer issue:
{user_description}

Provide a clear support response.
"""