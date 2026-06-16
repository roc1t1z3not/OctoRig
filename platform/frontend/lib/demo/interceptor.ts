// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import type { AxiosInstance, AxiosResponse, InternalAxiosRequestConfig } from "axios";
import { isDemoMode } from "@/stores/demo.store";
import {
  DEMO_ME,
  DEMO_PROFILE_ME,
  DEMO_MY_RANK,
  DEMO_SCOREBOARD,
  DEMO_EVENTS,
  DEMO_EVENT_CHALLENGES_SLUGS,
  DEMO_EVENT_SCOREBOARD,
  DEMO_NOTIFICATIONS,
  DEMO_DEPLOYMENTS,
  DEMO_TEAMS,
  DEMO_TEAM_DETAIL,
  DEMO_TEAM_MEMBERS,
  DEMO_API_KEYS,
  DEMO_HEALTH,
  DEMO_CONTAINERS,
  DEMO_ADMIN_STATS,
  DEMO_ADMIN_USERS,
  DEMO_ADMIN_TEAMS,
  DEMO_ADMIN_API_KEYS,
  DEMO_ADMIN_SETTINGS,
  DEMO_AUDIT_LOGS,
  augmentChallengeList,
  augmentChallengeDetail,
  augmentBadgeList,
  demoUserProfile,
  demoUserRank,
} from "./data";

// ─── URL helpers ──────────────────────────────────────────────────────────────

function url(config: InternalAxiosRequestConfig): string {
  return config.url ?? "";
}

function method(config: InternalAxiosRequestConfig): string {
  return (config.method ?? "get").toLowerCase();
}

// ─── Mock adapter factory ─────────────────────────────────────────────────────

function mockResponse(
  data: unknown,
  config: InternalAxiosRequestConfig,
  status = 200
): Promise<AxiosResponse> {
  return Promise.resolve({
    data,
    status,
    statusText: "OK",
    headers: { "content-type": "application/json" },
    config,
    request: {},
  } as AxiosResponse);
}

function withMock(data: unknown, config: InternalAxiosRequestConfig, status = 200) {
  config.adapter = () => mockResponse(data, config, status);
}

// ─── Route matching helpers ───────────────────────────────────────────────────

const SEG = "[^/]+";

const RE = {
  challengeList:    /^\/challenges\/?(\?.*)?$/,
  challengeAdminAll:/^\/challenges\/admin\/all/,
  challengeDetail:  /^\/challenges\/([^/?]+)$/,
  badgeAll:         /^\/badges\/?(\?.*)?$/,
  badgesMe:         /^\/badges\/me$/,
  badgesUser:       /^\/badges\/users\/\d+/,
  eventList:        /^\/events\/?(\?.*)?$/,
  eventSlug:        /^\/events\/([^/?]+)$/,
  eventChallenges:  new RegExp(`^/events/${SEG}/challenges`),
  eventScoreboard:  new RegExp(`^/events/${SEG}/scoreboard`),
  teamList:         /^\/teams\/?(\?.*)?$/,
  teamDetail:       /^\/teams\/(\d+)$/,
  teamMembers:      /^\/teams\/\d+\/members/,
  profileMe:        /^\/profiles\/me$/,
  profileUser:      /^\/profiles\/([^/?]+)$/,
  adminUsers:       /^\/admin\/users\//,
  adminTeams:       /^\/admin\/teams\//,
  adminDeployments: /^\/admin\/deployments\//,
  adminAuditLogs:   /^\/admin\/audit-logs\//,
  adminApiKeys:     /^\/admin\/api-keys\//,
  adminRanks:       /^\/admin\/ranks\//,
  rankUser:         /^\/ranks\/users\/\d+/,
};

// ─── Request interceptor — fully-replaced endpoints ───────────────────────────

