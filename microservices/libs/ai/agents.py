from typing import List


from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import BaseTool


class BaseAgent:
    def __init__(self, name: str, llm: BaseChatModel, tools: List[BaseTool], system_prompt: str):
        self.name = name

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])

        agent = create_tool_calling_agent(llm, tools, prompt)

        self.agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    def run(self, input_text: str) -> str:
        result = self.agent_executor.invoke({"input": input_text})
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


def create_producer_agent(llm: BaseChatModel, tools: List[BaseTool]) -> BaseAgent:
    prompt = (
        "You are a Creative Producer AI. Your goal is to generate content in the system. "
        "Use tools to create records in the 'movies' table (create it if missing) "
        "and add initial tags. Always return the ID of the created item."
    )
    return BaseAgent(name="Producer", llm=llm, tools=tools, system_prompt=prompt)


def create_consumer_agent(llm: BaseChatModel, tools: List[BaseTool]) -> BaseAgent:
    prompt = (
        "You are a Quality Control Consumer AI. You review items created by the Producer. "
        "Check the tags of the item using its ID. "
        "If the genre is 'sci-fi', ensure it has the 'recommended' tag. If not, add it. "
        "Report your actions concisely."
    )
    return BaseAgent(name="Consumer", llm=llm, tools=tools, system_prompt=prompt)
