"""
Quick test to verify Bedrock access using a short-term Bedrock API key.

Auth:
    boto3's bedrock-runtime client automatically uses the bearer token from the
    AWS_BEARER_TOKEN_BEDROCK environment variable. No access key / secret needed.

Prereqs:
    - AWS_BEARER_TOKEN_BEDROCK must be set in THIS terminal's environment.
      (setx sets it for new terminals only; for the current PowerShell session use:
       $env:AWS_BEARER_TOKEN_BEDROCK = "YOUR_KEY")
    - boto3 installed:  uv add boto3   (or)  pip install boto3

Run:
    uv run python temp.py
"""

import os
import sys
import json

import boto3
from botocore.exceptions import ClientError, BotoCoreError

# Region that hosts the model. Change if your access is in another region.
REGION = os.environ.get("AWS_REGION", "us-east-1")

# A widely-available, cheap model for a connectivity test.
# Use an inference profile ID if your account requires one.
MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "mistral.voxtral-mini-3b-2507")
# MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "google.gemma-4-e2b")


def main() -> int:
    if not os.environ.get("AWS_BEARER_TOKEN_BEDROCK"):
        print("ERROR: AWS_BEARER_TOKEN_BEDROCK is not set in this terminal.")
        print("Set it for the current session:  $env:AWS_BEARER_TOKEN_BEDROCK = \"YOUR_KEY\"")
        return 1

    print(f"Region : {REGION}")
    print(f"Model  : {MODEL_ID}")
    print("Calling Bedrock Converse API...\n")

    client = boto3.client("bedrock-runtime", region_name=REGION)

    try:
        response = client.converse(
            modelId=MODEL_ID,
            messages=[
                {
                    "role": "user",
                    "content": [{"text": "Reply with exactly: Bedrock access OK"}],
                }
            ],
            inferenceConfig={"maxTokens": 20, "temperature": 0},
        )
    except ClientError as e:
        err = e.response.get("Error", {})
        print("FAILED (ClientError)")
        print(f"  Code    : {err.get('Code')}")
        print(f"  Message : {err.get('Message')}")
        print("\nCommon causes:")
        print("  - AccessDeniedException   -> key lacks bedrock:InvokeModel or model not enabled")
        print("  - ValidationException     -> model id/region mismatch, try an inference profile id")
        print("  - UnrecognizedClientException/Unauthorized -> bad or expired bearer token")
        return 1
    except BotoCoreError as e:
        print(f"FAILED (BotoCoreError): {e}")
        return 1

    text = response["output"]["message"]["content"][0]["text"]
    usage = response.get("usage", {})

    print("SUCCESS - Bedrock responded:")
    print(f"  {text.strip()}")
    print(f"\n  Token usage: {json.dumps(usage)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
