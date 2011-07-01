Django Sentinel
===============

Sentinel blocks would-be scrapers dead in their tracks. Check it out. 

I caught thousands within the first few weeks in production. 

Idea is suspicious activity gets greylisted for a while. Then if they repeat offend, they
get blacklisted. You can define whitelists and blacklists manually too.

Then there's brownlists. If you want to get dirty with your scrapers, and feed them spoof
content, you can brownlist them and use `request.brownlisted` in your views and templates
to alter what they receive.

It works by using memcached to track visitor usage patterns. It's pretty well optimised, 
only one getmany() on the cache per hit. Only hits the database when it starts up, blocks,
or when stuff is changed via admin.

Custom admin forms for bulk entry of whitelists etc.

Network range and globbing support. eg 123.123.0.0/16 or 123.123.*.*

Experimental IPv6 support.


Coming soon
-----------

* Including fixtures of whitelists of known bots and their IP's. Eg googlebot, etc.
* Clever cookie-ing, so we don't block an IP that might be being shared by heaps of legit users.
* Make it even faster using a local in-process hash (aswell as cache and database)


Installation
------------

1. Add "sentinel" to your INSTALLED\_APPS
2. Add "SentinelMiddleware" to your MIDDLEWARE\_CLASSES
3. Tweak settings
4. Sit back and see what it catches. Make sure you whitelist bots you actually want.


Settings
--------

`SENTINEL_WINDOW`
`SENTINEL_WINDOW_MAX`
:   Max SENTINEL_WINDOW hits in SENTINEL_WINDOW_MAX hours, or greylist 'em

`SENTINEL_RATE`
:   Max hits per minute, or greylist 'em

`SENTINEL_EXPIRE`
:   Expire greylist after how many minutes (default 24 hours' worth)

`SENTINEL_AUTO_BLACK`
:   Auto blacklist a repeat offending greylister after this many offences

`SENTINEL_AUTO_BLACK_EMAIL`
:   Boolean, whether or not to email when sentinel auto blacklists an address

`SENTINEL_NETRANGE`
:   Optimise sentinel by restricting the number of network ranges it accepts
    for whitelisting, greylisting and brownlisting.
    By default it's /16, /24, /29, /30, /31, but you can reduce or expand it 
    to suit your needs. 
    Just a list/tuple of integers.
    Eg, disable network range support completely with an empty list. 




