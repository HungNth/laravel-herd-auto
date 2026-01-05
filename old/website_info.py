import os
import sys
import asyncio
import json
from datetime import datetime

import config
from commands import run_command, run_sql_command


class WebsiteInfoExtractor:
    def __init__(self):
        self.herd_sites_path = config.herd_sites_path
        self.admin_username = config.admin_username
        self.admin_password = config.admin_password
        self.admin_email = config.admin_email
        
    def get_website_list(self) -> list:
        try:
            websites = []
            if os.path.exists(self.herd_sites_path):
                for item in os.listdir(self.herd_sites_path):
                    website_path = os.path.join(self.herd_sites_path, item)
                    if os.path.isdir(website_path):
                        # Kiểm tra có phải website WordPress không
                        if os.path.exists(os.path.join(website_path, 'wp-login.php')):
                            websites.append(item)
            return sorted(websites)
        except Exception as e:
            print(f"❌ Lỗi khi lấy danh sách website: {e}")
            return []
    
    def print_website_list(self, websites: list):
        if not websites:
            print("❌ Không tìm thấy website WordPress nào!")
            return
            
        print("\n📋 DANH SÁCH WEBSITE WORDPRESS:")
        print("=" * 50)
        for i, website in enumerate(websites, 1):
            print(f"{i:2d}. {website}")
        print("=" * 50)
    
    def choose_website(self, websites: list) -> str:
        while True:
            try:
                choice = input("\n🔢 Chọn website (nhập số thứ tự): ").strip()
                choice_num = int(choice)
                
                if 1 <= choice_num <= len(websites):
                    return websites[choice_num - 1]
                else:
                    print(f"❌ Vui lòng nhập số từ 1 đến {len(websites)}!")
                    
            except ValueError:
                print("❌ Vui lòng nhập một số hợp lệ!")
            except KeyboardInterrupt:
                print("\n⏹️ Đã hủy!")
                sys.exit(0)
    
    async def get_wordpress_version(self, website_path: str) -> str:
        try:
            wp_cli_cmd = f'wp --path="{website_path}"'
            result = await run_command(f'{wp_cli_cmd} core version')
            return result.stdout.strip() if result.stdout else "Unknown"
        except Exception:
            return "Error"
    
    async def get_all_themes(self, website_path: str) -> list:
        try:
            wp_cli_cmd = f'wp --path="{website_path}"'
            result = await run_command(f'{wp_cli_cmd} theme list --format=json')
            
            if result.stdout:
                return json.loads(result.stdout)
            return []
        except Exception:
            return []
    
    async def get_all_plugins(self, website_path: str) -> list:
        try:
            wp_cli_cmd = f'wp --path="{website_path}"'
            result = await run_command(f'{wp_cli_cmd} plugin list --format=json')
            
            if result.stdout:
                return json.loads(result.stdout)
            return []
        except Exception:
            return []
    
    async def get_server_info(self, website_path: str) -> dict:
        try:
            wp_cli_cmd = f'wp --path="{website_path}"'
            
            # Lấy PHP version
            php_result = await run_command(f'{wp_cli_cmd} eval "echo phpversion();"')
            php_version = php_result.stdout.strip() if php_result.stdout else "Unknown"
            
            # Lấy MySQL version
            mysql_result = await run_sql_command('-e "SELECT VERSION();"')
            mysql_version = "Unknown"
            if mysql_result.stdout:
                lines = mysql_result.stdout.strip().split('\n')
                if len(lines) >= 2:
                    mysql_version = lines[1].strip()
            
            return {
                "php_version": php_version,
                "mysql_version": mysql_version
            }
        except Exception:
            return {"php_version": "Error", "mysql_version": "Error"}
    
    async def extract_all_info(self, website_name: str) -> dict:
        website_path = os.path.join(self.herd_sites_path, website_name)
        
        if not os.path.exists(website_path):
            raise Exception(f"Website '{website_name}' không tồn tại!")
            
        if not os.path.exists(os.path.join(website_path, 'wp-login.php')):
            raise Exception(f"'{website_name}' không phải là website WordPress!")
        
        print(f"🔍 Đang thu thập thông tin website: {website_name}")
        print("⏳ Vui lòng đợi...")
        
        # Thu thập thông tin song song
        wp_version_task = self.get_wordpress_version(website_path)
        themes_task = self.get_all_themes(website_path)
        plugins_task = self.get_all_plugins(website_path)
        server_info_task = self.get_server_info(website_path)
        
        # Đợi tất cả task hoàn thành
        wp_version, themes, plugins, server_info = await asyncio.gather(
            wp_version_task,
            themes_task,
            plugins_task,
            server_info_task
        )
        
        # Kết hợp tất cả thông tin
        all_info = {
            "website_name": website_name,
            "wordpress_version": wp_version,
            "themes": themes,
            "plugins": plugins,
            "admin_username": self.admin_username,
            "admin_password": self.admin_password,
            "admin_email": self.admin_email,
            **server_info,
            "scan_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return all_info
    
    def print_info(self, info: dict):
        print("\n" + "=" * 60)
        print("📊 THÔNG TIN WEBSITE WORDPRESS")
        print("=" * 60)
        
        print(f"🌐 Website: {info['website_name']}")
        print(f"📅 Thời gian quét: {info['scan_time']}")
        
        print(f"\n📦 WordPress Version: {info['wordpress_version']}")
        
        print(f"\n🎨 THEMES:")
        if info['themes']:
            for theme in info['themes']:
                status = "✅" if theme.get('status') == 'active' else "⭕"
                print(f"   {status} {theme.get('name', 'Unknown')} (v{theme.get('version', 'Unknown')})")
        else:
            print("   ❌ Không tìm thấy theme nào")
        
        print(f"\n🔌 PLUGINS:")
        if info['plugins']:
            for plugin in info['plugins']:
                status = "✅" if plugin.get('status') == 'active' else "⭕"
                print(f"   {status} {plugin.get('name', 'Unknown')} (v{plugin.get('version', 'Unknown')})")
        else:
            print("   ❌ Không tìm thấy plugin nào")
        
        print(f"\n👤 ADMIN INFO:")
        print(f"   Username: {info['admin_username']}")
        print(f"   Password: {info['admin_password']}")
        print(f"   Email: {info['admin_email']}")
        
        print(f"\n🖥️ SERVER INFO:")
        print(f"   PHP Version: {info['php_version']}")
        print(f"   MySQL Version: {info['mysql_version']}")
        
        print("=" * 60)
    
    def save_to_website_folder(self, info: dict):
        try:
            website_path = os.path.join(self.herd_sites_path, info['website_name'])
            output_path = os.path.join(website_path, f"website_info_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("THÔNG TIN WEBSITE WORDPRESS\n")
                f.write("=" * 60 + "\n\n")
                
                f.write(f"Website: {info['website_name']}\n")
                f.write(f"Thời gian quét: {info['scan_time']}\n\n")
                
                f.write(f"WordPress Version: {info['wordpress_version']}\n\n")
                
                f.write("THEMES:\n")
                f.write("-" * 20 + "\n")
                if info['themes']:
                    for theme in info['themes']:
                        status = "Active" if theme.get('status') == 'active' else "Inactive"
                        f.write(f"- {theme.get('name', 'Unknown')} (v{theme.get('version', 'Unknown')}) - {status}\n")
                else:
                    f.write("- Không tìm thấy theme nào\n")
                
                f.write("\nPLUGINS:\n")
                f.write("-" * 20 + "\n")
                if info['plugins']:
                    for plugin in info['plugins']:
                        status = "Active" if plugin.get('status') == 'active' else "Inactive"
                        f.write(f"- {plugin.get('name', 'Unknown')} (v{plugin.get('version', 'Unknown')}) - {status}\n")
                else:
                    f.write("- Không tìm thấy plugin nào\n")
                
                f.write("\nADMIN INFO:\n")
                f.write("-" * 20 + "\n")
                f.write(f"Username: {info['admin_username']}\n")
                f.write(f"Password: {info['admin_password']}\n")
                f.write(f"Email: {info['admin_email']}\n")
                
                f.write("\nSERVER INFO:\n")
                f.write("-" * 20 + "\n")
                f.write(f"PHP Version: {info['php_version']}\n")
                f.write(f"MySQL Version: {info['mysql_version']}\n")
                
                f.write("\n" + "=" * 60 + "\n")
            
            print(f"� Đã lưu thông tin vào: {output_path}")
            
        except Exception as e:
            print(f"❌ Lỗi khi lưu file: {e}")


async def main():
    print("🔍 CÔNG CỤ KIỂM TRA THÔNG TIN WEBSITE WORDPRESS")
    print("=" * 50)
    
    extractor = WebsiteInfoExtractor()
    
    # Lấy danh sách website
    websites = extractor.get_website_list()
    
    if not websites:
        print("❌ Không tìm thấy website WordPress nào trong thư mục sites!")
        return
    
    # Hiển thị danh sách và cho user chọn
    extractor.print_website_list(websites)
    website_name = extractor.choose_website(websites)
    
    try:
        # Trích xuất thông tin
        info = await extractor.extract_all_info(website_name)
        
        # Hiển thị thông tin
        extractor.print_info(info)
        
        # Tự động lưu vào thư mục website
        extractor.save_to_website_folder(info)
        
        print("\n✅ Hoàn tất!")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️ Đã hủy!")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Lỗi không xác định: {e}")
        sys.exit(1)