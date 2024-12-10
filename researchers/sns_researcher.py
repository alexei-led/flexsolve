from .base_researcher import BaseResearcher
from config import SNS_RESEARCHER_NAME

class SNSResearcher(BaseResearcher):
    def __init__(self, openai_config):
        super().__init__(openai_config)
        self.name = SNS_RESEARCHER_NAME
        self.description = "I am an SNS research specialist."
        self.expertise = [
            "Topic management",
            "Subscription types",
            "Message filtering",
            "SNS security",
            "Cross-region messaging"
        ]
        example_questions = """
        Example technical questions to consider:
        1. What subscription protocols do you need?
        2. Do you require message filtering?
        3. What's your expected message volume?
        4. Do you need FIFO topics?
        5. What are your message delivery retry requirements?
        6. Do you need cross-account delivery?
        7. What are your message encryption needs?
        8. Do you require message archiving?
        """
        self.system_message = self.base_system_message.format(
            service_area="Amazon SNS",
            expertise="\n- ".join(self.expertise)
        ) + example_questions 