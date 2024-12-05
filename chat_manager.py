"""Chat manager for the AWS Support System."""
import autogen
from termcolor import colored
from typing import List, Dict, Any, Optional
from config import AGENT_COLORS, MAX_ROUND
from utils.input_handler import get_user_input, create_prompt_session

class ChatManager:
    def __init__(self, coordinator, specialists: List[autogen.AssistantAgent], human_expert):
        """Initialize the chat manager."""
        self.coordinator = coordinator
        self.specialists = specialists
        self.human_expert = human_expert
        self.specialist_group = None
        self.specialist_manager = None
        self.prompt_session = create_prompt_session()
        
    def create_specialist_group(self):
        """Create a group chat for specialists and human expert."""
        if not self.specialist_group:
            self.specialist_group = autogen.GroupChat(
                agents=[self.coordinator] + self.specialists + [self.human_expert],
                messages=[],
                max_round=MAX_ROUND,
                speaker_selection_method="auto",
                allow_repeat_speaker=True,
                send_introductions=True
            )
            self.specialist_manager = autogen.GroupChatManager(
                groupchat=self.specialist_group,
                is_termination_msg=self._is_termination_msg,
            )
        return self.specialist_group, self.specialist_manager
    
    def _is_termination_msg(self, message: Dict[str, Any]) -> bool:
        """Determine if the conversation should terminate."""
        if isinstance(message, dict):
            content = message.get("content", "")
            # Terminate if human expert has validated the solution
            if message.get("name") == self.human_expert.name and (
                "APPROVE" in content
            ):
                return True
            # Terminate if coordinator indicates completion
            if message.get("name") == self.coordinator.name and (
                "SPECIALIST_CONSULTATION_COMPLETE" in content
            ):
                return True
        return False

    def print_message(self, agent_name: str, message: str):
        """Print agent messages with color coding."""
        print(colored(f"\n[{agent_name}]: {message}", AGENT_COLORS.get(agent_name, "white")))

    def print_header(self):
        """Print the FlexSolve header with controls."""
        print(colored("\n=== DoiT FlexSolve ===", "yellow"))

    def format_prompt(self, message: str, agent_type: str = "user") -> str:
        """Format the prompt message based on agent type."""
        if agent_type == "expert":
            return f"""AWS Architect Review Required:

Please review the following proposal and provide your expert feedback:

{message}

Guidelines for review:
- Validate the technical approach
- Check for security best practices
- Assess scalability and reliability
- Consider cost implications
- Suggest improvements if needed

Your response format:
```
EXPERT REVIEW:
1. Technical Assessment:
   [Your comments]
2. Security Review:
   [Your comments]
3. Scalability & Reliability:
   [Your comments]
4. Cost Considerations:
   [Your comments]
5. Recommendations:
   [Your suggestions]

Decision: [APPROVE/REJECT]
Reason: [Brief explanation]
```
"""
        else:
            return f"{message}\n\nYour response:"

    def handle_specialist_request(self, message: str) -> Optional[str]:
        """Handle request in the specialist group chat."""
        _, manager = self.create_specialist_group()
        
        # Start the specialist discussion
        self.coordinator.initiate_chat(
            manager,
            message=f"""COORDINATOR REQUEST: {message}

            As the coordinator, I need the team's expertise to address this AWS-related issue.

            PROCESS:
            1. Initial Assessment:
               - Identify relevant AWS services
               - Determine required specialist expertise
               - Highlight potential dependencies or conflicts

            2. Information Gathering:
               - Specialists: suggest specific technical questions
               - Coordinator: I will relay questions to the user
               - Focus on critical information only

            3. Solution Development:
               - Propose technical solutions with implementation details
               - Include complete commands and configurations
               - Consider security, scalability, and cost implications
               - Address potential risks and mitigation strategies

            4. Validation Steps:
               - Human Expert: Review proposed solutions
               - Validate architectural decisions
               - Confirm best practices compliance
               - Approve final implementation plan

            GUIDELINES:
            - Specialists: Focus on your domain expertise
            - Provide detailed, actionable guidance
            - Include all necessary commands and configurations
            - Highlight dependencies and prerequisites
            - Consider security implications
            - Think about cost optimization
            - Address potential failure scenarios

            RESPONSE FORMAT:
            1. For Questions:
               ```
               CLARIFICATION NEEDED:
               1. [Specific question]
               2. [Specific question]
               Reason: [Why this information is critical]
               ```

            2. For Solutions:
               ```
               PROPOSED SOLUTION:
               1. Overview:
                  - Purpose
                  - Architecture
                  - Components

               2. Implementation Steps:
                  [Detailed steps with commands]

               3. Validation:
                  [Testing and verification steps]

               4. Monitoring:
                  [Monitoring and alerting setup]
               ```

            3. For Validation:
               ```
               SOLUTION VALIDATION:
               - Architecture Review: [Comments]
               - Security Review: [Comments]
               - Cost Analysis: [Comments]
               - Risk Assessment: [Comments]
               Decision: [APPROVE/REJECT]
               Reason: [Brief explanation]
               ```

            Let's begin by analyzing the request and identifying the key areas that need attention.""",
        )
        
        # Return the last message from the conversation
        if self.specialist_group.messages:
            return self.specialist_group.messages[-1]["content"]
        return None

    def get_human_input(self, message: str, agent_type: str = "user") -> str:
        """Get input from human user with proper formatting."""
        self.print_header()
        formatted_prompt = self.format_prompt(message, agent_type)
        return get_user_input(formatted_prompt, self.prompt_session)

    def initiate_chat(self, user_proxy: autogen.UserProxyAgent, user_query: str):
        """Start the multi-agent conversation."""
        def reply_func(recipient, messages, sender, config):
            """Handle replies from the coordinator."""
            if recipient == user_proxy:
                last_message = messages[-1]["content"]
                
                # Determine if this is a request for expert review
                is_expert_review = (
                    "PROPOSED SOLUTION" in last_message or
                    "REVIEW NEEDED" in last_message or
                    "VALIDATION REQUIRED" in last_message
                )
                
                if "CLARIFICATION NEEDED:" in last_message or "?" in last_message:
                    # Extract just the questions part if it's a CLARIFICATION NEEDED message
                    if "CLARIFICATION NEEDED:" in last_message:
                        questions_start = last_message.find("CLARIFICATION NEEDED:")
                        prompt_content = last_message[questions_start:]
                    else:
                        prompt_content = last_message
                    
                    # Get user's response using the shared input handler
                    user_response = self.get_human_input(prompt_content, "user")
                    if user_response.lower() == "exit":
                        return True  # End the conversation
                    
                    # Pass the response to specialists
                    self.handle_specialist_request(
                        f"USER RESPONSE:\n{user_response}\n\nPlease analyze this information and continue with the solution."
                    )
                elif is_expert_review:
                    # Get expert's review using the shared input handler
                    expert_response = self.get_human_input(last_message, "expert")
                    if expert_response.lower() == "exit":
                        return True  # End the conversation
                    
                    # Pass the expert review to specialists
                    self.handle_specialist_request(
                        f"EXPERT REVIEW:\n{expert_response}\n\nPlease proceed based on the expert's feedback."
                    )
                else:
                    # Pass non-question messages to specialists
                    self.handle_specialist_request(last_message)
            return False  # Continue the conversation
        
        # Set up the reply functions
        user_proxy.register_reply([self.coordinator], reply_func)
        
        # Start the conversation between user and coordinator
        user_proxy.initiate_chat(
            self.coordinator,
            message=f"""USER QUERY: {user_query}

            I'll help coordinate our AWS support team to address your request.

            Our process:
            1. Initial Assessment
               - Understand your requirements
               - Identify relevant AWS services
               - Determine necessary expertise

            2. Information Gathering
               - Ask clarifying questions if needed
               - Collect technical details
               - Understand constraints and preferences

            3. Solution Development
               - Work with specialists to design solution
               - Consider security, scalability, and cost
               - Prepare detailed implementation plan

            4. Solution Validation
               - Review by AWS architect
               - Validate best practices
               - Ensure completeness and accuracy

            5. Final Delivery
               - Provide step-by-step implementation guide
               - Include all necessary commands
               - Add monitoring and validation steps

            Let me analyze your query and consult with our specialists."""
        )
  