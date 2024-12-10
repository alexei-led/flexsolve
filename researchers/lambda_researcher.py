from .base_researcher import BaseResearcher
from config import LAMBDA_RESEARCHER_NAME

class LambdaResearcher(BaseResearcher):
    def __init__(self, openai_config):
        super().__init__(openai_config)
        self.name = LAMBDA_RESEARCHER_NAME
        self.description = "I am a Lambda research specialist."
        self.expertise = [
            "Serverless architecture",
            "Function configuration",
            "Event sources and triggers",
            "Lambda networking",
            "Lambda security and permissions"
        ]
        example_questions = """
        Example technical questions to consider:
        1. What runtime and language are you using?
        2. What are your function memory and timeout requirements?
        3. Do you need VPC access from your function?
        4. What triggers or event sources are you using?
        5. Do you require custom layers or dependencies?
        6. What are your cold start latency requirements?
        7. Do you need concurrent execution controls?
        8. What's your expected invocation frequency?
        """
        self.system_message = self.base_system_message.format(
            service_area="AWS Lambda",
            expertise="\n- ".join(self.expertise)
        ) + example_questions 