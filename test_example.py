#!/usr/bin/env python3
"""
M2P Wallet Verification System - Test Example
Demonstrates how to test the verification system manually
"""
import requests
import time
import json

# Configuration
API_URL = 'http://localhost:5000'
ADMIN_API_KEY = 'change_this_in_production'  # Use your actual admin key

def print_response(title, response):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print('='*60)
    print(f"Status Code: {response.status_code}")
    try:
        data = response.json()
        print(json.dumps(data, indent=2))
    except:
        print(response.text)
    print('='*60)

def test_health_check():
    """Test health check endpoint"""
    response = requests.get(f'{API_URL}/health')
    print_response("Health Check", response)
    return response.status_code == 200

def test_player_registration(wallet_address):
    """Test player registration"""
    response = requests.post(
        f'{API_URL}/api/register',
        json={'wallet_address': wallet_address}
    )
    print_response(f"Register Player: {wallet_address}", response)

    if response.status_code in [200, 201]:
        data = response.json()
        if data.get('success'):
            return data
    return None

def test_get_player(wallet_address):
    """Test get player info"""
    response = requests.get(f'{API_URL}/api/player/{wallet_address}')
    print_response(f"Get Player: {wallet_address}", response)

    if response.status_code == 200:
        return response.json()
    return None

def test_verify_now(wallet_address):
    """Test manual verification check"""
    response = requests.post(
        f'{API_URL}/api/verify-now',
        json={'wallet_address': wallet_address}
    )
    print_response(f"Verify Now: {wallet_address}", response)

    if response.status_code == 200:
        return response.json()
    return None

def test_admin_verify_player(wallet_address, tx_hash='manual_test_verification'):
    """Test admin manual verification"""
    response = requests.post(
        f'{API_URL}/admin/verify-player',
        json={
            'wallet_address': wallet_address,
            'tx_hash': tx_hash
        },
        headers={'X-API-Key': ADMIN_API_KEY}
    )
    print_response(f"Admin Verify Player: {wallet_address}", response)

    if response.status_code == 200:
        return response.json()
    return None

def test_admin_get_players(verified=None):
    """Test admin get players"""
    params = {}
    if verified is not None:
        params['verified'] = 'true' if verified else 'false'

    response = requests.get(
        f'{API_URL}/admin/players',
        params=params,
        headers={'X-API-Key': ADMIN_API_KEY}
    )
    print_response("Admin Get Players", response)

    if response.status_code == 200:
        return response.json()
    return None

def test_admin_get_logs(wallet_address=None):
    """Test admin get verification logs"""
    params = {}
    if wallet_address:
        params['wallet_address'] = wallet_address

    response = requests.get(
        f'{API_URL}/admin/verification-logs',
        params=params,
        headers={'X-API-Key': ADMIN_API_KEY}
    )
    print_response("Admin Get Verification Logs", response)

    if response.status_code == 200:
        return response.json()
    return None

