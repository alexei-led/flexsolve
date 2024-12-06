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
        self.system_message = """You are an EC2 research specialist. Your role is to:
        1. Analyze EC2-related questions
        2. Identify missing technical details
        3. Suggest clarifying questions about:
           - Instance requirements
           - Scaling patterns
           - Performance issues
           - Network configuration
           - Security needs
        
        Focus on gathering:
        - Current instance state
        - Performance metrics
        - Scaling requirements
        - Network setup
        - Security groups
        
        Format questions to be:
        - Performance-focused
        - Resource-aware
        - Clear and specific
        - Cost-conscious"""

    def create_researcher(self):
        """Create the EC2 researcher agent."""
        return self.create_agent(self.system_message) 