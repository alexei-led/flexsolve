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
        example_questions = """
        Example technical questions to consider:
        1. Which specific metrics do you need to monitor? (e.g., CPU, Memory, Custom metrics)
        2. What are your alerting thresholds and evaluation periods?
        3. Do you need cross-account monitoring capabilities?
        4. What is your log retention requirement?
        5. Are you using structured logging formats?
        6. Do you need real-time log analysis or batch processing?
        7. What types of events do you need to track?
        8. Do you require custom metrics with dimensions?
        """
        self.system_message = self.base_system_message.format(
            service_area="Amazon CloudWatch",
            expertise="\n- ".join(self.expertise)
        ) + example_questions
