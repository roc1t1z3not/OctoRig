// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
// Demo mode fixture data — static records only (users, teams, deployments, admin
// records). Catalog data that lives in the real backend (labs, challenges,
// badges, ranks) is intentionally left to pass through to the live API in
// interceptor.ts and is only lightly augmented here — see augment* below —
// so it can never drift out of sync with app/labs/registry, app/badge_catalog,
// and app/services/rank_service.py.
// Dates are relative to 2026-06-16 (today when this was written).

// ─── Auth ─────────────────────────────────────────────────────────────────────
// Real platform role slugs (app/services/role_service.py ROLE_SEED): admin, creator, player, viewer.

export const DEMO_ME = {
  id: 1,
  username: "octorig_admin",
  email: "admin@octorig.io",
  platform_roles: ["admin", "creator"],
  permissions: [
    "platform.dashboard", "platform.challenges", "platform.events", "platform.scoreboard",
    "platform.badges", "platform.labs", "platform.deployments", "platform.teams",
    "admin.panel", "admin.users.view", "admin.users.manage", "admin.teams.view",
    "admin.deployments.view", "admin.deployments.manage", "admin.audit.view",
    "admin.challenges.manage", "admin.events.manage", "admin.api_keys.view",
    "admin.ranks.manage", "admin.assessments.manage", "admin.content.manage",
    "admin.settings.manage", "creator.access",
  ],
};

// ─── Profile ──────────────────────────────────────────────────────────────────
// Badge slugs/names/icons below are real entries from app/badge_catalog/*.
// Challenge slugs/titles/points are real entries from app/labs/registry/world.py.

export const DEMO_PROFILE_ME = {
  user_id: 1,
  username: "octorig_admin",
  bio: "Offensive security researcher and CTF enthusiast. Building tools to help people learn security hands-on.",
  avatar_url: null,
  website_url: "https://commonhuman.io",
  location: "Tranquility, Moon",
  github_handle: "commonhuman-lab",
  privacy_level: "public",
  show_activity: true,
  total_points: 4250,
  solve_count: 27,
  first_bloods: 5,
  team_count: 2,
  badges: [
    { slug: "first-steps",       name: "First Steps",     icon: "flag",     awarded_at: "2026-01-10T09:00:00Z" },
    { slug: "five-solves",       name: "Getting Started",  icon: "star",     awarded_at: "2026-01-18T11:30:00Z" },
    { slug: "ten-solves",        name: "Ten Solver",       icon: "hash",     awarded_at: "2026-02-03T14:00:00Z" },
    { slug: "twenty-five-solves",name: "On a Roll",        icon: "target",   awarded_at: "2026-05-11T13:00:00Z" },
    { slug: "first-blood",       name: "Bloodhound",       icon: "droplets", awarded_at: "2026-02-20T08:45:00Z" },
    { slug: "sqli-first",        name: "Injector",         icon: "database", awarded_at: "2026-03-01T10:00:00Z" },
    { slug: "recon-first",       name: "Lurker",           icon: "eye",      awarded_at: "2026-01-12T09:30:00Z" },
    { slug: "web-first",         name: "Web Rookie",       icon: "globe",    awarded_at: "2026-06-01T09:30:00Z" },
  ],
  recent_solves: [
    { challenge_id: 65, challenge_title: "Not Your Seat",            challenge_slug: "ll-idor-booking",         points_awarded: 100, submitted_at: "2026-06-15T20:12:00Z", is_first_blood: false },
    { challenge_id: 15, challenge_title: "Ticker Injection",         challenge_slug: "tf-xss-reflected-market", points_awarded: 100, submitted_at: "2026-06-14T17:05:00Z", is_first_blood: false },
    { challenge_id: 34, challenge_title: "Everyone's Balance",       challenge_slug: "hb-idor-accounts",        points_awarded: 100, submitted_at: "2026-06-12T11:30:00Z", is_first_blood: false },
    { challenge_id: 3,  challenge_title: "Bypass the Velvet Rope",   challenge_slug: "rw-sqli-login-bypass",    points_awarded: 100, submitted_at: "2026-06-10T09:00:00Z", is_first_blood: true },
    { challenge_id: 1,  challenge_title: "What's Off-Limits?",       challenge_slug: "rw-recon-robots",         points_awarded: 50,  submitted_at: "2026-06-08T21:44:00Z", is_first_blood: false },
  ],
};

export function demoUserProfile(username: string) {
  return {
    user_id: 42,
    username,
    bio: "Security enthusiast. Always learning.",
    avatar_url: null,
    website_url: null,
    location: "Remote",
    github_handle: username.toLowerCase().replace(/[^a-z0-9]/g, ""),
    privacy_level: "public",
    show_activity: true,
    total_points: 1850,
    solve_count: 12,
    first_bloods: 1,
    team_count: 1,
    badges: [
      { slug: "first-steps", name: "First Steps", icon: "flag",     awarded_at: "2026-02-01T10:00:00Z" },
      { slug: "sqli-first",  name: "Injector",     icon: "database", awarded_at: "2026-03-10T14:00:00Z" },
    ],
    recent_solves: [
      { challenge_id: 12, challenge_title: "Inside the Order Book", challenge_slug: "tf-sqli-market-union", points_awarded: 300, submitted_at: "2026-06-10T08:30:00Z", is_first_blood: false },
      { challenge_id: 71, challenge_title: "Hidden Community",      challenge_slug: "sv-recon-robots",      points_awarded: 50,  submitted_at: "2026-06-05T15:00:00Z", is_first_blood: false },
    ],
  };
}

// ─── Rank ─────────────────────────────────────────────────────────────────────
// Real tier names/points/icons/colors from app/services/rank_service.py RANK_SEED.

export const DEMO_MY_RANK = {
  points: 4250,
  rank: {
    id: 5,
    name: "Explorer",
    min_points: 2500,
    icon: "🧭",
    color: "#3b82f6",
    is_active: true,
  },
  next_rank: {
    id: 6,
    name: "Initiate",
    min_points: 5000,
    icon: "🔓",
    color: "#2563eb",
    is_active: true,
  },
  progress_pct: 70,
};

