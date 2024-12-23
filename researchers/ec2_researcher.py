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
        example_questions = """
        Example technical questions to consider:
        1. What are your CPU/Memory/Storage requirements?
        2. Do you need consistent performance or is burstable acceptable?
        3. What's your expected network throughput?
        4. Do you require specific instance features? (e.g., GPU, high memory)
        5. What's your expected scaling pattern? (time-based, metric-based)
        6. Do you need placement groups for high availability?
        7. What are your backup and recovery requirements?
        8. Do you need instance connect or bastion host access?
        """
        self.system_message = self.base_system_message.format(
            service_area="Amazon EC2",
            expertise="\n- ".join(self.expertise)
        ) + example_questions

    def create_researcher(self):
        """Create the EC2 researcher agent."""
        return self.create_agent(self.system_message) 