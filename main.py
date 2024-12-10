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
               - Identify mentioned AWS services
               - Note potential related services
               - Spot missing technical context

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
            - User provides answers to questions
            - Interaction is non-technical
            - No further context is needed
            - Human Expert has approved the questions with "APPROVE"

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
        code_execution_config=False,
        description="Expert who can APPROVE or request REWORK with feedback for clarifying questions and proposed solutions.",
        system_message="""
            You are an AWS Expert who reviews:
            1. Clarifying questions before they are sent to users
            2. Final solutions before they are presented
            
            For each review, you can:
            - Reply "APPROVE" to accept
            - Reply "REWORK: [your feedback]" to request changes
            
            Focus on technical accuracy and completeness.
            
            Reply with TERMINATE when APPROVED (questions or solutions)
        """,
        is_termination_msg=lambda x: x.get("content", "").find("APPROVE") >= 0,
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
        llm_config={"config_list": OPENAI_CONFIG},
    )

    # Create surveyer
    surveyer = autogen.AssistantAgent(
        name="surveyer",
        llm_config={"config_list": OPENAI_CONFIG},
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
                You are a classifier. Determine if the following question is technical in nature.
                Reply with "YES" if it is technical, otherwise reply with "NO".
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
                    Analyze all researcher responses and:
                    1. Identify missing technical details
                    2. Group questions by AWS service
                    3. Remove duplicates while preserving context
                    4. Do not invent new questions, use the questions provided by the researchers only!
                    5. Number the questions sequentially
                    
                    Format: 
                    [Service/Topic 1]:
                    1. Question 1 
                    2. Question 2
                    ...

                    [Service/Topic 2]:
                    3. Question 3
                    4. Question 4
                    ...

                    IMPORTANT:
                    - Only use questions from researchers
                    - Remove questions about info already provided
                    - Group similar questions together
                    - Keep questions focused and non-redundant
                    - This exact output will be shown to the user after approval
                    - Maintain question numbering and formatting for final display
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
                    Present the specialists' solutions exactly as provided, with NO modifications:

                    1. DO NOT rewrite or reformat solutions
                    2. DO NOT modify any technical details or examples
                    3. DO NOT summarize or shorten solutions
                    
                    ALLOWED MODIFICATIONS:
                    1. REMOVE duplicate solutions
                    2. REMOVE solutions that are not relevant to the user's problem
                    3. For conflicting solutions, keep the one that is most relevant (by most relevant expert) to the user's problem and REMOVE the others

                    For each specialist that provided a solution:
                    1. Include their complete solution with all:
                       - Code examples
                       - Implementation steps
                       - Commands
                       - YAML files
                       - Technical details
                       - Considerations
                    2. Maintain their original formatting and structure
                    3. Keep all explanations and comments

                    Format:
                    [Specialist Name]'s Solution:
                    [Present their complete solution exactly as provided]

                    [Next Specialist Name]'s Solution:
                    [Present their complete solution exactly as provided]

                    IMPORTANT:
                    - This is a direct presentation task, not a summarization
                    - Keep all technical details intact
                    - Preserve code blocks and examples exactly as given
                    - Maintain original formatting and structure
                    - Do not add any additional commentary or organization
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
