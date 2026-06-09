import { Match } from "../api/types";

export function getHomeName(match: Match) {
  return match.home_team ?? match.home_placeholder ?? "TBD";
}

export function getAwayName(match: Match) {
  return match.away_team ?? match.away_placeholder ?? "TBD";
}

export function getMatchTitle(match: Match) {
  return `${getHomeName(match)} vs ${getAwayName(match)}`;
}

export function formatStage(stage: string | null) {
  const labels: Record<string, string> = {
    group: "Group Stage",
    round_of_32: "Round of 32",
    round_of_16: "Round of 16",
    quarter_final: "Quarter Final",
    semi_final: "Semi Final",
    third_place: "Third Place",
    final: "Final"
  };
  return stage ? labels[stage] ?? stage.replace(/_/g, " ") : "Matches";
}
