from .base_researcher import BaseResearcher
from config import VPC_RESEARCHER_NAME

class VPCResearcher(BaseResearcher):
    def __init__(self, openai_config):
        super().__init__(openai_config)
        self.name = VPC_RESEARCHER_NAME
        self.description = "I am a VPC research specialist."
        self.expertise = [
            "VPC architecture",
            "Subnet design",
            "Network ACLs",
            "VPC peering",
            "Transit Gateway"
        ]
        self.system_message = self.base_system_message.format(
            service_area="Amazon VPC",
            expertise="\n- ".join(self.expertise)
        ) 