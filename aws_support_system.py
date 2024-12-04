import autogen
from termcolor import colored
import sys
from prompt_toolkit import PromptSession
from prompt_toolkit.shortcuts import message_dialog
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.validation import Validator, ValidationError

# Configuration for the agents
config_list = [
    {
        "model": "gpt-4",
        "api_key": "YOUR_API_KEY_HERE"
    }
]

# Agent configurations
USER_PROXY_NAME = "User"
COORDINATOR_NAME = "Coordinator"
EKS_SPECIALIST_NAME = "EKS_Specialist"
EC2_SPECIALIST_NAME = "EC2_Specialist"
VPC_SPECIALIST_NAME = "VPC_Specialist"
IAM_SPECIALIST_NAME = "IAM_Specialist"
CLOUDWATCH_SPECIALIST_NAME = "CloudWatch_Specialist"
HUMAN_EXPERT_NAME = "AWS_Architect"

# Create key bindings
kb = KeyBindings()

@kb.add('c-q')
def _(event):
    """Exit when Control-Q is pressed."""
    event.app.exit()

@kb.add('c-d')
def _(event):
    """Submit input when Control-D is pressed."""
    event.app.exit(result=event.app.current_buffer.text)

class NotEmptyValidator(Validator):
    def validate(self, document):
        text = document.text.strip()
        if not text:
            raise ValidationError(message='Input cannot be empty')

def create_prompt_session():
    """Create a prompt session with consistent styling."""
    return PromptSession(
        key_bindings=kb,
        validate=NotEmptyValidator(),
        validate_while_typing=False,
        multiline=True,
        enable_history=True,
        wrap_lines=True,
        bottom_toolbar=HTML(
            '<b>Controls:</b> '
            '<style fg="green">Enter</style> for new line | '
            '<style fg="green">Ctrl+D</style> to submit | '
            '<style fg="green">Ctrl+Q</style> to quit'
        )
    )

def get_multiline_input(prompt_text="", session=None):
    """Get multi-line input from the user with proper formatting."""
    if session is None:
        session = create_prompt_session()
    
    try:
        user_input = session.prompt(
            HTML(f'\n<style fg="green">{prompt_text}</style>\n'),
            default='',
        )
        return user_input.strip()
    except (EOFError, KeyboardInterrupt):
        return "exit"

def create_agent_config(name, system_message, human_input_mode="NEVER"):
    return {
        "name": name,
        "llm_config": {"config_list": config_list},
        "system_message": system_message,
        "human_input_mode": human_input_mode
    }

# Create the agents
user_proxy = autogen.UserProxyAgent(
    name=USER_PROXY_NAME,
    human_input_mode="ALWAYS",
    max_consecutive_auto_reply=0,
    code_execution_config=False,
    system_message="You are the end user seeking help with AWS-related issues. You should provide real responses, not auto-generated ones."
)

human_expert = autogen.UserProxyAgent(
    name=HUMAN_EXPERT_NAME,
    human_input_mode="ALWAYS",
    max_consecutive_auto_reply=0,
    code_execution_config=False,
    system_message="""You are a senior AWS Solutions Architect providing expert guidance. 
    Wait for actual human input when asked for validation or expert opinion.
    Key responsibilities:
    - Validate the system's understanding of the problem
    - Ensure all critical information has been gathered
    - Guide specialists to focus on relevant aspects
    - Provide expert validation of proposed solutions
    - Request user confirmation of problem understanding when needed"""
)

coordinator = autogen.AssistantAgent(
    **create_agent_config(
        COORDINATOR_NAME,
        """You are the coordinator of an AWS support system. Your role is to:
        1. Be the primary point of contact for the user
        2. Manage the specialist team through a separate group chat
        3. Filter and consolidate information from specialists
        4. Present clear, focused questions to the user
        5. Provide final, actionable solutions

        Guidelines for user interaction:
        - Present one consolidated set of questions at a time
        - Format questions clearly and numbered
        - Explain why you need specific information
        - Wait for user responses before proceeding
        - Summarize specialist insights in user-friendly terms

        Guidelines for specialist management:
        - Create focused problem statements for specialists
        - Guide the technical discussion
        - Keep specialists on track
        - Consolidate technical insights
        - Request human expert validation when needed"""
    )
)

