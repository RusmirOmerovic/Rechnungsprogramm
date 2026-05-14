from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from invoice_app.database.base import Base


class AppSettings(Base):
    __tablename__ = "app_settings"

    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[str] = mapped_column(String(1000), nullable=False)
