import logging
from typing import Dict

from langchain_google_genai import ChatGoogleGenerativeAI

from microservices.libs.ai.agents import create_producer_agent, create_consumer_agent, BaseAgent
from microservices.libs.ai.guardrails import SecurityGuardrail, TokenGuardrail
from microservices.libs.ai.tools import create_toolkit


class AIService:
    def __init__(self, google_api_key: str, gateway_url: str, logger: logging.Logger):
        self.logger = logger

        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=google_api_key,
            temperature=0
        )

        self.security_guard = SecurityGuardrail(api_key=google_api_key)
        self.tools = create_toolkit(api_gateway_url=gateway_url)

    def execute_chat(self, query: str) -> str:
        if not self.security_guard.is_safe(query):
            self.logger.warning(f"Security Guardrail blocked query: {query}")
            return "Request blocked by security policy."

        system_message = "You are a helpful assistant for microservices management."

        agent = BaseAgent(
            name="ChatAssistant",
            llm=self.llm,
            tools=self.tools,
            system_prompt=system_message
        )

        token_guard = TokenGuardrail(max_tokens=5000)

        try:
            self.logger.info(f"Agent processing query: {query}")

            result = agent.agent_executor.invoke(
                {"input": query},
                config={"callbacks": [token_guard]}
            )

            output = result["output"]

            if isinstance(output, list):
                text_parts = []
                for item in output:
                    if isinstance(item, dict):
                        text_parts.append(item.get("text", ""))
                    else:
                        text_parts.append(str(item))
                return " ".join(text_parts)

            return str(output)

        except Exception as e:
            self.logger.error(f"Error during agent execution: {e}")
            return f"Error: {str(e)}"

    def run_a2a_simulation(self) -> Dict[str, str]:
        self.logger.info("Starting A2A simulation...")

        producer = create_producer_agent(self.llm, self.tools)
        consumer = create_consumer_agent(self.llm, self.tools)

        producer_task = (
            "Check if table 'movies' exists, create if not. "
            "Ensure there is a record for 'Another Movie' with id=456. "
            "Then, add the 'sci-fi' tag to item 456."
        )
        producer_result = producer.run(producer_task)
        self.logger.info(f"Producer output: {producer_result}")

        consumer_task = (
            f"Producer report: '{producer_result}'. "
            "Verify item 456. If genre/tag contains 'sci-fi', add the 'recommended' tag."
        )
        consumer_result = consumer.run(consumer_task)
        self.logger.info(f"Consumer output: {consumer_result}")

        return {
            "producer_report": producer_result,
            "consumer_report": consumer_result
        }
