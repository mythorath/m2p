#!/usr/bin/env python3
"""
M2P Admin CLI Tool
Provides administrative commands for managing the M2P platform
"""

import argparse
import sys
import os
import json
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

# Database connection string from environment
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://m2p_user:password@localhost:5432/m2p_db')


class M2PAdmin:
    def __init__(self):
        try:
            self.conn = psycopg2.connect(DATABASE_URL)
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        except Exception as e:
            print(f"Error connecting to database: {e}")
            sys.exit(1)

    def __del__(self):
        if hasattr(self, 'cursor'):
            self.cursor.close()
        if hasattr(self, 'conn'):
            self.conn.close()

    def verify_player(self, wallet: str, level: int = 1):
        """Verify a player's account"""
        try:
            self.cursor.execute(
                """
                UPDATE players
                SET verification_level = %s
                WHERE wallet_address = %s
                RETURNING id, wallet_address, verification_level
                """,
                (level, wallet)
            )
            self.conn.commit()

            result = self.cursor.fetchone()
            if result:
                print(f"✓ Player verified successfully")
                print(f"  Wallet: {result['wallet_address']}")
                print(f"  Verification Level: {result['verification_level']}")
            else:
                print(f"✗ Player not found: {wallet}")
        except Exception as e:
            self.conn.rollback()
            print(f"✗ Error verifying player: {e}")

    def reset_verification(self, wallet: str):
        """Reset player verification"""
        try:
            self.cursor.execute(
                """
                UPDATE players
                SET verification_level = 0
                WHERE wallet_address = %s
                RETURNING id, wallet_address
                """,
                (wallet,)
            )
            self.conn.commit()

            result = self.cursor.fetchone()
            if result:
                print(f"✓ Verification reset for {result['wallet_address']}")
            else:
                print(f"✗ Player not found: {wallet}")
        except Exception as e:
            self.conn.rollback()
            print(f"✗ Error resetting verification: {e}")

    def award_ap(self, wallet: str, amount: int):
        """Award achievement points to a player"""
        try:
            self.cursor.execute(
                """
                UPDATE players
                SET achievement_points = achievement_points + %s
                WHERE wallet_address = %s
                RETURNING id, wallet_address, achievement_points
                """,
                (amount, wallet)
            )
            self.conn.commit()

            result = self.cursor.fetchone()
            if result:
                print(f"✓ Awarded {amount} AP")
                print(f"  Wallet: {result['wallet_address']}")
                print(f"  Total AP: {result['achievement_points']}")
            else:
                print(f"✗ Player not found: {wallet}")
        except Exception as e:
            self.conn.rollback()
            print(f"✗ Error awarding AP: {e}")

    def ban_player(self, wallet: str, reason: str = "Violation of terms"):
        """Ban a player"""
        try:
            self.cursor.execute(
                """
                UPDATE players
                SET is_banned = true
                WHERE wallet_address = %s
                RETURNING id, wallet_address
                """,
                (wallet,)
            )
            self.conn.commit()

            result = self.cursor.fetchone()
            if result:
                print(f"✓ Player banned")
                print(f"  Wallet: {result['wallet_address']}")
                print(f"  Reason: {reason}")

                # Log the ban
                self.cursor.execute(
                    """
                    INSERT INTO admin_actions (action_type, target_wallet, reason, created_at)
                    VALUES ('ban', %s, %s, NOW())
                    """,
                    (wallet, reason)
                )
                self.conn.commit()
            else:
                print(f"✗ Player not found: {wallet}")
        except Exception as e:
            self.conn.rollback()
            print(f"✗ Error banning player: {e}")

    def unban_player(self, wallet: str):
        """Unban a player"""
        try:
            self.cursor.execute(
                """
                UPDATE players
                SET is_banned = false
                WHERE wallet_address = %s
                RETURNING id, wallet_address
                """,
                (wallet,)
            )
            self.conn.commit()

            result = self.cursor.fetchone()
            if result:
                print(f"✓ Player unbanned: {result['wallet_address']}")
            else:
                print(f"✗ Player not found: {wallet}")
        except Exception as e:
            self.conn.rollback()
            print(f"✗ Error unbanning player: {e}")

    def show_stats(self):
        """Display system statistics"""
        try:
            # Total players
            self.cursor.execute("SELECT COUNT(*) as count FROM players")
            total_players = self.cursor.fetchone()['count']

            # Active players (last 24 hours)
            self.cursor.execute(
                """
                SELECT COUNT(*) as count FROM players
                WHERE last_active > NOW() - INTERVAL '24 hours'
                """
            )
            active_players = self.cursor.fetchone()['count']

            # Total pools
            self.cursor.execute("SELECT COUNT(*) as count FROM pools WHERE is_active = true")
            total_pools = self.cursor.fetchone()['count']

            # Total achievements
            self.cursor.execute("SELECT COUNT(*) as count FROM achievements")
            total_achievements = self.cursor.fetchone()['count']

            # Achievements unlocked
            self.cursor.execute("SELECT COUNT(*) as count FROM player_achievements")
            unlocked_achievements = self.cursor.fetchone()['count']

            # Database size
            self.cursor.execute(
                """
                SELECT pg_size_pretty(pg_database_size(current_database())) as size
                """
            )
            db_size = self.cursor.fetchone()['size']

            print("\n" + "="*50)
            print("M2P System Statistics")
            print("="*50)
            print(f"Total Players:         {total_players:,}")
            print(f"Active Players (24h):  {active_players:,}")
            print(f"Active Pools:          {total_pools:,}")
            print(f"Total Achievements:    {total_achievements:,}")
            print(f"Unlocked Achievements: {unlocked_achievements:,}")
            print(f"Database Size:         {db_size}")
            print("="*50 + "\n")

        except Exception as e:
            print(f"✗ Error fetching stats: {e}")

    def list_players(self, limit: int = 20, sort_by: str = 'ap'):
        """List top players"""
        try:
            order_map = {
                'ap': 'achievement_points DESC',
                'rewards': 'total_rewards DESC',
                'recent': 'last_active DESC',
            }

            order_clause = order_map.get(sort_by, 'achievement_points DESC')

            self.cursor.execute(
                f"""
                SELECT
                    id,
                    wallet_address,
                    username,
                    achievement_points,
                    total_rewards,
                    verification_level,
                    is_banned,
                    last_active
                FROM players
                ORDER BY {order_clause}
                LIMIT %s
                """,
                (limit,)
            )

            players = self.cursor.fetchall()

            print(f"\nTop {limit} Players (sorted by {sort_by})")
            print("=" * 100)
            print(f"{'ID':<6} {'Wallet':<44} {'Username':<20} {'AP':<8} {'Banned':<8}")
            print("-" * 100)

            for player in players:
                print(
                    f"{player['id']:<6} "
                    f"{player['wallet_address']:<44} "
                    f"{(player['username'] or 'N/A'):<20} "
                    f"{player['achievement_points']:<8} "
                    f"{'Yes' if player['is_banned'] else 'No':<8}"
                )

            print("=" * 100 + "\n")

        except Exception as e:
            print(f"✗ Error listing players: {e}")

    def check_achievements(self, wallet: str):
        """Check and unlock achievements for a player"""
        print(f"Checking achievements for {wallet}...")
        print("(This would trigger the achievement check system)")
        # In a real implementation, this would call the achievement service
        # For now, just show the player's current achievements

        try:
            self.cursor.execute(
                """
                SELECT p.id, p.wallet_address, p.achievement_points
                FROM players p
                WHERE p.wallet_address = %s
                """,
                (wallet,)
            )

            player = self.cursor.fetchone()
            if not player:
                print(f"✗ Player not found: {wallet}")
                return

            self.cursor.execute(
                """
                SELECT a.name, a.tier, a.ap_reward, pa.unlocked_at
                FROM player_achievements pa
                JOIN achievements a ON pa.achievement_id = a.id
                WHERE pa.player_id = %s
                ORDER BY pa.unlocked_at DESC
                LIMIT 10
                """,
                (player['id'],)
            )

            achievements = self.cursor.fetchall()

            print(f"\nPlayer: {player['wallet_address']}")
            print(f"Total AP: {player['achievement_points']}")
            print(f"\nRecent Achievements:")
            print("-" * 80)

            for ach in achievements:
                print(
                    f"[{ach['tier']}] {ach['name']:<30} "
                    f"({ach['ap_reward']} AP) - "
                    f"Unlocked: {ach['unlocked_at'].strftime('%Y-%m-%d')}"
                )

        except Exception as e:
            print(f"✗ Error checking achievements: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='M2P Admin CLI Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Verify a player
  python admin.py verify-player 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb --level 2

  # Award achievement points
  python admin.py award-ap 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb 100

  # Ban a player
  python admin.py ban-player 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb --reason "Cheating"

  # Show system statistics
  python admin.py stats

  # List top players
  python admin.py list-players --limit 50 --sort-by ap
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Verify player
    verify_parser = subparsers.add_parser('verify-player', help='Verify a player account')
    verify_parser.add_argument('wallet', help='Player wallet address')
    verify_parser.add_argument('--level', type=int, default=1, help='Verification level (default: 1)')

    # Reset verification
    reset_parser = subparsers.add_parser('reset-verification', help='Reset player verification')
    reset_parser.add_argument('wallet', help='Player wallet address')

    # Award AP
    ap_parser = subparsers.add_parser('award-ap', help='Award achievement points')
    ap_parser.add_argument('wallet', help='Player wallet address')
    ap_parser.add_argument('amount', type=int, help='Amount of AP to award')

    # Ban player
    ban_parser = subparsers.add_parser('ban-player', help='Ban a player')
    ban_parser.add_argument('wallet', help='Player wallet address')
    ban_parser.add_argument('--reason', default='Violation of terms', help='Ban reason')

    # Unban player
    unban_parser = subparsers.add_parser('unban-player', help='Unban a player')
    unban_parser.add_argument('wallet', help='Player wallet address')

    # Stats
    subparsers.add_parser('stats', help='Show system statistics')

    # List players
    list_parser = subparsers.add_parser('list-players', help='List top players')
    list_parser.add_argument('--limit', type=int, default=20, help='Number of players to show')
    list_parser.add_argument('--sort-by', choices=['ap', 'rewards', 'recent'], default='ap',
                           help='Sort criteria')

    # Check achievements
    check_parser = subparsers.add_parser('check-achievements', help='Check player achievements')
    check_parser.add_argument('wallet', help='Player wallet address')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    admin = M2PAdmin()

    # Execute command
    if args.command == 'verify-player':
        admin.verify_player(args.wallet, args.level)
    elif args.command == 'reset-verification':
        admin.reset_verification(args.wallet)
    elif args.command == 'award-ap':
        admin.award_ap(args.wallet, args.amount)
    elif args.command == 'ban-player':
        admin.ban_player(args.wallet, args.reason)
    elif args.command == 'unban-player':
        admin.unban_player(args.wallet)
    elif args.command == 'stats':
        admin.show_stats()
    elif args.command == 'list-players':
        admin.list_players(args.limit, args.sort_by)
    elif args.command == 'check-achievements':
        admin.check_achievements(args.wallet)


if __name__ == '__main__':
    main()
