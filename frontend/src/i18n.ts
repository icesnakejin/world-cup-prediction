import { Match, Market } from "./api/types";

export type Locale = "en" | "zh";

export const LOCALE_STORAGE_KEY = "wcp_locale";

const messages = {
  en: {
    appName: "World Cup Prediction League",
    worldChampion: "World Champion",
    matches: "Matches",
    tournaments: "Tournaments",
    leaderboard: "Leaderboard",
    wallet: "Wallet",
    admin: "Admin",
    logout: "Logout",
    language: "Language",
    english: "EN",
    chinese: "中文",
    groupStage: "Group Stage",
    knockoutStage: "Knockout Stage",
    matchWinner: "Match Winner",
    overUnder: "Over/Under",
    exactScore: "Exact Score",
    teamWin: "Team Win",
    betSlip: "Bet Slip",
    betSlipEmpty: "Bet slip empty",
    selectMarket: "Select a market to place a prediction",
    selectTeamToPlaceTournamentWinnerBet: "Select a team to place a tournament winner bet.",
    stake: "Stake",
    odds: "Odds",
    potentialPayout: "Potential payout",
    placeBet: "Place Bet",
    placingBet: "Placing bet",
    loadingMatches: "Loading matches",
    couldNotLoadMatches: "Could not load matches.",
    noMatchesAvailable: "No matches available",
    groupStageMatchesAndMarkets: "Group stage matches.",
    knockoutStageMatchesAndMarkets: "Knockout stage matches.",
    loadingTournaments: "Loading tournaments",
    noTournamentsAvailable: "No tournaments available",
    tournamentWinnerFuturesUseVirtualCoinsOnly: "Tournament winner futures use virtual coins only.",
    loadingTournament: "Loading tournament",
    tournamentNotFound: "Tournament not found",
    tournamentWinner: "Tournament Winner",
    myTournamentBets: "My Tournament Bets",
    noTournamentBetsYet: "No tournament bets yet",
    tournamentBetSlip: "Tournament Bet Slip",
    loadingBets: "Loading bets",
    noBetsPlacedYet: "No bets placed yet",
    myBets: "My Bets",
    placed: "Placed",
    loadingWallet: "Loading wallet",
    virtualCoinBalance: "Virtual coin balance",
    loadingLeaderboard: "Loading leaderboard",
    noLeaderboardEntriesYet: "No leaderboard entries yet",
    rank: "Rank",
    user: "User",
    balance: "Balance",
    status: "Status",
    action: "Action",
    winner: "Winner",
    market: "Market",
    selection: "Selection",
    register: "Register",
    signIn: "Sign in",
    signingIn: "Signing in",
    signInShort: "Sign in",
    signInAccount: "Use your prediction league account",
    startWithVirtualCoins: "Start with 10,000 virtual coins",
    createAccount: "Create account",
    creatingAccount: "Creating account",
    alreadyRegistered: "Already registered?",
    noAccount: "No account?",
    email: "Email",
    username: "Username",
    password: "Password",
    invalidEmailOrPassword: "Invalid email or password.",
    registrationFailed: "Registration failed. Use a unique username and email.",
    uniqueUsernameAndEmail: "Use a unique username and email.",
    adminPortal: "Admin Portal",
    deploymentAndLocalTestingControls: "Deployment and local testing controls.",
    importSampleData: "Import Sample Data",
    resetToWorldCup2026: "Reset To World Cup 2026",
    seedTournamentMarkets: "Seed Tournament Markets",
    loadingAdminControls: "Loading admin controls",
    matchSettlement: "Match Settlement",
    tournamentSettlement: "Tournament Settlement",
    matchBets: "Match Bets",
    tournamentBets: "Tournament Bets",
    setResult: "Set Result",
    setWinner: "Set Winner",
    unsettle: "Unsettle",
    voidBets: "Void Bets",
    void: "Void",
    loadingWalletBalance: "Loading wallet balance",
    coins: "coins",
    worldCupMatches: "World Cup Matches",
    matchWinnerMarket: "胜平负",
    overUnderLine: "大小球",
    overUnderTooltip: "Over wins when total goals are above 2.5. Under wins when total goals are below 2.5.",
    exactScoreMarket: "比分竞猜",
    groupStageLabel: "Group Stage",
    knockoutStageLabel: "Knockout Stage"
  },
  zh: {
    appName: "世界杯预测联盟",
    worldChampion: "世界冠军",
    matches: "比赛",
    tournaments: "世界冠军",
    leaderboard: "排行榜",
    wallet: "钱包",
    admin: "管理",
    logout: "退出",
    language: "语言",
    english: "EN",
    chinese: "中文",
    groupStage: "小组赛",
    knockoutStage: "淘汰赛",
    matchWinner: "胜平负",
    overUnder: "大小球",
    exactScore: "比分竞猜",
    teamWin: "胜平负",
    betSlip: "下注单",
    betSlipEmpty: "下注单为空",
    selectMarket: "选择一个竞猜开始",
    selectTeamToPlaceTournamentWinnerBet: "选择一个球队进行冠军投注。",
    stake: "投注金额",
    odds: "赔率",
    potentialPayout: "预计返还",
    placeBet: "下注",
    placingBet: "提交中",
    loadingMatches: "加载比赛中",
    couldNotLoadMatches: "无法加载比赛。",
    noMatchesAvailable: "暂无比赛",
    groupStageMatchesAndMarkets: "小组赛比赛",
    knockoutStageMatchesAndMarkets: "淘汰赛比赛",
    loadingTournaments: "加载冠军市场中",
    noTournamentsAvailable: "暂无冠军市场",
    tournamentWinnerFuturesUseVirtualCoinsOnly: "冠军市场仅使用虚拟币。",
    loadingTournament: "加载冠军市场中",
    tournamentNotFound: "未找到冠军市场",
    tournamentWinner: "世界冠军",
    myTournamentBets: "我的冠军下注",
    noTournamentBetsYet: "暂无冠军下注",
    tournamentBetSlip: "冠军下注单",
    loadingBets: "加载下注记录中",
    noBetsPlacedYet: "暂无下注记录",
    myBets: "下注记录",
    placed: "下注时间",
    loadingWallet: "加载钱包中",
    virtualCoinBalance: "虚拟币余额",
    loadingLeaderboard: "加载排行榜中",
    noLeaderboardEntriesYet: "暂无排行榜数据",
    rank: "排名",
    user: "用户",
    balance: "余额",
    status: "状态",
    action: "操作",
    winner: "冠军",
    market: "盘口",
    selection: "选项",
    register: "注册",
    signIn: "登录",
    signingIn: "登录中",
    signInShort: "登录",
    signInAccount: "使用你的预测联盟账号",
    startWithVirtualCoins: "注册即送 10,000 虚拟币",
    createAccount: "创建账号",
    creatingAccount: "创建中",
    alreadyRegistered: "已经注册过？",
    noAccount: "还没有账号？",
    email: "邮箱",
    username: "用户名",
    password: "密码",
    invalidEmailOrPassword: "邮箱或密码错误。",
    registrationFailed: "注册失败，请使用唯一的用户名和邮箱。",
    uniqueUsernameAndEmail: "请使用唯一的用户名和邮箱。",
    adminPortal: "管理后台",
    deploymentAndLocalTestingControls: "部署与本地测试控制。",
    importSampleData: "导入示例数据",
    resetToWorldCup2026: "重置为 2026 世界杯",
    seedTournamentMarkets: "生成冠军市场",
    loadingAdminControls: "加载管理控制中",
    matchSettlement: "比赛结算",
    tournamentSettlement: "冠军结算",
    matchBets: "比赛下注",
    tournamentBets: "冠军下注",
    setResult: "设置结果",
    setWinner: "设置冠军",
    unsettle: "撤销结算",
    voidBets: "作废下注",
    void: "作废",
    loadingWalletBalance: "加载钱包余额中",
    coins: "币",
    worldCupMatches: "世界杯比赛",
    matchWinnerMarket: "胜平负",
    overUnderLine: "大小球",
    overUnderTooltip: "大球：总进球大于 2.5 时中奖。小球：总进球小于 2.5 时中奖。",
    exactScoreMarket: "比分竞猜",
    groupStageLabel: "小组赛",
    knockoutStageLabel: "淘汰赛"
  }
} as const;

