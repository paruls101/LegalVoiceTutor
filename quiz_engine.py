import random
import json
import os
from openai import OpenAI
import streamlit as st

def get_client():
    api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)

class QuizEngine:
    def __init__(self):
        self.client = get_client()

    def generate_question(self, knowledge_base):
        """
        Selects a random item from the knowledge base and generates a question.
        """
        if not knowledge_base or not self.client:
            return None, None

        # Pick a random item (Case or Principle)
        item = random.choice(knowledge_base)
        
        # Determine question type based on available fields
        context = json.dumps(item)
        
        prompt = f"""
        You are a rigorous Oxford Law tutor. Based on the following legal note, generate a challenging oral exam question.
        
        The question should test ONE of the following:
        1. Recall of facts.
        2. Explanation of the ratio decidendi.
        3. Critical analysis of the decision.
        
        Keep the question concise (under 20 words) and direct, as if spoken in a tutorial.
        Do NOT include the answer.
        
        Context:
        {context}
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a demanding law tutor."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            question = response.choices[0].message.content
            return question, item
        except Exception as e:
            return f"Error generating question: {e}", None

    def evaluate_answer(self, question, user_answer, context_item):
        """
        Evaluates the user's answer against the context.
        """
        if not self.client:
            return "Error: No API Key"

        context_str = json.dumps(context_item)
        
        prompt = f"""
        You are an Oxford Law tutor evaluating a student's oral answer.
        
        Question: "{question}"
        Student's Answer: "{user_answer}"
        
        Source Material (Truth):
        {context_str}
        
        Task:
        1. Evaluate if the student is Correct, Partially Correct, or Incorrect.
        2. If Incorrect or Partial, explain specifically what they missed based ONLY on the Source Material (and general legal knowledge if the source is sparse).
        3. If Correct, briefly affirm and add a deeper insight or "plus" point.
        
        Tone: Encouraging but rigorous. Keep feedback under 100 words to maintain flow.
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful but rigorous tutor."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error evaluating answer: {e}"

