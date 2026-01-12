import sys
from typing import Literal


def get_input(prompt, default=None, required=False):
    while True:
        user_input = input(prompt)
        if user_input == 'exit':
            print("Exiting the program.")
            sys.exit(0)
        if not user_input and default is not None:
            return default
        if required and not user_input:
            print(f"This field is required. Please enter a value.")
            continue
        return user_input


def clean_input(user_input):
    return user_input.replace(" ", "-").lower()


# def clean_selection(user_input):
#     return user_input.replace(" ,", ",").replace(", ", ",").replace(" ", ",").split(",")
def clean_selection(selection: str):
    result = []
    
    selection = selection.replace(" ,", ",").replace(", ", ",").replace(" ", ",")
    parts = selection.split(",")
    
    for part in parts:
        if '-' in part:
            start, end = part.split('-', 1)
            start, end = int(start), int(end)
            
            if start > end:
                start, end = end, start
            
            result.extend(str(i) for i in range(start, end + 1))
        else:
            result.append(part)
    
    return list(dict.fromkeys(result))


def get_confirmation(prompt, default: Literal[True, False] = None):
    valid_yes = {'y', 'yes'}
    valid_no = {'n', 'no'}
    
    while True:
        choice = input(prompt).strip().lower()
        
        if choice == 'exit':
            print("Exiting the program.")
            sys.exit(0)
        
        if choice == '' and default is not None:
            return default
        
        if choice in valid_yes:
            return True
        
        if choice in valid_no:
            return False
        
        print("Invalid input. Please enter 'y' or 'n'.")


def get_input_options(options):
    exit_option = 'Exit'
    
    options.append(exit_option)
    for index, option in enumerate(options):
        print(f'{index + 1}. {option}')
    
    valid_choices = [str(i + 1) for i in range(len(options))]
    
    while True:
        choice = get_input(f'Your choice 1-{len(options)}: ', required=True)
        
        if choice not in valid_choices:
            print("Invalid choice. Please select a valid option.")
            continue
        
        if choice == str(len(options)):
            print('Exiting the program.')
            sys.exit(0)
        
        return choice