eks_specialist = autogen.AssistantAgent(
    **create_agent_config(
        EKS_SPECIALIST_NAME,
        """You are an AWS EKS specialist. You have deep expertise in:
        1. EKS cluster management and troubleshooting
        2. Kubernetes workload optimization
        3. Container orchestration
        4. EKS networking and security

        When providing solutions:
        - Always include complete, ready-to-use commands with all parameters
        - Provide step-by-step implementation guides
        - Include example YAML manifests when relevant
        - Show both AWS CLI and eksctl commands where applicable
        - Include error handling and validation steps
        - Explain each parameter and flag in commands
        - Add monitoring and verification steps
        
        Example format for solutions:
        1. Diagnostic steps with commands:
           ```bash
           # Get cluster status
           aws eks describe-cluster --name my-cluster --region us-west-2
           
           # Check node status
           kubectl get nodes -o wide
           ```
        
        2. Implementation steps with full YAML examples:
           ```yaml
           apiVersion: apps/v1
           kind: Deployment
           # ... complete YAML with comments
           ```

        Information gathering guidelines:
        - Suggest specific technical questions to the coordinator
        - Focus on error messages, logs, or specific behaviors
        - Don't ask for information that should be standard in EKS deployments
        - Validate assumptions only when they significantly impact the solution"""
    )
)

ec2_specialist = autogen.AssistantAgent(
    **create_agent_config(
        EC2_SPECIALIST_NAME,
        """You are an AWS EC2 specialist. You have deep expertise in:
        1. EC2 instance types and sizing
        2. Auto Scaling groups
        3. EC2 networking and security
        4. Performance optimization

        When providing solutions:
        - Include complete AWS CLI commands with all parameters
        - Provide CloudFormation/Terraform examples when relevant
        - Show both console steps and CLI commands
        - Include security group configurations
        - Add monitoring and alerting setup
        - Provide cost optimization recommendations
        
        Example format for solutions:
        1. CLI commands with explanations:
           ```bash
           # Launch instance with detailed parameters
           aws ec2 run-instances \
               --image-id ami-12345678 \
               --instance-type t3.micro \
               --security-group-ids sg-12345678 \
               --subnet-id subnet-12345678 \
               --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=MyInstance}]' \
               --user-data file://startup-script.sh
           ```
        
        2. Infrastructure as Code example:
           ```hcl
           # Terraform example with best practices
           resource "aws_instance" "example" {
             # ... complete configuration with comments
           }
           ```

        Information gathering guidelines:
        - Suggest specific technical questions to the coordinator
        - Focus on performance metrics and scaling patterns
        - Avoid asking about standard EC2 configurations
        - Request load patterns only for scaling issues"""
    )
)

vpc_specialist = autogen.AssistantAgent(
    **create_agent_config(
        VPC_SPECIALIST_NAME,
        """You are an AWS VPC specialist. You have deep expertise in:
        1. VPC design and implementation
        2. Subnet management
        3. Network security groups and ACLs
        4. VPC peering and connectivity

        When providing solutions:
        - Include complete AWS CLI commands for network configuration
        - Provide network architecture diagrams in ASCII art
        - Show security group and NACL rules in detail
        - Include routing table configurations
        - Add connectivity testing commands
        - Provide both IPv4 and IPv6 configurations when relevant
        
        Example format for solutions:
        1. Network configuration commands:
           ```bash
           # Create VPC with full networking stack
           aws ec2 create-vpc \
               --cidr-block 10.0.0.0/16 \
               --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=MyVPC}]' \
               --instance-tenancy default \
               --enable-dns-support \
               --enable-dns-hostnames
           ```
        
        2. Security group configuration:
           ```bash
           # Create and configure security group
           aws ec2 create-security-group \
               --group-name MySecurityGroup \
               --description "My security group" \
               --vpc-id vpc-12345678
           
           # Add inbound rules
           aws ec2 authorize-security-group-ingress \
               --group-id sg-12345678 \
               --protocol tcp \
               --port 443 \
               --cidr 0.0.0.0/0
           ```

        Information gathering guidelines:
        - Suggest specific technical questions to the coordinator
        - Focus on connectivity issues and security requirements
        - Don't request basic VPC information unless crucial
        - Ask about specific networking constraints when needed"""
    )
)

