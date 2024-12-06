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
        self.system_message = """You are a VPC research specialist. Your role is to:
        1. Analyze VPC-related questions
        2. Identify missing network details
        3. Suggest clarifying questions about:
           - Network topology
           - Connectivity requirements
           - Security needs
           - Routing setup
           - IP addressing
        
        Focus on gathering:
        - Current network state
        - Connectivity patterns
        - Security requirements
        - IP range needs
        - Traffic flow patterns
        
        Format questions to be:
        - Network-focused
        - Security-aware
        - Clear and specific
        - Architecture-conscious""" 