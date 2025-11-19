import os
import json
import time
from typing import List
from openai import Client
from pydantic import BaseModel, Field
from LLM4Intent.common.utils import get_logger, try_validate_json
from LLM4Intent.roles.stateless_checker import CheckReport


class CheckEval(BaseModel):
    """The evaluation of the check reports"""

    coherence: float = Field(
        description="Coherence with known knowledge and the provided evaluation criteria in each domain check report, between 0.0 and 1.0",
        ge=0.0,
        le=1.0,
    )
    strength: float = Field(
        description="Supporting evidence strength in each domain analysis report, between 0.0 and 1.0",
        ge=0.0,
        le=1.0,
    )
    # Cross-validation with other analysis perspectives in the dataset


class FinalReport(BaseModel):
    check_evaluations: List[CheckEval] = Field(
        description="The evaluation of the analysis check reports in each domain"
    )
    final_intent: str = Field(
        description="The most possible intent category from hierarchy of intents"
    )
    possible_intents: List[str] = Field(
        description="List of possible intent categories from the hierarchy of intents"
    )
    possible_intent_paths: List[str] = Field(
        description="List of possible intent paths in the hierarchy of intents"
    )
    confidence_score: float = Field(
        description="Overall confidence score between 0.0 and 1.0", ge=0.0, le=1.0
    )
    summary: str = Field(description="Summary of the intent analysis and justification")
    improvement: List[str] = Field(
        description="List of improvements needed for a better analysis and more accurate intent identification"
    )


class StatelessScorer:
    def __init__(self, model: str, client: Client, transaction_hash: str):
        self.name = "FinalEvaluator"
        self.model = model

        self.client = client

        self.system_message = """
ROLE: You are the final evaluator determining the intent of the transaction.
""".strip()
        self.log = get_logger("FinalEvaluator", transaction_hash=transaction_hash)

    def score(
        self,
        transaction_hash: str,
        perspective_analyst_reports: dict,
        check_report: CheckReport,
        hierarchical_intents: dict,
    ) -> FinalReport:
        human_message = """
Here are different perspective analysis reports for analyzing a same transaction:
{analysis}

And a weighted assessment of intents and credibilities from each perspective is provided:
{check_report}

Evaluate step by step as below:
1. Evaluate the logical consistency of the reasoning chain in the analysis result. 
2. Identify any contradictions or missing logical links. 
3. Explain the reasoning behind any detected inconsistencies. 
4. Infer the overall intent from the provided analysis reports and credibilities. 
5. Provide an explanation for the classifications. 

Wrap the output in `json` tags with the structure of the FinalReport.

{final_report_schema}"""

        system_message = self.system_message.format(
            categories=json.dumps(hierarchical_intents),
        )

        analysis = ""
        for perspective, report in perspective_analyst_reports.items():
            analysis += f"Report on {perspective} perspective:\n{report}\n\n"

        messages = [
            {"role": "system", "content": system_message},
            {
                "role": "user",
                "content": human_message.format(
                    final_report_schema=FinalReport.model_json_schema(),
                    check_report=check_report,
                    analysis=analysis,
                ).strip(),
            },
        ]
        self.log.debug(messages)

        while True:
            try:
                completion = self.client.chat.completions.create(
                    model=self.model, messages=messages, temperature=0
                )
                response = completion.choices[0].message.content
                self.log.debug(response)
                reports = [
                    try_validate_json(FinalReport, no_prefix.strip("\n```"))
                    for no_prefix in response.split("```json\n")
                    if no_prefix and '"$defs"' not in no_prefix 
                ]
                existing_reports = [report for report in reports if report]
                if not existing_reports:
                    raise ValueError(
                        "No valid JSON found in the response {}".format(response)
                    )
                # else return the first non-None
                report = existing_reports[0]

                break
            except Exception as e:
                self.log.error(f"Error in scoring: {e}")
                time.sleep(10)

                continue

        os.makedirs("score_reports", exist_ok=True)
        with open(f"score_reports/{transaction_hash}.output.md", "w") as f:
            f.write(report.model_dump_json(indent=4))

        return report
