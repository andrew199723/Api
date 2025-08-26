from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Provider(Base):
	__tablename__ = "providers"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
	name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
	enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
	method: Mapped[str] = mapped_column(String(10), default="GET", nullable=False)
	url_template: Mapped[str] = mapped_column(String(1000), nullable=False)
	headers_json: Mapped[str | None] = mapped_column(String(4000), nullable=True)
	jmespath_expr: Mapped[str | None] = mapped_column(String(2000), nullable=True)
	timeout_seconds: Mapped[int] = mapped_column(Integer, default=10, nullable=False)