/**
 * Leaderboard types and interfaces
 */

export type LeaderboardPeriod = 'all_time' | 'this_week' | 'today' | 'efficiency';

export interface LeaderboardEntry {
  rank: number;
  previous_rank: number | null;
  rank_change: string;
  user_id: number;
  wallet_address: string;
  wallet_truncated: string;
  display_name: string | null;
  is_verified: boolean;
  total_mined_advc: number;
  total_ap: number;
  period_score: number;
  last_mining_event: string | null;
}

export interface LeaderboardResponse {
  period: string;
  total_entries: number;
  limit: number;
  offset: number;
  entries: LeaderboardEntry[];
}

export interface PlayerRankResponse {
  player_rank: number;
  previous_rank: number | null;
  rank_change: string;
  period_score: number;
  nearby_rankings: LeaderboardEntry[];
}

export interface RankChangeEvent {
  event: 'rank_changed';
  data: {
    wallet_address: string;
    period: string;
    old_rank: number;
    new_rank: number;
    rank_change: number;
    direction: 'up' | 'down' | 'same';
    period_score: number;
    timestamp: string;
  };
}

export interface LeaderboardUpdateEvent {
  event: 'leaderboard_updated';
  data: {
    period: string;
    timestamp: string;
  };
}

export type WebSocketMessage = RankChangeEvent | LeaderboardUpdateEvent;
