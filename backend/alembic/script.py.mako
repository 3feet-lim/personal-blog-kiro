"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# 리비전 식별자 (Alembic에서 자동 관리)
revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    """마이그레이션 적용 (업그레이드)"""
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    """마이그레이션 롤백 (다운그레이드)"""
    ${downgrades if downgrades else "pass"}
