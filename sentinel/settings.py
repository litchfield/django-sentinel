from django.conf import settings

# Max WINDOW_MAX hits in WINDOW hours or greylist
WINDOW = getattr(settings, 'SENTINEL_WINDOW', 1) 
WINDOW_MAX = getattr(settings, 'SENTINEL_WINDOW_MAX', 50) 

# Max hits per minute or greylist
RATE_MAX = getattr(settings, 'SENTINEL_RATE', 10) 

# Expire greylist after how many minutes (default 24 hours)
# NOTE If it's less than WINDOW, you *may* get some unintentional expiries
# when the cache is restarted
EXPIRE = getattr(settings, 'SENTINEL_EXPIRE', 24*60) * 60

# Blacklist the buggers after this many greylistings and maybe mail_admins
AUTO_BLACK = getattr(settings, 'SENTINEL_AUTO_BLACK', 3)
AUTO_BLACK_EMAIL = getattr(settings, 'SENTINEL_AUTO_BLACK_EMAIL', True)

# If you really just like tweaking stuff
CACHE_PREFIX = getattr(settings, 'SENTINEL_CACHE_PREFIX', 'DJS!')
