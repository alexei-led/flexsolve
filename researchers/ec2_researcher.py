"""EC2 researcher for AWS support system."""
from .base_researcher import BaseResearcher
from config import EC2_RESEARCHER_NAME

class EC2Researcher(BaseResearcher):
    def __init__(self, openai_config):
        super().__init__(openai_config)
        self.name = EC2_RESEARCHER_NAME
        self.description = "I am an EC2 research specialist."
        self.expertise = [
            "EC2 instance types",
            "Auto Scaling",
            "Instance performance",
            "EC2 networking",
            "EC2 security"
        ]
        self.system_message = self.base_system_message.format(
            service_area="Amazon EC2",
            expertise="\n- ".join(self.expertise)
        )

    def create_researcher(self):
        """Create the EC2 researcher agent."""
        return self.create_agent(self.system_message) 