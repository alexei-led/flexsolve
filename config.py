"""Configuration settings for the AWS Support System."""
from typing import Dict, List
import os

# OpenAI API configuration
OPENAI_CONFIG: List[Dict] = [
    {
        "model": "gpt-4o",
        "api_key": os.getenv("OPENAI_API_KEY")
    }
]

# Agent names
USER_PROXY_NAME = "User"
COORDINATOR_NAME = "Coordinator"
EKS_SPECIALIST_NAME = "EKS_Specialist"
EC2_SPECIALIST_NAME = "EC2_Specialist"
VPC_SPECIALIST_NAME = "VPC_Specialist"
IAM_SPECIALIST_NAME = "IAM_Specialist"
CLOUDWATCH_SPECIALIST_NAME = "CloudWatch_Specialist"
HUMAN_EXPERT_NAME = "AWS_Architect"

# Color configuration for terminal output
AGENT_COLORS = {
    USER_PROXY_NAME: "white",
    COORDINATOR_NAME: "yellow",
    EKS_SPECIALIST_NAME: "green",
    EC2_SPECIALIST_NAME: "blue",
    VPC_SPECIALIST_NAME: "magenta",
    IAM_SPECIALIST_NAME: "cyan",
    CLOUDWATCH_SPECIALIST_NAME: "grey",
    HUMAN_EXPERT_NAME: "red"
}

# Chat configuration
MAX_ROUND = 20