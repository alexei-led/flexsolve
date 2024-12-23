"""Base specialist configuration for AWS support system."""
import autogen

class BaseSpecialist:
    def __init__(self, name, config_list):
        self.name = name
        self.config_list = config_list
        self.description = ""
        self.system_message = """
        RESPONSE FORMAT:
        Always structure your response as:
        
        [If solutions exist]:
        
        Solution 1: [Solution Name]
        Description: [Brief description]
        Implementation:
        ```[language]
        [Implementation details, code, commands]
        ```
        Best Practices:
        - [List relevant AWS best practices]
        Considerations:
        - Complexity: [Low/Medium/High]
        - Cost: [Low/Medium/High]
        - Scalability: [Low/Medium/High]
        - Maintenance: [Low/Medium/High]
        
        Solution 2: [If applicable]
        ...
        
        [If no viable solution]:
        No viable solution available for the given requirements.
        """
        
    def create_agent(self) -> autogen.AssistantAgent:
        """Create a configuration for an agent."""
        return autogen.AssistantAgent(
            name=self.name,
            description=self.description,
            llm_config={"config_list": self.config_list},
            system_message=self.system_message,
            human_input_mode="TERMINATE",
            max_consecutive_auto_reply=2,
            is_termination_msg=lambda msg: "TERMINATE" in msg["content"].upper(),
        )
