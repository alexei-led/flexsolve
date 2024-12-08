from .base_researcher import BaseResearcher
from config import CLOUDWATCH_RESEARCHER_NAME

class CloudWatchResearcher(BaseResearcher):
    def __init__(self, openai_config):
        super().__init__(openai_config)
        self.name = CLOUDWATCH_RESEARCHER_NAME
        self.description = "I am a CloudWatch research specialist."
        self.expertise = [
            "Metrics and Alarms",
            "Log Analysis",
            "Events/EventBridge",
            "Container Insights",
            "Application Insights"
        ]
        self.system_message = self.base_system_message.format(
            service_area="Amazon CloudWatch",
            expertise="\n- ".join(self.expertise)
        )
