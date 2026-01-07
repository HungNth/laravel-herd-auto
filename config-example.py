# Laravel Herd Configuration File
win_herd_sites_path = r"F:\laravel-herd\sites"
win_herd_cached_path = r"F:\laravel-herd\cached"
win_herd_bin_path = r"C:\Users\HungOMS\.config\herd\bin"

mac_herd_sites_path = r""
mac_herd_cached_path = r""
mac_herd_bin_path = r""

admin_username = "admin"
admin_password = "admin"
admin_email = "thienhungdev@gmail.com"

db_host = "localhost"
db_port = 3306
db_username = "root"
db_password = ""
db_socket = ""

theme_api = "themes.json"
plugin_api = "plugins.json"

bulk_restore_path = "bulk_restore.csv"

api_base_url = ""
api_key = ""

wp_version_api = "https://api.wordpress.org/core/version-check/1.7/"
language = "vi"

wp_options = [
    "config set WP_DEBUG true",
    "config set WP_DEBUG_LOG true",
    "config set WP_DEBUG_DISPLAY true",
    "config set WP_MEMORY_LIMIT 256M",
    "config set AUTOSAVE_INTERVAL 600",
    "config set WP_POST_REVISIONS 5",
    "config set EMPTY_TRASH_DAYS 21",
    'rewrite structure "/%category%/%postname%/"',
    'option update timezone_string "Asia/Ho_Chi_Minh"',
    'option update time_format "H:i"',
    'option update date_format "d/m/Y"',
    'option update large_size_w 0',
    'option update large_size_h 0',
    'option update medium_large_size_w 0',
    'option update medium_large_size_h 0',
    'option update medium_size_w 0',
    'option update medium_size_h 0',
    'option update thumbnail_size_w 0',
    'option update thumbnail_size_h 0',
    'option update thumbnail_crop 0',
    'option update comment_moderation 1',
    'option update default_ping_status closed',
    'option update posts_per_page 30',
    'option update posts_per_rss 210',
    'option update rss_use_excerpt 1',
    'option update avatar_default identicon'
]
