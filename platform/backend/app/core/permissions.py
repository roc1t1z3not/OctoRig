"""
RBAC permission constants and checking functions.
All functions are pure (no DB calls) — call sites must resolve memberships first.
"""
from typing import Optional

from app.models.deployment import Deployment
from app.models.team import TeamMember, TeamRole
from app.models.user import User

# ── Permission constants ────────────────────────────────────────────────────

DEPLOY_LAB = "deploy_lab"
DESTROY_LAB = "destroy_lab"
MANAGE_TEMPLATES = "manage_templates"
VIEW_LOGS = "view_logs"
MANAGE_USERS = "manage_users"
MANAGE_TEAMS = "manage_teams"
MANAGE_SETTINGS = "manage_settings"
VIEW_AUDIT_LOGS = "view_audit_logs"
INVITE_MEMBERS = "invite_members"
SCHEDULE_ACTIONS = "schedule_actions"

# ── Role ordering for comparisons ───────────────────────────────────────────

_ROLE_RANK: dict[TeamRole, int] = {
    TeamRole.VIEWER: 0,
    TeamRole.MEMBER: 1,
    TeamRole.MANAGER: 2,
    TeamRole.OWNER: 3,
}


def role_gte(membership: Optional[TeamMember], minimum: TeamRole) -> bool:
    """True if the membership role is >= the minimum required role."""
    if membership is None:
        return False
    return _ROLE_RANK[membership.role] >= _ROLE_RANK[minimum]


# ── System-level checks ──────────────────────────────────────────────────────

def is_privileged(user: User) -> bool:
    """Super admin or admin."""
    return user.is_superuser or user.is_admin


# ── Deployment checks ────────────────────────────────────────────────────────

def can_deploy(user: User, membership: Optional[TeamMember] = None) -> bool:
    if is_privileged(user):
        return True
    if membership is None:
        return True  # personal deployment
    return role_gte(membership, TeamRole.MEMBER)


def can_destroy_deployment(
    user: User,
    deployment: Deployment,
    membership: Optional[TeamMember] = None,
) -> bool:
    if is_privileged(user):
        return True
    if deployment.started_by_id == user.id:
        return True
    if deployment.team_id is not None and membership is not None:
        return role_gte(membership, TeamRole.MANAGER)
    return False


def can_view_logs(user: User, deployment: Deployment, membership: Optional[TeamMember] = None) -> bool:
    if is_privileged(user):
        return True
    if deployment.started_by_id == user.id:
        return True
    if deployment.team_id is not None and membership is not None:
        return role_gte(membership, TeamRole.VIEWER)
    if deployment.visibility == "public":
        return True
    return False


# ── Team checks ──────────────────────────────────────────────────────────────

def can_manage_team(user: User, membership: Optional[TeamMember] = None) -> bool:
    """Update name/description, manage settings."""
    if is_privileged(user):
        return True
    return role_gte(membership, TeamRole.MANAGER)


def can_delete_team(user: User, membership: Optional[TeamMember] = None) -> bool:
    if is_privileged(user):
        return True
    return role_gte(membership, TeamRole.OWNER)


def can_invite_members(user: User, membership: Optional[TeamMember] = None) -> bool:
    if is_privileged(user):
        return True
    return role_gte(membership, TeamRole.MANAGER)


def can_remove_member(user: User, membership: Optional[TeamMember] = None) -> bool:
    if is_privileged(user):
        return True
    return role_gte(membership, TeamRole.MANAGER)


def can_change_member_role(user: User, membership: Optional[TeamMember] = None) -> bool:
    if is_privileged(user):
        return True
    return role_gte(membership, TeamRole.MANAGER)


def can_transfer_ownership(user: User, membership: Optional[TeamMember] = None) -> bool:
    if is_privileged(user):
        return True
    return role_gte(membership, TeamRole.OWNER)


def can_view_team_audit(user: User, membership: Optional[TeamMember] = None) -> bool:
    if is_privileged(user):
        return True
    return role_gte(membership, TeamRole.MANAGER)


# ── Admin checks ─────────────────────────────────────────────────────────────

def can_manage_templates(user: User) -> bool:
    return is_privileged(user)


def can_manage_users(user: User) -> bool:
    return is_privileged(user)


def can_view_all_audit_logs(user: User) -> bool:
    return is_privileged(user)


def can_schedule(user: User, membership: Optional[TeamMember] = None) -> bool:
    if is_privileged(user):
        return True
    if membership is None:
        return True  # personal schedule
    return role_gte(membership, TeamRole.MEMBER)
