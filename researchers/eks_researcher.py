from .base_researcher import BaseResearcher
from config import EKS_RESEARCHER_NAME

class EKSResearcher(BaseResearcher):
    def __init__(self, openai_config):
        super().__init__(openai_config)
        self.name = EKS_RESEARCHER_NAME
        self.description = "I am an EKS research specialist."
        self.expertise = [
            "EKS cluster architecture",
            "Kubernetes workloads",
            "Container orchestration",
            "EKS networking",
            "EKS security"
        ]
        example_questions = """
        Example technical questions to consider:
        1. What Kubernetes version do you require?
        2. Do you need managed node groups or self-managed nodes?
        3. What are your pod networking requirements?
        4. Do you need cluster autoscaling?
        5. What container runtime do you prefer?
        6. Do you require specific add-ons or operators?
        7. What are your pod security policy requirements?
        8. Do you need private cluster endpoints?
        """
        self.system_message = self.base_system_message.format(
            service_area="Amazon EKS",
            expertise="\n- ".join(self.expertise)
        ) + example_questions 