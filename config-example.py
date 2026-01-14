# Laravel Herd Configuration File
win_herd_sites_path = r'F:\laravel-herd\sites'
win_herd_cached_path = r'F:\laravel-herd\cached'

mac_herd_sites_path = r''
mac_herd_cached_path = r''

admin_username = 'admin'
admin_password = 'admin'
admin_email = 'admin@gmail.com'

db_host = 'localhost'
db_port = 3306
db_username = 'root'
db_password = ''
db_socket = ''

default_theme_slug = 'flatsome'

themes = [
    {
        "name": "Flatsome",
        "slug": "flatsome",
    },
    {
        "name": "Jannah",
        "slug": "jannah",
    },
    {
        "name": "Avada",
        "slug": "Avada",
    },
    {
        "name": "Woodmart",
        "slug": "flatsome",
    },
    {
        "name": "Bricks",
        "slug": "bricks",
    },
    {
        "name": "Etch Theme",
        "slug": "etch-theme",
    }
]

plugins = [
    {
        'name': 'Advanced Custom Fields PRO',
        'slug': 'advanced-custom-fields-pro'
    },
    {
        'name': 'All-in-One WP Migration Unlimited Extension',
        'slug': 'all-in-one-wp-migration-unlimited-extension'
    },
    {
        'name': 'Rank Math SEO PRO',
        'slug': 'seo-by-rank-math-pro'
    },
    {
        'name': 'UpdraftPlus - Backup/Restore',
        'slug': 'updraftplus'
    },
    {
        'name': 'WP Mail SMTP Pro',
        'slug': 'wp-all-import-pro'
    },
    {
        'name': 'Admin and Site Enhancements (ASE) Pro',
        'slug': 'admin-site-enhancements-pro'
    },
    {
        'name': 'WP Rocket',
        'slug': 'wp-rocket'
    },
    {
        'name': 'Duplicator Pro',
        'slug': 'duplicator-pro'
    },
    {
        'name': 'Elementor Pro',
        'slug': 'elementor-pro'
    },
    {
        'name': 'FluentCart Pro',
        'slug': 'fluent-cart-pro'
    },
    {
        'name': 'Blocksy Companion (Premium)',
        'slug': 'blocksy-companion-pro'
    },
    {
        'name': 'Etch',
        'slug': 'etch'
    },
    {
        'name': 'Automatic.css',
        'slug': 'automaticcss-plugin'
    },
    {
        'name': 'GP Premium',
        'slug': 'gp-premium'
    },
    {
        'name': 'GenerateBlocks Pro',
        'slug': 'generateblocks-pro'
    },
    {
        'name': 'Tocer',
        'slug': 'tocer'
    },
    {
        'name': 'Perfmatters',
        'slug': 'perfmatters'
    }

]

bulk_restore_path = 'bulk_restore.csv'

api_base_url = ''
api_key = ''

wp_version_api = 'https://api.wordpress.org/core/version-check/1.7/'
language = 'vi'

wp_options = [
    'config set WP_DEBUG true',
    'config set WP_DEBUG_LOG true',
    'config set WP_DEBUG_DISPLAY true',
    'config set WP_MEMORY_LIMIT 256M',
    'config set AUTOSAVE_INTERVAL 600',
    'config set WP_POST_REVISIONS 5',
    'config set EMPTY_TRASH_DAYS 21',
    'config set DISABLE_WP_CRON true',
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

excludes = [
    '*/node_modules/*',
    '*/.git/*',
    '*/.idea/*',
    '*/.vscode/*',
    '*/.DS_Store',
    '*/debug.log',
    '*/cache/*',
    '*/wp-content/cache/*',
    '*/wp-content/upgrade/*',
    '*/wp-content/backup-db/*',
    '*/wp-content/backups/*',
]
