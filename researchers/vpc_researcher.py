from .base_researcher import BaseResearcher

class VPCResearcher(BaseResearcher):
    def __init__(self, openai_config):
        super().__init__(openai_config)
        self.name = "VPC_Researcher"
        self.expertise = [
            "VPC architecture",
            "Subnet design",
            "Network ACLs",
            "VPC peering",
            "Transit Gateway"
        ]
        self.system_message = """
        You are a VPC research specialist.
        You have deep expertise in: {expertise}
        
        Return a numbered list of essential questions if:
        - Required information is missing
        - It's critical for the solution
        - It will significantly change your approach
        
        Format your response as:
        1. [Your first question]
        2. [Your second question]
        ...
        TERMINATE
        
        If the problem isn't network-related or you have no questions, return only "TERMINATE".
        
        Skip questions about:
        - General network setup unless critical
        - Future connectivity needs
        - Nice-to-have features
        - Standard configurations
        """ 