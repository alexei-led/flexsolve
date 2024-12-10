from .base_researcher import BaseResearcher
from config import ECS_RESEARCHER_NAME

class ECSResearcher(BaseResearcher):
    def __init__(self, openai_config):
        super().__init__(openai_config)
        self.name = ECS_RESEARCHER_NAME
        self.description = "I am an ECS research specialist."
        self.expertise = [
            "Container orchestration",
            "Task definitions",
            "Service configuration",
            "ECS networking",
            "ECS security"
        ]
        example_questions = """
        Example technical questions to consider:
        1. Are you using Fargate or EC2 launch type?
        2. What container image registry are you using?
        3. What are your task memory and CPU requirements?
        4. Do you need service auto-scaling?
        5. What type of service discovery do you require?
        6. Do you need load balancer integration?
        7. What are your container logging requirements?
        8. Do you need task IAM roles for container permissions?
        """
        self.system_message = self.base_system_message.format(
            service_area="Amazon ECS",
            expertise="\n- ".join(self.expertise)
        ) + example_questions
 