def get_input(prompt, default=None, required=False):
    while True:
        user_input = input(prompt)
        cleaned_input = clean_input(user_input)
        if not user_input and default is not None:
            return default
        if required and not user_input:
            print(f"This field is required. Please enter a value.")
            continue
        return cleaned_input


def clean_input(user_input):
    return user_input.replace(" ", "-").lower()
