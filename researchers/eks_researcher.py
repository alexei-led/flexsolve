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
        self.system_message = self.base_system_message.format(
            service_area="Amazon EKS",
            expertise="\n- ".join(self.expertise)
        ) 