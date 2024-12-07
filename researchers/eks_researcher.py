from .base_researcher import BaseResearcher

class EKSResearcher(BaseResearcher):
    def __init__(self, openai_config):
        super().__init__(openai_config)
        self.name = "EKS_Researcher"
        self.expertise = [
            "EKS cluster architecture",
            "Kubernetes workloads",
            "Container orchestration",
            "EKS networking",
            "EKS security"
        ]
        self.system_message = """
        You are an EKS research specialist.
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
        
        If the problem isn't EKS-related or you have no questions, return only "TERMINATE".
        
        Skip questions about:
        - General cluster setup unless critical
        - Future scaling plans
        - Nice-to-have features
        - Standard configurations
        """ 