from typing import NotRequired, TypedDict


class FlagDef(TypedDict):
    value: str
    flag_type: str          # "static" | "dynamic" | "regex"
    case_sensitive: bool


class HintDef(TypedDict):
    order_num: int
    content: str
    cost: int               # 0 = free hint


class ChallengeDef(TypedDict):
    slug: str
    title: str
    description: str
    challenge_type: str     # "flag" | "short_answer" | "web" | "container" etc.
    difficulty: str         # "easy" | "medium" | "hard" | "insane"
    category: str
    tags: list[str]
    skills: list[str]
    points: int
    flags: list[FlagDef]
    hints: NotRequired[list[HintDef]]
    content: NotRequired[dict]  # type-specific extra data (code_snippet, language, etc.)


class LabDefinition(TypedDict):
    id: int
    slug: str
    name: str
    description: str
    category: str           # "world" | "firerange" | "thirdparty"
    container_names: list[str]
    images: dict[str, str]  # role → image tag
    build_contexts: dict[str, str]  # role → path relative to OctoRig repo root
    start_order: list[str]  # roles in the order containers must start
    network_name: str
    subnet: str
    app_ip: str
    exposed_ports: dict[str, int]   # service name → port number
    access_info: list[dict[str, str]]  # [{"key": "URL", "value": "..."}]
    volume_names: list[str]
    env_vars: dict[str, str]
    requires_privileged: bool
    challenges: NotRequired[list[ChallengeDef]]
