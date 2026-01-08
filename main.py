import argparse
import sys


def main():
    from wordpress.wp import WordPress
    from wordpress.wp_cli import WPCLI
    from wordpress.wp_api import WPApi
    from db.mysql import MySQL
    
    wp_cli = WPCLI()
    wp_api = WPApi()
    mysql = MySQL()
    
    wp = WordPress(wp_cli, wp_api, mysql)
    
    parser = argparse.ArgumentParser(
        description='WordPress CLI Tool'
    )
    
    parser.add_argument(
        '-a', '--add',
        action='store_true',
        help='Add a new website'
    )
    
    parser.add_argument(
        '-d', '--delete',
        action='store_true',
        help='Delete website(s)'
    )
    
    parser.add_argument(
        '-b', '--backup',
        action='store_true',
        help='Backup website options'
    )
    
    parser.add_argument(
        '-r', '--restore',
        action='store_true',
        help='Restore website options'
    )
    
    if len(sys.argv) == 1:
        wp.configure_wp()
    
    args = parser.parse_args()
    
    if args.add:
        wp.create_website()
    
    if args.delete:
        wp.delete_websites()
    
    if args.backup:
        wp.backup_options()
    
    if args.restore:
        wp.restore_options()


if __name__ == "__main__":
    main()
