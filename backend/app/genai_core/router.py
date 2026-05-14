# TODO: Implement LLM-based router that decides between Data Tools and Database queries


class Router:
    def __init__(self):
        """
        TODO: Initialize LLM client (OpenAI/LangChain)
        TODO: Load database schema
        TODO: Load system prompts
        """
        pass

    async def route_request(self, question: str, context: dict) -> dict:
        """
        TODO: Implement LLM call with system prompt
        TODO: Return decision: {"path": "data_tools"|"database", "reasoning": "..."}
        """
        raise NotImplementedError("Router.route_request is not implemented yet")
