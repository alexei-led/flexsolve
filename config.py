"""Configuration settings for the AWS Support System."""
from typing import Dict, List
import os

# OpenAI API configuration
OPENAI_CONFIG: List[Dict] = [
    {
        "cache_seed": None, # Disable caching for LLM calls (temporary)
        "model": "gpt-4o",
        "api_key": os.getenv("OPENAI_API_KEY")

    }
]

# Agent names
USER_PROXY_NAME = "User"
SOLUTION_COORDINATOR_NAME = "Solution_Coordinator"
RESEARCH_COORDINATOR_NAME = "Research_Coordinator"
EKS_SPECIALIST_NAME = "EKS_Specialist"
EKS_RESEARCHER_NAME = "EKS_Researcher"
EC2_SPECIALIST_NAME = "EC2_Specialist"
EC2_RESEARCHER_NAME = "EC2_Researcher"
VPC_SPECIALIST_NAME = "VPC_Specialist"
VPC_RESEARCHER_NAME = "VPC_Researcher"
IAM_SPECIALIST_NAME = "IAM_Specialist"
IAM_RESEARCHER_NAME = "IAM_Researcher"
CLOUDWATCH_SPECIALIST_NAME = "CloudWatch_Specialist"
CLOUDWATCH_RESEARCHER_NAME = "CloudWatch_Researcher"
HUMAN_EXPERT_NAME = "AWS_Architect"


# Chat configuration
MAX_ROUND = 20