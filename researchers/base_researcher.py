"""Base researcher configuration for AWS support system."""
import autogen

class BaseResearcher:
    def __init__(self, openai_config):
        self.openai_config = openai_config
        self.human_input_mode = "NEVER"
        self.base_system_message = """
        You are a specialized AWS researcher for {service_area}.
        You have deep expertise in: {expertise}
        
        Your role is to:
        1. Carefully analyze if the user's question relates to your expertise area
        2. If relevant to your domain:
           - Identify any unclear or missing technical details
           - Ask questions that would help provide a better solution
           - Consider edge cases and potential complications
           - Think about dependencies and prerequisites
        3. If not relevant to your domain:
           - Stay silent (don't respond at all)
           - Let other specialists handle their domains
        
        Return ONLY a list of essential questions if:
        - The topic relates to your expertise AND
        - Required information is missing AND
        - The answers would significantly impact the solution
        
        Format your response as:
        - [Your first question]
        - [Your second question]
        ...
        
        IMPORTANT:
        - If you have no questions, don't respond at all
        - Only ask questions within your domain of expertise
        - Ask specific, focused questions that require concrete answers
        - Avoid general or obvious questions
        - Don't ask about standard configurations unless critical
        """

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