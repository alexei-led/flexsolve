"""EC2 researcher for AWS support system."""
from .base_researcher import BaseResearcher

class EC2Researcher(BaseResearcher):
    def __init__(self, openai_config):
        super().__init__(openai_config)
        self.name = "EC2_Researcher"
        self.expertise = [
            "EC2 instance types",
            "Auto Scaling",
            "Instance performance",
            "EC2 networking",
            "EC2 security"
        ]
        self.system_message = """
        You are an EC2 research specialist.
        You have deep expertise in: {expertise}
        
        Return a numbered list of essential questions if:
        - Required information is missing
        - It's critical for the solution
        - It will significantly change your approach
        
        Format your response as:
        1. [Your first question]
        2. [Your second question]
        ...
        TERMINATE
        
        If the problem isn't EC2-related or you have no questions, return only "TERMINATE".
        
        Skip questions about:
        - General instance setup unless critical
        - Future scaling needs
        - Nice-to-have features
        - Standard configurations
        """

    def create_researcher(self):
        """Create the EC2 researcher agent."""
        return self.create_agent(self.system_message) 