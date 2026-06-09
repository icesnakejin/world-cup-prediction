# World Cup Prediction League MVP

## Overview

Build a World Cup Prediction League application where users use virtual coins to predict match outcomes and compete on leaderboards.

This is NOT a real-money betting platform.

## Tech Stack

### Backend
- FastAPI
- SQLAlchemy 2.0
- Alembic
- PostgreSQL
- Pydantic

### Frontend
- Next.js
- TypeScript
- TailwindCSS

## Core Entities

### User
- id
- username
- email
- balance

### Match
- id
- home_team
- away_team
- kickoff_time
- status
- home_score
- away_score

### Bet
- id
- user_id
- match_id
- selection
- stake
- odds
- payout
- status

### WalletTransaction
- id
- user_id
- amount
- transaction_type
- reference_id

## MVP Features

1. User registration/login
2. Initial 10,000 virtual coins
3. World Cup match schedule
4. Match winner predictions
5. Wallet ledger
6. Bet settlement engine
7. Betting history
8. Leaderboard

## API

### Auth
- POST /auth/register
- POST /auth/login
- GET /me

### Matches
- GET /matches
- GET /matches/{id}

### Bets
- POST /bets
- GET /bets/me

### Wallet
- GET /wallet
- GET /wallet/transactions

### Leaderboard
- GET /leaderboard

## Non-Goals

- Real money betting
- Deposits
- Withdrawals
- Payment processing
- Live betting
- Parlays
