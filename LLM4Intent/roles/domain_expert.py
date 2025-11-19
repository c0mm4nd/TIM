import json
import logging
import time

from openai import Client
from pydantic import BaseModel, Field
from LLM4Intent.common.utils import get_logger, try_validate_json


class TODOItem(BaseModel):
    question: str = Field(
        ..., description="The TODO item in the plan, in form of a question"
    )
    prompt: str = Field(
        ..., description="The detailed prompt for better handling the question"
    )


class PerspectivePlan(BaseModel):
    target: str = Field(..., description="The target of the plan")
    items: list[TODOItem] = Field(..., description="The TODO items in the plan")


BREAKDOWN_PROMPT = """
To analyze the intent behind the Ethereum transaction {transaction_hash}, we have assembled the team with multiple analysts.

Based on known and unknown facts, please devise a short bullet-point plan for each analyst to follow. The plan should include the target of the analysis and the TODO items with detailed prompts for better handling each item.

Here are some TIPs to help you with the plan and prompts:
{tips}

Please output an answer in pure JSON format according to the following schema. The JSON object must be parsable as-is. DO NOT OUTPUT ANYTHING OTHER THAN JSON, AND DO NOT DEVIATE FROM THIS SCHEMA:
{plan_json_schema}
"""


class DomainExpertAnalyst:
    def __init__(
        self,
        model: str,
        client: Client,
        transaction_hash: str,
        perspective: str,
        tips: str,
    ):
        self.name = "DomainExpertAnalyst"
        self.model = model
        self.client = client
        self.perspective = perspective
        self.tips = tips

        self.system_message = """
ROLE: You are a professional blockchain transaction intent analyst on {perspective} domain. Below I will present you a request. Keep in mind that you are Ken Jennings-level with trivia, and Mensa-level with puzzles, so there should be a deep well to draw from.
ACTION: Analyze the blockchain transaction intent from the {perspective} perspective for digging the real intent.
        """.format(
            perspective=self.perspective
        ).strip()

        self.log = get_logger(f"{perspective}-DomainExpert", transaction_hash)

        self.plan = None

    def breakdown(self, transaction_hash) -> PerspectivePlan:
        breakdown_prompt = BREAKDOWN_PROMPT.format(
            transaction_hash=transaction_hash,
            tips=self.tips,
            plan_json_schema=PerspectivePlan.model_json_schema(),
        )

        messages = [
            {"role": "system", "content": self.system_message},
            {"role": "assistant", "content": breakdown_prompt},
        ]

        while True:
            try:
                completion = self.client.chat.completions.create(
                    model=self.model, messages=messages, temperature=0.7
                )
                response = completion.choices[0].message.content
                self.log.info("Breakdown response: %s", response)

                plans = [
                    try_validate_json(PerspectivePlan, no_prefix.strip("\n```"))
                    for no_prefix in response.split("```json\n")
                    if no_prefix and '"$defs"' not in no_prefix 
                ]
                existing_plans = [plan for plan in plans if plan]

                if not existing_plans:
                    raise ValueError(
                        "No valid JSON found in the response {}".format(response)
                    )

                plan = existing_plans[0]
                break
            except Exception as e:
                self.log.error(f"Error in breakdown: {e}")
                time.sleep(10)
                continue

        self.log.info("Plan: %s", plan)

        self.plan = plan

        return plan

    def analyze(self, hierarchical_intents, merged_chat_history) -> str:
        chat_history = [
            {
                "role": "user",
                "content": f"Please analyze the {self.plan.target}.",
            },
            {
                "role": "assistant",
                "content": f"""Here is the plan to analyze the {self.plan.target}:
{"\n".join(f'- {item}' for item in self.plan.items)}
""",
            },
            *merged_chat_history,
        ]

        while True:
            system_message = self.system_message.format()
            messages = [
                {"role": "system", "content": system_message},
                *chat_history,
                {
                    "role": "user",
                    "content": f"""Please infer the intent behind the {self.plan.target} from the perspective of the {self.perspective}.

The intent inferred should be one of the following:
{hierarchical_intents}
                    """,
                },
            ]
            self.log.debug("Analyst messages: %s", messages)
            completion = self.client.chat.completions.create(
                model=self.model, messages=messages, temperature=0
            )
            self.log.debug("Analyst completion: %s", completion)
            response = completion.choices[0].message.content

            # Save the analysis to the state
            chat_history.extend(
                [
                    {
                        "role": "user",
                        "content": f"Please analyze against the retrieved data.",
                    },
                    {"role": "assistant", "content": response},
                ]
            )

            return response
