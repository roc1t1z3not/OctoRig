// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
// Demo mode fixture data — all static, no backend calls.
// Dates are relative to 2026-06-16 (today when this was written).

// ─── Auth ─────────────────────────────────────────────────────────────────────

export const DEMO_ME = {
  id: 1,
  username: "octorig_admin",
  email: "admin@octorig.io",
  platform_roles: ["admin", "creator", "reviewer", "publisher"],
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

export const DEMO_PROFILE_ME = {
  user_id: 1,
  username: "octorig_admin",
  bio: "Offensive security researcher and CTF enthusiast. Building tools to help people learn security hands-on.",
  avatar_url: null,
  website_url: "https://commonhuman.io",
  location: "Tranquility, Moon",
  github_handle: "commonhuman-lab",
  twitter_handle: "commonhuman_io",
  privacy_level: "public",
  show_activity: true,
  total_points: 4250,
  solve_count: 27,
  first_bloods: 5,
  team_count: 1,
  badges: [
    { slug: "first-solve", name: "First Solve", icon: "flag", awarded_at: "2026-01-10T09:00:00Z" },
    { slug: "sql-apprentice", name: "SQL Apprentice", icon: "database", awarded_at: "2026-01-15T11:30:00Z" },
    { slug: "xss-hunter", name: "XSS Hunter", icon: "zap", awarded_at: "2026-02-03T14:00:00Z" },
    { slug: "first-blood", name: "First Blood", icon: "droplets", awarded_at: "2026-02-20T08:45:00Z" },
    { slug: "team-player", name: "Team Player", icon: "shield", awarded_at: "2026-03-01T10:00:00Z" },
    { slug: "python-coder", name: "Python Coder", icon: "code", awarded_at: "2026-04-05T16:20:00Z" },
    { slug: "recon-ranger", name: "Recon Ranger", icon: "eye", awarded_at: "2026-05-11T13:00:00Z" },
    { slug: "web-warrior", name: "Web Warrior", icon: "globe", awarded_at: "2026-06-01T09:30:00Z" },
  ],
  recent_solves: [
    { challenge_id: 101, challenge_title: "Blind Date", challenge_slug: "blind-date", points_awarded: 300, submitted_at: "2026-06-15T20:12:00Z", is_first_blood: true },
    { challenge_id: 102, challenge_title: "Cookie Monster", challenge_slug: "cookie-monster", points_awarded: 150, submitted_at: "2026-06-14T17:05:00Z", is_first_blood: false },
    { challenge_id: 103, challenge_title: "Rate Me Not", challenge_slug: "rate-me-not", points_awarded: 200, submitted_at: "2026-06-12T11:30:00Z", is_first_blood: false },
    { challenge_id: 104, challenge_title: "Hidden in Plain Sight", challenge_slug: "hidden-in-plain-sight", points_awarded: 100, submitted_at: "2026-06-10T09:00:00Z", is_first_blood: false },
    { challenge_id: 105, challenge_title: "Union Jack", challenge_slug: "union-jack", points_awarded: 200, submitted_at: "2026-06-08T21:44:00Z", is_first_blood: false },
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
    twitter_handle: null,
    privacy_level: "public",
    show_activity: true,
    total_points: 1850,
    solve_count: 12,
    first_bloods: 1,
    team_count: 1,
    badges: [
      { slug: "first-solve", name: "First Solve", icon: "flag", awarded_at: "2026-02-01T10:00:00Z" },
      { slug: "sql-apprentice", name: "SQL Apprentice", icon: "database", awarded_at: "2026-03-10T14:00:00Z" },
    ],
    recent_solves: [
      { challenge_id: 101, challenge_title: "Union Jack", challenge_slug: "union-jack", points_awarded: 200, submitted_at: "2026-06-10T08:30:00Z", is_first_blood: false },
      { challenge_id: 102, challenge_title: "Reflected Glory", challenge_slug: "reflected-glory", points_awarded: 100, submitted_at: "2026-06-05T15:00:00Z", is_first_blood: false },
    ],
  };
}

// ─── Rank ─────────────────────────────────────────────────────────────────────

export const DEMO_MY_RANK = {
  points: 4250,
  rank: {
    id: 14,
    name: "Advanced Operator",
    min_points: 4000,
    icon: "flame",
    color: "#f97316",
    is_active: true,
  },
  next_rank: {
    id: 15,
    name: "Elite Operator",
    min_points: 6000,
    icon: "crown",
    color: "#a855f7",
    is_active: true,
  },
  progress_pct: 68,
};

export function demoUserRank(userId: number) {
  return {
    points: 1850,
    rank: {
      id: 11,
      name: "Intermediate",
      min_points: 1500,
      icon: "target",
      color: "#3b82f6",
      is_active: true,
    },
    next_rank: {
      id: 12,
      name: "Senior Analyst",
      min_points: 2500,
      icon: "shield",
      color: "#06b6d4",
      is_active: true,
    },
    progress_pct: 35,
  };
}

// ─── Scoreboard ───────────────────────────────────────────────────────────────

export const DEMO_SCOREBOARD = [
  { rank: 1,  user_id: 7,  username: "vx_phantom",       team_id: null, total: 6820, solve_count: 54, badge_count: 12, last_tx: "2026-06-15T23:55:00Z" },
  { rank: 2,  user_id: 3,  username: "r0otkit",           team_id: null, total: 5940, solve_count: 47, badge_count: 10, last_tx: "2026-06-15T22:10:00Z" },
  { rank: 3,  user_id: 11, username: "nullderef",         team_id: null, total: 5200, solve_count: 41, badge_count: 9,  last_tx: "2026-06-15T20:30:00Z" },
  { rank: 4,  user_id: 1,  username: "octorig_admin",     team_id: null, total: 4250, solve_count: 27, badge_count: 8,  last_tx: "2026-06-15T20:12:00Z" },
  { rank: 5,  user_id: 19, username: "idor_detective",    team_id: null, total: 3780, solve_count: 30, badge_count: 7,  last_tx: "2026-06-14T18:45:00Z" },
  { rank: 6,  user_id: 23, username: "sqli_witch",        team_id: null, total: 3210, solve_count: 25, badge_count: 6,  last_tx: "2026-06-14T14:20:00Z" },
  { rank: 7,  user_id: 8,  username: "xss_reaper",        team_id: null, total: 2900, solve_count: 22, badge_count: 5,  last_tx: "2026-06-13T19:00:00Z" },
  { rank: 8,  user_id: 31, username: "packet_surgeon",    team_id: null, total: 2550, solve_count: 20, badge_count: 5,  last_tx: "2026-06-13T11:30:00Z" },
  { rank: 9,  user_id: 14, username: "redteam_rook",      team_id: null, total: 2100, solve_count: 17, badge_count: 4,  last_tx: "2026-06-12T09:15:00Z" },
  { rank: 10, user_id: 42, username: "byte_bandit",       team_id: null, total: 1850, solve_count: 12, badge_count: 3,  last_tx: "2026-06-10T08:30:00Z" },
  { rank: 11, user_id: 55, username: "l0gic_error",       team_id: null, total: 1600, solve_count: 11, badge_count: 3,  last_tx: "2026-06-09T17:00:00Z" },
  { rank: 12, user_id: 61, username: "h3x_witch",         team_id: null, total: 1320, solve_count: 9,  badge_count: 2,  last_tx: "2026-06-07T21:45:00Z" },
  { rank: 13, user_id: 72, username: "payload_artisan",   team_id: null, total: 980,  solve_count: 7,  badge_count: 2,  last_tx: "2026-06-05T13:20:00Z" },
  { rank: 14, user_id: 88, username: "enum_everything",   team_id: null, total: 640,  solve_count: 5,  badge_count: 1,  last_tx: "2026-06-03T10:00:00Z" },
  { rank: 15, user_id: 93, username: "n00b_hunter",       team_id: null, total: 420,  solve_count: 3,  badge_count: 1,  last_tx: "2026-05-28T14:30:00Z" },
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
];

// Shared challenge slugs used in event challenge lists (mapped from real challenges)
export const DEMO_EVENT_CHALLENGES_SLUGS = [
  "union-jack", "reflected-glory", "cookie-monster", "blind-date", "rate-me-not",
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
    title: "Badge unlocked: Web Warrior",
    body: "You earned the Web Warrior badge for completing 5 web challenges.",
    data: { badge_slug: "web-warrior", badge_name: "Web Warrior" },
    read_at: null,
    created_at: "2026-06-15T21:00:00Z",
  },
  {
    id: 3,
    type: "first_blood",
    title: "First Blood! 🩸",
    body: "You were first to solve Blind Date and earned 300 pts.",
    data: { challenge_slug: "blind-date", challenge_title: "Blind Date" },
    read_at: null,
    created_at: "2026-06-15T20:12:00Z",
  },
  {
    id: 4,
    type: "badge_earned",
    title: "Badge unlocked: Recon Ranger",
    body: "You earned the Recon Ranger badge for completing 3 reconnaissance challenges.",
    data: { badge_slug: "recon-ranger", badge_name: "Recon Ranger" },
    read_at: "2026-06-11T10:00:00Z",
    created_at: "2026-05-11T13:00:00Z",
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
];

// ─── Deployments ──────────────────────────────────────────────────────────────

export const DEMO_DEPLOYMENTS = [
  {
    id: 1001,
    lab_template_id: 8,
    started_by_id: 1,
    team_id: null,
    challenge_id: null,
    instance_for_user_id: null,
    status: "running",
    visibility: "private",
    container_names: ["breachsql-fire-range-1001"],
    container_ids: ["c3a7f1d8b2e4"],
    dynamic_flag: null,
    auto_destroy_at: "2026-06-16T22:00:00Z",
    error_message: null,
    started_at: "2026-06-16T10:00:00Z",
    stopped_at: null,
    created_at: "2026-06-16T10:00:00Z",
    lab_name: "BreachSQL Fire Range",
    lab_slug: "breachsql-fire-range",
    lab_category: "firerange",
    started_by_username: "octorig_admin",
    team_name: null,
  },
  {
    id: 1002,
    lab_template_id: 1,
    started_by_id: 1,
    team_id: null,
    challenge_id: null,
    instance_for_user_id: null,
    status: "running",
    visibility: "private",
    container_names: ["rewind-1002", "rewind-db-1002"],
    container_ids: ["f9d2e3a1c5b7", "a4b8c2d1e6f0"],
    dynamic_flag: null,
    auto_destroy_at: "2026-06-17T08:00:00Z",
    error_message: null,
    started_at: "2026-06-15T08:00:00Z",
    stopped_at: null,
    created_at: "2026-06-15T08:00:00Z",
    lab_name: "Rewind",
    lab_slug: "rewind",
    lab_category: "world",
    started_by_username: "octorig_admin",
    team_name: null,
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
];

export const DEMO_TEAM_DETAIL = {
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
};

export const DEMO_TEAM_MEMBERS = [
  { id: 10, team_id: 1, user_id: 7,  username: "vx_phantom",     email: "vx@redops.io",      role: "owner",   joined_at: "2026-01-05T10:00:00Z" },
  { id: 11, team_id: 1, user_id: 3,  username: "r0otkit",        email: "root@redops.io",     role: "manager", joined_at: "2026-01-06T09:00:00Z" },
  { id: 12, team_id: 1, user_id: 11, username: "nullderef",      email: "null@redops.io",     role: "member",  joined_at: "2026-02-01T11:00:00Z" },
  { id: 13, team_id: 1, user_id: 1,  username: "octorig_admin",  email: "admin@octorig.io",   role: "member",  joined_at: "2026-03-10T15:30:00Z" },
];

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
  docker: { status: "healthy", message: "Docker daemon is running" },
  database: { status: "healthy", message: "Database connection is active" },
  running_labs: 5,
  total_containers: 11,
};

export const DEMO_CONTAINERS = [
  { name: "rewind-1002",              id: "f9d2e3a1c5b7", status: "running", lab: "rewind" },
  { name: "rewind-db-1002",           id: "a4b8c2d1e6f0", status: "running", lab: "rewind" },
  { name: "breachsql-fire-range-1001",id: "c3a7f1d8b2e4", status: "running", lab: "breachsql-fire-range" },
  { name: "tradefloor-1003",          id: "d5e6f7a8b9c0", status: "running", lab: "tradefloor" },
  { name: "golden-ace-1004",          id: "e1f2a3b4c5d6", status: "running", lab: "golden-ace" },
];

// ─── Admin ────────────────────────────────────────────────────────────────────

export const DEMO_ADMIN_STATS = {
  total_users: 847,
  total_teams: 142,
  active_deployments: 23,
  active_api_keys: 12,
  pending_scheduled: 3,
};

export const DEMO_ADMIN_USERS = [
  { id: 7,   username: "vx_phantom",      email: "vx@redops.io",          is_active: true, platform_roles: ["player"],         created_at: "2026-01-01T10:00:00Z", last_login_at: "2026-06-16T07:00:00Z" },
  { id: 3,   username: "r0otkit",         email: "root@redops.io",        is_active: true, platform_roles: ["player", "reviewer"], created_at: "2026-01-02T11:00:00Z", last_login_at: "2026-06-15T22:00:00Z" },
  { id: 11,  username: "nullderef",       email: "null@redops.io",        is_active: true, platform_roles: ["player"],         created_at: "2026-01-20T09:00:00Z", last_login_at: "2026-06-15T20:00:00Z" },
  { id: 1,   username: "octorig_admin",   email: "admin@octorig.io",      is_active: true, platform_roles: ["admin", "creator", "reviewer", "publisher"], created_at: "2025-12-01T08:00:00Z", last_login_at: "2026-06-16T09:00:00Z" },
  { id: 19,  username: "idor_detective",  email: "idor@example.com",      is_active: true, platform_roles: ["player"],         created_at: "2026-02-01T10:00:00Z", last_login_at: "2026-06-14T18:00:00Z" },
  { id: 23,  username: "sqli_witch",      email: "sqli@example.com",      is_active: true, platform_roles: ["player", "creator"], created_at: "2026-02-10T10:00:00Z", last_login_at: "2026-06-14T14:00:00Z" },
  { id: 8,   username: "xss_reaper",      email: "xss@example.com",       is_active: true, platform_roles: ["player"],         created_at: "2026-02-15T10:00:00Z", last_login_at: "2026-06-13T19:00:00Z" },
  { id: 42,  username: "byte_bandit",     email: "byte@example.com",      is_active: true, platform_roles: ["player"],         created_at: "2026-03-01T10:00:00Z", last_login_at: "2026-06-10T08:00:00Z" },
  { id: 55,  username: "l0gic_error",     email: "logic@example.com",     is_active: false,platform_roles: ["player"],         created_at: "2026-03-10T10:00:00Z", last_login_at: "2026-06-09T17:00:00Z" },
  { id: 61,  username: "h3x_witch",       email: "hex@example.com",       is_active: true, platform_roles: ["player"],         created_at: "2026-04-01T10:00:00Z", last_login_at: "2026-06-07T21:00:00Z" },
];

export const DEMO_ADMIN_TEAMS = [
  { id: 1,  name: "Red_Operators",   slug: "red-operators",   member_count: 4, deployment_count: 2, created_at: "2026-01-05T10:00:00Z" },
  { id: 2,  name: "BinaryNinjas",    slug: "binary-ninjas",   member_count: 3, deployment_count: 1, created_at: "2026-02-01T10:00:00Z" },
  { id: 3,  name: "NullPointers",    slug: "null-pointers",   member_count: 2, deployment_count: 0, created_at: "2026-03-05T10:00:00Z" },
  { id: 4,  name: "HexHunters",      slug: "hex-hunters",     member_count: 5, deployment_count: 3, created_at: "2026-03-20T10:00:00Z" },
  { id: 5,  name: "ExploitFactory",  slug: "exploit-factory", member_count: 2, deployment_count: 1, created_at: "2026-04-10T10:00:00Z" },
];

export const DEMO_AUDIT_LOGS = [
  { id: 201, action: "flag_submit",      actor_username: "vx_phantom",     target: "blind-date",           details: { correct: true,  points: 300 }, created_at: "2026-06-15T23:55:00Z" },
  { id: 202, action: "flag_submit",      actor_username: "r0otkit",        target: "cookie-monster",       details: { correct: true,  points: 150 }, created_at: "2026-06-15T22:10:00Z" },
  { id: 203, action: "deployment_start", actor_username: "octorig_admin",  target: "rewind",               details: { deployment_id: 1002 },          created_at: "2026-06-15T08:00:00Z" },
  { id: 204, action: "user_login",       actor_username: "octorig_admin",  target: null,                   details: { ip: "10.0.0.1" },               created_at: "2026-06-16T09:00:00Z" },
  { id: 205, action: "badge_awarded",    actor_username: "octorig_admin",  target: "octorig_admin",        details: { badge: "web-warrior" },         created_at: "2026-06-15T21:00:00Z" },
  { id: 206, action: "flag_submit",      actor_username: "nullderef",      target: "rate-me-not",          details: { correct: false },               created_at: "2026-06-15T19:30:00Z" },
  { id: 207, action: "deployment_stop",  actor_username: "idor_detective", target: "tradefloor",           details: { deployment_id: 999 },           created_at: "2026-06-15T17:00:00Z" },
  { id: 208, action: "team_invite",      actor_username: "vx_phantom",     target: "octorig_admin",        details: { team: "red-operators" },        created_at: "2026-06-16T08:30:00Z" },
  { id: 209, action: "flag_submit",      actor_username: "sqli_witch",     target: "union-jack",           details: { correct: true,  points: 200 }, created_at: "2026-06-14T14:20:00Z" },
  { id: 210, action: "deployment_start", actor_username: "r0otkit",        target: "breachsql-fire-range", details: { deployment_id: 998 },           created_at: "2026-06-14T10:00:00Z" },
];

export const DEMO_ADMIN_API_KEYS = [
  { id: 1, prefix: "oktor_Xk9mQp", name: "CI Pipeline",  user_id: 1, username: "octorig_admin", created_at: "2026-05-01T08:00:00Z", expires_at: null,                  last_used_at: "2026-06-15T04:30:00Z", is_active: true },
  { id: 2, prefix: "oktor_Rn3vJw", name: "Local Dev",    user_id: 1, username: "octorig_admin", created_at: "2026-06-01T12:00:00Z", expires_at: "2026-12-31T23:59:59Z", last_used_at: "2026-06-16T09:15:00Z", is_active: true },
  { id: 3, prefix: "oktor_Tz7pLm", name: "Monitoring",   user_id: 3, username: "r0otkit",        created_at: "2026-04-10T09:00:00Z", expires_at: null,                  last_used_at: "2026-06-16T00:05:00Z", is_active: true },
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
  updated_at: "2026-06-01T10:00:00Z",
};

// ─── Augmentation helpers (applied to real API responses) ─────────────────────

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
}>(challenge: T, index = 0): T {
  return {
    ...challenge,
    solve_count: 15 + ((challenge.id * 7 + index * 3) % 170),
    solved_by_me: index % 3 !== 0,
    first_blood_user: index % 5 === 0
      ? DEMO_USERNAMES[index % DEMO_USERNAMES.length]
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
