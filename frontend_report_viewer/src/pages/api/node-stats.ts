import type { NextApiRequest, NextApiResponse } from "next";

interface UANodeInfo {
  listening: number;
  est_unreachable: number;
  services?: Record<string, number>; // Optional, not used in current aggregation
  poli?: Record<string, number>; // Optional
}

interface UAInfoJson {
  [userAgent: string]: UANodeInfo;
}

export interface ProcessedNodeStats {
  core: {
    count: number;
    versions: Record<string, number>;
  };
  knots: {
    count: number;
    versions: Record<string, number>;
  };
  btcsuite: {
    // Example for btcsuite nodes from the provided HTML
    count: number;
    versions: Record<string, number>;
  };
  other: {
    count: number;
    uas: Record<string, number>; // Store UAs and their counts for transparency
  };
  totalReachable: number;
  coreShare: number;
  knotsShare: number;
  btcsuiteShare: number;
  otherShare: number;
  last_updated?: string;
}

// Simple cache to avoid hitting the external URL too often during dev/build
let cache: ProcessedNodeStats | null = null;
let lastCacheTime: number = 0;
const CACHE_DURATION_MS = 10 * 60 * 1000; // 10 minutes

const simpleUasMapping: Record<string, string> = {
  bcoin: "bcoin",
  "bitcoin xt": "Bitcoin XT",
  bitcore: "bitcore",
  bither: "Bither",
  bitsquare: "Bitsquare",
  bread: "bread",
  hodlwallet: "hodlwallet",
  libbitcoin: "libbitcoin",
  multibit: "MultiBit",
  nbitcoin: "NBitcoin",
  "therealbitcoin.org": "therealbitcoin.org",
  "satoshi rbf": "Satoshi RBF",
};

const keywordUasMapping: Record<string, string> = {
  "bitcoin-qt": "Bitcoin Core",
  satoshi: "Bitcoin Core", // General catch-all for Satoshi, ensure it's checked after Knots
  bitcoinunlimited: "Bitcoin Unlimited",
  breadwallet: "bread",
  btcd: "btcsuite",
  btcwire: "btcsuite",
  knots: "Bitcoin Knots",
  next: "Bitcoin Knots", // Luke's mapping
  "next-test": "Bitcoin Knots", // Luke's mapping
  ljr: "Bitcoin Knots", // Luke's mapping
  eligius: "Bitcoin Knots", // Luke's mapping
  multibithd: "MultiBit HD",
  "nbitcoin-bitcoin": "NBitcoin",
  therealbitcoin: "therealbitcoin.org",
};

function categorizeUserAgent(ua: string): string {
  const uaLower = ua.toLowerCase();

  // Priority for Knots due to generic "Satoshi" in its UA string
  if (
    uaLower.includes("/knots:") ||
    uaLower.includes("/next:") ||
    uaLower.includes("/next-test:") ||
    uaLower.includes("/ljr:") ||
    uaLower.includes("/eligius:")
  ) {
    return "Bitcoin Knots";
  }

  // Check for specific mappable keywords
  for (const keyword in keywordUasMapping) {
    if (uaLower.includes(keyword)) {
      return keywordUasMapping[keyword];
    }
  }

  // Check for simple direct matches (often a single segment of UA)
  const uaSegments = uaLower.split("/");
  for (const segment of uaSegments) {
    const segmentKey = segment.split(":")[0]; // Get part before version if any
    if (simpleUasMapping[segmentKey]) {
      return simpleUasMapping[segmentKey];
    }
  }

  // Specific cases from Luke's JS
  if (uaLower.includes("bitcoinj") && uaLower.includes("bitcoin wallet")) {
    return "Bitcoin Wallet for Android";
  }
  if (ua.match(/^Bither1\.[\d\.]+$/i)) {
    return "Bither";
  }
  if (uaLower.includes("classic") && !uaLower.includes("bitcoinj")) {
    return "Bitcoin Classic";
  }

  return "other";
}

