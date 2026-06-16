# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from .competition import COMPETITION_BADGES
from .milestone import MILESTONE_BADGES
from .skill_idor import IDOR_BADGES
from .skill_python import PYTHON_BADGES
from .skill_recon import RECON_BADGES
from .skill_sqli import SQLI_BADGES
from .skill_web import WEB_BADGES
from .skill_xss import XSS_BADGES

SEED_CATALOG = [
    *MILESTONE_BADGES,
    *COMPETITION_BADGES,
    *XSS_BADGES,
    *SQLI_BADGES,
    *IDOR_BADGES,
    *RECON_BADGES,
    *WEB_BADGES,
    *PYTHON_BADGES,
]
