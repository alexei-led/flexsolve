"""Main entry point for the AWS Support System."""

import autogen

from config import OPENAI_CONFIG, USER_PROXY_NAME, COORDINATOR_NAME

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

    # Create the coordinator
    coordinator = autogen.AssistantAgent(
        name=COORDINATOR_NAME,
        system_message="""You are an AWS Research Coordinator focused on problem understanding and clarification.

            CORE RESPONSIBILITIES:
            1. Direct user interaction
            2. Research team coordination
            3. Question consolidation and refinement

            WORKFLOW:
            For technical questions:
            1. Inform user: "I'll consult with our research team to better understand your needs."
            2. Start researcher group chat
            3. Guide researchers to:
            - Identify knowledge gaps
            - Propose relevant questions
            - Consider edge cases
            4. Consolidate questions:
            - Remove duplicates
            - Filter out obvious questions
            - Skip anything already mentioned by user
            - Group related questions
            5. Present consolidated questions to user
            6. Collect answers for deeper problem understanding

            For greetings:
            - Respond briefly and ask how you can help

            RESEARCH MANAGEMENT:
            - Direct researchers to specific aspects of the problem
            - Keep focus on gathering missing context
            - Ensure questions are:
            * Specific and actionable
            * Relevant to the problem
            * Not already answered
            * Critical for solution design

            QUESTION DELIVERY:
            - Present questions in clear, numbered format
            - Group related questions together
            - Explain briefly why certain information is needed
            - End with "TERMINATE" when all questions are answered

            COMMUNICATION STYLE:
            - Be concise and professional
            - Use clear, technical language
            - Focus on gathering critical information
            - Avoid assumptions""",
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

    return user_proxy, coordinator, specialists, researchers, human_expert, formatter


def main():
    """Main application entry point."""
    # Create agents
    user_proxy, coordinator, specialists, researchers, human_expert, formatter = create_agents()

    # Create group chat with specialists
    specialist_group = autogen.GroupChat(
        agents=[coordinator] + specialists,
        messages=[],
    )
    specialists_manager = autogen.GroupChatManager(
        groupchat=specialist_group,
        llm_config={"config_list": OPENAI_CONFIG},
    )
    
    # Create group chat with researchers
    researcher_group = autogen.GroupChat(
        agents=[coordinator] + researchers,
        messages=[],
    )
    researchers_manager = autogen.GroupChatManager(
        groupchat=researcher_group,
        llm_config={"config_list": OPENAI_CONFIG},
    )

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
        response = coordinator.initiate_chat(
            recipient=classifier,
            message=agent.last_message(),
            max_turns=1,
        )

        # return True if the response is "YES", False otherwise
        return response.summary.strip().upper() == "YES"

    nested_chat_queue = [
        {
            "recipient": researchers_manager,
            "summary_method": "reflection_with_llm",
        },
        {
            "recipient": human_expert,
            "summary_method": "last_msg",
            "message": """
                Please validate the solution.
                Reply with:
                - 'APPROVE' if the solution is good
                - 'REWORK: <feedback>' if changes are needed""",
            "max_turns": 1,
        },
        {
            "recipient": formatter,
            "summary_method": "last_msg",
            "message": "Please format the clarifying questions.",
            "max_turns": 1,
        },
    ]

    # Create solution nested chats
    coordinator.register_nested_chats(
        nested_chat_queue,
        trigger=lambda sender: sender is user_proxy
        and is_technical_question_llm(user_proxy),
    )

    # user starts the conversation with the coordinator
    user_proxy.initiate_chats(
        [
            {
                "recipient": coordinator,
                "message": "hi",
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
