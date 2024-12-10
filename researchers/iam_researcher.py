from .base_researcher import BaseResearcher
from config import IAM_RESEARCHER_NAME

class IAMResearcher(BaseResearcher):
    def __init__(self, openai_config):
        super().__init__(openai_config)
        self.name = IAM_RESEARCHER_NAME
        self.description = "I am an IAM research specialist."
        self.expertise = [
            "IAM policies and roles",
            "Permission boundaries",
            "Identity federation",
            "Access management",
            "Security best practices"
        ]
        example_questions = """
        Example technical questions to consider:
        1. What specific AWS services need access?
        2. Do you require cross-account access?
        3. Are you implementing federation with external identity providers?
        4. Do you need temporary credentials for applications?
        5. What are your audit and compliance requirements?
        6. Do you need to implement permission boundaries?
        7. Are there specific IP restrictions needed?
        8. Do you require MFA for specific actions?
        """
        self.system_message = self.base_system_message.format(
            service_area="AWS IAM",
            expertise="\n- ".join(self.expertise)
        ) + example_questions 