export type TranslationKey = keyof typeof messages.en;

export function createTranslator(locale: Locale) {
  return (key: TranslationKey) => messages[locale][key] ?? messages.en[key] ?? key;
}

export function formatDateTime(value: string, locale: Locale) {
  return new Date(value).toLocaleString(locale === "zh" ? "zh-CN" : "en-US");
}

export function formatDate(value: string, locale: Locale) {
  return new Date(value).toLocaleDateString(locale === "zh" ? "zh-CN" : "en-US");
}

export function getMatchTeamName(match: Match, side: "home" | "away", locale: Locale) {
  const fallback = locale === "zh" ? "待定" : "TBD";
  if (side === "home") {
    return match.home_team ?? match.home_placeholder ?? fallback;
  }
  return match.away_team ?? match.away_placeholder ?? fallback;
}

export function getMatchTitle(match: Match, locale: Locale) {
  return `${getMatchTeamName(match, "home", locale)} vs ${getMatchTeamName(match, "away", locale)}`;
}

export function getStageLabel(stage: string | null, locale: Locale) {
  const labels: Record<string, string> = {
    group: locale === "zh" ? "小组赛" : "Group Stage",
    round_of_32: locale === "zh" ? "1/16 决赛" : "Round of 32",
    round_of_16: locale === "zh" ? "1/8 决赛" : "Round of 16",
    quarter_final: locale === "zh" ? "1/4 决赛" : "Quarter Final",
    semi_final: locale === "zh" ? "半决赛" : "Semi Final",
    third_place: locale === "zh" ? "三四名决赛" : "Third Place",
    final: locale === "zh" ? "决赛" : "Final"
  };
  return stage ? labels[stage] ?? stage.replace(/_/g, " ") : locale === "zh" ? "比赛" : "Matches";
}

