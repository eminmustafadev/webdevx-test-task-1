import os

from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GENAI_API_KEY"))

def generate_tasks(project_name: str, location: str) -> list:
    prompt = f"""
    Generate comma-separated construction tasks for building {project_name} in {location}
    No extra content, just comma-separated tasks.
    """
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=prompt
    )
    return [task.strip() for task in response.text.split(",")]
