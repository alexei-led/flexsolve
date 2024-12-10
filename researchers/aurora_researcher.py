from .base_researcher import BaseResearcher
from config import AURORA_RESEARCHER_NAME

class AuroraResearcher(BaseResearcher):
    def __init__(self, openai_config):
        super().__init__(openai_config)
        self.name = AURORA_RESEARCHER_NAME
        self.description = "I am an Aurora research specialist."
        self.expertise = [
            "Cluster management",
            "Global databases",
            "Serverless configuration",
            "Replication",
            "Performance optimization"
        ]
        example_questions = """
        Example technical questions to consider:
        1. Do you need Aurora Serverless or provisioned?
        2. What's your expected read/write workload ratio?
        3. Do you need global database capabilities?
        4. What are your auto-scaling requirements?
        5. Do you need parallel query enabled?
        6. What's your backup retention requirement?
        7. Do you need cross-region read replicas?
        8. What are your failover requirements?
        9. Do you need Aurora Replicas for read scaling?
        10. What's your expected cluster endpoint usage pattern?
        """
        self.system_message = self.base_system_message.format(
            service_area="Amazon Aurora",
            expertise="\n- ".join(self.expertise)
        ) + example_questions 