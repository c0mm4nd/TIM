import os
import time
from openai import Client
from pydantic import BaseModel, Field

from LLM4Intent.common.utils import convert_tool, get_logger, try_validate_json


class Perspective(BaseModel):
    name: str = Field(description="The name of the perspective")
    description: str = Field(
        description="The description of the perspective, explaining the focus of the analysis",
    )
    prompt: str = Field(
        description="The prompt for the perspective, helping the analysts to analyze the transaction better and more effectively from this perspective",
    )
    tool_suggestions: list[str] = Field(
        description="The list of tools used in the perspective, providing suggestions for the analysts",
    )
    tips: list[str] = Field(
        description="The tips for the perspective, guiding the analysts to analyze the transaction more effectively",
    )


class MetaPlan(BaseModel):
    perspectives: list[Perspective] = Field(
        description="The list of perspectives for the analysis"
    )


class MetaController:
    def __init__(self, model: str, client: Client, transaction_hash: str):
        self.name = "MetaController"
        self.model = model
        self.client = client
        self.transaction_hash = transaction_hash

        self.system_message = """
ROLE: You are the meta controller for bootstrapping the blockchain transaction intent analysis. You are responsible for building the analysis pipeline and coordinating the analysis perspectives.

ACTION: To analyze the intent behind the Ethereum transaction {transaction_hash}, we have assembled the team with many domain expert analysts.
Based on your expertise, please devise a structured plan for each analyst to follow. The plan should include multiple perspectives, each with be auto assigned to a specific agent.
Each task should include a detailed prompt to guide the analysts effectively.

Suggest Considerations:
- Smart Contract Behavior: 
    Analyze transaction interactions with smart contracts, detailing function calls, inter-contract communication, and asset flow. This includes scrutiny of advanced features like upgradeable proxies, flash loans, and the underlying logic(i.e. where the yield comes from).
- Off-Chain Situation: 
    Investigate relevant external (Web2) information that could provide context for the on-chain activity. This includes project reputation and news, regulatory announcements, broader macroeconomic trends, significant news events (hacks, exploits), and social media sentiment that might explain user actions or market movements reflected on-chain.
- On-Chain Context: 
    Examine the transaction within the broader blockchain environment, considering both historical and potential future interactions. This involves tracing the origin and destination of funds, analyzing past transaction patterns of involved addresses, understanding the behavioral history and risk profile of associated entities, and identifying potential connections to illicit activities or known actors.
- Other Perspectives:
    If you have other perspectives in mind, please add them to the plan.

Known Tools:
{tools}
""".strip()
        self.human_message = """
To analyze the intent behind the Ethereum transaction {transaction_hash}, please devise a structured plan for each analyst to follow

REQUIREMENTS for ALL analysts:
- ALL ANALYSTS SHOULD NEVER DECODE the raw data directly by yourself, ALWAYS USE the tools provided!
- When encountering Transfer Events, retrieve Token Info using get_contract_basic_info_from_jsonrpc.
- When encountering Smart Contracts, use get_contract_ABI to get the contract's functions and events.
- Only classify Swap or Swap-like Events as token exchanges; do not assume two Transfer Events constitute an exchange.
- Off-Chain Considerations Must be relevant to the token in the transaction, and Do not infer intent unless there's significant news or a direct impact.

The response MUST be in the following JSON schema:

{meta_plan_schema}

Make sure your response is ONE valid JSON that follows this schema exactly
""".strip()
        self.log = get_logger("MetaController", transaction_hash)

    def build_meta_plan(self, tools: list) -> MetaPlan:
        messages = [
            {
                "role": "system",
                "content": self.system_message.format(
                    tools=[convert_tool(tool) for tool in tools],
                    transaction_hash=self.transaction_hash,
                ),
            },
            {
                "role": "user",
                "content": self.human_message.format(
                    transaction_hash=self.transaction_hash,
                    meta_plan_schema=MetaPlan.model_json_schema(),
                ),
            },
        ]
        while True:
            try:
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=1,
                )
                response = completion.choices[0].message.content

                self.log.info("Meta plan response: %s", response)
                plans = [
                    try_validate_json(MetaPlan, no_prefix.strip("\n```"))
                    for no_prefix in response.split("```json\n")
                    if no_prefix and '"$defs"' not in no_prefix 
                ]
                existing_plans = [plan for plan in plans if plan]
                if not existing_plans:
                    raise ValueError(
                        "No valid JSON found in the response {}".format(response)
                    )
                # else return the first non-None
                plan = existing_plans[0]

                break
            except Exception as e:
                self.log.error(f"Error in building meta plan: {e}")
                time.sleep(10)

                continue

        os.makedirs("meta_plans", exist_ok=True)
        with open(f"meta_plans/{self.transaction_hash}.json", "w") as f:
            f.write(plan.model_dump_json(indent=4))

        return plan
