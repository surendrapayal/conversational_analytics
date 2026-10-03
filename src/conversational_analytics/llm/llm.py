"""LLM factory supporting multiple providers.

The provider is selected via the LLM_PROVIDER environment variable:
    - "vertexai" (default): Google Gemini via Vertex AI (ADC authentication)
    - "bedrock": AWS Bedrock via the Converse API

Both providers return a LangChain BaseChatModel, so callers can use the same
interface (`.invoke`, `.bind_tools`, etc.) regardless of the backend.
"""

import logging

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_google_genai import HarmBlockThreshold, HarmCategory

from conversational_analytics.config import get_settings

logger = logging.getLogger(__name__)

DEFAULT_SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
}


def _get_vertexai_llm(**kwargs) -> BaseChatModel:
    """Build a ChatGoogleGenerativeAI instance using Vertex AI with ADC."""
    from langchain_google_genai import ChatGoogleGenerativeAI

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


def _get_bedrock_llm(**kwargs) -> BaseChatModel:
    """Build a ChatBedrockConverse instance for AWS Bedrock.

    Authentication is handled by langchain-aws / boto3, which automatically
    reads the AWS_BEARER_TOKEN_BEDROCK environment variable (short-term Bedrock
    API key). Standard AWS credential chains are also supported.
    """
    from langchain_aws import ChatBedrockConverse

    cfg = get_settings()
    defaults = {
        "model": cfg.bedrock_model,
        "region_name": cfg.bedrock_region,
        "temperature": cfg.llm_temperature,
        "max_tokens": cfg.bedrock_max_tokens,
        "top_p": cfg.llm_top_p,
    }
    defaults.update(kwargs)
    return ChatBedrockConverse(**defaults)


_PROVIDERS = {
    "vertexai": _get_vertexai_llm,
    "bedrock": _get_bedrock_llm,
}


def get_llm(**kwargs) -> BaseChatModel:
    """Returns a LangChain chat model for the configured provider.

    Set LLM_PROVIDER=vertexai (default) or LLM_PROVIDER=bedrock in the environment.
    Any kwargs override the provider defaults.
    """
    cfg = get_settings()
    provider = cfg.llm_provider.lower()
    builder = _PROVIDERS.get(provider)
    if builder is None:
        raise ValueError(
            f"Unsupported LLM_PROVIDER '{cfg.llm_provider}'. "
            f"Expected one of: {', '.join(_PROVIDERS)}."
        )
    logger.debug("Building LLM via provider=%s", provider)
    return builder(**kwargs)
