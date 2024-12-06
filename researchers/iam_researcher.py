from .base_researcher import BaseResearcher

class IAMResearcher(BaseResearcher):
    def __init__(self, openai_config):
        super().__init__(openai_config)
        self.name = "IAM_Researcher"
        self.expertise = [
            "IAM policies and roles",
            "Permission boundaries",
            "Identity federation",
            "Access management",
            "Security best practices"
        ]
        self.system_message = """You are an IAM research specialist. Your role is to:
        1. Analyze IAM-related questions
        2. Identify missing security details
        3. Suggest clarifying questions about:
           - Access patterns
           - Security requirements
           - Cross-account access
           - Federation needs
           - Compliance requirements
        
        Focus on gathering:
        - Current IAM setup
        - Access requirements
        - Security constraints
        - Audit requirements
        - Compliance needs
        
        Format questions to be:
        - Security-focused
        - Compliance-aware
        - Clear and specific
        - Risk-conscious""" 