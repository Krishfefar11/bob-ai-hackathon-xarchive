"""Thin wrapper around the IBM watsonx.ai foundation models SDK — optional, fails gracefully without credentials."""
import os

from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL = "ibm/granite-3-8b-instruct"


class WatsonxConfigError(RuntimeError):
    pass


class WatsonxClient:
    def __init__(self, model_id: str = DEFAULT_MODEL):
        api_key = os.getenv("WATSONX_API_KEY")
        project_id = os.getenv("WATSONX_PROJECT_ID")
        url = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")

        if not api_key or not project_id:
            raise WatsonxConfigError("WATSONX_API_KEY and WATSONX_PROJECT_ID must be set (see .env.example).")

        from ibm_watsonx_ai import Credentials
        from ibm_watsonx_ai.foundation_models import ModelInference

        self._model = ModelInference(
            model_id=model_id,
            credentials=Credentials(url=url, api_key=api_key),
            project_id=project_id,
        )

    def generate(self, prompt: str, max_new_tokens: int = 200) -> str:
        response = self._model.generate_text(
            prompt=prompt,
            params={"max_new_tokens": max_new_tokens, "temperature": 0.3},
        )
        return response.strip()