export function demoUserRank(_userId: number) {
  return {
    points: 1850,
    rank: {
      id: 4,
      name: "Apprentice",
      min_points: 1000,
      icon: "🔑",
      color: "#16a34a",
      is_active: true,
    },
    next_rank: {
      id: 5,
      name: "Explorer",
      min_points: 2500,
      icon: "🧭",
      color: "#3b82f6",
      is_active: true,
    },
    progress_pct: 57,
  };
}

// ─── Scoreboard ───────────────────────────────────────────────────────────────

export const DEMO_SCOREBOARD = [
  { rank: 1,  user_id: 7,  username: "vx_phantom",      team_id: null, total: 8420, solve_count: 61, badge_count: 14, last_tx: "2026-06-15T23:55:00Z" },
  { rank: 2,  user_id: 3,  username: "r0otkit",          team_id: null, total: 7650, solve_count: 55, badge_count: 13, last_tx: "2026-06-15T22:10:00Z" },
  { rank: 3,  user_id: 11, username: "nullderef",        team_id: null, total: 6890, solve_count: 49, badge_count: 11, last_tx: "2026-06-15T20:30:00Z" },
  { rank: 4,  user_id: 96, username: "ctf_valkyrie",     team_id: null, total: 5980, solve_count: 44, badge_count: 10, last_tx: "2026-06-15T19:45:00Z" },
  { rank: 5,  user_id: 1,  username: "octorig_admin",    team_id: null, total: 4250, solve_count: 27, badge_count: 8,  last_tx: "2026-06-15T20:12:00Z" },
  { rank: 6,  user_id: 19, username: "idor_detective",   team_id: null, total: 3780, solve_count: 30, badge_count: 7,  last_tx: "2026-06-14T18:45:00Z" },
  { rank: 7,  user_id: 23, username: "sqli_witch",       team_id: null, total: 3210, solve_count: 25, badge_count: 6,  last_tx: "2026-06-14T14:20:00Z" },
  { rank: 8,  user_id: 8,  username: "xss_reaper",       team_id: null, total: 2900, solve_count: 22, badge_count: 5,  last_tx: "2026-06-13T19:00:00Z" },
  { rank: 9,  user_id: 31, username: "packet_surgeon",   team_id: null, total: 2550, solve_count: 20, badge_count: 5,  last_tx: "2026-06-13T11:30:00Z" },
  { rank: 10, user_id: 14, username: "redteam_rook",     team_id: null, total: 2100, solve_count: 17, badge_count: 4,  last_tx: "2026-06-12T09:15:00Z" },
  { rank: 11, user_id: 77, username: "shellcode_siren",  team_id: null, total: 1980, solve_count: 16, badge_count: 4,  last_tx: "2026-06-12T07:50:00Z" },
  { rank: 12, user_id: 42, username: "byte_bandit",      team_id: null, total: 1850, solve_count: 12, badge_count: 3,  last_tx: "2026-06-10T08:30:00Z" },
  { rank: 13, user_id: 55, username: "l0gic_error",      team_id: null, total: 1600, solve_count: 11, badge_count: 3,  last_tx: "2026-06-09T17:00:00Z" },
  { rank: 14, user_id: 61, username: "h3x_witch",        team_id: null, total: 1320, solve_count: 9,  badge_count: 2,  last_tx: "2026-06-07T21:45:00Z" },
  { rank: 15, user_id: 84, username: "cipher_jockey",    team_id: null, total: 1180, solve_count: 8,  badge_count: 2,  last_tx: "2026-06-06T16:10:00Z" },
  { rank: 16, user_id: 72, username: "payload_artisan",  team_id: null, total: 980,  solve_count: 7,  badge_count: 2,  last_tx: "2026-06-05T13:20:00Z" },
  { rank: 17, user_id: 67, username: "ghost_in_the_wire",team_id: null, total: 860,  solve_count: 6,  badge_count: 1,  last_tx: "2026-06-04T10:40:00Z" },
  { rank: 18, user_id: 88, username: "enum_everything",  team_id: null, total: 640,  solve_count: 5,  badge_count: 1,  last_tx: "2026-06-03T10:00:00Z" },
  { rank: 19, user_id: 91, username: "stack_smasher",    team_id: null, total: 590,  solve_count: 4,  badge_count: 1,  last_tx: "2026-06-02T08:15:00Z" },
  { rank: 20, user_id: 93, username: "n00b_hunter",      team_id: null, total: 420,  solve_count: 3,  badge_count: 1,  last_tx: "2026-05-28T14:30:00Z" },
  { rank: 21, user_id: 99, username: "kernel_panic",     team_id: null, total: 310,  solve_count: 2,  badge_count: 0,  last_tx: "2026-05-25T12:00:00Z" },
  { rank: 22, user_id: 102,username: "fresh_meat_22",    team_id: null, total: 150,  solve_count: 1,  badge_count: 0,  last_tx: "2026-05-20T09:30:00Z" },
];

// ─── Events ───────────────────────────────────────────────────────────────────

