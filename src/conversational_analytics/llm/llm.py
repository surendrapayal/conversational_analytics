"""LLM factory supporting multiple providers.

The provider is selected via the LLM_PROVIDER environment variable:
    - "vertexai" (default): Google Gemini via Vertex AI (ADC authentication)
    - "bedrock": AWS Bedrock via the Converse API

Both providers return a LangChain BaseChatModel, so callers can use the same
interface (`.invoke`, `.bind_tools`, etc.) regardless of the backend.
"""

import logging
import os

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


def _resolve(settings_value: str, *env_vars: str) -> str | None:
    """Resolve a config value: use the .env/settings value if set, else fall
    back to the first non-empty shell environment variable. Returns None if
    nothing is set, so the caller can defer to boto3's default resolution.
    """
    if settings_value:
        return settings_value
    for name in env_vars:
        val = os.environ.get(name, "").strip()
        if val:
            return val
    return None


def _get_bedrock_llm(**kwargs) -> BaseChatModel:
    """Build a ChatBedrockConverse instance for AWS Bedrock.

    Credential resolution is delegated to boto3's standard chain. This supports:
      - AWS SSO:  `aws sso login --profile <name>` + AWS_PROFILE (and AWS_REGION)
      - API key:  AWS_BEARER_TOKEN_BEDROCK (short-term Bedrock API key)
      - Standard: AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY

    For profile and region, values are taken from .env first, then from the shell
    environment the user set (e.g. `$env:AWS_PROFILE = "my-profile"`). If neither
    is set, the parameter is omitted so boto3 applies its own defaults.
    """
    from langchain_aws import ChatBedrockConverse

    cfg = get_settings()

    profile = _resolve(cfg.aws_profile, "AWS_PROFILE")
    region = _resolve(cfg.aws_region, "AWS_REGION", "AWS_DEFAULT_REGION")
    model_id = _resolve(cfg.bedrock_model_id, "BEDROCK_MODEL_ID")

    if not model_id:
        raise ValueError(
            "No Bedrock model configured. Set BEDROCK_MODEL_ID in .env or the "
            "environment (e.g. $env:BEDROCK_MODEL_ID = \"anthropic.claude-3-haiku-20240307-v1:0\")."
        )

    defaults = {
        "model": model_id,
        "temperature": cfg.llm_temperature,
        "max_tokens": cfg.bedrock_max_tokens,
        "top_p": cfg.llm_top_p,
    }
    # Only pass these when known, otherwise let boto3 resolve from its default chain.
    if region:
        defaults["region_name"] = region
    if profile:
        defaults["credentials_profile_name"] = profile

    # If an SSO profile is requested but a Bedrock API key is also present,
    # langchain-aws prefers the API key and silently ignores the profile.
    if profile and os.environ.get("AWS_BEARER_TOKEN_BEDROCK", "").strip():
        logger.warning(
            "AWS_PROFILE '%s' is set but AWS_BEARER_TOKEN_BEDROCK is also present; "
            "langchain-aws will use the API key and ignore the SSO profile. "
            "Unset AWS_BEARER_TOKEN_BEDROCK to authenticate via SSO.",
            profile,
        )

    logger.debug(
        "Bedrock config: model=%s region=%s profile=%s",
        model_id, region or "(boto3 default)", profile or "(boto3 default)",
    )

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
