"""Main entry point for the AWS Support System."""

import autogen

from config import OPENAI_CONFIG, USER_PROXY_NAME, RESEARCH_COORDINATOR_NAME, SOLUTION_COORDINATOR_NAME

from specialists import (
    EKSSpecialist,
    CloudWatchSpecialist,
    EC2Specialist,
    VPCSpecialist,
    IAMSpecialist,
)

from researchers import (
    CloudWatchResearcher,
    EC2Researcher,
    IAMResearcher,
    EKSResearcher,
    VPCResearcher,
)


def create_agents():
    """Create all the necessary agents for the system."""
    # Create the user proxy
    user_proxy = autogen.UserProxyAgent(
        name=USER_PROXY_NAME,
        human_input_mode="ALWAYS",
        code_execution_config=False,
    )

    # Create the research coordinator with simplified prompt
    research_coordinator = autogen.AssistantAgent(
        name=RESEARCH_COORDINATOR_NAME,
        system_message="""
            You are an AWS Research Coordinator managing a team of AWS service researchers. Your role is to gather context through clarifying questions ONLY.

            CORE RESPONSIBILITIES:
            1. Analyze user's initial problem
            2. Route to relevant researchers for questions
            3. Consolidate researchers' questions
            4. Present organized questions to user

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

            RESPONSE FORMAT:
            For technical queries:
            "Routing to research team for [context gaps].
            Will return with clarifying questions."

            After receiving researcher input:
            "Based on our research team's analysis:

            [Service/Topic 1]:
            - Question 1
            - Question 2

            [Service/Topic 2]:
            - Question 3
            - Question 4"

            Reply with TERMINATE when:
            - User provides answers to questions
            - Interaction is non-technical
            - No further context is needed

            IMPORTANT:
            - Never suggest solutions
            - Only use questions from researchers
            - Focus on gathering context
            """,
        llm_config={"config_list": OPENAI_CONFIG},
    )
    
    # Create the solution coordinator
    solution_coordinator = autogen.AssistantAgent(
        name=SOLUTION_COORDINATOR_NAME,
        system_message="""
            You are an AWS Solution Coordinator focused on problem solving and solution design.

            CORE RESPONSIBILITIES:
            1. Direct user interaction
            2. Specialist team coordination
            3. Solution consolidation and refinement

            WORKFLOW:
            1. Analyze the problem and identify which AWS services are involved
            2. Engage ALL relevant specialists based on the services involved
            3. Direct each specialist to focus on their domain expertise
            4. Guide specialists to:
               - Propose viable solutions
               - Consider best practices
               - Evaluate trade-offs
            5. Consolidate ALL specialists' solutions into a comprehensive list:
               - Remove duplicates
               - Combine complementary approaches
               - Evaluate each solution for:
                 * Complexity
                 * Cost considerations
                 * Scalability
                 * Operational overhead
                 * AWS best practices alignment

            RESPONSE FORMAT:
            Always structure your response as:
            
            Solutions Found:
            [If solutions exist]:
            1. [Solution Name]
               Implementation:
               - Step 1
               - Step 2
               ...
               Considerations:
               - Complexity: [Low/Medium/High]
               - Cost: [Low/Medium/High]
               - Scalability: [Low/Medium/High]
               - Best Practices: [List key alignments]
               - Trade-offs: [List main trade-offs]
            
            2. [Next Solution...]
            
            [If no viable solutions]:
            No viable solutions found for the given requirements.
            
            Comparison Summary:
            [Brief comparison of solutions, highlighting key differences and recommendations]
            
            TERMINATE

            COMMUNICATION STYLE:
            - Be concise and technical
            - Focus on actionable details
            - Highlight key decision factors
            - Provide clear recommendations
        """,
        llm_config={"config_list": OPENAI_CONFIG},
    )

    # Create the human expert
    human_expert = autogen.UserProxyAgent(
        name="AWS_Architect",
        human_input_mode="ALWAYS",
        code_execution_config=False,
        description="This agent can approve or refine clarifying questions and validate the proposed solutions returned by the specialists.",
    )

    # Create researchers
    researchers = [
        IAMResearcher(OPENAI_CONFIG).create_agent(),
        CloudWatchResearcher(OPENAI_CONFIG).create_agent(),
        EC2Researcher(OPENAI_CONFIG).create_agent(),
        EKSResearcher(OPENAI_CONFIG).create_agent(),
        VPCResearcher(OPENAI_CONFIG).create_agent(),
    ]

    # Create specialists
    specialists = [
        IAMSpecialist(OPENAI_CONFIG).create_agent(),
        CloudWatchSpecialist(OPENAI_CONFIG).create_agent(),
        EC2Specialist(OPENAI_CONFIG).create_agent(),
        EKSSpecialist(OPENAI_CONFIG).create_agent(),
        VPCSpecialist(OPENAI_CONFIG).create_agent(),
    ]

    # Add new formatter agent
    formatter = autogen.AssistantAgent(
        name="formatter",
        llm_config={"config_list": OPENAI_CONFIG},
        system_message="""You are a formatting specialist. Your job is to:
        1. Format responses from the specialist team
        2. For questions:
           - Create numbered or bulleted lists
           - Highlight key terms in bold
           - Group related questions
        3. For solutions:
           - Create clear step-by-step instructions using markdown
           - Add proper code blocks with syntax highlighting
           - Include relevant AWS documentation links
           - Use headers and sections for better readability
           - Highlight important warnings or notes
        
        Always maintain technical accuracy while improving readability.
        Reply with the formatted content only, no meta-commentary.""",
    )

    return user_proxy, research_coordinator, solution_coordinator, specialists, researchers, human_expert, formatter


def main():
    """Main application entry point."""
    # Create agents
    user_proxy, research_coordinator, solution_coordinator, specialists, researchers, human_expert, formatter = create_agents()
    
    # Create group chat with researchers
    researcher_group = autogen.GroupChat(
        agents=researchers,
        messages=[],
        speaker_selection_method="auto",
        allow_repeat_speaker=False,
        max_round=2,
    )
    researchers_manager = autogen.GroupChatManager(
        groupchat=researcher_group,
        llm_config={"config_list": OPENAI_CONFIG},
    )
    
    # Create group chat with specialists
    specialist_group = autogen.GroupChat(
        agents=specialists,
        messages=[],
        select_speaker_auto_verbose=True,
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
                    
                    Format: 
                    [Service/Topic 1]:
                    - Question 1 
                    - Question 2

                    [Service/Topic 2]:
                    - Question 3
                    - Question 4

                    IMPORTANT:
                    - Only use questions from researchers
                    - Remove questions about info already provided
                    - Group similar questions together
                    - Keep questions focused and non-redundant
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
        },
        # {
        #     "recipient": human_expert,
        #     "summary_method": "reflection_with_llm",
        #     "message": """
        #         Please validate the solution.
        #         Reply with:
        #         - 'APPROVE' if the solution is good
        #         - 'REWORK: <feedback>' if changes are needed""",
        # },
        # {
        #     "recipient": formatter,
        #     "summary_method": "reflection_with_llm",
        #     "message": "Please format the solutions. Do not invent new solutions, only format the solutions provided by the specialists.",
        #     "max_turns": 1,
        # },
    ]

    # Create solution nested chats
    solution_coordinator.register_nested_chats(
        solution_nested_chat_queue,
        trigger=research_coordinator,
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
                "message": "Consider initial and clarifying questions and work together to provide valuable solutions.",
                "summary_method": "reflection_with_llm",
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
