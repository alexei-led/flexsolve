"""Main entry point for the AWS Support System."""

import autogen

from config import OPENAI_CONFIG, USER_PROXY_NAME, RESEARCH_COORDINATOR_NAME, SOLUTION_COORDINATOR_NAME, HUMAN_EXPERT_NAME

from specialists import (
    EKSSpecialist,
    CloudWatchSpecialist,
    EC2Specialist,
    VPCSpecialist,
    IAMSpecialist,
    LambdaSpecialist,
    ECSSpecialist,
    S3Specialist,
    SNSSpecialist,
    SQSSpecialist,
    RDSSpecialist,
    ElastiCacheSpecialist,
    AuroraSpecialist
)

from researchers import (
    CloudWatchResearcher,
    EC2Researcher,
    IAMResearcher,
    EKSResearcher,
    VPCResearcher,
    LambdaResearcher,
    ECSResearcher,
    S3Researcher,
    SNSResearcher,
    SQSResearcher,
    RDSResearcher,
    ElastiCacheResearcher,
    AuroraResearcher
)


def create_agents():
    """Create all the necessary agents for the system."""
    # Create the user proxy
    user_proxy = autogen.UserProxyAgent(
        name=USER_PROXY_NAME,
        human_input_mode="ALWAYS",
        code_execution_config=False,
    )

    # Create the research coordinator with modified prompt
    research_coordinator = autogen.AssistantAgent(
        name=RESEARCH_COORDINATOR_NAME,
        system_message="""
            You are an AWS Research Coordinator managing a team of AWS service researchers. Your role is to gather context through clarifying questions ONLY.

            CORE RESPONSIBILITIES:
            1. Analyze user's initial problem
            2. Route to relevant researchers for questions
            3. Consolidate researchers' questions
            4. Validate questions with human expert before presenting to user
            5. Rework questions if human expert requests it (repeat the process)
            6. Present organized questions to user if approved by human expert

            WORKFLOW:
            1. For user's input:
               - If input matches pattern "1. [answer] 2. [answer]..." -> Reply "TERMINATE"
           - If input contains phrases like "proceed", "continue with solution" -> Reply "TERMINATE"
           - Otherwise continue normal workflow:
             * Identify mentioned AWS services
             * Note potential related services
             * Spot missing technical context

            2. When engaging researchers:
               - Include ALL potentially relevant researchers
               - Provide clear context of the problem
               - Request specific types of questions needed

            3. When consolidating questions:
               - Group by AWS service/topic
               - Remove duplicate questions
               - Preserve technical context
               - DO NOT create new questions
               - DO NOT suggest solutions

            4. When handling Human Expert responses:
               - For APPROVE: Present the exact approved questions to the user
               - For REWORK: Route back to researchers with feedback

            RESPONSE FORMAT:
            After receiving researchers' input or APPROVE from Human Expert:
            "Based on our research team's analysis:

            [Service/Topic 1]:
            1. Question 1
            2. Question 2

            [Service/Topic 2]:
            3. Question 3
            4. Question 4"

            Reply with TERMINATE when:
            - User provides numbered answers to clarifying questions (e.g., "1. Yes 2. No")
        - User explicitly requests to proceed with solution
        - Follow-up interaction is non-technical
        - No further context is needed for working on the solution

            IMPORTANT:
            - Never suggest solutions
            - Only use questions from researchers
            - Focus on gathering context
            - Preserve approved questions exactly as reviewed
            """,
        llm_config={"config_list": OPENAI_CONFIG},
    )
    
    # Create the solution coordinator
    solution_coordinator = autogen.AssistantAgent(
        name=SOLUTION_COORDINATOR_NAME,
        system_message="""
            You are an AWS Solution Coordinator managing a team of AWS service specialists. Your role is to coordinate solution development.

            CORE RESPONSIBILITIES:
            1. Analyze user's requirements and context
            2. Route to relevant specialists for solutions
            3. Present specialists' solutions exactly as provided after human expert approval
            4. DO NOT modify or rewrite specialist solutions
            5. DO NOT create new solutions or formats

            WORKFLOW:
            1. For user's input:
               - Identify mentioned AWS services
               - Route to relevant specialists

            2. When presenting solutions:
               - Present the exact solutions provided by specialists and approved by human expert
               - Maintain all technical details, code examples, and formatting
               - Include all implementation steps and commands
               - Preserve the original structure and examples
               
            3. When handling Human Expert responses:
               - For APPROVE: Present the exact approved solutions to the user
               - For REWORK: Route back to specialists with feedback

            Reply with TERMINATE when:
            - Solutions have been provided
            - No viable solutions exist
            - Further context is needed
            - Human Expert has approved the solutions with "APPROVE"

            IMPORTANT:
            - Never modify specialist solutions
            - Present solutions exactly as approved
            - Maintain all technical details and examples
            - Keep original formatting and structure
            """,
        llm_config={"config_list": OPENAI_CONFIG},
    )

    # Create the human expert
    human_expert = autogen.UserProxyAgent(
        name=HUMAN_EXPERT_NAME,
        human_input_mode="ALWAYS",
        default_auto_reply="APPROVE",
        code_execution_config=False,
        description="Human Expert can APPROVE or request REWORK with feedback for clarifying questions and proposed solutions.",
        system_message="""
            You are an AWS Human Expert who reviews:
            1. Clarifying questions before they are sent to user
            2. Final solutions before they are presented to user
            
            For each review, you can:
            - Reply "APPROVE" to accept
            - Reply "REWORK: [your feedback]" to request changes
            
            Focus on technical accuracy and completeness.
        """,
        is_termination_msg=lambda msg: "APPROVE" in msg["content"].upper(),
    )

    # Create researchers
    researchers = [
        IAMResearcher(OPENAI_CONFIG).create_agent(),
        CloudWatchResearcher(OPENAI_CONFIG).create_agent(),
        EC2Researcher(OPENAI_CONFIG).create_agent(),
        EKSResearcher(OPENAI_CONFIG).create_agent(),
        VPCResearcher(OPENAI_CONFIG).create_agent(),
        LambdaResearcher(OPENAI_CONFIG).create_agent(),
        ECSResearcher(OPENAI_CONFIG).create_agent(),
        S3Researcher(OPENAI_CONFIG).create_agent(),
        SNSResearcher(OPENAI_CONFIG).create_agent(),
        SQSResearcher(OPENAI_CONFIG).create_agent(),
        RDSResearcher(OPENAI_CONFIG).create_agent(),
        ElastiCacheResearcher(OPENAI_CONFIG).create_agent(),
        AuroraResearcher(OPENAI_CONFIG).create_agent(),
    ]

    # Create specialists
    specialists = [
        IAMSpecialist(OPENAI_CONFIG).create_agent(),
        CloudWatchSpecialist(OPENAI_CONFIG).create_agent(),
        EC2Specialist(OPENAI_CONFIG).create_agent(),
        EKSSpecialist(OPENAI_CONFIG).create_agent(),
        VPCSpecialist(OPENAI_CONFIG).create_agent(),
        LambdaSpecialist(OPENAI_CONFIG).create_agent(),
        ECSSpecialist(OPENAI_CONFIG).create_agent(),
        S3Specialist(OPENAI_CONFIG).create_agent(),
        SNSSpecialist(OPENAI_CONFIG).create_agent(),
        SQSSpecialist(OPENAI_CONFIG).create_agent(),
        RDSSpecialist(OPENAI_CONFIG).create_agent(),
        ElastiCacheSpecialist(OPENAI_CONFIG).create_agent(),
        AuroraSpecialist(OPENAI_CONFIG).create_agent(),
    ]

    return user_proxy, research_coordinator, solution_coordinator, specialists, researchers, human_expert


