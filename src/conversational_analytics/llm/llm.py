from langchain_google_genai import ChatGoogleGenerativeAI, HarmBlockThreshold, HarmCategory
from conversational_analytics.config import get_settings

DEFAULT_SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
}


def get_llm(**kwargs) -> ChatGoogleGenerativeAI:
    """Returns a LangChain-compatible ChatGoogleGenerativeAI instance using Vertex AI with ADC."""
    cfg = get_settings()
    defaults = {
        "model": cfg.llm_model,
        "vertexai": True,
        "project": cfg.google_cloud_project,
        "location": cfg.llm_region,
        "temperature": cfg.llm_temperature,
        "max_output_tokens": cfg.llm_max_output_tokens,
        "top_p": cfg.llm_top_p,
        "safety_settings": DEFAULT_SAFETY_SETTINGS,
        "thinking_level": cfg.thinking_level,
        "include_thoughts": cfg.include_thoughts,
    }
    defaults.update(kwargs)
    return ChatGoogleGenerativeAI(**defaults)