export function getMarketSelectionLabel(market: Market, locale: Locale) {
  const labels: Record<string, string> = {
    HOME: locale === "zh" ? "主胜" : "Home",
    HOME_WIN: locale === "zh" ? "主胜" : "Home",
    DRAW: locale === "zh" ? "平局" : "Draw",
    AWAY: locale === "zh" ? "客胜" : "Away",
    AWAY_WIN: locale === "zh" ? "客胜" : "Away",
    OVER: locale === "zh" ? "大球" : "Over",
    UNDER: locale === "zh" ? "小球" : "Under"
  };
  return labels[market.selection] ?? market.selection;
}

export function getSelectionLabel(selection: string, locale: Locale) {
  return getMarketSelectionLabel({ selection } as Market, locale);
}

export function getMarketGroupTitle(market: Market, locale: Locale) {
  if (market.market_type === "match_winner") {
    return locale === "zh" ? "胜平负" : "Team Win";
  }
  if (market.market_type === "over_under") {
    return market.line ? `${locale === "zh" ? "大小球" : "Over/Under"} ${Number(market.line).toFixed(1)}` : locale === "zh" ? "大小球" : "Over/Under";
  }
  if (market.market_type === "exact_score") {
    return locale === "zh" ? "比分竞猜" : "Exact Score";
  }
  return market.market_type;
}

export function getMatchStatusLabel(status: string, locale: Locale) {
  const normalized = status.toLowerCase();
  const labels: Record<string, string> = {
    scheduled: locale === "zh" ? "未开始" : "Scheduled",
    open: locale === "zh" ? "开放中" : "Open",
    completed: locale === "zh" ? "已完成" : "Completed",
    settled: locale === "zh" ? "已结算" : "Settled",
    pending: locale === "zh" ? "待结算" : "Pending",
    won: locale === "zh" ? "已中奖" : "Won",
    lost: locale === "zh" ? "未中奖" : "Lost",
    void: locale === "zh" ? "已作废" : "Void",
    completed_tournament: locale === "zh" ? "已完成" : "Completed"
  };
  return labels[normalized] ?? status;
}

export function getTournamentStatusLabel(status: string, locale: Locale) {
  return getMatchStatusLabel(status, locale);
}
