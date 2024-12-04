"""Main entry point for the AWS Support System."""
import autogen
from termcolor import colored
from prompt_toolkit import PromptSession
from prompt_toolkit.shortcuts import message_dialog
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.validation import Validator, ValidationError

from config import (
    OPENAI_CONFIG, USER_PROXY_NAME, COORDINATOR_NAME,
    MAX_CONSECUTIVE_AUTO_REPLY, CODE_EXECUTION_CONFIG
)
from specialists import (
    EKSSpecialist,
    CloudWatchSpecialist,
    EC2Specialist,
    VPCSpecialist,
    IAMSpecialist
)
from chat_manager import ChatManager

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
        validator=NotEmptyValidator(),
        validate_while_typing=False,
        multiline=True,
        wrap_lines=True,
        bottom_toolbar=HTML(
            '<b>Controls:</b> '
            '<style fg="green">Enter</style> for new line | '
            '<style fg="green">Ctrl+D</style> to submit | '
            '<style fg="green">Ctrl+Q</style> to quit'
        ),
        history=None
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

def create_agents():
    """Create all the necessary agents for the system."""
    # Create the user proxy
    user_proxy = autogen.UserProxyAgent(
        name=USER_PROXY_NAME,
        human_input_mode="ALWAYS",
        max_consecutive_auto_reply=MAX_CONSECUTIVE_AUTO_REPLY,
        code_execution_config=CODE_EXECUTION_CONFIG,
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
        - Request human expert validation when needed""",
        llm_config={"config_list": OPENAI_CONFIG},
    )

    # Create the human expert
    human_expert = autogen.UserProxyAgent(
        name="AWS_Architect",
        human_input_mode="ALWAYS",
        max_consecutive_auto_reply=MAX_CONSECUTIVE_AUTO_REPLY,
        code_execution_config=CODE_EXECUTION_CONFIG,
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
        EKSSpecialist(OPENAI_CONFIG).create_specialist(),
        CloudWatchSpecialist(OPENAI_CONFIG).create_specialist(),
        EC2Specialist(OPENAI_CONFIG).create_specialist(),
        VPCSpecialist(OPENAI_CONFIG).create_specialist(),
        IAMSpecialist(OPENAI_CONFIG).create_specialist()
    ]

    return user_proxy, coordinator, specialists, human_expert

def main():
    """Main application entry point."""
    # Create agents
    user_proxy, coordinator, specialists, human_expert = create_agents()
    
    # Create chat manager
    chat_manager = ChatManager(coordinator, specialists, human_expert)
    
    # Create prompt session
    session = create_prompt_session()
    
    while True:
        chat_manager.print_header()  # Print header before each input
        user_query = get_multiline_input(
            "Enter your AWS-related question:",
            session=session
        )
        
        if user_query.lower() == 'exit':
            message_dialog(
                title='Exiting',
                text='Thank you for using DoiT FlexSolve!'
            ).run()
            break
        
        if user_query.strip():
            chat_manager.initiate_chat(user_proxy, user_query)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")