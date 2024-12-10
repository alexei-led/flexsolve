from .base_researcher import BaseResearcher
from config import S3_RESEARCHER_NAME

class S3Researcher(BaseResearcher):
    def __init__(self, openai_config):
        super().__init__(openai_config)
        self.name = S3_RESEARCHER_NAME
        self.description = "I am an S3 research specialist."
        self.expertise = [
            "Storage classes",
            "Bucket policies",
            "Data lifecycle",
            "S3 security",
            "Performance optimization"
        ]
        example_questions = """
        Example technical questions to consider:
        1. What storage class best fits your access patterns?
        2. Do you need versioning enabled?
        3. What are your data lifecycle requirements?
        4. Do you need cross-region replication?
        5. What are your encryption requirements?
        6. Do you need object lock or retention policies?
        7. What's your expected request rate?
        8. Do you need transfer acceleration?
        """
        self.system_message = self.base_system_message.format(
            service_area="Amazon S3",
            expertise="\n- ".join(self.expertise)
        ) + example_questions 