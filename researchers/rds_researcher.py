from .base_researcher import BaseResearcher
from config import RDS_RESEARCHER_NAME

class RDSResearcher(BaseResearcher):
    def __init__(self, openai_config):
        super().__init__(openai_config)
        self.name = RDS_RESEARCHER_NAME
        self.description = "I am an RDS research specialist."
        self.expertise = [
            "Database engines",
            "Instance scaling",
            "High availability",
            "Backup and recovery",
            "Performance insights"
        ]
        example_questions = """
        Example technical questions to consider:
        1. Which database engine and version do you need?
        2. What are your instance size requirements (CPU/Memory)?
        3. Do you need Multi-AZ deployment?
        4. What's your backup retention requirement?
        5. Do you need read replicas for scaling?
        6. What are your storage IOPS requirements?
        7. Do you need encryption at rest?
        8. What's your maintenance window preference?
        9. Do you need Performance Insights enabled?
        10. What are your automated backup requirements?
        """
        self.system_message = self.base_system_message.format(
            service_area="Amazon RDS",
            expertise="\n- ".join(self.expertise)
        ) + example_questions
  