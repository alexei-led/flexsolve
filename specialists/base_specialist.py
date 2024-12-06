"""Base specialist configuration for AWS support system."""
import autogen

class BaseSpecialist:
    def __init__(self, name, config_list):
        self.name = name
        self.config_list = config_list

    def create_agent(self, system_message, human_input_mode="NEVER") -> autogen.AssistantAgent:
        """Create a configuration for an agent."""
        return autogen.AssistantAgent(
            name=self.name,
            description=self.description,
            llm_config={"config_list": self.config_list},
            system_message=system_message,
            human_input_mode=human_input_mode,
            is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
        )
