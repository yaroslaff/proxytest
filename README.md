# Proxytest

Test HTTP / SOCKS proxies.

### Install
~~~
pipx install git+http://github.com/yaroslaff/proxytest.git
~~~

### Configuration
Example config file (`/etc/proxytest.conf`)
~~~
[wireproxy-jul]
type = http
host = localhost
port = 31281
description = my main http proxy

[warp]
type = socks5
host = 127.0.0.1
port = 1188
~~~

### Usage
(I skipped some data in output)

~~~
$ proxytest warp
[proxytest] Using config: /etc/proxytest.conf
Testing proxy: warp
type: socks5
address: 127.0.0.1:1188
test url: http://ip-api.com/json/
--------------------------------------------------
✅ OK: proxy works!
status: 200
response (json):
{
  "status": "success",
  "country": "---",
  "countryCode": "---",
  "region": "---",
  "regionName": "---",
  "city": "---",
  "zip": "---",
  "lat": ---,
  "lon": ---,
  "timezone": "---",
  "isp": "Cloudflare, Inc.",
  "org": "Cloudflare WARP",
  "as": "--- Cloudflare, Inc.",
  "query": "---"
}
~~~

### Options
~~~
$ proxytest -h
usage: proxytest [-h] [--url URL] [-c CONFIG] [proxy_name]

proxy server check

positional arguments:
  proxy_name            proxy name

options:
  -h, --help            show this help message and exit
  --url URL             URL for testing
  -c, ---config CONFIG  Path to config file
~~~