function extractVersion(ua: string, category: string): string {
  if (category === "Bitcoin Knots") {
    const match =
      ua.match(/Knots:(\d+)/i) ||
      ua.match(/next:([\w\d.-]+)/i) ||
      ua.match(/next-test:([\w\d.-]+)/i) ||
      ua.match(/ljr:([\w\d.-]+)/i) ||
      ua.match(/eligius:([\w\d.-]+)/i);
    return match ? match[1] : "unknown";
  } else if (category === "Bitcoin Core") {
    const match =
      ua.match(/Satoshi:([\d\.]+)/i) || ua.match(/bitcoin-qt:([\d\.]+)/i);
    return match ? match[1] : "unknown";
  } else if (category === "btcsuite") {
    const match = ua.match(/btcd:([\d\.]+)/i) || ua.match(/btcwire:([\d\.]+)/i);
    return match ? match[1] : "unknown";
  }
  // Basic version extraction for others if needed, could be more sophisticated
  const segments = ua.split("/");
  for (const segment of segments) {
    const parts = segment.split(":");
    if (
      parts.length > 1 &&
      parts[0].toLowerCase().includes(category.split(" ")[0].toLowerCase())
    ) {
      return parts[1];
    }
  }
  const versionMatch = ua.match(/[\/:\s]([\d\.]+[^\s\/]*)/); // Generic attempt
  return versionMatch ? versionMatch[1] : "unknown";
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<ProcessedNodeStats | { error: string }>
) {
  const now = Date.now();
  // Default to including unreachables, matching Luke's default behavior
  const inclUnreachable = req.query.onlylistening !== "true";
  // Default to skipping groups with no listeners, matching Luke's default
  const skipGroupsWithNoListeners = req.query.keep_all_groups !== "true";

  const cacheKey = `nodeStats_inclUnreachable:${inclUnreachable}_skipNoListeners:${skipGroupsWithNoListeners}`;
  // This simplistic cache won't work well with multiple cache keys. Should be a Map.
  // For now, effectively, only one version of params is cached.
  if (
    cache &&
    now - lastCacheTime < CACHE_DURATION_MS &&
    req.query.refresh !== "true"
  ) {
    // Added refresh param
    console.log("Serving node stats from cache");
    return res.status(200).json(cache);
  }
  console.log(
    `Fetching fresh node stats (inclUnreachable: ${inclUnreachable}, skipGroupsWithNoListeners: ${skipGroupsWithNoListeners})`
  );

  try {
    const response = await fetch(
      "https://luke.dashjr.org/programs/bitcoin/files/charts/data/uainfo.json"
    );
    if (!response.ok) {
      throw new Error(
        `Failed to fetch node info: ${response.status} ${response.statusText}`
      );
    }
    const rawData: UAInfoJson = await response.json();

    const initialCounts: Record<string, number> = {};
    const versions: Record<string, Record<string, number>> = {};
    const categoryHasListener: Record<string, boolean> = {}; // To track if any UA in a category was listening
    // let totalNodesPreFilter = 0; // All nodes initially summed up

    for (const uaString in rawData) {
      const nodeInfo = rawData[uaString];
      let n = nodeInfo.listening;
      if (inclUnreachable) {
        n += nodeInfo.est_unreachable;
      }

      if (n === 0) continue; // If total (listening + maybe unreachable) is 0, skip.

      const category = categorizeUserAgent(uaString);

      initialCounts[category] = (initialCounts[category] || 0) + n;
      // totalNodesPreFilter += n;

      if (nodeInfo.listening > 0) {
        categoryHasListener[category] = true;
      }

      if (!versions[category]) {
        versions[category] = {};
      }
      const version = extractVersion(uaString, category);
      versions[category][version] = (versions[category][version] || 0) + n;
    }

    let finalCounts = { ...initialCounts };
    let totalNodesForPercentage = 0;

    if (skipGroupsWithNoListeners) {
      const categoriesToKeep: Record<string, number> = {};
      for (const category in finalCounts) {
        if (categoryHasListener[category] || category === "other") {
          // Always keep 'other' initially
          categoriesToKeep[category] = finalCounts[category];
          totalNodesForPercentage += finalCounts[category];
        } else {
          console.log(
            `Excluding category ${category} (count: ${finalCounts[category]}) due to no listening nodes.`
          );
          // Effectively remove this category from percentage calculation by not adding to totalNodesForPercentage
          // and not including in final counts passed to shares if we were to rebuild finalCounts here.
        }
      }
      // If we were to strictly rebuild finalCounts for share calculation:
      finalCounts = categoriesToKeep;
    } else {
      for (const category in finalCounts) {
        totalNodesForPercentage += finalCounts[category];
      }
    }

    // Merging small groups into "other" - Luke's logic: min_nodes = Math.ceil(tot / 0x200);
    // This should happen *after* the skipGroupsWithNoListeners filter, using totalNodesForPercentage
    const minNodesThreshold = Math.ceil(totalNodesForPercentage / 512); // 0x200 = 512
    let finalOtherAggregatedCount = finalCounts["other"] || 0;
    const categoriesForFinalStats: Record<string, number> = {};

    for (const category in finalCounts) {
      if (category === "other") continue; // Handle 'other' separately
      if (
        finalCounts[category] < minNodesThreshold &&
        category !== "Bitcoin Core" &&
        category !== "Bitcoin Knots"
      ) {
        console.log(
          `Merging small category ${category} (count: ${finalCounts[category]}) into other.`
        );
        finalOtherAggregatedCount += finalCounts[category];
        // Also merge versions if you want detailed 'other' versions
        if (versions[category]) {
          versions["other"] = {
            ...(versions["other"] || {}),
            ...versions[category],
          };
          delete versions[category]; // remove from main versions list
        }
      } else {
        categoriesForFinalStats[category] = finalCounts[category];
      }
    }
    categoriesForFinalStats["other"] = finalOtherAggregatedCount;
    if (
      finalCounts["other"] &&
      finalCounts["other"] < minNodesThreshold &&
      Object.keys(categoriesForFinalStats).length > 1
    ) {
      // if original 'other' was too small and got emptied, ensure it doesn't get double counted if merged into itself
      // This logic might need refinement based on how 'other' is initially populated vs merged into.
    }

    const coreCount = categoriesForFinalStats["Bitcoin Core"] || 0;
    const knotsCount = categoriesForFinalStats["Bitcoin Knots"] || 0;
    const btcsuiteCount = categoriesForFinalStats["btcsuite"] || 0; // Example specific client
    const otherCount = categoriesForFinalStats["other"] || 0;

    const processedStats: ProcessedNodeStats = {
      core: { count: coreCount, versions: versions["Bitcoin Core"] || {} },
      knots: { count: knotsCount, versions: versions["Bitcoin Knots"] || {} },
      btcsuite: { count: btcsuiteCount, versions: versions["btcsuite"] || {} },
      other: { count: otherCount, uas: {} }, // UAS part is not fully aligned with merged 'other' logic yet
      totalReachable: totalNodesForPercentage, // This total is after potential exclusions
      coreShare:
        totalNodesForPercentage > 0
          ? (coreCount / totalNodesForPercentage) * 100
          : 0,
      knotsShare:
        totalNodesForPercentage > 0
          ? (knotsCount / totalNodesForPercentage) * 100
          : 0,
      btcsuiteShare:
        totalNodesForPercentage > 0
          ? (btcsuiteCount / totalNodesForPercentage) * 100
          : 0,
      otherShare:
        totalNodesForPercentage > 0
          ? (otherCount / totalNodesForPercentage) * 100
          : 0,
      last_updated: new Date().toISOString(),
    };

    cache = processedStats;
    lastCacheTime = now;

    res.status(200).json(processedStats);
  } catch (error: any) {
    console.error("Error in /api/node-stats:", error);
    res.status(500).json({
      error: error.message || "Failed to fetch or process node statistics",
    });
  }
}
