import os
from typing import Optional

from openai import OpenAI


def get_chatgpt_client(api_key: Optional[str] = None) -> OpenAI:
    """Return an OpenAI client for ChatGPT (OpenAI endpoint)."""
    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    # Avoid sending mismatched organization headers unless explicitly requested.
    # Some environments set OPENAI_ORG_ID globally; if it doesn't match the key's org,
    # the API returns 401 (mismatched_organization). Default is to NOT send the header.
    force_org = os.getenv("OPENAI_FORCE_ORG_HEADER")
    org_id = os.getenv("OPENAI_ORG_ID")
    if force_org and org_id:
        return OpenAI(api_key=key, organization=org_id)
    # Temporarily suppress env-provided org header during client creation
    prev = None
    if org_id and not force_org:
        prev = os.environ.pop("OPENAI_ORG_ID", None)
    try:
        return OpenAI(api_key=key)
    finally:
        if prev is not None:
            os.environ["OPENAI_ORG_ID"] = prev


def get_deepseek_client(api_key: Optional[str] = None, base_url: Optional[str] = None) -> OpenAI:
    """Return an OpenAI-compatible client for DeepSeek (OpenAI SDK with custom base_url)."""
    key = api_key or os.getenv("DEEPSEEK_API_KEY")
    if not key:
        raise RuntimeError("DEEPSEEK_API_KEY is not set")
    url = base_url or os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    return OpenAI(api_key=key, base_url=url)


def get_ollama_client(base_url: Optional[str] = None, api_key: Optional[str] = None) -> OpenAI:
    """Return an OpenAI-compatible client for Ollama's local OpenAI API.

    Defaults: base_url=http://127.0.0.1:11434/v1, api_key='ollama' (unused)
    """
    url = base_url or os.getenv("OLLAMA_OPENAI_BASE_URL") or os.getenv("OLLAMA_BASE_URL") or "http://127.0.0.1:11434/v1"
    key = api_key or os.getenv("OLLAMA_API_KEY") or "ollama"
    return OpenAI(api_key=key, base_url=url)


def get_gemini_model(api_key: Optional[str] = None, model_name: Optional[str] = None):
    """Return a configured Google Generative AI (Gemini) model instance.

    Lazily imports google.generativeai to avoid hard dependency at import time.
    Environment variables:
    - GEMINI_API_KEY or GOOGLE_API_KEY
    - GEMINI_MODEL (default: 'gemini-1.5-flash')
    """
    key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY/GOOGLE_API_KEY is not set")
    try:
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            import google.generativeai as genai  # type: ignore
    except Exception as e:
        raise RuntimeError("google-generativeai package not installed. Install with: pip install google-generativeai") from e
    model = model_name or os.getenv("GEMINI_MODEL", "gemini-flash-latest")
    genai.configure(api_key=key, transport='rest')
    return genai.GenerativeModel(model)
