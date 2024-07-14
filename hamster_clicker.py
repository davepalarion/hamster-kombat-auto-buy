from requests import post
from time import time, sleep
from heapq import heappush, heappop

# Colors for terminal output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[0;33m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    BLUE = '\033[0;34m'
    RESET = '\033[0m'

# Function to wait for cooldown period
def wait_for_cooldown(cooldown_seconds):
    print(f"{Colors.YELLOW}Upgrade is on cooldown. Waiting for cooldown period of {Colors.CYAN}{cooldown_seconds}{Colors.YELLOW} seconds...{Colors.RESET}")
    sleep(cooldown_seconds)

# Function to purchase upgrade
def purchase_upgrade(authorization, upgrade_id):
    timestamp = int(time() * 1000)
    url = "https://api.hamsterkombatgame.io/clicker/buy-upgrade"
    headers = {
        "Content-Type": "application/json",
        "Authorization": authorization,
        "Origin": "https://hamsterkombatgame.io",
        "Referer": "https://hamsterkombatgame.io/"
    }
    data = {
        "upgradeId": upgrade_id,
        "timestamp": timestamp
    }
    response = post(url, headers=headers, json=data)
    return response.json()

# Headers for requests
authorization = input(f"{Colors.GREEN}Enter Authorization [{Colors.CYAN}Example: {Colors.YELLOW}Bearer 171852....{Colors.GREEN}]: {Colors.RESET}")

headers = {
    'User-Agent': 'Mozilla/5.0 (Android 12; Mobile; rv:102.0) Gecko/102.0 Firefox/102.0',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://hamsterkombatgame.io/',
    'Authorization': authorization,
    'Origin': 'https://hamsterkombatgame.io',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'Priority': 'u=4',
}

while True:
    # Get available upgrades
    response = post('https://api.hamsterkombatgame.io/clicker/upgrades-for-buy', headers=headers).json()

    # Filter and sort upgrades
    upgrades = [
        item for item in response["upgradesForBuy"]
        if not item["isExpired"] and item["isAvailable"] and item["price"] > 0
    ]

    upgrades_with_ratios = []
    for item in upgrades:
        upgrades_with_ratios.append({
            'ratio': item["profitPerHourDelta"] / item["price"] * 100,
            'max_profit': item["profitPerHourDelta"],
            'budget': item["price"],
            'item': item,
        })

    upgrades_with_ratios.sort(key=lambda x: x['ratio'], reverse=True)
    upgrades_with_ratios = upgrades_with_ratios[:20]
    print(f"{Colors.PURPLE}================================================{Colors.RESET}")
    # Get current balance
    url = "https://api.hamsterkombatgame.io/clicker/sync"
    response = post(url, headers=headers)
    current_balance = float(response.json().get('clickerUser', {}).get('balanceCoins', 0))
    print(f"{Colors.GREEN}Current Balance: {Colors.CYAN}{current_balance:,}{Colors.RESET}")
    print(f"{Colors.PURPLE}=================================================================================================={Colors.RESET}")

    # Find the first upgrade that meets the criteria
    selected_upgrade = None
    for upgrade in upgrades_with_ratios[:20]:  # Only consider the top 10 upgrades
        cooldown_seconds = upgrade['item'].get('cooldownSeconds', 0)
        if cooldown_seconds == 0 and current_balance >= upgrade['budget']:
            selected_upgrade = upgrade['item']  # Assign the entire upgrade object
            break  # Stop looping once the first suitable upgrade is found

    # Print the selected upgrade if found
    if selected_upgrade:
        print(f"{Colors.GREEN}First upgrade with no cooldown and affordable: {Colors.CYAN}{selected_upgrade['name']}{Colors.RESET}")
    else:
        print(f"{Colors.RED}No upgrade found that meets the criteria.{Colors.RESET}")

    # Further code remains the same...

    print(f"{Colors.PURPLE}=================================================================================================={Colors.RESET}")
    # Print headers for columns
    print(f"{Colors.GREEN}{'No':<3} | {'Upgrade Name':<40} | {'Budget':<10} | {'Max Profit':<10} | {'Ratio (%)':<10} | {'Cooldown':<10}{Colors.RESET}")
    print(f"{Colors.PURPLE}{'='*3} | {'='*40} | {'='*10} | {'='*10} | {'='*10} | {'='*10}{Colors.RESET}")
    # Print each upgrade in columns
    i = 1
    for upgrade in upgrades_with_ratios:
        cooldown_seconds = upgrade['item'].get('cooldownSeconds', 0)
        hours, remainder = divmod(cooldown_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        cooldown_message = f"{Colors.RED}{hours:02}:{minutes:02}:{seconds:02}{Colors.RESET}" if cooldown_seconds > 0 else ""
        print(f"{Colors.GREEN}{i:<3} | {upgrade['item']['name']:<40} | {upgrade['budget']:<10,} | {upgrade['max_profit']:<10,} | {upgrade['ratio']:.2f}%{'':<5} | {cooldown_message:<10}{Colors.RESET}")

        i += 1

    # Attempt to purchase the upgrade if selected
    if selected_upgrade:
        upgrade_id = selected_upgrade['id']  # Access 'id' field from selected_upgrade
        print(f"{Colors.GREEN}Attempting to purchase upgrade '{Colors.YELLOW}{upgrade_id}{Colors.GREEN}'...{Colors.RESET}\n")

        purchase_status = purchase_upgrade(authorization, upgrade_id)

        if 'error_code' in purchase_status:
            wait_for_cooldown(cooldown_seconds)
        else:
            print(f"{Colors.GREEN}Upgrade '{Colors.YELLOW}{upgrade_id}{Colors.GREEN}' purchased successfully.{Colors.RESET}")
            print(f"{Colors.GREEN}Waiting 8 seconds before next purchase...{Colors.RESET}")
            sleep(8)  # Wait for 8 seconds after a successful purchase

    # Wait for 10 seconds before the next iteration
    print(f"{Colors.PURPLE}=================================================================================================={Colors.RESET}")
    print(f"{Colors.YELLOW}Waiting for 10 seconds before next iteration...{Colors.RESET}")
    sleep(10)
