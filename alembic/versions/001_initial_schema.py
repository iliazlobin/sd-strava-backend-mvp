"""Initial schema — all 5 tables for Strava MVP.

Revision ID: 001
Revises: None
Create Date: 2025-06-25
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users
    op.create_table(
        "users",
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("display_name", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    # Activities
    op.create_table(
        "activities",
        sa.Column(
            "activity_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.user_id"),
            nullable=False,
        ),
        sa.Column(
            "sport_type",
            sa.String(10),
            nullable=False,
        ),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("elapsed_time", sa.Integer(), nullable=False),
        sa.Column("distance_m", sa.Float(), nullable=False),
        sa.Column(
            "elevation_gain_m",
            sa.Float(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column("polyline", postgresql.JSONB(), nullable=False),
        sa.Column(
            "visibility",
            sa.String(10),
            nullable=False,
            server_default=sa.text("'everyone'"),
        ),
        sa.Column(
            "kudos_count",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_check_constraint(
        "ck_activities_sport_type",
        "activities",
        "sport_type IN ('run','ride','swim','hike','walk','other')",
    )
    op.create_check_constraint(
        "ck_activities_elapsed_time",
        "activities",
        "elapsed_time > 0",
    )
    op.create_check_constraint(
        "ck_activities_distance_m",
        "activities",
        "distance_m >= 0",
    )
    op.create_check_constraint(
        "ck_activities_elevation_gain_m",
        "activities",
        "elevation_gain_m >= 0",
    )
    op.create_check_constraint(
        "ck_activities_visibility",
        "activities",
        "visibility IN ('everyone','followers','only_me')",
    )
    op.create_index(
        "idx_activities_user_created",
        "activities",
        ["user_id", sa.text("created_at DESC")],
    )

    # Segments
    op.create_table(
        "segments",
        sa.Column(
            "segment_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("polyline", postgresql.JSONB(), nullable=False),
        sa.Column("distance_m", sa.Float(), nullable=False),
        sa.Column(
            "total_efforts",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_check_constraint(
        "ck_segments_distance_m",
        "segments",
        "distance_m >= 0",
    )

    # Segment Efforts
    op.create_table(
        "segment_efforts",
        sa.Column(
            "effort_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "segment_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("segments.segment_id"),
            nullable=False,
        ),
        sa.Column(
            "activity_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("activities.activity_id"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.user_id"),
            nullable=False,
        ),
        sa.Column("elapsed_time", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint(
            "activity_id", "segment_id", name="uq_efforts_activity_segment"
        ),
    )
    op.create_check_constraint(
        "ck_efforts_elapsed_time",
        "segment_efforts",
        "elapsed_time > 0",
    )
    op.create_index(
        "idx_efforts_leaderboard",
        "segment_efforts",
        ["segment_id", sa.text("elapsed_time ASC"), sa.text("effort_id ASC")],
    )

    # Kudos
    op.create_table(
        "kudos",
        sa.Column(
            "activity_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("activities.activity_id"),
            primary_key=True,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.user_id"),
            primary_key=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )


def downgrade() -> None:
    op.drop_table("kudos")
    op.drop_table("segment_efforts")
    op.drop_table("segments")
    op.drop_table("activities")
    op.drop_table("users")