export const DEMO_EVENTS = [
  {
    id: 1,
    slug: "winter-ctf-2025",
    title: "Winter CTF 2025",
    description: "Our first community CTF event. Challenges spanning web, reversing, and forensics.",
    status: "ended",
    visibility: "public",
    scoring_mode: "static",
    start_at: "2025-12-01T10:00:00Z",
    end_at: "2025-12-03T22:00:00Z",
    max_team_size: 4,
    freeze_scoreboard_at: "2025-12-03T20:00:00Z",
    created_at: "2025-11-01T09:00:00Z",
    scoreboard_frozen: true,
  },
  {
    id: 2,
    slug: "spring-qualifier-2026",
    title: "Spring Qualifier 2026",
    description: "48-hour qualifier event. Top 10 teams advance to the Summer Invitational. Dynamic scoring — first solve is worth the most.",
    status: "running",
    visibility: "public",
    scoring_mode: "dynamic",
    start_at: "2026-06-14T12:00:00Z",
    end_at: "2026-06-19T12:00:00Z",
    max_team_size: 3,
    freeze_scoreboard_at: "2026-06-19T10:00:00Z",
    created_at: "2026-05-15T10:00:00Z",
    scoreboard_frozen: false,
  },
  {
    id: 3,
    slug: "summer-invitational-2026",
    title: "Summer Invitational 2026",
    description: "Invite-only competition for the top qualifying teams. High-difficulty challenges with cash prizes.",
    status: "published",
    visibility: "private",
    scoring_mode: "dynamic",
    start_at: "2026-07-15T12:00:00Z",
    end_at: "2026-07-17T20:00:00Z",
    max_team_size: 3,
    freeze_scoreboard_at: "2026-07-17T18:00:00Z",
    created_at: "2026-06-01T10:00:00Z",
    scoreboard_frozen: false,
  },
  {
    id: 4,
    slug: "campus-recruiting-night",
    title: "Campus Recruiting Night",
    description: "Beginner-friendly recon/SQLi/XSS challenges for a university recruiting event. Solo entries only.",
    status: "draft",
    visibility: "unlisted",
    scoring_mode: "static",
    start_at: null,
    end_at: null,
    max_team_size: 1,
    freeze_scoreboard_at: null,
    created_at: "2026-06-12T09:00:00Z",
    scoreboard_frozen: false,
  },
  {
    id: 5,
    slug: "autumn-classic-2025",
    title: "Autumn Classic 2025",
    description: "Archived single-day CTF. Kept around for the writeups and the scoreboard bragging rights.",
    status: "archived",
    visibility: "public",
    scoring_mode: "static",
    start_at: "2025-09-20T10:00:00Z",
    end_at: "2025-09-20T22:00:00Z",
    max_team_size: 4,
    freeze_scoreboard_at: "2025-09-20T20:00:00Z",
    created_at: "2025-08-15T09:00:00Z",
    scoreboard_frozen: true,
  },
];

// Real challenge metadata (from app/labs/registry/world.py) for the 5
// challenges bundled into the Spring Qualifier 2026 event.
export const DEMO_EVENT_CHALLENGES = [
  { id: 1,  slug: "rw-recon-robots",         title: "What's Off-Limits?",      category: "recon", difficulty: "easy",   points: 50,  solve_count: 38, solved_by_me: true },
  { id: 3,  slug: "rw-sqli-login-bypass",    title: "Bypass the Velvet Rope",  category: "sqli",  difficulty: "easy",   points: 100, solve_count: 31, solved_by_me: true },
  { id: 15, slug: "tf-xss-reflected-market", title: "Ticker Injection",        category: "xss",   difficulty: "easy",   points: 100, solve_count: 27, solved_by_me: true },
  { id: 34, slug: "hb-idor-accounts",        title: "Everyone's Balance",      category: "idor",  difficulty: "easy",   points: 100, solve_count: 22, solved_by_me: true },
  { id: 65, slug: "ll-idor-booking",         title: "Not Your Seat",           category: "idor",  difficulty: "easy",   points: 100, solve_count: 19, solved_by_me: true },
];

export const DEMO_EVENT_SCOREBOARD = [
  { rank: 1, user_id: 7,  username: "vx_phantom",    team_id: null, total: 2400, solve_count: 12, badge_count: 0, last_tx: "2026-06-15T23:55:00Z" },
  { rank: 2, user_id: 3,  username: "r0otkit",        team_id: null, total: 2100, solve_count: 10, badge_count: 0, last_tx: "2026-06-15T21:10:00Z" },
  { rank: 3, user_id: 1,  username: "octorig_admin",  team_id: null, total: 1850, solve_count: 9,  badge_count: 0, last_tx: "2026-06-15T20:12:00Z" },
  { rank: 4, user_id: 19, username: "idor_detective", team_id: null, total: 1500, solve_count: 7,  badge_count: 0, last_tx: "2026-06-14T18:45:00Z" },
  { rank: 5, user_id: 23, username: "sqli_witch",     team_id: null, total: 1200, solve_count: 6,  badge_count: 0, last_tx: "2026-06-14T14:20:00Z" },
];

// ─── Notifications ────────────────────────────────────────────────────────────

export const DEMO_NOTIFICATIONS = [
  {
    id: 1,
    type: "team_invite",
    title: "Team invitation",
    body: "vx_phantom invited you to join Red_Operators as a member.",
    data: { token: "demo-invite-token-abc123", team_name: "Red_Operators" },
    read_at: null,
    created_at: "2026-06-16T08:30:00Z",
  },
  {
    id: 2,
    type: "badge_earned",
    title: "Badge unlocked: Web Rookie",
    body: "You earned the Web Rookie badge for solving your first web exploitation challenge.",
    data: { badge_slug: "web-first", badge_name: "Web Rookie" },
    read_at: null,
    created_at: "2026-06-15T21:00:00Z",
  },
  {
    id: 3,
    type: "first_blood",
    title: "First Blood! 🩸",
    body: "You were first to solve Bypass the Velvet Rope and earned 100 pts.",
    data: { challenge_slug: "rw-sqli-login-bypass", challenge_title: "Bypass the Velvet Rope" },
    read_at: null,
    created_at: "2026-06-10T09:05:00Z",
  },
  {
    id: 4,
    type: "badge_earned",
    title: "Badge unlocked: Lurker",
    body: "You earned the Lurker badge for completing your first reconnaissance challenge.",
    data: { badge_slug: "recon-first", badge_name: "Lurker" },
    read_at: "2026-01-13T10:00:00Z",
    created_at: "2026-01-12T09:30:00Z",
  },
  {
    id: 5,
    type: "event_starting",
    title: "Event starting soon",
    body: "Spring Qualifier 2026 starts in 1 hour. Good luck!",
    data: { event_slug: "spring-qualifier-2026", event_title: "Spring Qualifier 2026" },
    read_at: "2026-06-14T11:30:00Z",
    created_at: "2026-06-14T11:00:00Z",
  },
  {
    id: 6,
    type: "team_invite",
    title: "Team invitation",
    body: "nullderef invited you to join BinaryNinjas as a manager.",
    data: { token: "demo-invite-token-def456", team_name: "BinaryNinjas" },
    read_at: "2026-04-02T09:00:00Z",
    created_at: "2026-04-01T18:00:00Z",
  },
];

