import re

def is_question(message):
    return re.search(r'\?', message) or re.search(r'\b(what|when|how|why|who|where)\b', message, re.IGNORECASE)

def is_addressed_to_author(message, author_name):
    return re.search(fr'\b{author_name}\b', message, re.IGNORECASE)

def generate_response(message, author_name):
    if is_question(message) and is_addressed_to_author(message, author_name):
        return "I saw your question and will get back to you as soon as I can."
    else:
        return "Thank you for your comment!"
