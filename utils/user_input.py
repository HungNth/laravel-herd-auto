from typing import Literal


def get_input(prompt, default=None, required=False):
    while True:
        user_input = input(prompt)
        if not user_input and default is not None:
            return default
        if required and not user_input:
            print(f"This field is required. Please enter a value.")
            continue
        return user_input


def clean_input(user_input):
    return user_input.replace(" ", "-").lower()


def clean_selection(user_input):
    return user_input.replace(" ,", ",").replace(", ", ",").replace(" ", ",").split(",")


def get_confirmation(prompt, default: Literal[True, False] = None):
    valid_yes = {'y', 'yes'}
    valid_no = {'n', 'no'}
    
    while True:
        choice = input(prompt).strip().lower()
        
        if choice == '' and default is not None:
            return default
        
        if choice in valid_yes:
            return True
        
        if choice in valid_no:
            return False
        
        print("Invalid input. Please enter 'y' or 'n'.")
