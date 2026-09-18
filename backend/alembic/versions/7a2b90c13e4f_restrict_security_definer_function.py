"""restrict_security_definer_function

Revision ID: 7a2b90c13e4f
Revises: 6f1a89c02d3e
Create Date: 2026-09-18 11:15:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '7a2b90c13e4f'
down_revision: Union[str, Sequence[str], None] = '6f1a89c02d3e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name
    if dialect != "postgresql":
        return

    # 1. Revoke public/anon execute on get_user_business_ids()
    op.execute("""
    REVOKE EXECUTE ON FUNCTION public.get_user_business_ids() FROM PUBLIC;
    REVOKE EXECUTE ON FUNCTION public.get_user_business_ids() FROM anon;
    """)

    # 2. Grant execute strictly to authenticated and service_role for RLS evaluation
    op.execute("""
    GRANT EXECUTE ON FUNCTION public.get_user_business_ids() TO authenticated;
    GRANT EXECUTE ON FUNCTION public.get_user_business_ids() TO service_role;
    """)


def downgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name
    if dialect != "postgresql":
        return

    op.execute("""
    GRANT EXECUTE ON FUNCTION public.get_user_business_ids() TO PUBLIC;
    """)
