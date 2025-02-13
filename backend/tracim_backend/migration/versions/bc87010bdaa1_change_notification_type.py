"""change notification type

Revision ID: bc87010bdaa1
Revises: b7aa3b477519
Create Date: 2023-03-01 10:03:22.829583

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "bc87010bdaa1"
down_revision = "b7aa3b477519"

# Upgrade

get_notification_deactivated_query = """
select user_id, workspace_id from user_workspace where do_notify = false
"""

get_notification_activated_query = """
select user_id, workspace_id from user_workspace where do_notify = true
"""

update_email_notification_type_none = f"""
update user_workspace
set email_notification_type = 'NONE'
where (user_id, workspace_id) in ({get_notification_deactivated_query})
"""

update_email_notification_type_individual = f"""
update user_workspace
set email_notification_type = 'INDIVIDUAL'
where (user_id, workspace_id) in ({get_notification_activated_query})
"""

# Downgrade

downgrade_email_notification_type_true = """
update user_workspace
set do_notify = true
where email_notification_type != 'NONE'
"""

downgrade_email_notification_type_false = """
update user_workspace
set do_notify = false
where email_notification_type = 'NONE'
"""


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    enum = sa.Enum("INDIVIDUAL", "NONE", "SUMMARY", name="emailnotificationtype")
    enum.create(op.get_bind(), checkfirst=False)

    with op.batch_alter_table("user_workspace") as batch_op:
        batch_op.add_column(
            sa.Column("email_notification_type", enum, server_default="SUMMARY", nullable=False,)
        )

    connection = op.get_bind()
    connection.execute(update_email_notification_type_none)
    connection.execute(update_email_notification_type_individual)

    with op.batch_alter_table("user_workspace") as batch_op:
        batch_op.drop_column("do_notify")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("user_workspace") as batch_op:
        batch_op.add_column(
            sa.Column(
                "do_notify",
                sa.Boolean(),
                nullable=False,
                server_default=sa.sql.expression.literal(True),
            )
        )

    connection = op.get_bind()
    connection.execute(downgrade_email_notification_type_false)
    connection.execute(downgrade_email_notification_type_true)

    with op.batch_alter_table("user_workspace") as batch_op:
        batch_op.drop_column("email_notification_type")

    sa.Enum(name="emailnotificationtype").drop(op.get_bind(), checkfirst=False)
    # ### end Alembic commands ###