function onRequest(config: InternalAxiosRequestConfig): InternalAxiosRequestConfig {
  if (!isDemoMode()) return config;

  const u = url(config);
  const m = method(config);

  if (m !== "get") {
    // Let mutations pass through but return success shapes for key POST endpoints
    if (/\/notifications\/\d+\/read$/.test(u) || /\/notifications\/read-all/.test(u))
      config.adapter = () => mockResponse({ count: 0, marked: 0 }, config);
    if (/\/badges\/evaluate/.test(u))
      config.adapter = () => mockResponse([], config);
    if (/\/challenges\/[^/]+\/submit$/.test(u))
      config.adapter = () => mockResponse({ correct: false, already_solved: false, first_blood: false, points_awarded: 0, message: "Demo mode — flag submission disabled." }, config);
    return config;
  }

  // Auth
  if (u === "/auth/me") { withMock(DEMO_ME, config); return config; }

  // Scoreboards
  if (/^\/scoreboards\/global/.test(u)) { withMock(DEMO_SCOREBOARD, config); return config; }
  if (RE.eventScoreboard.test(u)) { withMock(DEMO_EVENT_SCOREBOARD, config); return config; }
  if (/^\/scoreboards\/events\/\d+/.test(u)) { withMock(DEMO_EVENT_SCOREBOARD, config); return config; }

  // Events — full replacement
  if (RE.eventChallenges.test(u)) {
    // Return a minimal EventChallenge[] with the first 5 slugs as placeholder.
    // The real challenge list will be fetched separately; here we just need valid shapes.
    withMock(DEMO_EVENT_CHALLENGES_SLUGS.map((slug, i) => ({
      id: 100 + i, slug, title: slug.replace(/-/g, " ").replace(/\b\w/g, c => c.toUpperCase()),
      category: ["sql-injection","xss","idor","web","recon"][i % 5],
      difficulty: ["easy","medium","hard","medium","easy"][i % 5],
      points: [100,200,300,200,100][i % 5],
      tags: [], solve_count: 10 + i * 8, solved_by_me: i % 2 === 0, released_at: null,
    })), config);
    return config;
  }
  if (RE.eventList.test(u)) { withMock(DEMO_EVENTS, config); return config; }
  if (RE.eventSlug.test(u)) {
    const slug = RE.eventSlug.exec(u)?.[1] ?? "";
    const ev = DEMO_EVENTS.find((e) => e.slug === slug) ?? DEMO_EVENTS[0];
    withMock(ev, config);
    return config;
  }

  // Ranks — me and by-user-id are replaced; /ranks/ list passes through
  if (/^\/ranks\/me$/.test(u)) { withMock(DEMO_MY_RANK, config); return config; }
  if (RE.rankUser.test(u)) {
    const id = parseInt(u.split("/").pop() ?? "0");
    withMock(demoUserRank(id), config);
    return config;
  }

  // Deployments
  if (/^\/deployments\/instance/.test(u)) { withMock(null, config, 404); return config; }
  if (/^\/deployments\/?(\?.*)?$/.test(u)) { withMock(DEMO_DEPLOYMENTS, config); return config; }
  if (/^\/deployments\/\d+$/.test(u)) { withMock(DEMO_DEPLOYMENTS[0], config); return config; }

  // Notifications
  if (/^\/notifications\/unread-count/.test(u)) {
    withMock({ count: DEMO_NOTIFICATIONS.filter(n => !n.read_at).length }, config);
    return config;
  }
  if (/^\/notifications\/?(\?.*)?$/.test(u)) { withMock(DEMO_NOTIFICATIONS, config); return config; }
  if (/^\/notifications\/preferences/.test(u)) {
    withMock({ in_app: true, email: false, discord_webhook_url: null, slack_webhook_url: null, event_filter: {} }, config);
    return config;
  }

  // Profiles
  if (RE.profileMe.test(u)) { withMock(DEMO_PROFILE_ME, config); return config; }
  if (RE.profileUser.test(u)) {
    const username = RE.profileUser.exec(u)?.[1] ?? "user";
    if (username === "search") { withMock([], config); return config; } // /profiles/search
    withMock(demoUserProfile(username), config);
    return config;
  }
  if (/^\/profiles\/search/.test(u)) { withMock([], config); return config; }

  // Teams
  if (RE.teamMembers.test(u)) { withMock(DEMO_TEAM_MEMBERS, config); return config; }
  if (RE.teamDetail.test(u)) { withMock(DEMO_TEAM_DETAIL, config); return config; }
  if (RE.teamList.test(u)) { withMock(DEMO_TEAMS, config); return config; }

  // API Keys
  if (/^\/api-keys\/?(\?.*)?$/.test(u)) { withMock(DEMO_API_KEYS, config); return config; }

  // System
  if (/^\/system\/health/.test(u)) { withMock(DEMO_HEALTH, config); return config; }
  if (/^\/system\/containers/.test(u)) { withMock(DEMO_CONTAINERS, config); return config; }
  if (/^\/system\/plugins/.test(u)) { withMock([], config); return config; }

  // Schedule
  if (/^\/schedule\//.test(u) || /^\/schedule\/?(\?.*)?$/.test(u)) { withMock([], config); return config; }

  // Admin
  if (/^\/admin\/stats/.test(u)) { withMock(DEMO_ADMIN_STATS, config); return config; }
  if (RE.adminUsers.test(u)) { withMock(DEMO_ADMIN_USERS, config); return config; }
  if (RE.adminTeams.test(u)) { withMock(DEMO_ADMIN_TEAMS, config); return config; }
  if (RE.adminDeployments.test(u)) { withMock(DEMO_DEPLOYMENTS, config); return config; }
  if (RE.adminAuditLogs.test(u)) { withMock(DEMO_AUDIT_LOGS, config); return config; }
  if (RE.adminApiKeys.test(u)) { withMock(DEMO_ADMIN_API_KEYS, config); return config; }
  if (/^\/admin\/settings/.test(u)) { withMock(DEMO_ADMIN_SETTINGS, config); return config; }
  if (RE.adminRanks.test(u)) { withMock(null, config); return config; } // pass to ranks list

  return config;
}

// ─── Response interceptor — augment real responses ────────────────────────────

function onResponse(response: AxiosResponse): AxiosResponse {
  if (!isDemoMode()) return response;
  const u = url(response.config);

  // Challenge list — overlay solve_count + solved_by_me
  if (RE.challengeList.test(u) || RE.challengeAdminAll.test(u)) {
    if (Array.isArray(response.data)) {
      response.data = augmentChallengeList(response.data);
    }
    return response;
  }

  // Challenge detail — overlay solve_count + solved_by_me + first_blood_user
  if (RE.challengeDetail.test(u) && !RE.challengeAdminAll.test(u)) {
    if (response.data && typeof response.data === "object" && "id" in response.data) {
      response.data = augmentChallengeDetail(response.data as Parameters<typeof augmentChallengeDetail>[0]);
    }
    return response;
  }

  // Badge list — mark ~half as earned
  if (RE.badgeAll.test(u)) {
    if (Array.isArray(response.data)) {
      response.data = augmentBadgeList(response.data);
    }
    return response;
  }

  // My badges — same augmentation but filter to earned only
  if (RE.badgesMe.test(u) || RE.badgesUser.test(u)) {
    if (Array.isArray(response.data)) {
      response.data = augmentBadgeList(response.data).filter((b: { earned: boolean }) => b.earned);
    }
    return response;
  }

  return response;
}

// ─── Install ──────────────────────────────────────────────────────────────────

export function installDemoInterceptor(client: AxiosInstance): void {
  client.interceptors.request.use(onRequest);
  client.interceptors.response.use(onResponse);
}
