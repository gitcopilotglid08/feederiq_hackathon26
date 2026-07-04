"""
LLM client for FeederIQ agents via AWS Bedrock.
Each agent uses this to reason about results and generate human-readable outputs.

Setup:
  1. pip install boto3
  2. Configure AWS credentials: aws configure (or set AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION)
  3. Ensure Bedrock model access is enabled in your AWS account

If Bedrock is unavailable, agents fall back to template-based outputs (no crash).
"""
import json
import os
import logging

logger = logging.getLogger(__name__)

# Default model - can be overridden via environment variable
BEDROCK_MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0")
BEDROCK_REGION = os.environ.get("AWS_DEFAULT_REGION", os.environ.get("AWS_REGION", "us-east-1"))


def get_bedrock_client():
    """Get Bedrock runtime client. Returns None if credentials unavailable."""
    try:
        import boto3
        client = boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)
        return client
    except Exception as e:
        logger.warning(f"Bedrock client unavailable: {e}")
        return None


def invoke_llm(system_prompt: str, user_message: str, max_tokens: int = 2000) -> str:
    """
    Invoke Bedrock LLM with system prompt and user message.
    Returns the LLM response text, or empty string if unavailable.
    """
    client = get_bedrock_client()
    if client is None:
        return ""

    try:
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_message}],
            "temperature": 0.3,
        })

        response = client.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            contentType="application/json",
            accept="application/json",
            body=body,
        )

        result = json.loads(response["body"].read())
        return result["content"][0]["text"]

    except Exception as e:
        logger.warning(f"Bedrock invocation failed: {e}")
        return ""


def is_llm_available() -> bool:
    """Check if LLM is configured and accessible."""
    client = get_bedrock_client()
    if client is None:
        return False
    try:
        # Quick check - list models (lightweight call)
        import boto3
        bedrock = boto3.client("bedrock", region_name=BEDROCK_REGION)
        bedrock.list_foundation_models(maxResults=1)
        return True
    except Exception:
        return False