// ─── Deployments ──────────────────────────────────────────────────────────────
// Real lab ids/slugs/names from app/labs/registry/{world,firerange}.py. Real
// container naming convention from app/services/deployment_provisioning.py
// is "{template container name}-{deployment id}".

export const DEMO_DEPLOYMENTS = [
  {
    id: 1001,
    lab_template_id: 9,
    started_by_id: 1,
    team_id: null,
    challenge_id: null,
    instance_for_user_id: null,
    status: "running",
    visibility: "private",
    container_names: ["octorig-breachsql-db-1001", "octorig-breachsql-pg-1001", "octorig-breachsql-app-1001"],
    container_ids: ["c3a7f1d8b2e4", "b6d9e2a7c4f1", "a1f4c8d3e6b9"],
    dynamic_flag: null,
    auto_destroy_at: "2026-06-16T22:00:00Z",
    error_message: null,
    started_at: "2026-06-16T10:00:00Z",
    stopped_at: null,
    created_at: "2026-06-16T10:00:00Z",
    lab_name: "BreachSQL",
    lab_slug: "breachsql",
    lab_category: "firerange",
    started_by_username: "octorig_admin",
    team_name: null,
  },
  {
    id: 1002,
    lab_template_id: 1,
    started_by_id: 1,
    team_id: 1,
    challenge_id: null,
    instance_for_user_id: null,
    status: "running",
    visibility: "team",
    container_names: ["octorig-rewindrange-1002"],
    container_ids: ["f9d2e3a1c5b7"],
    dynamic_flag: null,
    auto_destroy_at: "2026-06-17T08:00:00Z",
    error_message: null,
    started_at: "2026-06-15T08:00:00Z",
    stopped_at: null,
    created_at: "2026-06-15T08:00:00Z",
    lab_name: "Rewind",
    lab_slug: "rewindrange",
    lab_category: "world",
    started_by_username: "octorig_admin",
    team_name: "Red_Operators",
  },
];

// ─── Teams ────────────────────────────────────────────────────────────────────

export const DEMO_TEAMS = [
  {
    id: 1,
    name: "Red_Operators",
    slug: "red-operators",
    description: "Elite offensive security research team.",
    is_personal: false,
    created_by_id: 7,
    created_at: "2026-01-05T10:00:00Z",
    updated_at: "2026-05-20T14:00:00Z",
    my_role: "member",
    member_count: 4,
  },
  {
    id: 2,
    name: "BinaryNinjas",
    slug: "binary-ninjas",
    description: "Reverse engineering and exploit dev crew.",
    is_personal: false,
    created_by_id: 11,
    created_at: "2026-04-01T10:00:00Z",
    updated_at: "2026-06-02T09:00:00Z",
    my_role: "manager",
    member_count: 3,
  },
];

const DEMO_TEAM_DETAIL_BY_ID: Record<number, typeof DEMO_TEAMS[number]> = {
  1: DEMO_TEAMS[0],
  2: DEMO_TEAMS[1],
};

const DEMO_TEAM_MEMBERS_BY_ID: Record<number, Array<{
  id: number; team_id: number; user_id: number; username: string;
  email: string; role: string; joined_at: string;
}>> = {
  1: [
    { id: 10, team_id: 1, user_id: 7,  username: "vx_phantom",     email: "vx@redops.io",     role: "owner",   joined_at: "2026-01-05T10:00:00Z" },
    { id: 11, team_id: 1, user_id: 3,  username: "r0otkit",        email: "root@redops.io",   role: "manager", joined_at: "2026-01-06T09:00:00Z" },
    { id: 12, team_id: 1, user_id: 84, username: "cipher_jockey",  email: "cipher@redops.io", role: "member",  joined_at: "2026-02-01T11:00:00Z" },
    { id: 13, team_id: 1, user_id: 1,  username: "octorig_admin",  email: "admin@octorig.io", role: "member",  joined_at: "2026-03-10T15:30:00Z" },
  ],
  2: [
    { id: 20, team_id: 2, user_id: 11, username: "nullderef",     email: "null@binja.dev",   role: "owner",   joined_at: "2026-04-01T10:00:00Z" },
    { id: 21, team_id: 2, user_id: 1,  username: "octorig_admin", email: "admin@octorig.io", role: "manager", joined_at: "2026-04-02T09:00:00Z" },
    { id: 22, team_id: 2, user_id: 67, username: "ghost_in_the_wire", email: "ghost@binja.dev", role: "member", joined_at: "2026-05-01T13:00:00Z" },
  ],
};

export function demoTeamDetail(id: number) {
  return DEMO_TEAM_DETAIL_BY_ID[id] ?? DEMO_TEAMS[0];
}

export function demoTeamMembers(id: number) {
  return DEMO_TEAM_MEMBERS_BY_ID[id] ?? DEMO_TEAM_MEMBERS_BY_ID[1];
}

// ─── API Keys ─────────────────────────────────────────────────────────────────

export const DEMO_API_KEYS = [
  {
    id: 1,
    prefix: "oktor_Xk9mQp",
    name: "CI Pipeline",
    created_at: "2026-05-01T08:00:00Z",
    expires_at: null,
    last_used_at: "2026-06-15T04:30:00Z",
    is_active: true,
  },
  {
    id: 2,
    prefix: "oktor_Rn3vJw",
    name: "Local Dev",
    created_at: "2026-06-01T12:00:00Z",
    expires_at: "2026-12-31T23:59:59Z",
    last_used_at: "2026-06-16T09:15:00Z",
    is_active: true,
  },
];

