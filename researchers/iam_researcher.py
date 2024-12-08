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
        self.system_message = self.base_system_message.format(
            service_area="AWS IAM",
            expertise="\n- ".join(self.expertise)
        ) 