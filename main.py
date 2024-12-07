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

    # Create the research coordinator
    research_coordinator = autogen.AssistantAgent(
        name=RESEARCH_COORDINATOR_NAME,
        system_message="""
            You are an AWS Research Coordinator focused on problem understanding and clarification.

            CORE RESPONSIBILITIES:
            1. Direct user interaction
            2. Research team coordination
            3. Question consolidation and refinement

            WORKFLOW:
            For technical questions:
            1. Inform user: "I'll consult with our research team to better understand your needs."
            2. Analyze the problem and identify which AWS services are involved
            3. Engage ALL relevant researchers based on the services involved
            4. Guide researchers to:
            - Identify knowledge gaps
            - Propose relevant questions
            - Consider edge cases
            5. Consolidate ALL researchers' questions into a single list:
            - Remove duplicates
            - Filter out obvious questions
            - Skip anything already mentioned by user
            - Group related questions
            6. Format your response as:
              Problem Understanding:
              [Summarize the current understanding of the problem]
              
              Questions:
              [If clarification needed]:
              1. [First question]
              2. [Second question]
              ...
              [If no questions needed]:
              No additional questions needed - problem is clear.
              
              TERMINATE

            For greetings:
            - Respond briefly and ask how you can help

            RESEARCH MANAGEMENT:
            - Ensure ALL relevant researchers participate based on their expertise
            - Direct each researcher to their specific domain aspects
            - Keep focus on gathering missing context
            - Ignore solutions, focus on collecting questions only
            - Ensure questions are:
            * Specific and actionable
            * Relevant to the problem
            * Not already answered
            * Critical for solution design

            RESPONSE FORMAT:
            Always structure your response as:
            Problem Understanding:
            [Clear summary of the current understanding]
            
            Questions:
            [Numbered list of questions OR "No additional questions needed - problem is clear."]
            
            TERMINATE

            COMMUNICATION STYLE:
            - Be concise and professional
            - Use clear, technical language
            - Focus on gathering critical information
            - Avoid assumptions
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
        agents=[research_coordinator] + researchers,
        messages=[],
        admin_name=research_coordinator.name,
        select_speaker_auto_verbose=True,
    )
    researchers_manager = autogen.GroupChatManager(
        groupchat=researcher_group,
        llm_config={"config_list": OPENAI_CONFIG},
    )
    
    # Create group chat with specialists
    specialist_group = autogen.GroupChat(
        agents=[research_coordinator] + specialists,
        messages=[],
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

        # return True if the response is "YES", False otherwise
        return response.summary.strip().upper() == "YES"

    # Create research nested chats
    research_nested_chat_queue = [
        {
            "recipient": researchers_manager,
            "summary_method": "reflection_with_llm",
            "max_turns": 1,
        },
        # {
        #     "recipient": human_expert,
        #     "summary_method": "reflection_with_llm",
        #     "message": """
        #         Please validate the clarifying questions.
        #         Reply with:
        #         - 'APPROVE' if the clarifying questions are good
        #         - 'REWORK: <feedback>' if changes are needed""",
        #     "max_turns": 1,
        # },
        {
            "recipient": formatter,
            "summary_method": "reflection_with_llm",
            "message": "Please format the clarifying questions. Do not invent new questions, only format the questions provided by the researchers.",
            "max_turns": 1,
        },
    ]
    
    solution_nested_chat_queue = [
        {
            "recipient": specialists_manager,
            "summary_method": "reflection_with_llm",
            "max_turns": 1,
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

    # Create research nested chats
    research_coordinator.register_nested_chats(
        research_nested_chat_queue,
        trigger=lambda sender: sender is user_proxy
        and is_technical_question_llm(user_proxy),
    )
    
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
