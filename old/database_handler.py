import os
import sys
import re
from commands import run_sql_command
import aiofiles

async def check_database_exists(db_name):
    db_name = db_name.replace('-', '_')

    try:
        result = await run_sql_command(f'-e "SHOW DATABASES LIKE \'{db_name}\';"')
        return db_name in result.stdout
    except Exception as e:
        print(f'Lỗi khi kiểm tra database: {e}')
        return False


async def create_database(db_name):
    db_name = db_name.replace('-', '_')

    try:
        await run_sql_command(f'-e "CREATE DATABASE IF NOT EXISTS {db_name}; GRANT ALL PRIVILEGES ON {db_name}.* TO root@localhost WITH GRANT OPTION; FLUSH PRIVILEGES;"')
        print(f'Đã tạo database: "{db_name}"\n')
    except Exception as e:
        print(f'Lỗi khi tạo database "{db_name}": {e}')
        sys.exit(1)


async def drop_database(db_name):
    db_name = db_name.replace('-', '_')

    try:
        await run_sql_command(f'-e "DROP DATABASE IF EXISTS \"{db_name}\";"')
        print(f'Đã xóa database: "{db_name}"')
    except Exception as e:
        print(f'Lỗi khi xóa database "{db_name}": {e}')
        raise e


async def find_sql_file(dir_path: str):
    for file in os.listdir(dir_path):
        if file.endswith('.sql'):
            return file
    return None


async def get_table_prefix(db_name):
    db_name = db_name.replace('-', '_')

    result = await run_sql_command(f'--silent --skip-column-names -e "SELECT table_name FROM information_schema.tables WHERE table_schema = \'{db_name}\' AND table_name LIKE \'%options\'"')
    if result.stdout and result.stderr == '':
        table_names = result.stdout.strip().split('\n')

        for table in table_names:
            table = table.strip()
            if table.endswith('options'):
                prefix = table[:-len('options')]
                return prefix
    return None


async def update_table_prefix(db_name, website_path):
    db_name = db_name.replace('-', '_')

    print(f'Kiểm tra prefix của database {db_name}...')
    
    prefix = await get_table_prefix(db_name)
    if prefix == 'wp_':
        return prefix
    else:
        print(f'Đã phát hiện prefix: "{prefix}"')

        wp_config_path = os.path.join(website_path, 'wp-config.php')
        try:
            if os.path.exists(wp_config_path):
                async with aiofiles.open(wp_config_path, 'r', encoding='utf-8') as f:
                    config_content = await f.read()
                
                if "$table_prefix" in config_content:
                    updated_content = re.sub(
                        r"\$table_prefix\s*=\s*'[^']*';",
                        f"$table_prefix = '{prefix}';",
                        config_content
                    )
                else:
                    updated_content = config_content + f"\n$table_prefix = '{prefix}';\n"
                
                async with aiofiles.open(wp_config_path, 'w', encoding='utf-8') as f:
                    await f.write(updated_content)
                
                print(f'Đã cập nhật prefix trong wp-config.php thành: "{prefix}"')
                return prefix
            else:
                print(f'Không tìm thấy file wp-config.php tại: {wp_config_path}')
                return False
        except IOError as e:
            print(f'Lỗi khi đọc/ghi file wp-config.php: {e}')
            return False
        except Exception as e:
            print(f'Lỗi không xác định: {e}')
            return False


async def get_admin_id(db_name, prefix="wp_"):
    db_name = db_name.replace('-', '_')

    result = await run_sql_command(f'{db_name} --silent --skip-column-names -e "SELECT ID FROM {prefix}users;"')
    users_id = result.stdout.replace('\n', ',').split(',')

    return users_id[0]

async def change_admin_username(db_name, admin_id, new_username, prefix="wp_"):
    db_name = db_name.replace('-', '_')

    await run_sql_command(f'{db_name} -e "UPDATE {prefix}users SET user_login = \'{new_username}\' WHERE ID = {admin_id};"', print_text=f"Đặt lại admin username")

async def change_admin_password(db_name, admin_id, new_password, prefix="wp_"):
    db_name = db_name.replace('-', '_')

    await run_sql_command(f'{db_name} -e "UPDATE {prefix}users SET user_pass = MD5(\'{new_password}\') WHERE ID = {admin_id};"', print_text=f"Đặt lại admin password")

async def change_admin_user_email(db_name, admin_id, new_email, prefix="wp_"):
    db_name = db_name.replace('-', '_')

    await run_sql_command(f'{db_name} -e "UPDATE {prefix}users SET user_email = \'{new_email}\' WHERE ID = {admin_id};"', print_text=f"Thay đổi user email")

async def change_admin_email(db_name, new_email, prefix="wp_"):
    db_name = db_name.replace('-', '_')

    await run_sql_command(f'{db_name} -e "UPDATE {prefix}options SET option_value = \'{new_email}\' WHERE option_name = \'admin_email\';"', print_text=f"Thay đổi admin email")
