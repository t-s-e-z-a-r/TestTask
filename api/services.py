import vertexai
from vertexai.generative_models import GenerativeModel
from google.api_core.exceptions import ResourceExhausted
from fastapi import HTTPException, status
import time

def is_text_toxic(text: str) -> bool:
    project_id = "cool-arch-410910"
    vertexai.init(project=project_id, location="us-central1")

    model = GenerativeModel(model_name="gemini-1.5-flash-001")
    prompt = f"Analyze the following text in any language and return 'true' if the text could be offensive or contains harmful language in any way, otherwise return 'false':\n{text}"

    max_retries = 5
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            if response.candidates[0].content and response.candidates[0].content.parts:
                result_text = response.candidates[0].content.parts[0].text.strip().lower()
                if "false" in result_text:
                    return False
            return True
        except ResourceExhausted as e:
            if attempt < max_retries - 1:
                time.sleep(3)
            else:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Quota exceeded. Please try again later.",
                )
