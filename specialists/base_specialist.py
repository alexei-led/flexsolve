"""Base specialist configuration for AWS support system."""
import autogen

class BaseSpecialist:
    def __init__(self, name, config_list):
        self.name = name
        self.config_list = config_list

    def create_agent_config(self, system_message, human_input_mode="NEVER"):
        """Create a configuration for an agent."""
        return {
            "name": self.name,
            "llm_config": {"config_list": self.config_list},
            "system_message": system_message,
            "human_input_mode": human_input_mode
        }

    def create_agent(self, system_message, human_input_mode="NEVER"):
        """Create an AssistantAgent with the given configuration."""
        return autogen.AssistantAgent(
            **self.create_agent_config(system_message, human_input_mode)
        ) 