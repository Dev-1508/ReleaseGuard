from ollama import chat
from pydantic import BaseModel


class SemanticJudgment(BaseModel):
    equivalent: bool
    reason: str


def evaluate_semantic_match(expected_output, actual_output):

    prompt = f"""
You are evaluating an AI agent response.

Expected answer:
{expected_output}

Actual answer:
{actual_output}

Determine whether the actual answer communicates the same essential meaning
as the expected answer.

Ignore harmless differences in wording, capitalization, and phrasing.

Return equivalent=true only if the actual answer is semantically correct.
"""

    response = chat(
        model="qwen3.5:4b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        format=SemanticJudgment.model_json_schema(),
        options={
            "temperature": 0
        }
    )

    judgment = SemanticJudgment.model_validate_json(
        response.message.content
    )

    if judgment.equivalent:
        return 1

    return 0