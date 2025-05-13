export const getDisplayName = (repoFullName: string | undefined): string => {
  if (!repoFullName) return "Fighter"; // Default if name is undefined
  if (repoFullName.toLowerCase().includes("bitcoinknots")) return "Knots";
  if (repoFullName.toLowerCase().includes("bitcoin/bitcoin")) return "Core";
  // Fallback to a shortened version if it's a full owner/repo
  const parts = repoFullName.split("/");
  if (parts.length === 2) return parts[1];
  return repoFullName;
};

export const getRepoUrl = (repoFullName: string | undefined): string => {
  if (!repoFullName) return "#"; // Default to a safe link
  return `https://github.com/${repoFullName}`;
};
