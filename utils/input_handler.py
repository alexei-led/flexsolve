"""Input handling utilities for the AWS Support System."""
from prompt_toolkit import PromptSession
from prompt_toolkit.shortcuts import message_dialog
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.validation import Validator, ValidationError

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

def get_user_input(prompt_text="", session=None):
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