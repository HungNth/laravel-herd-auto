import argparse


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
        help='Add item'
    )
    
    parser.add_argument(
        '-d', '--delete',
        action='store_true',
        help='Delete item'
    )
    
    args = parser.parse_args()
    
    if args.add:
        wp.create_website()
    
    if args.delete:
        wp.delete_websites()


if __name__ == "__main__":
    main()
