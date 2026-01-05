def get_input(prompt, default=None, required=False):
    while True:
        user_input = input(prompt).strip()
        if not user_input and default is not None:
            return default
        if required and not user_input:
            print(f"This field is required. Please enter a value.")
            continue
        return user_input