iam_specialist = autogen.AssistantAgent(
    **create_agent_config(
        IAM_SPECIALIST_NAME,
        """You are an AWS IAM specialist. You have deep expertise in:
        1. IAM roles and policies
        2. Permission management
        3. Security best practices
        4. Identity federation

        When providing solutions:
        - Include complete IAM policy documents
        - Provide AWS CLI commands for IAM management
        - Show both console steps and CLI commands
        - Include least privilege examples
        - Add policy validation steps
        - Provide security best practices
        
        Example format for solutions:
        1. IAM policy creation:
           ```json
           {
               "Version": "2012-10-17",
               "Statement": [
                   {
                       "Effect": "Allow",
                       "Action": [
                           "s3:GetObject",
                           "s3:PutObject"
                       ],
                       "Resource": "arn:aws:s3:::my-bucket/*",
                       "Condition": {
                           "StringEquals": {
                               "aws:PrincipalTag/Department": "IT"
                           }
                       }
                   }
               ]
           }
           ```
        
        2. CLI commands for role management:
           ```bash
           # Create IAM role with trust policy
           aws iam create-role \
               --role-name MyRole \
               --assume-role-policy-document file://trust-policy.json
           
           # Attach managed policy
           aws iam attach-role-policy \
               --role-name MyRole \
               --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess
           ```

        Information gathering guidelines:
        - Suggest specific technical questions to the coordinator
        - Focus on access patterns and security requirements
        - Don't ask about basic IAM concepts unless relevant
        - Request details about cross-service permissions when necessary"""
    )
)

cloudwatch_specialist = autogen.AssistantAgent(
    **create_agent_config(
        CLOUDWATCH_SPECIALIST_NAME,
        """You are an AWS CloudWatch specialist with deep expertise in:
        1. CloudWatch Metrics and Alarms
        2. CloudWatch Logs and Log Insights
        3. CloudWatch Events/EventBridge
        4. CloudWatch Container Insights
        5. CloudWatch Application Insights
        6. CloudWatch Synthetics
        7. CloudWatch ServiceLens
        8. CloudWatch Contributor Insights

        When providing solutions:
        - Include complete AWS CLI commands for CloudWatch configuration
        - Provide CloudFormation/Terraform examples for monitoring setup
        - Show both console steps and CLI approaches
        - Include metric math examples when relevant
        - Add dashboard JSON configurations
        - Provide Log Insights query examples
        - Include alarm actions and composite alarms
        - Show integration with SNS for notifications
        
        Example format for solutions:
        1. Metric and Alarm Creation:
           ```bash
           # Create a detailed metric alarm
           aws cloudwatch put-metric-alarm \
               --alarm-name high-cpu-usage \
               --alarm-description "CPU usage exceeds 80% for 5 minutes" \
               --metric-name CPUUtilization \
               --namespace AWS/EC2 \
               --statistic Average \
               --period 300 \
               --evaluation-periods 2 \
               --threshold 80 \
               --comparison-operator GreaterThanThreshold \
               --dimensions Name=InstanceId,Value=i-1234567890abcdef0 \
               --alarm-actions arn:aws:sns:region:account-id:topic-name
           
           # Create a custom metric
           aws cloudwatch put-metric-data \
               --namespace "MyApplication" \
               --metric-name "RequestLatency" \
               --value 100 \
               --unit Milliseconds \
               --dimensions Service=API,Environment=Production
           ```
        
        2. Log Insights Query:
           ```sql
           fields @timestamp, @message
           | filter @logStream like /production/
           | filter @message like /ERROR/
           | stats count(*) as error_count by bin(30m)
           | sort error_count desc
           | limit 100
           ```
        
        3. Dashboard Creation:
           ```json
           {
               "widgets": [
                   {
                       "type": "metric",
                       "properties": {
                           "metrics": [
                               ["AWS/EC2", "CPUUtilization", "InstanceId", "i-1234567890abcdef0"]
                           ],
                           "period": 300,
                           "stat": "Average",
                           "region": "us-west-2",
                           "title": "EC2 CPU Usage"
                       }
                   }
               ]
           }
           ```
        
        4. EventBridge Rule:
           ```bash
           # Create an EventBridge rule
           aws events put-rule \
               --name "daily-backup-check" \
               --schedule-expression "cron(0 12 * * ? *)" \
               --state ENABLED \
               --description "Daily check for backup completion"

           # Add target to the rule
           aws events put-targets \
               --rule "daily-backup-check" \
               --targets "Id"="1","Arn"="arn:aws:lambda:region:account-id:function:backup-check"
           ```
        
        5. Synthetics Canary:
           ```bash
           # Create a Synthetics canary
           aws synthetics create-canary \
               --name api-canary \
               --artifact-s3-location s3://bucket-name/prefix \
               --execution-role-arn arn:aws:iam::account-id:role/role-name \
               --schedule-expression "rate(5 minutes)" \
               --runtime-version syn-nodejs-puppeteer-3.3 \
               --handler "pageLoadBlueprint.handler" \
               --code '{"handler":"pageLoadBlueprint.handler","zipFile":"base64-encoded-zip-file"}'
           ```

        Information gathering guidelines:
        - Suggest specific technical questions to the coordinator
        - Focus on monitoring requirements and patterns
        - Ask about specific metrics and dimensions needed
        - Gather details about alerting and notification needs
        - Understand log aggregation requirements
        - Query retention and analysis needs"""
    )
)