// ─── System ───────────────────────────────────────────────────────────────────

export const DEMO_HEALTH = {
  docker: "ok",
  database: "ok",
  running_labs: 2,
  total_containers: 5,
};

// Shape matches ContainerInfo { name, status, image, created } exactly.
// First four mirror DEMO_DEPLOYMENTS containers (tracked); the last one has
// no deployment row — a lab started directly via octorig.sh, which keeps its
// base name (no per-deployment suffix), demonstrating the "Externally
// Managed" dashboard section.
export const DEMO_CONTAINERS = [
  { name: "octorig-breachsql-db-1001",  status: "running", image: "mysql:8.0",                       created: "2026-06-16T10:00:00Z" },
  { name: "octorig-breachsql-pg-1001",  status: "running", image: "postgres:16-alpine",               created: "2026-06-16T10:00:00Z" },
  { name: "octorig-breachsql-app-1001", status: "running", image: "octorig-breachsql:latest",         created: "2026-06-16T10:00:00Z" },
  { name: "octorig-rewindrange-1002",   status: "running", image: "octorig-rewindrange:latest",       created: "2026-06-15T08:00:00Z" },
  { name: "octorig-stingxss",           status: "running", image: "octorig-stingxss:latest",          created: "2026-06-14T16:00:00Z" },
];

// ─── Admin ────────────────────────────────────────────────────────────────────

export const DEMO_ADMIN_STATS = {
  user_count: 22,
  team_count: 5,
  active_deployments: 2,
  total_deployments: 14,
  api_key_count: 3,
  pending_scheduled_actions: 1,
};

// platform_roles use real seeded slugs (admin/creator/player/viewer) — see
// app/services/role_service.py ROLE_SEED. No custom roles in this fixture.
export const DEMO_ADMIN_USERS = [
  { id: 7,   username: "vx_phantom",       email: "vx@redops.io",          is_active: true,  platform_roles: ["player"],            created_at: "2026-01-01T10:00:00Z", last_login_at: "2026-06-16T07:00:00Z" },
  { id: 3,   username: "r0otkit",          email: "root@redops.io",        is_active: true,  platform_roles: ["player"],            created_at: "2026-01-02T11:00:00Z", last_login_at: "2026-06-15T22:00:00Z" },
  { id: 11,  username: "nullderef",        email: "null@binja.dev",        is_active: true,  platform_roles: ["player", "creator"], created_at: "2026-01-20T09:00:00Z", last_login_at: "2026-06-15T20:00:00Z" },
  { id: 96,  username: "ctf_valkyrie",     email: "valkyrie@example.com",  is_active: true,  platform_roles: ["player"],            created_at: "2026-01-22T09:00:00Z", last_login_at: "2026-06-15T19:45:00Z" },
  { id: 1,   username: "octorig_admin",    email: "admin@octorig.io",      is_active: true,  platform_roles: ["admin", "creator"],  created_at: "2025-12-01T08:00:00Z", last_login_at: "2026-06-16T09:00:00Z" },
  { id: 19,  username: "idor_detective",   email: "idor@example.com",      is_active: true,  platform_roles: ["player"],            created_at: "2026-02-01T10:00:00Z", last_login_at: "2026-06-14T18:00:00Z" },
  { id: 23,  username: "sqli_witch",       email: "sqli@example.com",      is_active: true,  platform_roles: ["player", "creator"], created_at: "2026-02-10T10:00:00Z", last_login_at: "2026-06-14T14:00:00Z" },
  { id: 8,   username: "xss_reaper",       email: "xss@example.com",       is_active: true,  platform_roles: ["player"],            created_at: "2026-02-15T10:00:00Z", last_login_at: "2026-06-13T19:00:00Z" },
  { id: 31,  username: "packet_surgeon",   email: "packet@example.com",    is_active: true,  platform_roles: ["player"],            created_at: "2026-02-20T10:00:00Z", last_login_at: "2026-06-13T11:30:00Z" },
  { id: 14,  username: "redteam_rook",     email: "rook@example.com",      is_active: true,  platform_roles: ["player"],            created_at: "2026-02-25T10:00:00Z", last_login_at: "2026-06-12T09:15:00Z" },
  { id: 77,  username: "shellcode_siren",  email: "siren@example.com",     is_active: true,  platform_roles: ["player"],            created_at: "2026-03-01T10:00:00Z", last_login_at: "2026-06-12T07:50:00Z" },
  { id: 42,  username: "byte_bandit",      email: "byte@example.com",      is_active: true,  platform_roles: ["player"],            created_at: "2026-03-01T10:00:00Z", last_login_at: "2026-06-10T08:00:00Z" },
  { id: 55,  username: "l0gic_error",      email: "logic@example.com",     is_active: false, platform_roles: ["player"],            created_at: "2026-03-10T10:00:00Z", last_login_at: "2026-06-09T17:00:00Z" },
  { id: 61,  username: "h3x_witch",        email: "hex@example.com",       is_active: true,  platform_roles: ["player"],            created_at: "2026-04-01T10:00:00Z", last_login_at: "2026-06-07T21:00:00Z" },
  { id: 84,  username: "cipher_jockey",    email: "cipher@redops.io",      is_active: true,  platform_roles: ["player"],            created_at: "2026-04-05T10:00:00Z", last_login_at: "2026-06-06T16:10:00Z" },
  { id: 72,  username: "payload_artisan",  email: "payload@example.com",   is_active: true,  platform_roles: ["player"],            created_at: "2026-04-10T10:00:00Z", last_login_at: "2026-06-05T13:20:00Z" },
  { id: 67,  username: "ghost_in_the_wire",email: "ghost@binja.dev",       is_active: true,  platform_roles: ["player"],            created_at: "2026-04-15T10:00:00Z", last_login_at: "2026-06-04T10:40:00Z" },
  { id: 88,  username: "enum_everything",  email: "enum@example.com",      is_active: true,  platform_roles: ["player"],            created_at: "2026-04-20T10:00:00Z", last_login_at: "2026-06-03T10:00:00Z" },
  { id: 91,  username: "stack_smasher",    email: "stack@example.com",     is_active: true,  platform_roles: ["player"],            created_at: "2026-04-25T10:00:00Z", last_login_at: "2026-06-02T08:15:00Z" },
  { id: 93,  username: "n00b_hunter",      email: "noob@example.com",      is_active: true,  platform_roles: ["player"],            created_at: "2026-05-01T10:00:00Z", last_login_at: "2026-05-28T14:30:00Z" },
  { id: 99,  username: "kernel_panic",     email: "kernel@example.com",    is_active: false, platform_roles: ["player"],            created_at: "2026-05-10T10:00:00Z", last_login_at: "2026-05-25T12:00:00Z" },
  { id: 102, username: "fresh_meat_22",    email: "fresh22@example.com",   is_active: true,  platform_roles: ["viewer"],            created_at: "2026-05-18T10:00:00Z", last_login_at: "2026-05-20T09:30:00Z" },
];

