import os
import sys
import zipfile
import shutil
import asyncio

import config
from commands import run_command, run_sql_command
from database_handler import create_database, find_sql_file, update_table_prefix


class ZipRestore:
    def __init__(self):
        self.herd_sites_path = config.herd_sites_path
        self.admin_username = config.admin_username
        self.admin_password = config.admin_password
        self.admin_email = config.admin_email
        
    def validate_zip_file(self, zip_path: str) -> bool:
        if not os.path.exists(zip_path):
            print(f"❌ Lỗi: File zip '{zip_path}' không tồn tại!")
            return False
            
        if not zip_path.lower().endswith('.zip'):
            print(f"❌ Lỗi: File '{zip_path}' không phải là file zip!")
            return False
            
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Kiểm tra file zip có thể đọc được
                zip_ref.testzip()
            print(f"✅ File zip hợp lệ: {zip_path}")
            return True
        except zipfile.BadZipFile:
            print(f"❌ Lỗi: File zip '{zip_path}' bị hỏng hoặc không hợp lệ!")
            return False
        except Exception as e:
            print(f"❌ Lỗi khi kiểm tra file zip: {e}")
            return False
    
    def validate_website_name(self, website_name: str) -> bool:
        """Kiểm tra tên website có hợp lệ không"""
        if not website_name or not website_name.strip():
            print("❌ Lỗi: Tên website không được để trống!")
            return False
            
        # Kiểm tra ký tự hợp lệ
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', website_name):
            print("❌ Lỗi: Tên website chỉ được chứa chữ cái, số, dấu gạch dưới (_) và dấu gạch ngang (-)!")
            return False
            
        website_path = os.path.join(self.herd_sites_path, website_name)
        if os.path.exists(website_path):
            print(f"❌ Lỗi: Thư mục website '{website_name}' đã tồn tại!")
            return False
            
        print(f"✅ Tên website hợp lệ: {website_name}")
        return True
    
    async def extract_and_organize_files(self, zip_path: str, website_path: str) -> bool:
        try:
            print("📂 Đang giải nén file zip...")
            
            # Tạo thư mục tạm để giải nén
            temp_extract_path = os.path.join(website_path, "temp_extract")
            os.makedirs(temp_extract_path, exist_ok=True)
            
            # Giải nén toàn bộ file zip vào thư mục tạm
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_extract_path)
            
            print("✅ Giải nén hoàn tất!")
            
            # Tìm file wp-login.php để xác định cấu trúc đúng
            wp_login_path = self.find_wp_login_php(temp_extract_path)
            
            if wp_login_path:
                # Xác định thư mục gốc chứa WordPress
                wp_root_dir = os.path.dirname(wp_login_path)
                print(f"📍 Tìm thấy WordPress tại: {wp_root_dir}")
                
                # Di chuyển tất cả file từ thư mục WordPress gốc ra thư mục website
                await self.move_wordpress_files(wp_root_dir, website_path)
                
                # Xóa thư mục tạm
                shutil.rmtree(temp_extract_path)
                
                return True
            else:
                print("❌ Lỗi: Không tìm thấy file wp-login.php trong file zip!")
                print("💡 Đảm bảo file zip chứa backup website WordPress hợp lệ")
                return False
                
        except Exception as e:
            print(f"❌ Lỗi khi giải nén file: {e}")
            return False
    
    def find_wp_login_php(self, extract_path: str) -> str:
        """Tìm file wp-login.php trong thư mục đã giải nén"""
        for root, dirs, files in os.walk(extract_path):
            if 'wp-login.php' in files:
                return os.path.join(root, 'wp-login.php')
        return None
    
    async def move_wordpress_files(self, source_dir: str, target_dir: str):
        """Di chuyển tất cả file WordPress từ source đến target"""
        try:
            print("📁 Đang sắp xếp lại cấu trúc file...")
            
            for item in os.listdir(source_dir):
                source_path = os.path.join(source_dir, item)
                target_path = os.path.join(target_dir, item)
                
                # Bỏ qua thư mục temp_extract
                if item == "temp_extract":
                    continue
                
                if os.path.isdir(source_path):
                    # Nếu là thư mục, copy toàn bộ thư mục
                    if os.path.exists(target_path):
                        shutil.rmtree(target_path)
                    shutil.copytree(source_path, target_path)
                else:
                    # Nếu là file, copy file
                    shutil.copy2(source_path, target_path)
            
            print("✅ Sắp xếp cấu trúc file hoàn tất!")
            
        except Exception as e:
            print(f"❌ Lỗi khi di chuyển file: {e}")
            raise e
    
    async def find_and_import_database(self, website_path: str, website_name: str) -> bool:
        """Tìm và import database"""
        try:
            print("🔍 Đang tìm file database...")
            
            # Tìm file SQL trong thư mục website
            sql_files = []
            for root, dirs, files in os.walk(website_path):
                for file in files:
                    if file.lower().endswith('.sql'):
                        sql_files.append(os.path.join(root, file))
            
            if not sql_files:
                print("❌ Lỗi: Không tìm thấy file database (.sql) trong backup!")
                return False
            
            # Nếu có nhiều file SQL, chọn file đầu tiên
            sql_file = sql_files[0]
            print(f"📊 Tìm thấy file database: {os.path.basename(sql_file)}")
            
            # Tạo database
            print("🗄️ Đang tạo database...")
            await create_database(website_name)
            
            # Import database
            print("📥 Đang import database...")
            db_name = website_name.replace('-', '_')
            await run_sql_command(f'{db_name} < "{sql_file}"', print_text=f"Import database: {os.path.basename(sql_file)}")
            
            print("✅ Import database hoàn tất!")
            return True
            
        except Exception as e:
            print(f"❌ Lỗi khi import database: {e}")
            return False
    
    async def create_wp_config(self, website_path: str, website_name: str):
        """Tạo file wp-config.php bằng WP-CLI"""
        try:
            wp_config_path = os.path.join(website_path, 'wp-config.php')
            
            # Kiểm tra nếu wp-config.php đã tồn tại
            if os.path.exists(wp_config_path):
                print("✅ File wp-config.php đã tồn tại!")
                return
            
            print("📝 Đang tạo file wp-config.php...")
            
            db_name = website_name.replace('-', '_')
            wp_cli_cmd = f'wp --path="{website_path}"'
            
            # Tạo file wp-config.php
            wp_config_cmd = f"config create --dbname={db_name} --dbuser=root --dbpass= --dbhost=localhost"
            await run_command(f"{wp_cli_cmd} {wp_config_cmd}", print_text="Tạo file wp-config.php")
            
            print("✅ Tạo file wp-config.php thành công!")
            
        except Exception as e:
            print(f"⚠️ Cảnh báo: Lỗi khi tạo wp-config.php: {e}")
            # Tạo wp-config.php thủ công nếu WP-CLI thất bại
            await self.create_wp_config_manual(website_path, website_name)
    
    async def create_wp_config_manual(self, website_path: str, website_name: str):
        """Tạo file wp-config.php thủ công nếu WP-CLI thất bại"""
        try:
            wp_config_path = os.path.join(website_path, 'wp-config.php')
            
            # Kiểm tra nếu wp-config.php đã tồn tại
            if os.path.exists(wp_config_path):
                print("✅ File wp-config.php đã tồn tại!")
                return
                
            print("📝 Đang tạo file wp-config.php thủ công...")
            
            db_name = website_name.replace('-', '_')
            
            wp_config_content = f"""<?php
/**
 * The base configuration for WordPress
 *
 * The wp-config.php creation script uses this file during the installation.
 * You don't have to use the web site, you can copy this file to "wp-config.php"
 * and fill in the values.
 *
 * This file contains the following configurations:
 *
 * * Database settings
 * * Secret keys
 * * Database table prefix
 * * ABSPATH
 *
 * @link https://wordpress.org/support/article/editing-wp-config-php/
 *
 * @package WordPress
 */

// ** Database settings - You can get this info from your web host ** //
/** The name of the database for WordPress */
define( 'DB_NAME', '{db_name}' );

/** Database username */
define( 'DB_USER', 'root' );

/** Database password */
define( 'DB_PASSWORD', '' );

/** Database hostname */
define( 'DB_HOST', 'localhost' );

/** Database charset to use in creating database tables. */
define( 'DB_CHARSET', 'utf8mb4' );

/** The database collate type. Don't change this if in doubt. */
define( 'DB_COLLATE', '' );

/**#@+
 * Authentication unique keys and salts.
 *
 * Change these to different unique phrases! You can generate these using
 * the WordPress.org secret-key service.
 *
 * You can change these at any point in time to invalidate all existing cookies.
 * This will force all users to have to log in again.
 *
 * @since 2.6.0
 */
define( 'AUTH_KEY',         'put your unique phrase here' );
define( 'SECURE_AUTH_KEY',  'put your unique phrase here' );
define( 'LOGGED_IN_KEY',    'put your unique phrase here' );
define( 'NONCE_KEY',        'put your unique phrase here' );
define( 'AUTH_SALT',        'put your unique phrase here' );
define( 'SECURE_AUTH_SALT', 'put your unique phrase here' );
define( 'LOGGED_IN_SALT',   'put your unique phrase here' );
define( 'NONCE_SALT',       'put your unique phrase here' );

/**#@-*/

/**
 * WordPress database table prefix.
 *
 * You can have multiple installations in one database if you give each
 * a unique prefix. Only numbers, letters, and underscores please!
 */
$table_prefix = 'wp_';

/**
 * For developers: WordPress debugging mode.
 *
 * Change this to true to enable the display of notices during development.
 * It is strongly recommended that plugin and theme developers use WP_DEBUG
 * in their development environments.
 *
 * For information on other constants that can be used for debugging,
 * visit the documentation.
 *
 * @link https://wordpress.org/support/article/debugging-in-wordpress/
 */
define( 'WP_DEBUG', false );

/* Add any custom values between this line and the "stop editing" comment. */



/* That's all, stop editing! Happy publishing. */

/** Absolute path to the WordPress directory. */
if ( ! defined( 'ABSPATH' ) ) {{
	define( 'ABSPATH', __DIR__ . '/' );
}}

/** Sets up WordPress vars and included files. */
require_once ABSPATH . 'wp-settings.php';
"""
            
            with open(wp_config_path, 'w', encoding='utf-8') as f:
                f.write(wp_config_content)
            
            print("✅ Tạo file wp-config.php thủ công thành công!")
            
        except Exception as e:
            print(f"❌ Lỗi khi tạo wp-config.php thủ công: {e}")
    
    async def configure_wordpress(self, website_path: str, website_name: str) -> bool:
        """Cấu hình WordPress sau khi restore"""
        try:
            print("⚙️ Đang cấu hình WordPress...")
            
            # Tạo file wp-config.php nếu chưa có
            await self.create_wp_config(website_path, website_name)
            
            # Cập nhật table prefix trong wp-config.php
            prefix = await update_table_prefix(website_name, website_path)
            if not prefix:
                prefix = "wp_"
            
            # Tạo URL website
            website_url = f"https://{website_name}.test"
            
            # Cấu hình WP-CLI command
            wp_cli_cmd = f'wp --path="{website_path}"'
            
            print("🔧 Đang cập nhật thông tin website...")
            
            # Cập nhật siteurl và home
            db_name = website_name.replace('-', '_')
            await asyncio.gather(
                run_sql_command(f'{db_name} -e "UPDATE {prefix}options SET option_value = \'{website_url}\' WHERE option_name = \'home\';"'),
                run_sql_command(f'{db_name} -e "UPDATE {prefix}options SET option_value = \'{website_url}\' WHERE option_name = \'siteurl\';"'),
                run_sql_command(f'{db_name} -e "UPDATE {prefix}options SET option_value = \'{self.admin_email}\' WHERE option_name = \'admin_email\';"')
            )
            
            # Lấy ID admin đầu tiên
            result = await run_sql_command(f'{db_name} --silent --skip-column-names -e "SELECT ID FROM {prefix}users LIMIT 1;"')
            admin_id = result.stdout.strip()
            
            if admin_id:
                print("👤 Đang cập nhật thông tin admin...")
                # Cập nhật thông tin admin
                await asyncio.gather(
                    run_sql_command(f'{db_name} -e "UPDATE {prefix}users SET user_login = \'{self.admin_username}\' WHERE ID = {admin_id};"'),
                    run_sql_command(f'{db_name} -e "UPDATE {prefix}users SET user_pass = MD5(\'{self.admin_password}\') WHERE ID = {admin_id};"'),
                    run_sql_command(f'{db_name} -e "UPDATE {prefix}users SET user_email = \'{self.admin_email}\' WHERE ID = {admin_id};"')
                )
            
            # Flush cache và rewrite rules bằng WP-CLI
            try:
                await asyncio.gather(
                    run_command(f'{wp_cli_cmd} rewrite flush'),
                    run_command(f'{wp_cli_cmd} cache flush')
                )
            except:
                # Nếu WP-CLI không hoạt động, bỏ qua
                pass
            
            print("✅ Cấu hình WordPress hoàn tất!")
            return True
            
        except Exception as e:
            print(f"❌ Lỗi khi cấu hình WordPress: {e}")
            return False
    
    async def save_credentials(self, website_path: str, website_name: str):
        """Lưu thông tin đăng nhập"""
        try:
            website_url = f"https://{website_name}.test"
            credentials_file = os.path.join(website_path, "wp_credentials.txt")
            
            credentials_content = f"""WordPress Login Credentials:
------------------------------------------
Website: {website_name}
Login URL: {website_url}/wp-admin/
Username: {self.admin_username}
Password: {self.admin_password}
Email: {self.admin_email}
------------------------------------------
Restored from ZIP file on {asyncio.get_event_loop().time()}
"""
            
            with open(credentials_file, "w", encoding="utf-8") as f:
                f.write(credentials_content)
            
            print(f"💾 Đã lưu thông tin đăng nhập tại: {credentials_file}")
            
        except Exception as e:
            print(f"⚠️ Cảnh báo: Không thể lưu file thông tin đăng nhập: {e}")
    
    def print_success_info(self, website_name: str):
        """In thông tin thành công"""
        website_url = f"https://{website_name}.test"
        
        print("\n" + "="*60)
        print("🎉 RESTORE WEBSITE THÀNH CÔNG!")
        print("="*60)
        print(f"📱 Website: {website_name}")
        print(f"🌐 URL: {website_url}")
        print(f"🔐 Admin URL: {website_url}/wp-admin/")
        print(f"👤 Username: {self.admin_username}")
        print(f"🔑 Password: {self.admin_password}")
        print(f"📧 Email: {self.admin_email}")
        print("="*60)
        print("💡 Lưu ý: Hãy restart Herd Services nếu gặp lỗi 500 hoặc SSL Error")
        print("🚀 Bạn có thể truy cập website ngay bây giờ!")
        print("="*60)
    
    async def restart_herd_services(self):
        """Restart Herd Services"""
        try:
            print("🔄 Đang restart Herd Services...")
            await run_command("herd restart", print_text="Khởi động lại Herd Services...")
            print("✅ Restart Herd Services thành công!")
        except Exception as e:
            print(f"⚠️ Cảnh báo: Không thể restart Herd Services: {e}")
            print("💡 Bạn có thể restart thủ công nếu gặp vấn đề")


