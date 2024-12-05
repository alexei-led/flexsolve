"""Main entry point for the AWS Support System."""
import autogen
from termcolor import colored
from prompt_toolkit import PromptSession
from prompt_toolkit.shortcuts import message_dialog
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.validation import Validator, ValidationError

from config import (
    OPENAI_CONFIG, USER_PROXY_NAME, COORDINATOR_NAME
)

from specialists import (
    EKSSpecialist,
    CloudWatchSpecialist,
    EC2Specialist,
    VPCSpecialist,
    IAMSpecialist
)
from chat_manager import ChatManager
from utils.input_handler import create_prompt_session, get_user_input

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
        system_message="""You are the coordinator of an AWS support system. Your role is to:
        1. Be the primary point of contact for the user
        2. Manage the specialist team through a separate group chat
        3. Filter and consolidate information from specialists
        4. Present clear, focused questions to the user
        5. Provide final, actionable solutions

        Guidelines for user interaction:
        - If the user greets you with a kind message, greet them back and ask how you can help
        - When the user asks a technical question, inform them you need to think and start a group chat with specialists
        - Format a final answer from the specialists' replies and present it to the user
        - Reply "TERMINATE" when you are done

        Guidelines for specialist management:
        - Create focused problem statements for specialists
        - Guide the technical discussion
        - Keep specialists on track
        - Consolidate technical insights
        - Request human expert validation when needed""",
        llm_config={"config_list": OPENAI_CONFIG},
    )

    # Create the human expert
    human_expert = autogen.UserProxyAgent(
        name="AWS_Architect",
        human_input_mode="ALWAYS",
        code_execution_config=False,
        description="This agent can approve or refine clarifying questions and validate the proposed solutions returned by the specialists.",
        system_message="""You are a senior AWS Solutions Architect providing expert guidance. 
        Wait for actual human input when asked for validation or expert opinion.
        Key responsibilities:
        - Validate the system's understanding of the problem
        - Ensure all critical information has been gathered
        - Guide specialists to focus on relevant aspects
        - Provide expert validation of proposed solutions
        - Request user confirmation of problem understanding when needed""",
    )

    # Create specialists
    specialists = [
        IAMSpecialist(OPENAI_CONFIG).create_specialist(),
        CloudWatchSpecialist(OPENAI_CONFIG).create_specialist(),
        EC2Specialist(OPENAI_CONFIG).create_specialist(),
        EKSSpecialist(OPENAI_CONFIG).create_specialist(),
        VPCSpecialist(OPENAI_CONFIG).create_specialist(),
    ]

    return user_proxy, coordinator, specialists, human_expert

def main():
    """Main application entry point."""
    # Create agents
    user_proxy, coordinator, specialists, human_expert = create_agents()
    
    # Create group chat with specialists and human expert
    specialist_group = autogen.GroupChat(
        agents=[coordinator, human_expert] + specialists,
        messages=[],
    )
    specialists_group_manager = autogen.GroupChatManager(
        groupchat=specialist_group,
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

    coordinator.register_nested_chats(
        [
            {
                "recipient": specialists_group_manager,
                "summary_method": "reflection_with_llm",
                "message": user_proxy.last_message(),
            }
        ],
        trigger=lambda sender: sender is user_proxy and is_technical_question_llm(user_proxy)
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
            }
        ]
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")