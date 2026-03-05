from django.conf import settings
from google import genai


def test_gemini():
    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Explain what Artificial Intelligence is in one sentence."
    )

    return response.text