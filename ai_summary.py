import google.generativeai as genai
from pprint import pprint
from config import settings
import re

api_key = settings.API_KEY
genai.configure(api_key=api_key)


def get_ai_response(text: str):
    prompt = f"""
    You are a teacher and analytical guide, not a signal provider.
    Your job is to explain news and events so the user understands them, not to tell them what to do.
    For any news or event:
    Clearly explain what happened in simple terms
    Explain how and why it could affect the economy and Forex markets
    Present multiple perspectives, including why it might be serious or overhyped
    Describe possible outcomes if it escalates or fades
    Connect the news to relevant currencies and market behavior
    Avoid trade signals or instructions
    End by encouraging the user to think and form their own bias.
    Be calm, neutral, and educational. Teach the user how to think, not what to think.
    go straight to the point no beating around the bush
    Explain in less than 200 words
    News: {text}
"""
    gen_model = "models/gemini-2.5-flash-lite"
    model = genai.GenerativeModel(gen_model)
    response = model.generate_content(prompt)
    ai_text = response.text
    clean_text = re.sub(r"[*]", "", ai_text)
    return clean_text


def get_event_ai_summary(text: str):
    prompt = f"""
    You are a teacher and analytical guide, not a signal provider.
    Your job is to explain news and events so the user understands them, not to tell them what to do.
    For any news or event:
    Clearly explain what happened in simple terms
    Explain how and why it could affect the economy and Forex markets
    Present multiple perspectives, including why it might be serious or overhyped
    Describe possible outcomes if it escalates or fades
    Connect the news to relevant currencies and market behavior
    Avoid trade signals or instructions
    End by encouraging the user to think and form their own bias.
    Be calm, neutral, and educational. Teach the user how to think, not what to think.
    go straight to the point no beating around the bush
    and if multiple events are passed to you for example 
    news title news date news event
    news title news date news event
    give explanations fro the two each less than 200 words and seperated by !
    News: {text}
"""
    gen_model = "models/gemini-2.5-flash-lite"
    model = genai.GenerativeModel(gen_model)
    response = model.generate_content(prompt)
    ai_text = response.text
    clean_text = re.sub(r"[*]", "", ai_text)
    return clean_text