export const DEMO_ADMIN_TEAMS = [
  { id: 1, name: "Red_Operators",  slug: "red-operators",  is_personal: false, created_by_id: 7,  created_by_username: "vx_phantom",  member_count: 4, deployment_count: 2, created_at: "2026-01-05T10:00:00Z" },
  { id: 2, name: "BinaryNinjas",   slug: "binary-ninjas",  is_personal: false, created_by_id: 11, created_by_username: "nullderef",   member_count: 3, deployment_count: 1, created_at: "2026-04-01T10:00:00Z" },
  { id: 3, name: "NullPointers",   slug: "null-pointers",  is_personal: false, created_by_id: 91, created_by_username: "stack_smasher", member_count: 2, deployment_count: 0, created_at: "2026-03-05T10:00:00Z" },
  { id: 4, name: "HexHunters",     slug: "hex-hunters",    is_personal: false, created_by_id: 61, created_by_username: "h3x_witch",   member_count: 5, deployment_count: 3, created_at: "2026-03-20T10:00:00Z" },
  { id: 5, name: "ExploitFactory", slug: "exploit-factory",is_personal: false, created_by_id: 72, created_by_username: "payload_artisan", member_count: 2, deployment_count: 1, created_at: "2026-04-10T10:00:00Z" },
];

// Action strings are real audit_service.py constants (dotted namespace —
// the admin audit UI color-codes badges by the prefix before the first dot).
export const DEMO_AUDIT_LOGS = [
  { id: 201, user_id: 1,  username: "octorig_admin",   team_id: null, team_name: null,            deployment_id: null, action: "auth.login",              detail: { ip: "10.0.0.4" },                 ip_address: "10.0.0.4",  created_at: "2026-06-16T09:00:00Z" },
  { id: 202, user_id: 1,  username: "octorig_admin",   team_id: null, team_name: null,            deployment_id: 1001, action: "lab.deployed",            detail: { lab: "breachsql" },                ip_address: "10.0.0.4",  created_at: "2026-06-16T10:00:00Z" },
  { id: 203, user_id: 7,  username: "vx_phantom",      team_id: 1,    team_name: "Red_Operators", deployment_id: null, action: "team.member_invited",     detail: { invitee: "octorig_admin" },        ip_address: "10.0.0.11", created_at: "2026-06-16T08:30:00Z" },
  { id: 204, user_id: 23, username: "sqli_witch",      team_id: null, team_name: null,            deployment_id: null, action: "challenge.solved",        detail: { challenge: "tf-sqli-market-union", points: 300 }, ip_address: "10.0.0.23", created_at: "2026-06-14T14:20:00Z" },
  { id: 205, user_id: null,username: null,             team_id: null, team_name: null,            deployment_id: null, action: "badge.awarded",           detail: { badge: "web-first", user: "octorig_admin" }, ip_address: null, created_at: "2026-06-15T21:00:00Z" },
  { id: 206, user_id: 19, username: "idor_detective",  team_id: null, team_name: null,            deployment_id: 999,  action: "lab.destroyed",           detail: { lab: "tradefloor" },               ip_address: "10.0.0.19", created_at: "2026-06-15T17:00:00Z" },
  { id: 207, user_id: 3,  username: "r0otkit",         team_id: null, team_name: null,            deployment_id: null, action: "auth.login_failed",       detail: { reason: "bad_password" },          ip_address: "10.0.0.3",  created_at: "2026-06-15T07:55:00Z" },
  { id: 208, user_id: 11, username: "nullderef",       team_id: 2,    team_name: "BinaryNinjas",  deployment_id: null, action: "team.created",            detail: {},                                  ip_address: "10.0.0.11", created_at: "2026-04-01T10:00:00Z" },
  { id: 209, user_id: 1,  username: "octorig_admin",   team_id: null, team_name: null,            deployment_id: null, action: "api_key.created",         detail: { name: "CI Pipeline" },             ip_address: "10.0.0.4",  created_at: "2026-05-01T08:00:00Z" },
  { id: 210, user_id: 1,  username: "octorig_admin",   team_id: null, team_name: null,            deployment_id: null, action: "admin.role_changed",      detail: { target: "sqli_witch", added: "creator" }, ip_address: "10.0.0.4", created_at: "2026-02-10T10:05:00Z" },
  { id: 211, user_id: 1,  username: "octorig_admin",   team_id: null, team_name: null,            deployment_id: null, action: "admin.user_deactivated",  detail: { target: "l0gic_error" },           ip_address: "10.0.0.4",  created_at: "2026-06-09T17:05:00Z" },
  { id: 212, user_id: 1,  username: "octorig_admin",   team_id: null, team_name: null,            deployment_id: null, action: "schedule.created",        detail: { action: "destroy", scheduled_at: "2026-06-17T08:00:00Z" }, ip_address: "10.0.0.4", created_at: "2026-06-15T08:05:00Z" },
];

