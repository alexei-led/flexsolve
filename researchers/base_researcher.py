"""Base researcher configuration for AWS support system."""
import autogen

class BaseResearcher:
    def __init__(self, openai_config):
        self.openai_config = openai_config
        self.name = "base_researcher"
        self.description = "This agent works with the coordinator to identify only the critical missing information needed to solve the user's specific problem."
        self.system_message = """
        Focus ONLY on the user's specific problem.
        Return a numbered list of essential questions if:
        - Required information is missing
        - It's critical for the solution
        - It will significantly change your approach
        
        Format your response as:
        1. [Your first question]
        2. [Your second question]
        ...
        TERMINATE
        
        If you have no relevant questions, return only "TERMINATE".
        
        Before asking any question, verify:
        - Is this information critical for solving THIS specific problem?
        - Has this been mentioned already?
        - Will this meaningfully change the solution?
        
        Skip questions about:
        - General setup unless critical
        - Future requirements
        - Nice-to-have features
        - Standard configurations"""
        self.human_input_mode = "NEVER"

    def create_agent(self) -> autogen.AssistantAgent:
        """Create a researcher agent with specific expertise."""
        return autogen.AssistantAgent(
            name=self.name,
            llm_config={"config_list": self.openai_config},
            description=self.description,
            system_message=self.system_message,
            human_input_mode=self.human_input_mode,
            is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
        ) 