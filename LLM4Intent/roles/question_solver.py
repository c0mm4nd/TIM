import json
import logging
import tiktoken
from typing import Callable, Dict, List
from openai import BadRequestError, Client
from openai.types.chat import ChatCompletionMessage
from LLM4Intent.common.utils import convert_tool, get_logger


class QuestionSolverAnalyst:
    def __init__(
        self,
        model: str,
        client: Client,
        transaction_hash: str,
        known_facts: str,
        main_perspective: str,
        tools: List[Callable],
    ):
        self.name = "QuestionSolver"
        self.model = model
        self.client = client
        self.main_perspective = main_perspective
        self.tools = tools
        self.facts = known_facts
        self.transaction_hash = transaction_hash
        self.system_prompt = """
ROLE: You are a professional blockchain transaction intent analyst on the {perspective} domain, good at solving questions. Below I will present you a request. Keep in mind that you are Ken Jennings-level with trivia, and Mensa-level with puzzles, so there should be a deep well to draw from.
ACTION: Collect as much information as possible about the transaction from the {perspective} perspective for the main analyst digging the real intent, until the request is fully satisfied. Provide complete information and conclusions in your analysis. DO NOT ask questions or request further instructions - simply provide your best complete analysis based on available information. NEVER use any placeholder when requesting. When you have fully addressed the request, please say END.
""".format(
            perspective=main_perspective
        ).strip()

        self.log = get_logger(
            f"{self.main_perspective}-QuestionSolver", transaction_hash
        )
        self.tool_map = {tool.__name__: tool for tool in tools}

        # Convert tools safely with error handling
        converted_tools = []
        for tool in self.tools:
            try:
                converted_tool = convert_tool(tool)
                converted_tools.append(converted_tool)
            except ValueError as e:
                self.log.error(f"Failed to convert tool {tool.__name__}: {str(e)}")
                # Skip this tool or create a simplified version if needed
        self.converted_tools = converted_tools

        self.model_info = client.models.retrieve(self.model)
        self.log.info(f"Model info: {self.model_info}")
        self.token_limit = self.model_info.to_dict().get("token_limit", 130000)
        self.log.warning(f"Token limit: {self.token_limit}")

    def call_tools(self, question: str, response: ChatCompletionMessage) -> list:
        tool_messages = [
            response.to_dict(),
        ]

        for tool_call in response.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            self.log.warning(
                f"For {question} call Tool: {tool_name} with args {tool_args}"
            )

            tool = self.tool_map.get(tool_name)
            if tool:
                try:
                    result = tool(**tool_args)
                    tool_messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(result),
                        }
                    )
                except Exception as e:
                    error_message = (
                        f"Error in tool {tool_name} with args {tool_args}: {str(e)}"
                    )
                    self.log.error(error_message)
                    tool_messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": error_message,
                        }
                    )
            else:
                raise ValueError(f"Tool {tool_name} not found in tool map")

        return tool_messages

    def cut_history(self, previous_chat_history: list) -> list:
        """
        Cuts the chat history to include only messages that fit within the token limit.
        If possible, starts from the earliest user message that fits.
        """
        if not previous_chat_history:
            return []

        encoding = tiktoken.get_encoding("o200k_base")

        # More accurate token counting by including message structure
        def count_tokens(message):
            # Count tokens for role, content and basic message structure
            role_tokens = len(encoding.encode(message["role"]))
            content_tokens = len(encoding.encode(message.get("content", "")))
            # Add tokens for basic message structure (~4 tokens)
            return role_tokens + content_tokens + 4

        # Step 1: Accumulate messages from back to front
        total_tokens = 0
        accumulated_messages = []
        for message in reversed(previous_chat_history):
            tokens = count_tokens(message)
            if total_tokens + tokens > self.token_limit:
                break
            accumulated_messages.append(message)
            total_tokens += tokens

        # If no messages were accumulated, return empty list
        if not accumulated_messages:
            return []

        # Step 2: Restore original order
        accumulated_messages.reverse()

        # Step 3: Try to find the first user message and trim from there
        for idx, message in enumerate(accumulated_messages):
            if message["role"] == "user":
                return accumulated_messages[idx:]

        # If no user message found, return all accumulated messages
        # This is the key change - don't raise an error, just return what we have
        self.log.warning(
            f"No user message found in pruned chat history, returning all accumulated messages"
        )
        return accumulated_messages

    def rollback_history(self, previous_chat_history: list, e: Exception) -> list:
        """
        Rollback the chat history to the last tool use and say rate limit

        Args:
            previous_chat_history (list): The complete chat history
            e: The exception that triggered the rollback

        Returns:
            list: A subset of the chat history starting from the last user message
        """

        # Prevent infinite loop if no matching message is found
        original_length = len(previous_chat_history)
        processed = 0

        while previous_chat_history and processed < original_length:
            processed += 1
            last_message = previous_chat_history.pop()
            if (
                last_message["role"] == "assistant"
                and "tool_calls" in last_message
                and last_message["tool_calls"]
            ):
                # push back
                previous_chat_history.append(last_message)
                previous_chat_history.extend(
                    [
                        {
                            "role": "tool",
                            "tool_call_id": tool_call["id"],
                            "content": str(e),
                        }
                        for tool_call in last_message["tool_calls"]
                    ]
                )
                break

        # If we went through the entire history without finding a tool call, return original
        if processed >= original_length and not previous_chat_history:
            self.log.warning(
                "No tool calls found in history during rollback, returning to last user message"
            )
            # Return at least the last user message if possible
            return previous_chat_history

        return previous_chat_history

    def analyze(self, previous_chat_history: list, question: str, prompt: str) -> str:
        """
        Analyze a specific sub-question using tools and LLM capabilities

        Args:
            previous_chat_history (list): The chat history so far
            question: The sub-question to analyze
            prompt: The prompt to use for the analysis

        Returns:
            str: The analysis result
        """

        chat_history = [
            *previous_chat_history,
            {
                "role": "user",
                "content": f"Known Transaction Facts: {json.dumps(self.facts)}\n\nQuestion to analyze: {question}\n\n{prompt}",
            },
        ]
        max_iterations = 10  # Prevent infinite loops
        iterations = 0

        while iterations < max_iterations:
            iterations += 1
            self.log.info(
                f"Iteration {iterations} for question: {question} ({self.main_perspective})"
            )

            messages = [
                {"role": "system", "content": self.system_prompt},
                *self.cut_history(chat_history),
            ]

            try:
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=self.converted_tools,
                    tool_choice="auto",
                    temperature=0,
                )
            except BadRequestError as e:
                if "maximum" in str(e).lower():
                    self.log.warning(
                        f"Max context length exceeded for question: {question} ({e}), rolling back history"
                    )
                    chat_history = self.rollback_history(chat_history, e)
                    continue
                else:
                    # raise unknown error
                    raise e
            except Exception as e:
                # back to last user message when rate limit
                if (
                    "rate" in str(e).lower()
                    or "quota" in str(e).lower()
                    or "resource" in str(e).lower()
                    or "maximum" in str(e).lower()
                ):
                    self.log.warning(
                        f"Rate limit exceeded for question: {question}, rolling back history"
                    )
                    chat_history = self.rollback_history(chat_history, e)
                    continue
                else:
                    # raise unknown error
                    raise e

            response = completion.choices[0].message

            # Check if the response has tool calls that need to be processed
            if response.tool_calls:
                # Process tool calls and add results to conversation
                tool_messages = self.call_tools(question, response)
                chat_history.extend(
                    tool_messages
                )  # Skip the first item as it's the assistant's message already in conversation
            else:
                # Check if analysis is complete (when "END" appears in the response)
                if "END" in response.content:
                    # Clean up the response by removing the END marker
                    final_response = response.content.replace("END", "").strip()
                    self.log.info(f"Analysis complete after {iterations} iterations")
                    chat_history.append(
                        {
                            "role": "assistant",
                            "content": final_response,
                        }
                    )

                    self.log.info(f"Final response: {final_response}")

                    return [
                        {
                            "role": "user",
                            "content": question,
                        },
                        {
                            "role": "assistant",
                            "content": final_response,
                        },
                    ]

                # No tool calls, add response to conversation
                chat_history.append({"role": "assistant", "content": response.content})

                self.log.info(f"Response: {response.content}")

                # Ask for additional analysis if not complete
                chat_history.append(
                    {
                        "role": "user",
                        "content": "Continue analyzing this question. When you have completed the analysis, include 'END' at the end of your response.",
                    }
                )

        # If we reach max iterations without completion
        self.log.warning(
            f"Reached maximum iterations ({max_iterations}) without completing analysis"
        )

        self.log.warning(f"Final chat history: {chat_history}")

        return [
            {
                "role": "user",
                "content": question,
            },
            {
                "role": "assistant",
                "content": chat_history[-1]["content"],
            },
        ]
