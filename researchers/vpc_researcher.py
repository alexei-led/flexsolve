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
        example_questions = """
        Example technical questions to consider:
        1. What's your required IP address space?
        2. How many availability zones do you need?
        3. Do you require public and private subnets?
        4. Do you need VPC peering or Transit Gateway connectivity?
        5. What are your NAT requirements?
        6. Do you need VPC endpoints for AWS services?
        7. What are your security group requirements?
        8. Do you need flow logs for network monitoring?
        """
        self.system_message = self.base_system_message.format(
            service_area="Amazon VPC",
            expertise="\n- ".join(self.expertise)
        ) + example_questions 