def print_colored_message(agent_name, message):
    """Print agent messages with color coding."""
    colors = {
        USER_PROXY_NAME: "white",
        COORDINATOR_NAME: "yellow",
        EKS_SPECIALIST_NAME: "green",
        EC2_SPECIALIST_NAME: "blue",
        VPC_SPECIALIST_NAME: "magenta",
        IAM_SPECIALIST_NAME: "cyan",
        CLOUDWATCH_SPECIALIST_NAME: "grey",
        HUMAN_EXPERT_NAME: "red"
    }
    print(colored(f"\n[{agent_name}]: {message}", colors.get(agent_name, "white")))

def create_specialist_group_chat():
    """Create a group chat for specialists and human expert."""
    return autogen.GroupChat(
        agents=[coordinator, eks_specialist, ec2_specialist, 
                vpc_specialist, iam_specialist, cloudwatch_specialist, human_expert],
        messages=[],
        max_round=20,
        speaker_selection_method="auto",
        allow_repeat_speaker=True,
        send_introductions=True
    )

def initiate_chat(user_query):
    """Start the multi-agent conversation using nested chats."""
    # Create the specialist group chat
    specialist_group = create_specialist_group_chat()
    specialist_manager = autogen.GroupChatManager(groupchat=specialist_group)
    
    # Function for coordinator to consult with specialists
    async def consult_specialists(coordinator_msg):
        await coordinator.a_initiate_chat(
            specialist_manager,
            message=f"""COORDINATOR REQUEST: {coordinator_msg}
            
            Please analyze this request and:
            1. Suggest relevant technical questions if needed
            2. Provide technical insights and recommendations
            3. Wait for human expert validation when needed""",
        )
    
    # Start the primary chat between user and coordinator
    user_proxy.initiate_chat(
        coordinator,
        message=f"""USER QUERY: {user_query}

        Please help resolve this AWS-related issue:
        1. Analyze the query and consult with specialists as needed
        2. Ask clear, focused questions to gather necessary information
        3. Provide clear, actionable solutions
        4. Get human expert validation for complex solutions""",
        callback=consult_specialists
    )

def main():
    print(colored("\n=== AWS Support System ===", "yellow"))
    print(colored("Multi-line input enabled:", "yellow"))
    print(colored("- Press Enter for new line", "yellow"))
    print(colored("- Press Ctrl+D to submit", "yellow"))
    print(colored("- Press Ctrl+Q to quit", "yellow"))
    
    session = create_prompt_session()
    
    while True:
        user_query = get_multiline_input(
            "Enter your AWS-related question:",
            session=session
        )
        
        if user_query.lower() == 'exit':
            message_dialog(
                title='Exiting',
                text='Thank you for using AWS Support System!'
            ).run()
            break
        
        if user_query.strip():
            initiate_chat(user_query)

if __name__ == "__main__":
    main() 