import { Match } from "../api/types";
import {
  formatDateTime,
  getMatchTeamName,
  getMatchTitle as getLocalizedMatchTitle,
  getStageLabel,
  Locale
} from "../i18n";

export function getHomeName(match: Match, locale: Locale) {
  return getMatchTeamName(match, "home", locale);
}

export function getAwayName(match: Match, locale: Locale) {
  return getMatchTeamName(match, "away", locale);
}

export function getMatchTitle(match: Match, locale: Locale) {
  return getLocalizedMatchTitle(match, locale);
}

export function formatStage(stage: string | null, locale: Locale) {
  return getStageLabel(stage, locale);
}

export function formatMatchDate(value: string, locale: Locale) {
  return formatDateTime(value, locale);
}