def run_full_test():
    """Run complete test flow"""
    print("\n" + "="*60)
    print("M2P Wallet Verification System - Full Test")
    print("="*60)

    test_wallet = f"ADVC_test_wallet_{int(time.time())}"

    # 1. Health Check
    print("\n1. Testing Health Check...")
    if not test_health_check():
        print("❌ Health check failed!")
        return

    # 2. Register Player
    print("\n2. Testing Player Registration...")
    registration = test_player_registration(test_wallet)
    if not registration:
        print("❌ Registration failed!")
        return

    verification_amount = registration.get('verification_amount')
    print(f"\n✓ Player registered! Verification amount: {verification_amount} ADVC")

    # 3. Get Player Info
    print("\n3. Testing Get Player Info...")
    player_info = test_get_player(test_wallet)
    if not player_info:
        print("❌ Get player failed!")
        return
    print("✓ Player info retrieved")

    # 4. Try Automatic Verification (will fail - no real transaction)
    print("\n4. Testing Automatic Verification Check...")
    verify_result = test_verify_now(test_wallet)
    if verify_result and not verify_result.get('verified'):
        print("✓ Verification pending (expected - no real transaction)")

    # 5. Admin Manual Verification
    print("\n5. Testing Admin Manual Verification...")
    admin_verify = test_admin_verify_player(test_wallet)
    if admin_verify and admin_verify.get('success'):
        player = admin_verify.get('player', {})
        ap_credited = player.get('total_ap', 0)
        print(f"✓ Player manually verified! AP credited: {ap_credited}")

    # 6. Verify Player Status Changed
    print("\n6. Verifying Player Status Changed...")
    updated_player = test_get_player(test_wallet)
    if updated_player:
        player = updated_player.get('player', {})
        if player.get('verified'):
            print("✓ Player verified status confirmed")
        else:
            print("❌ Player not verified")

    # 7. Get All Players
    print("\n7. Testing Get All Players (Admin)...")
    all_players = test_admin_get_players()
    if all_players:
        total = all_players.get('total', 0)
        print(f"✓ Retrieved {total} players")

    # 8. Get Verified Players Only
    print("\n8. Testing Get Verified Players (Admin)...")
    verified_players = test_admin_get_players(verified=True)
    if verified_players:
        total = verified_players.get('total', 0)
        print(f"✓ Retrieved {total} verified players")

    # 9. Get Verification Logs
    print("\n9. Testing Get Verification Logs (Admin)...")
    logs = test_admin_get_logs()
    if logs:
        total = logs.get('total', 0)
        print(f"✓ Retrieved {total} verification logs")

    # 10. Get Logs for Test Wallet
    print("\n10. Testing Get Logs for Specific Wallet (Admin)...")
    wallet_logs = test_admin_get_logs(test_wallet)
    if wallet_logs:
        total = wallet_logs.get('total', 0)
        print(f"✓ Retrieved {total} logs for {test_wallet}")

    print("\n" + "="*60)
    print("✓ All Tests Completed Successfully!")
    print("="*60)

def run_interactive_test():
    """Interactive test mode"""
    print("\n" + "="*60)
    print("M2P Wallet Verification System - Interactive Test")
    print("="*60)

    while True:
        print("\nOptions:")
        print("1. Health Check")
        print("2. Register Player")
        print("3. Get Player Info")
        print("4. Check Verification")
        print("5. Admin: Manually Verify Player")
        print("6. Admin: Get All Players")
        print("7. Admin: Get Verification Logs")
        print("8. Run Full Test")
        print("0. Exit")

        choice = input("\nEnter choice: ").strip()

        if choice == '0':
            break
        elif choice == '1':
            test_health_check()
        elif choice == '2':
            wallet = input("Enter wallet address: ").strip()
            test_player_registration(wallet)
        elif choice == '3':
            wallet = input("Enter wallet address: ").strip()
            test_get_player(wallet)
        elif choice == '4':
            wallet = input("Enter wallet address: ").strip()
            test_verify_now(wallet)
        elif choice == '5':
            wallet = input("Enter wallet address: ").strip()
            tx_hash = input("Enter tx hash (or press enter for default): ").strip()
            test_admin_verify_player(wallet, tx_hash or 'manual_verification')
        elif choice == '6':
            verified = input("Filter by verified? (yes/no/all): ").strip().lower()
            if verified == 'yes':
                test_admin_get_players(verified=True)
            elif verified == 'no':
                test_admin_get_players(verified=False)
            else:
                test_admin_get_players()
        elif choice == '7':
            wallet = input("Filter by wallet? (or press enter for all): ").strip()
            test_admin_get_logs(wallet or None)
        elif choice == '8':
            run_full_test()
        else:
            print("Invalid choice!")

if __name__ == '__main__':
    import sys

    print("""
M2P Wallet Verification System - Test Suite

Before running tests:
1. Ensure the server is running: python -m server.app
2. Update ADMIN_API_KEY in this script with your actual key
3. Server should be accessible at http://localhost:5000
    """)

    if len(sys.argv) > 1 and sys.argv[1] == 'auto':
        run_full_test()
    else:
        run_interactive_test()