async def main():
    """Hàm chính để restore website từ file zip"""
    print("🚀 CÔNG CỤ RESTORE WEBSITE TỪ FILE ZIP")
    print("="*50)
    
    restore_tool = ZipRestore()
    
    # Bước 1: Nhập và kiểm tra đường dẫn file zip
    while True:
        zip_path = input("\n📁 Nhập đường dẫn file zip: ").strip().strip('"')
        if restore_tool.validate_zip_file(zip_path):
            break
    
    # Bước 2: Nhập và kiểm tra tên website
    while True:
        website_name = input("\n🏷️ Nhập tên thư mục website: ").strip()
        if restore_tool.validate_website_name(website_name):
            break
    
    # Bước 3: Tạo thư mục website
    website_path = os.path.join(restore_tool.herd_sites_path, website_name)
    try:
        os.makedirs(website_path, exist_ok=True)
        print(f"✅ Đã tạo thư mục website: {website_path}")
    except Exception as e:
        print(f"❌ Lỗi khi tạo thư mục website: {e}")
        return False
    
    try:
        # Bước 4: Giải nén và kiểm tra cấu trúc
        if not await restore_tool.extract_and_organize_files(zip_path, website_path):
            print("❌ Quá trình restore thất bại!")
            # Xóa thư mục đã tạo nếu thất bại
            if os.path.exists(website_path):
                shutil.rmtree(website_path)
            return False
        
        # Bước 5: Tạo và import database
        if not await restore_tool.find_and_import_database(website_path, website_name):
            print("❌ Quá trình restore thất bại!")
            # Xóa thư mục đã tạo nếu thất bại
            if os.path.exists(website_path):
                shutil.rmtree(website_path)
            return False
        
        # Bước 6: Cấu hình WordPress
        if not await restore_tool.configure_wordpress(website_path, website_name):
            print("⚠️ Cảnh báo: Có lỗi khi cấu hình WordPress, nhưng website vẫn có thể hoạt động")
        
        # Bước 7: Lưu thông tin đăng nhập
        # await restore_tool.save_credentials(website_path, website_name)
        
        # Bước 8: Restart Herd Services
        await restore_tool.restart_herd_services()
        
        # Bước 9: Hiển thị thông tin thành công
        restore_tool.print_success_info(website_name)
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi trong quá trình restore: {e}")
        # Xóa thư mục đã tạo nếu thất bại
        if os.path.exists(website_path):
            shutil.rmtree(website_path)
        return False


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        if result:
            print("\n🎯 Quá trình restore hoàn tất thành công!")
        else:
            print("\n💥 Quá trình restore thất bại!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⏹️ Đã hủy quá trình restore!")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Lỗi không xác định: {e}")
        sys.exit(1)