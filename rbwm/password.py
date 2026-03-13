"""Password generation utilities."""
import random
import string


def generate_password(length=16, special=True, numbers=True, letters=True):
    """Generate a random password with specified characteristics."""
    if length < 1:
        length = 1
    
    charset = ""
    if letters:
        charset += string.ascii_letters
    if numbers:
        charset += string.digits
    if special:
        charset += string.punctuation
    
    # If no charset selected, default to letters
    if not charset:
        charset = string.ascii_letters
    
    return ''.join(random.choice(charset) for _ in range(length))


def password_menu():
    """Show password input submenu and return password or None."""
    from .menu import select_from_menu, prompt_for_input
    from .config import CONFIG
    
    choice = select_from_menu(
        ["Enter manually", "Generate password"],
        "Password input method"
    )
    
    if not choice:
        return None
    
    if choice == "Enter manually":
        return prompt_for_input("Enter password")
    
    # Generate password with settings menu
    settings = CONFIG.get_password_settings()
    
    while True:
        # Build menu items
        menu_items = [
            "[Generate]",
            f"Length: {settings['length']}",
            f"Special characters: {'Yes' if settings['special'] else 'No'}",
            f"Numbers: {'Yes' if settings['numbers'] else 'No'}",
            f"Letters: {'Yes' if settings['letters'] else 'No'}",
        ]
        
        setting_choice = select_from_menu(menu_items, "Password generation settings")
        
        if not setting_choice:
            return None
        
        if setting_choice == "[Generate]":
            password = generate_password(
                length=settings['length'],
                special=settings['special'],
                numbers=settings['numbers'],
                letters=settings['letters']
            )
            # Save settings for future use
            CONFIG.save_password_settings(
                settings['length'],
                settings['special'],
                settings['numbers'],
                settings['letters']
            )
            return password
        
        # Handle setting changes
        if setting_choice.startswith("Length:"):
            new_length = prompt_for_input(f"Enter password length (current: {settings['length']})")
            if new_length:
                try:
                    settings['length'] = max(1, int(new_length))
                except ValueError:
                    pass
        
        elif setting_choice.startswith("Special characters:"):
            settings['special'] = not settings['special']
        
        elif setting_choice.startswith("Numbers:"):
            settings['numbers'] = not settings['numbers']
        
        elif setting_choice.startswith("Letters:"):
            settings['letters'] = not settings['letters']
