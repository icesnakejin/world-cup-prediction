const configuredAdminEmails = import.meta.env.VITE_ADMIN_EMAILS ?? "ian@test.com";

export const ADMIN_EMAILS = new Set(
  configuredAdminEmails
    .split(",")
    .map((email: string) => email.trim().toLowerCase())
    .filter(Boolean)
);

export function isAdminEmail(email: string | null | undefined) {
  return Boolean(email && ADMIN_EMAILS.has(email.toLowerCase()));
}
