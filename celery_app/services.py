import vertexai
from vertexai.generative_models import GenerativeModel
from google.api_core.exceptions import ResourceExhausted
from fastapi import HTTPException, status
import time

project_id = "cool-arch-410910"
vertexai.init(project=project_id, location="us-central1")

model = GenerativeModel(model_name="gemini-1.5-flash-001")


def is_text_toxic(text: str) -> bool:
    prompt = f"Analyze the following text in any language and return 'true' if the text could be offensive or contains harmful language in any way, otherwise return 'false':\n{text}"

    max_retries = 65
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            if response.candidates[0].content and response.candidates[0].content.parts:
                result_text = (
                    response.candidates[0].content.parts[0].text.strip().lower()
                )
                if "false" in result_text:
                    return False
            return True
        except ResourceExhausted as e:
            if attempt < max_retries - 1:
                time.sleep(1)
            else:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Quota exceeded. Please try again later.",
                )


def generate_auto_response(text: str) -> str:
    prompt = f"""
    Generate a polite and relevant response to the following comment as if a person is responding. If the comment is personal, provide the most popular or general response. Keep the response 2 or 3 sentences:
    
    Comment: {text}
    """
    max_retries = 61
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            if response.candidates[0].content and response.candidates[0].content.parts:
                return response.candidates[0].content.parts[0].text.strip()
        except ResourceExhausted as e:
            if attempt < max_retries - 1:
                time.sleep(1)
            else:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Quota exceeded. Please try again later.",
                )
