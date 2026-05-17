"""add queue schema and user tier fields

Revision ID: e9f1c2d4a6b7
Revises: d4b8f3e91a22
Create Date: 2026-03-22 20:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e9f1c2d4a6b7"
down_revision: Union[str, None] = "d4b8f3e91a22"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_names(inspector) -> set[str]:
    return set(inspector.get_table_names())


def _column_names(inspector, table_name: str) -> set[str]:
    return {column["name"] for column in inspector.get_columns(table_name)}


def _index_names(inspector, table_name: str) -> set[str]:
    return {index["name"] for index in inspector.get_indexes(table_name)}


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_names = _table_names(inspector)

    if "users" in table_names:
        user_columns = _column_names(inspector, "users")
        with op.batch_alter_table("users") as batch_op:
            if "quality_tier" not in user_columns:
                batch_op.add_column(
                    sa.Column("quality_tier", sa.String(length=32), nullable=True, server_default="FREE")
                )
            if "watermark_enabled" not in user_columns:
                batch_op.add_column(
                    sa.Column("watermark_enabled", sa.Boolean(), nullable=True, server_default=sa.text("1"))
                )
        op.execute("UPDATE users SET quality_tier = 'FREE' WHERE quality_tier IS NULL")
        op.execute("UPDATE users SET watermark_enabled = 1 WHERE watermark_enabled IS NULL")

    if "jobs" not in table_names:
        op.create_table(
            "jobs",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("status", sa.String(), nullable=True, server_default="queued"),
            sa.Column("progress", sa.Integer(), nullable=True, server_default="0"),
            sa.Column("request_payload", sa.Text(), nullable=True),
            sa.Column("attempt_count", sa.Integer(), nullable=True, server_default="0"),
            sa.Column("worker_id", sa.String(), nullable=True),
            sa.Column("claimed_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("lease_expires_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("video_path", sa.String(), nullable=True),
            sa.Column("video_url", sa.String(), nullable=True),
            sa.Column("plan_path", sa.String(), nullable=True),
            sa.Column("plan_url", sa.String(), nullable=True),
            sa.Column("log_path", sa.String(), nullable=True),
            sa.Column("log_url", sa.String(), nullable=True),
            sa.Column("out_dir", sa.String(), nullable=True),
            sa.Column("log", sa.Text(), nullable=True, server_default=""),
            sa.Column("user_id", sa.Integer(), nullable=True),
            sa.Column("idempotency_key", sa.String(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=True, server_default=sa.text("(CURRENT_TIMESTAMP)")),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True, server_default=sa.text("(CURRENT_TIMESTAMP)")),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_jobs_created_at"), "jobs", ["created_at"], unique=False)
        op.create_index(op.f("ix_jobs_id"), "jobs", ["id"], unique=False)
        op.create_index(op.f("ix_jobs_idempotency_key"), "jobs", ["idempotency_key"], unique=True)
        op.create_index(op.f("ix_jobs_status"), "jobs", ["status"], unique=False)
    else:
        job_columns = _column_names(inspector, "jobs")
        with op.batch_alter_table("jobs") as batch_op:
            if "status" not in job_columns:
                batch_op.add_column(sa.Column("status", sa.String(), nullable=True, server_default="queued"))
            if "progress" not in job_columns:
                batch_op.add_column(sa.Column("progress", sa.Integer(), nullable=True, server_default="0"))
            if "request_payload" not in job_columns:
                batch_op.add_column(sa.Column("request_payload", sa.Text(), nullable=True))
            if "attempt_count" not in job_columns:
                batch_op.add_column(sa.Column("attempt_count", sa.Integer(), nullable=True, server_default="0"))
            if "worker_id" not in job_columns:
                batch_op.add_column(sa.Column("worker_id", sa.String(), nullable=True))
            if "claimed_at" not in job_columns:
                batch_op.add_column(sa.Column("claimed_at", sa.DateTime(timezone=True), nullable=True))
            if "started_at" not in job_columns:
                batch_op.add_column(sa.Column("started_at", sa.DateTime(timezone=True), nullable=True))
            if "finished_at" not in job_columns:
                batch_op.add_column(sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True))
            if "lease_expires_at" not in job_columns:
                batch_op.add_column(sa.Column("lease_expires_at", sa.DateTime(timezone=True), nullable=True))
            if "video_path" not in job_columns:
                batch_op.add_column(sa.Column("video_path", sa.String(), nullable=True))
            if "video_url" not in job_columns:
                batch_op.add_column(sa.Column("video_url", sa.String(), nullable=True))
            if "plan_path" not in job_columns:
                batch_op.add_column(sa.Column("plan_path", sa.String(), nullable=True))
            if "plan_url" not in job_columns:
                batch_op.add_column(sa.Column("plan_url", sa.String(), nullable=True))
            if "log_path" not in job_columns:
                batch_op.add_column(sa.Column("log_path", sa.String(), nullable=True))
            if "log_url" not in job_columns:
                batch_op.add_column(sa.Column("log_url", sa.String(), nullable=True))
            if "out_dir" not in job_columns:
                batch_op.add_column(sa.Column("out_dir", sa.String(), nullable=True))
            if "log" not in job_columns:
                batch_op.add_column(sa.Column("log", sa.Text(), nullable=True, server_default=""))
            if "user_id" not in job_columns:
                batch_op.add_column(sa.Column("user_id", sa.Integer(), nullable=True))
            if "idempotency_key" not in job_columns:
                batch_op.add_column(sa.Column("idempotency_key", sa.String(), nullable=True))
            if "created_at" not in job_columns:
                batch_op.add_column(
                    sa.Column("created_at", sa.DateTime(timezone=True), nullable=True, server_default=sa.text("(CURRENT_TIMESTAMP)"))
                )
            if "updated_at" not in job_columns:
                batch_op.add_column(
                    sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True, server_default=sa.text("(CURRENT_TIMESTAMP)"))
                )

        op.execute("UPDATE jobs SET attempt_count = 0 WHERE attempt_count IS NULL")

        index_names = _index_names(sa.inspect(bind), "jobs")
        if op.f("ix_jobs_created_at") not in index_names:
            op.create_index(op.f("ix_jobs_created_at"), "jobs", ["created_at"], unique=False)
        if op.f("ix_jobs_id") not in index_names:
            op.create_index(op.f("ix_jobs_id"), "jobs", ["id"], unique=False)
        if op.f("ix_jobs_idempotency_key") not in index_names:
            op.create_index(op.f("ix_jobs_idempotency_key"), "jobs", ["idempotency_key"], unique=True)
        if op.f("ix_jobs_status") not in index_names:
            op.create_index(op.f("ix_jobs_status"), "jobs", ["status"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_names = _table_names(inspector)

    if "jobs" in table_names:
        index_names = _index_names(inspector, "jobs")
        if op.f("ix_jobs_status") in index_names:
            op.drop_index(op.f("ix_jobs_status"), table_name="jobs")
        if op.f("ix_jobs_idempotency_key") in index_names:
            op.drop_index(op.f("ix_jobs_idempotency_key"), table_name="jobs")
        if op.f("ix_jobs_id") in index_names:
            op.drop_index(op.f("ix_jobs_id"), table_name="jobs")
        if op.f("ix_jobs_created_at") in index_names:
            op.drop_index(op.f("ix_jobs_created_at"), table_name="jobs")

        job_columns = _column_names(sa.inspect(bind), "jobs")
        with op.batch_alter_table("jobs") as batch_op:
            for column_name in [
                "request_payload",
                "attempt_count",
                "worker_id",
                "claimed_at",
                "started_at",
                "finished_at",
                "lease_expires_at",
            ]:
                if column_name in job_columns:
                    batch_op.drop_column(column_name)

    if "users" in table_names:
        user_columns = _column_names(sa.inspect(bind), "users")
        with op.batch_alter_table("users") as batch_op:
            if "watermark_enabled" in user_columns:
                batch_op.drop_column("watermark_enabled")
            if "quality_tier" in user_columns:
                batch_op.drop_column("quality_tier")
