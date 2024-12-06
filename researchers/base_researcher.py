"""Base researcher configuration for AWS support system."""
import autogen

class BaseResearcher:
    def __init__(self, openai_config):
        self.openai_config = openai_config
        self.name = "base_researcher"
        self.description = "This agent works with the coordinator to refine the problem and create a list of clarifying questions for the user."
        self.expertise = []
        self.system_message = ""
        self.human_input_mode = "NEVER"

    def create_agent(self) -> autogen.AssistantAgent:
        """Create a researcher agent with specific expertise."""
        return autogen.AssistantAgent(
            name=self.name,
            llm_config={"config_list": self.openai_config},
            system_message=self.system_message
        ) 