def main():
    """Main application entry point."""
    # Create agents
    user_proxy, research_coordinator, solution_coordinator, specialists, researchers, human_expert = create_agents()
    
    # Create group chat with researchers
    researcher_group = autogen.GroupChat(
        agents=researchers + [human_expert],
        messages=[],
        speaker_selection_method="auto",
        select_speaker_auto_verbose=True,
        allow_repeat_speaker=True,
        max_round=10,
    )
    researchers_manager = autogen.GroupChatManager(
        groupchat=researcher_group,
        human_input_mode="TERMINATE",
        llm_config={"config_list": OPENAI_CONFIG},
    )
    
    # Create group chat with specialists
    specialist_group = autogen.GroupChat(
        agents=specialists + [human_expert],
        messages=[],
        speaker_selection_method="auto",
        select_speaker_auto_verbose=True,
        allow_repeat_speaker=True,
        max_round=10,
    )
    specialists_manager = autogen.GroupChatManager(
        groupchat=specialist_group,
        human_input_mode="TERMINATE",
        llm_config={"config_list": OPENAI_CONFIG},
    )

    # Create surveyer
    surveyer = autogen.AssistantAgent(
        name="surveyer",
        llm_config={"config_list": OPENAI_CONFIG},
        human_input_mode="NEVER",
        system_message="""
            You are a surveyer.
            Your ask a single question.
            You job is to get a number between 1 and 10 from the user about support experience before ending the conversation.

            Reply "TERMINATE" when you have no more questions.
        """,
    )

    # Function to determine if a question is technical using LLM
    def is_technical_question_llm(agent):
        # Use an LLM to classify the question
        classifier = autogen.AssistantAgent(
            name="question_classifier",
            llm_config={"config_list": OPENAI_CONFIG},
            system_message="""
                You are a classifier. Determine if the input is a technical question or problem that needs AWS expertise.
                
                Reply "YES" if:
                - Message asks about AWS technical issues/problems
                - Message requests technical guidance or troubleshooting
                - Message describes technical errors or system behavior
                
                Reply "NO" if:
                - Message is casual chat/greetings ("hi", "hello", etc)
                - Message is a numbered list of answers to previous questions
                - Message contains only status updates or confirmations
                - Message is non-technical feedback or comments
                
                Examples:
                "Hi there" -> "NO"
                "1. Yes 2. Production 3. Last week" -> "NO" 
                "How do I configure VPC peering?" -> "YES"
                "My Lambda function is timing out" -> "YES"
            """,
        )
        response = research_coordinator.initiate_chat(
            recipient=classifier,
            message=agent.last_message(),
            max_turns=1,
        )

        return response.summary.strip().upper() == "YES"

    # Function to handle follow-up questions that returns boolean
    def should_trigger_research(sender):
        # Only trigger for user_proxy messages
        if sender is not user_proxy:
            return False
            
        # Get last message
        try:
            last_message = sender.last_message()['content']  # Extract the content from the message dict
        except:
            return False
            
        # Skip empty messages
        if not last_message:
            return False
            
        # First check if it's a technical question
        is_technical = is_technical_question_llm(sender)
        
        # For non-technical initial messages, don't trigger research
        if not is_technical and "TERMINATE" not in last_message:
            return False
            
        # For technical questions or responses to clarifying questions
        if is_technical or (last_message and "TERMINATE" not in last_message and len(last_message.strip()) > 0):
            return True
            
        return False

    # Create research nested chats
    research_nested_chat_queue = [
        {
            "recipient": researchers_manager,
            "summary_method": "reflection_with_llm",
            "summary_args": { 
                "summary_prompt": """
                    Analyze all researcher responses and provide raw grouped questions:
                    1. Remove duplicate questions
                    2. Remove questions about already provided information
                    3. Group by AWS service/topic
                    4. Use only questions from researchers
                    5. Do not create new questions
                    6. Number all questions sequentially across all groups
                    
                    Output raw questions and groupings only, no formatting needed.
                    The Research Coordinator will handle the final formatting.
                """
            },
        },
    ]

    # Register research nested chats with fixed trigger
    research_coordinator.register_nested_chats(
        research_nested_chat_queue,
        trigger=should_trigger_research,
    )
    
    solution_nested_chat_queue = [
        {
            "recipient": specialists_manager,
            "summary_method": "reflection_with_llm",
            "summary_args": { 
                "summary_prompt": """
                    Aggregate specialists' solutions with these rules:
                    1. REMOVE duplicate solutions
                    2. REMOVE solutions not relevant to the user's problem
                    3. For conflicting solutions, keep the most relevant specialist's solution
                    4. Preserve all technical content exactly as provided
                    
                    Output raw solutions only, no additional formatting needed.
                    The Solution Coordinator will handle the final presentation.
                """
            },
        },
    ]

    # Create solution nested chats
    solution_coordinator.register_nested_chats(
        solution_nested_chat_queue,
        trigger=user_proxy,
    )
    
    # user starts the conversation with the coordinator
    user_proxy.initiate_chats(
        [
            {
                "recipient": research_coordinator,
                "message": "hi",
                "summary_method": "reflection_with_llm",
            },
            {
                "recipient": solution_coordinator,
                "message": "Based on the research findings, create a detailed solution plan.",
                "summary_method": "last_msg",
            },
            {
                "recipient": surveyer,
                "message": "Based on the provided information, determine whether the user is satisfied with the support experience.",
                "carryover": "The customer is a newbie AWS user.",
            },
        ]
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
