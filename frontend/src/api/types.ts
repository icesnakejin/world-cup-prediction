export type User = {
  id: number;
  username: string;
  email: string;
};

export type Match = {
  id: number;
  home_team: string;
  away_team: string;
  kickoff_time: string;
  status: string;
  home_score: number | null;
  away_score: number | null;
};

export type Market = {
  id: number;
  market_type: string;
  selection: "HOME_WIN" | "DRAW" | "AWAY_WIN" | string;
  line: string | null;
  odds: string;
  status: string;
};

export type Wallet = {
  balance: number;
};

export type Bet = {
  bet_id: number;
  market_id: number;
  match_id: number;
  match: {
    home_team: string;
    away_team: string;
    kickoff_time: string;
  };
  selection: string;
  odds: string;
  stake: number;
  payout: number | null;
  status: string;
  created_at: string;
};

export type LeaderboardEntry = {
  rank: number;
  user_id: number;
  username: string;
  balance: number;
};

export type Tournament = {
  id: number;
  name: string;
  year: number;
  status: string;
  winner_team: string | null;
};

export type TournamentMarket = {
  id: number;
  tournament_id: number;
  market_type: string;
  selection: string;
  odds: string;
  status: string;
};

export type TournamentBet = {
  id: number;
  tournament_market_id: number;
  tournament_id: number;
  tournament_name: string;
  selection: string;
  odds: string;
  stake: number;
  payout: number | null;
  status: string;
  created_at: string;
};

export type AdminMatchBet = {
  id: number;
  user_id: number;
  username: string;
  match_id: number;
  home_team: string;
  away_team: string;
  kickoff_time: string;
  market_id: number;
  market_type: string;
  selection: string;
  odds: string;
  stake: number;
  payout: number | null;
  status: string;
  created_at: string;
};

export type AdminTournamentBet = {
  id: number;
  user_id: number;
  username: string;
  tournament_id: number;
  tournament_name: string;
  tournament_market_id: number;
  market_type: string;
  selection: string;
  odds: string;
  stake: number;
  payout: number | null;
  status: string;
  created_at: string;
};

export type TokenResponse = {
  access_token: string;
  token_type: string;
};
