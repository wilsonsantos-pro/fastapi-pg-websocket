"""Add listener trigger

Revision ID: e35eea0aa748
Revises: f9d9bb3a854f
Create Date: 2025-05-31 16:27:27.869896

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e35eea0aa748"
down_revision: Union[str, None] = "f9d9bb3a854f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        -- 1. Define the function
        CREATE OR REPLACE FUNCTION notify_status_change() RETURNS trigger AS $$
        BEGIN
        IF NEW.status IS DISTINCT FROM OLD.status THEN
            PERFORM pg_notify('status_channel', row_to_json(NEW)::text);
        END IF;
        RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        -- 2. Create the trigger
        DROP TRIGGER IF EXISTS status_change_trigger ON users;

        CREATE TRIGGER status_change_trigger
        AFTER UPDATE ON users
        FOR EACH ROW
        WHEN (OLD.status IS DISTINCT FROM NEW.status)
        EXECUTE FUNCTION notify_status_change();
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        """
        DROP FUNCTION IF EXISTS notify_status_change CASCADE;
        """
    )
