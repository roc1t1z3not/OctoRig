from sqlalchemy.orm import Session

from app.models.site_settings import SiteSettings


def get_settings(db: Session) -> SiteSettings:
    row = db.get(SiteSettings, 1)
    if row is None:
        row = SiteSettings(id=1)
        db.add(row)
        db.commit()
        db.refresh(row)
    return row
