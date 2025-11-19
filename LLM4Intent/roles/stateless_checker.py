import json
import os
import time
from typing import List, Dict, Any, Optional, Mapping
from openai import Client
from pydantic import BaseModel, Field

from LLM4Intent.common.utils import get_logger, try_validate_json


class PerspectiveWeight(BaseModel):
    perspective: str = Field(description="The perspective name")
    credibility: float = Field(
        description="Credibility weight between 0.0 and 1.0", ge=0.0, le=1.0
    )
    credibility_reasoning: str = Field(
        description="Reasoning for the assigned credibility weight"
    )
    problems: List[str] = Field(
        description="List of contradictions or missing logical mistakes in the analysis"
    )


class CheckReport(BaseModel):
    perspective_weights: List[PerspectiveWeight] = Field(
        description="List of analyses with their assigned credibility weights"
    )


class StatelessChecker:
    def __init__(self, model: str, client: Client, transaction_hash: str):
        self.name = "TaskChecker"
        self.model = model
        self.client = client
        self.system_message = """
ROLE: Intent Analysis Report Evaluator

You are an expert evaluator to check the logical consistency and reasoning chain of the analysis result. You need to evaluate the provided analysis step by step and identify any contradictions or missing logical links. You should infer the intent for each provided analysis report and credibilities and provide an explanation for the classifications.
""".strip()
        self.log = get_logger("TaskChecker", transaction_hash=transaction_hash)

    def check(
        self,
        transaction_hash: str,
        hierarchical_intents: dict,
        perspective_analyst_reports: dict,
    ) -> CheckReport:
        system_message = self.system_message.format()

        analysis = ""
        for perspective, report in perspective_analyst_reports.items():
            analysis += f"Report on {perspective} perspective:\n{report}\n\n"

        analysis_content = """
Here are different perspective analysis reports for analyzing a same transaction:
{analysis}

Analyze this content, determine credibility weights for each perspective, and identify which intent category 
from the hierarchical intents below best matches the user's intent. Provide justification for your decision.

{hierarchical_intents}

Provide a weighted assessment of intents and credibilities from each perspective in the analysis.
- Review the provided analysis carefully
- For each perspective analysis, assign a credibility weight based on:
  - Evidence quality
  - Reasoning soundness
  - Consistency with blockchain behaviors
  - Presence of speculation vs. factual reasoning
  - Calculate a confidence score for each perspective
  - and so on...

The response MUST be in the following JSON schema:

{check_report_schema}

Make sure your response is ONE valid JSON that follows this schema exactly."""

        messages = [
            {"role": "system", "content": system_message},
            {
                "role": "user",
                "content": analysis_content.format(
                    analysis=analysis,
                    hierarchical_intents=hierarchical_intents,
                    check_report_schema=CheckReport.model_json_schema(),
                ),
            },
        ]

        self.log.debug(messages)

        while True:
            try:
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0,
                )

                self.log.debug(completion)
                response = completion.choices[0].message.content

                reports = [
                    try_validate_json(CheckReport, no_prefix.strip("\n```"))
                    for no_prefix in response.split("```json\n")
                    if no_prefix and '"$defs"' not in no_prefix 
                ]
                existing_reports = [report for report in reports if report]
                if not existing_reports:
                    raise ValueError(
                        "No valid JSON found in the response {}".format(response)
                    )
                report = existing_reports[0]
                break
            except Exception as e:
                self.log.error(f"Error in checking: {e}")
                time.sleep(10)
                continue

        os.makedirs("check_reports", exist_ok=True)
        with open(f"check_reports/{transaction_hash}.output.md", "w") as f:
            f.write(report.model_dump_json(indent=4))

        return report
