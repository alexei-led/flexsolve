from .base_researcher import BaseResearcher
from config import SQS_RESEARCHER_NAME

class SQSResearcher(BaseResearcher):
    def __init__(self, openai_config):
        super().__init__(openai_config)
        self.name = SQS_RESEARCHER_NAME
        self.description = "I am an SQS research specialist."
        self.expertise = [
            "Queue types",
            "Message processing",
            "Dead-letter queues",
            "SQS security",
            "Queue scaling"
        ]
        example_questions = """
        Example technical questions to consider:
        1. Do you need standard or FIFO queues?
        2. What's your message retention requirement?
        3. Do you need dead-letter queue configuration?
        4. What's your expected message throughput?
        5. Do you need message deduplication?
        6. What's your visibility timeout requirement?
        7. Do you need long polling?
        8. What are your message size requirements?
        """
        self.system_message = self.base_system_message.format(
            service_area="Amazon SQS",
            expertise="\n- ".join(self.expertise)
        ) + example_questions 