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


def get_admin_credentials():
    import config
    from wordpress.wp import wp
    
    admin_username = config.admin_username
    admin_password = config.admin_password
    admin_email = config.admin_email
    
    site_name = get_input('Enter the site name: ', required=True)
    if wp.is_website_exists(site_name):
        print(f'Site "{site_name}" already exists. Please choose a different name.')
        return get_admin_credentials()
    
    is_default = get_input(f'Do you want to use default admin credentials? (y/n): ', default='y')
    
    if is_default != 'y':
        admin_name_input = get_input(f'Enter the admin username "{admin_username}": ', default=admin_username,
                                     required=True)
        admin_pass_input = get_input(f'Enter the admin password "{admin_password}":', default=admin_password,
                                     required=True)
        admin_email_input = get_input(f'Enter the admin email "{admin_email}": ', default=admin_email, required=True)
    else:
        admin_name_input = admin_username
        admin_pass_input = admin_password
        admin_email_input = admin_email
    
    return site_name, admin_name_input, admin_pass_input, admin_email_input


def get_confirmation():
    while True:
        confirmation = get_input("Are you sure you want to proceed? (y/n): ", required=True)
        if confirmation in ['y', 'n']:
            return confirmation == 'y'
        print("Invalid input. Please enter 'y' or 'n'.")
