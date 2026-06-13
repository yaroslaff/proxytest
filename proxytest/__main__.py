#!/usr/bin/env python3
"""
Скрипт для управления и тестирования прокси-серверов
"""

import requests
import sys
import argparse
from typing import Dict, Any
import json
from urllib.parse import urlparse

import configparser
import os
from pathlib import Path

__version__ = '0.1.2'

# pingtunnel:
#   https://habr.com/ru/articles/1036100/
#   srv: 
#     echo 1 > /proc/sys/net/ipv4/icmp_echo_ignore_all
#     pingtunnel -type server -key 6667
#   client:
#     pingtunnel -type client -l :6667 -s india.okerr.com -sock5 1 -key 6667
#
# masterdnsvpn: https://github.com/masterking32/MasterDnsVPN/
#   srv: masterdnsvpn -config /etc/masterdnsvpn/server_config.toml
#   client: masterdnsvpnclient -config /etc/vpn/client_config.toml -resolvers /etc/vpn/client_resolvers.txt
#

proxies = None


def list_proxies():
    """Вывести список всех прокси"""
    print("Avalable proxy server:\n")
    for name, config in proxies.items():
        print(f"Name: {name}")
        print(f"  Type: {config['type']}")
        print(f"  address: {config['host']}:{config['port']}")
        print(f"  Description: {config['description']}")
        print()

def test_proxy(proxy_name: str, test_url: str = "http://ip-api.com/json/"):
    if proxy_name not in proxies:
        print(f"Ошибка: прокси '{proxy_name}' не найден")
        print("Доступные прокси:", ", ".join(proxies.keys()))
        return False
    
    proxy_config = proxies[proxy_name]
    
    # Формируем строку прокси для requests
    proxy_url = f"{proxy_config['type']}://{proxy_config['host']}:{proxy_config['port']}"
    
    requests_proxies = {
        'http': proxy_url,
        'https': proxy_url
    }
    
    print(f"Testing proxy: {proxy_name}")
    print(f"type: {proxy_config['type']}")
    print(f"address: {proxy_config['host']}:{proxy_config['port']}")
    print(f"test url: {test_url}")
    print("-" * 50)
    
    try:
        # Настройка таймаутов
        timeout = 30
        
        # Выполняем запрос через прокси
        response = requests.get(
            test_url, 
            proxies=requests_proxies,
            timeout=timeout,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        
        # Проверяем статус ответа
        if response.status_code == 200:
            print("✅ OK: proxy works!")
            print(f"status: {response.status_code}")
            # print content type
            if "application/json" in response.headers.get('Content-Type', ''):
                print("response (json):")
                print(json.dumps(response.json(), indent=2))
            else:
                print("response (text):")
                print(response.text[:500] + "...")
            
            
            return True
        else:
            print(f"❌ ERROR: invalid code: {response.status_code}")
            print(f"server response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.ConnectTimeout:
        print("❌ ERROR: Timeout")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Connection error")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR: {e}")
        return False
    except Exception as e:
        print(f"❌ ERROR (unexpected): {e}")
        return False





def find_config() -> Path | None:
    CONFIG_FILENAME = f"proxytest.conf"

    CONFIG_SEARCH_PATHS = [
        Path(f"/etc/{CONFIG_FILENAME}"),
        Path(f"/etc/proxytest/{CONFIG_FILENAME}"),
        Path(f"/usr/local/etc/{CONFIG_FILENAME}"),
        Path.home() / f".{CONFIG_FILENAME}",
        Path.home() / f".config" / "proxytext" / CONFIG_FILENAME,
        Path(CONFIG_FILENAME),  # текущая директория
    ]

    for path in CONFIG_SEARCH_PATHS:
        if path.exists():
            return path

    searched = "\n  ".join(str(p) for p in CONFIG_SEARCH_PATHS)
    raise FileNotFoundError(
        f"Config file not found. Searched in:\n  {searched}"
    )

def load_config(path: Path) -> dict:
    parser = configparser.ConfigParser()
    parser.read(path, encoding="utf-8")
    result = {section: dict(parser[section]) for section in parser.sections()}
    for cfg in result.values():
        cfg["port"] = int(cfg["port"])
    return result

def load_proxies(config_path: str | None) -> dict:
    global proxies
    
    if config_path is None:
        config_path = find_config()

    print(f"[proxytest] Using config: {config_path}")
    proxies = load_config(config_path)


def existing_file(value: str) -> Path:
    path = Path(value)
    if not path.is_file():
        raise argparse.ArgumentTypeError(f"File not found: {value}")
    return path

def main():
    parser = argparse.ArgumentParser(description='proxy server check')
    parser.add_argument('proxy_name', nargs='?', help='proxy name')
    parser.add_argument('--url', default='http://ip-api.com/json/', help='URL for testing')    
    parser.add_argument('-c', '---config', help='Path to config file', default=None, type=existing_file)
    
    args = parser.parse_args()

    load_proxies(args.config)

    if args.proxy_name:
        # Basic test
        try:
            success = test_proxy(args.proxy_name, args.url)
            sys.exit(0 if success else 1)
        except KeyboardInterrupt:
            print("Ctrl-C? Okay, bye!")
    else:
        list_proxies()
        print("\nИспользование:")
        print("  python proxy_manager.py [имя_прокси] --url [URL]")
        print("  python proxy_manager.py proxy1")
        print("  python proxy_manager.py proxy2 --url https://httpbin.org/ip")
        print("  python proxy_manager.py --test throne")
        print("  URLs for IP: https://linuxconfig.org/how-to-use-curl-to-get-public-ip-address")

if __name__ == "__main__":
    main()