export const DEMO_ADMIN_API_KEYS = [
  { id: 1, prefix: "oktor_Xk9mQp", name: "CI Pipeline",  user_id: 1,  username: "octorig_admin", created_at: "2026-05-01T08:00:00Z", expires_at: null,                  last_used_at: "2026-06-15T04:30:00Z", is_active: true },
  { id: 2, prefix: "oktor_Rn3vJw", name: "Local Dev",    user_id: 1,  username: "octorig_admin", created_at: "2026-06-01T12:00:00Z", expires_at: "2026-12-31T23:59:59Z", last_used_at: "2026-06-16T09:15:00Z", is_active: true },
  { id: 3, prefix: "oktor_Tz7pLm", name: "Monitoring",   user_id: 3,  username: "r0otkit",        created_at: "2026-04-10T09:00:00Z", expires_at: null,                  last_used_at: "2026-06-16T00:05:00Z", is_active: true },
];

export const DEMO_ADMIN_SETTINGS = {
  registration_open: true,
  maintenance_mode: false,
  maintenance_message: null,
  max_flag_attempts: 10,
  dynamic_scoring_enabled: true,
  dynamic_decay_factor: 0.9,
  dynamic_min_floor_pct: 10,
  scoreboard_frozen_at: null,
  first_blood_enabled: true,
  python_editor_enabled: true,
  hide_lab_ports: false,
  company_name: "CommonHuman-Lab",
  company_logo_url: null,
  default_theme: "dark",
  updated_at: "2026-06-01T10:00:00Z",
};

// ─── Content creator / review queue ────────────────────────────────────────────
// These are usage records (drafts an author wrote), not seeded catalog data —
// there's no real-backend equivalent to mirror, so plausible fixtures are fine.
// They reference real lab slugs/categories for the "which lab does this attach
// to" context.

export const DEMO_CONTENT_MINE = [
  {
    id: 301,
    author_id: 1,
    author_username: "octorig_admin",
    content_type: "challenge",
    title: "Cache Me If You Can",
    body: { lab_slug: "netpulse", category: "web", difficulty: "medium", points: 250, description: "A CDN cache key that ignores a query parameter it shouldn't." },
    status: "draft",
    reviewer_id: null,
    created_at: "2026-06-10T09:00:00Z",
    updated_at: "2026-06-14T16:00:00Z",
  },
  {
    id: 295,
    author_id: 1,
    author_username: "octorig_admin",
    content_type: "challenge",
    title: "Borrowed Boarding Pass",
    body: { lab_slug: "limelight", category: "idor", difficulty: "easy", points: 100, description: "A seat-confirmation endpoint that trusts the booking ID alone." },
    status: "in_review",
    reviewer_id: 11,
    created_at: "2026-05-28T10:00:00Z",
    updated_at: "2026-06-05T11:00:00Z",
  },
  {
    id: 280,
    author_id: 1,
    author_username: "octorig_admin",
    content_type: "challenge",
    title: "Audit Trail Amnesia",
    body: { lab_slug: "smartgridops", category: "web", difficulty: "hard", points: 400, description: "Zone override commands that never make it into the operator audit log." },
    status: "published",
    reviewer_id: 11,
    created_at: "2026-05-01T10:00:00Z",
    updated_at: "2026-05-10T09:00:00Z",
  },
];

export const DEMO_CONTENT_PENDING = [
  {
    id: 295,
    author_id: 1,
    author_username: "octorig_admin",
    content_type: "challenge",
    title: "Borrowed Boarding Pass",
    body: { lab_slug: "limelight", category: "idor", difficulty: "easy", points: 100, description: "A seat-confirmation endpoint that trusts the booking ID alone." },
    status: "pending_review",
    reviewer_id: null,
    created_at: "2026-05-28T10:00:00Z",
    updated_at: "2026-05-28T10:00:00Z",
  },
  {
    id: 297,
    author_id: 23,
    author_username: "sqli_witch",
    content_type: "challenge",
    title: "Second-Order Surprise",
    body: { lab_slug: "subverse", category: "sqli", difficulty: "hard", points: 400, description: "A display-name field that's safe on write and dangerous on a later read." },
    status: "pending_review",
    reviewer_id: null,
    created_at: "2026-06-09T13:00:00Z",
    updated_at: "2026-06-09T13:00:00Z",
  },
];

export const DEMO_CONTENT_APPROVED = [
  {
    id: 280,
    author_id: 1,
    author_username: "octorig_admin",
    content_type: "challenge",
    title: "Audit Trail Amnesia",
    body: { lab_slug: "smartgridops", category: "web", difficulty: "hard", points: 400, description: "Zone override commands that never make it into the operator audit log." },
    status: "approved",
    reviewer_id: 11,
    created_at: "2026-05-01T10:00:00Z",
    updated_at: "2026-05-09T15:00:00Z",
  },
  {
    id: 271,
    author_id: 11,
    author_username: "nullderef",
    content_type: "challenge",
    title: "Stale Session, Fresh Access",
    body: { lab_slug: "medihuman", category: "web", difficulty: "medium", points: 250, description: "A logout endpoint that revokes the cookie but not the underlying session token." },
    status: "approved",
    reviewer_id: 1,
    created_at: "2026-04-20T10:00:00Z",
    updated_at: "2026-04-25T09:00:00Z",
  },
];

// ─── Client assessments ─────────────────────────────────────────────────────────
// Also usage records (a creator bundles real labs into a timed take-home
// assessment for a candidate) — lab_slugs below are real registry slugs.

export const DEMO_ASSESSMENTS = [
  {
    id: 401,
    name: "Senior AppSec Engineer — Take-Home",
    slug: "senior-appsec-takehome",
    company_name: "Vantage Risk Partners",
    company_logo_url: null,
    description: "4-hour practical assessment covering SQLi, IDOR, and broken access control.",
    candidate_instructions: "Find and document the flag in each lab. Submit your report before the timer expires.",
    duration_hours: 4,
    lab_slugs: ["rewindrange", "humanbank", "smartgridops"],
    lab_display_names: { rewindrange: "Lab 1", humanbank: "Lab 2", smartgridops: "Lab 3" },
    is_active: true,
    created_by_id: 1,
    created_at: "2026-05-20T10:00:00Z",
    invite_count: 3,
    active_invite_count: 0,
  },
  {
    id: 402,
    name: "Junior Pentester Screening",
    slug: "junior-pentester-screening",
    company_name: "Northbridge Security",
    company_logo_url: null,
    description: "2-hour entry-level screen — recon and reflected/stored XSS.",
    candidate_instructions: "Work through both labs and submit flags as you find them.",
    duration_hours: 2,
    lab_slugs: ["tradefloor", "limelight"],
    lab_display_names: { tradefloor: "Lab A", limelight: "Lab B" },
    is_active: true,
    created_by_id: 1,
    created_at: "2026-06-01T10:00:00Z",
    invite_count: 1,
    active_invite_count: 1,
  },
  {
    id: 403,
    name: "Red Team Bench Test — Q1 (archived)",
    slug: "redteam-bench-q1",
    company_name: "Vantage Risk Partners",
    company_logo_url: null,
    description: "Older bench test, superseded by the take-home above.",
    candidate_instructions: null,
    duration_hours: 6,
    lab_slugs: ["goldenace", "medihuman", "subverse", "netpulse"],
    lab_display_names: {},
    is_active: false,
    created_by_id: 1,
    created_at: "2026-02-10T10:00:00Z",
    invite_count: 9,
    active_invite_count: 0,
  },
];

export const DEMO_ASSESSMENT_INVITES: Record<number, Array<{
  id: number; assessment_id: number; email: string; candidate_name: string | null;
  token: string; user_id: number | null; accepted_at: string | null; started_at: string | null;
  expires_at: string | null; completed_at: string | null; deployment_ids: number[];
  is_revoked: boolean; status: string;
}>> = {
  401: [
    { id: 1, assessment_id: 401, email: "j.romero@candidatemail.com", candidate_name: "Javier Romero", token: "tok_8h2kq", user_id: 110, accepted_at: "2026-06-10T13:00:00Z", started_at: "2026-06-10T13:05:00Z", expires_at: "2026-06-10T17:05:00Z", completed_at: null, deployment_ids: [2001, 2002], is_revoked: false, status: "expired" },
    { id: 2, assessment_id: 401, email: "a.chen@candidatemail.com",   candidate_name: "Amy Chen",     token: "tok_9j3lr", user_id: 111, accepted_at: "2026-06-15T09:00:00Z", started_at: "2026-06-15T09:02:00Z", expires_at: "2026-06-15T11:40:00Z", completed_at: "2026-06-15T11:40:00Z", deployment_ids: [2010], is_revoked: false, status: "completed" },
    { id: 3, assessment_id: 401, email: "pending.candidate@example.com", candidate_name: null,         token: "tok_2m9zx", user_id: null, accepted_at: null, started_at: null, expires_at: null, completed_at: null, deployment_ids: [], is_revoked: false, status: "pending" },
  ],
  402: [
    { id: 4, assessment_id: 402, email: "k.osei@candidatemail.com", candidate_name: "Kwame Osei", token: "tok_4p7qs", user_id: 112, accepted_at: "2026-06-14T10:00:00Z", started_at: "2026-06-14T10:01:00Z", expires_at: "2026-06-14T12:01:00Z", completed_at: null, deployment_ids: [2020], is_revoked: false, status: "active" },
  ],
  403: [],
};

export const DEMO_ASSESSMENT_FLAGS: Array<{
  challenge_slug: string; challenge_title: string; points: number; solved_at: string;
}> = [
  { challenge_slug: "rw-recon-robots", challenge_title: "What's Off-Limits?", points: 100, solved_at: "2026-06-10T13:30:00Z" },
  { challenge_slug: "hb-idor-accounts", challenge_title: "Everyone's Balance", points: 250, solved_at: "2026-06-10T14:10:00Z" },
];

// ─── Augmentation helpers (applied to real API responses) ─────────────────────
// These overlay fake personal/social state (solve_count, solved_by_me, earned)
// on top of catalog data that always comes from the real backend, so the
// catalog itself (labs/challenges/badges) can never drift from app/labs and
// app/badge_catalog.

const DEMO_USERNAMES = [
  "vx_phantom", "r0otkit", "nullderef", "idor_detective", "sqli_witch",
  "xss_reaper", "packet_surgeon", "redteam_rook", "byte_bandit",
];

export function augmentChallengeList<T extends {
  id: number;
  solve_count: number;
  solved_by_me: boolean;
  first_blood_user: string | null;
}>(challenges: T[]): T[] {
  return challenges.map((ch, i) => ({
    ...ch,
    solve_count: 15 + ((ch.id * 7 + i * 3) % 170),
    solved_by_me: i % 3 !== 0,
    first_blood_user: i % 5 === 0
      ? DEMO_USERNAMES[i % DEMO_USERNAMES.length]
      : ch.first_blood_user,
  }));
}

export function augmentChallengeDetail<T extends {
  id: number;
  solve_count: number;
  solved_by_me: boolean;
  first_blood_user: string | null;
}>(challenge: T, index?: number): T {
  // Default to the same index this challenge would occupy in the list (id
  // is 1-based and sequential), so a challenge's solved/solve_count state
  // is consistent whether viewed from the list or the detail page.
  const i = index ?? Math.max(0, challenge.id - 1);
  return {
    ...challenge,
    solve_count: 15 + ((challenge.id * 7 + i * 3) % 170),
    solved_by_me: i % 3 !== 0,
    first_blood_user: i % 5 === 0
      ? DEMO_USERNAMES[i % DEMO_USERNAMES.length]
      : challenge.first_blood_user,
  };
}

export function augmentBadgeList<T extends {
  slug: string;
  earned: boolean;
  awarded_at?: string | null;
}>(badges: T[]): T[] {
  return badges.map((b, i) => ({
    ...b,
    earned: i % 2 === 0,
    awarded_at: i % 2 === 0 ? "2026-03-15T10:00:00Z" : null,
  }));
}
