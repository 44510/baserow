import pytest

from baserow.core.models import WorkspaceUser
from baserow.core.notifications.exceptions import NotificationDoesNotExist
from baserow.core.notifications.handler import NotificationHandler
from baserow.core.notifications.models import Notification, NotificationRecipient


@pytest.mark.django_db
def test_get_workspace_notifications(data_fixture):
    user = data_fixture.create_user()
    workspace = data_fixture.create_workspace(user=user)

    workspace_notification = data_fixture.create_workspace_notification(
        recipients=[user], workspace=workspace, type="test_workspace_notification"
    )
    user_notification = data_fixture.create_user_notification(
        recipients=[user], type="test_user_notification"
    )

    notification_recipients = NotificationHandler.list_notifications(
        user=user, workspace=workspace
    )

    assert len(notification_recipients) == 2
    assert notification_recipients[0].notification_id == user_notification.id
    assert notification_recipients[0].notification.type == "test_user_notification"
    assert notification_recipients[1].notification_id == workspace_notification.id
    assert notification_recipients[1].notification.type == "test_workspace_notification"


@pytest.mark.django_db
def test_get_notification_by_id(data_fixture):
    user = data_fixture.create_user()
    notification = data_fixture.create_user_notification(recipients=[user])

    assert (
        NotificationHandler.get_notification_by_id(user, notification.id).id
        == notification.id
    )

    with pytest.raises(NotificationDoesNotExist):
        NotificationHandler.get_notification_by_id(user, 999)


@pytest.mark.django_db
def test_annotate_workspaces_with_unread_notifications_count(data_fixture):
    user = data_fixture.create_user()
    workspace = data_fixture.create_workspace(user=user)

    q = WorkspaceUser.objects.filter(user=user, workspace=workspace).all()
    annotated_q = (
        NotificationHandler.annotate_workspaces_with_unread_notifications_count(
            user, q, outer_ref_key="workspace_id"
        )
    )

    assert annotated_q[0].unread_notifications_count == 0

    data_fixture.create_workspace_notification(recipients=[user], workspace=workspace)

    annotated_q = (
        NotificationHandler.annotate_workspaces_with_unread_notifications_count(
            user, q, outer_ref_key="workspace_id"
        )
    )

    assert annotated_q[0].unread_notifications_count == 1


@pytest.mark.django_db
def test_get_unread_notifications_count(data_fixture):
    user = data_fixture.create_user()

    assert NotificationHandler.get_unread_notifications_count(user) == 0

    data_fixture.create_user_notification(recipients=[user])

    assert NotificationHandler.get_unread_notifications_count(user) == 1


@pytest.mark.django_db
def test_mark_notification_as_read(data_fixture):
    user = data_fixture.create_user()
    workspace = data_fixture.create_workspace(user=user)

    notification = data_fixture.create_workspace_notification(
        recipients=[user], workspace=workspace
    )

    qs = NotificationRecipient.objects.filter(recipient=user, notification=notification)
    assert qs.get().read is False

    NotificationHandler.mark_notification_as_read(user, notification)

    assert qs.get().read is True


@pytest.mark.django_db
def test_mark_all_notifications_as_read(data_fixture):
    user = data_fixture.create_user()
    workspace = data_fixture.create_workspace(user=user)

    data_fixture.create_workspace_notification(recipients=[user], workspace=workspace)
    data_fixture.create_user_notification(recipients=[user])

    assert NotificationHandler.get_unread_notifications_count(user, workspace) == 2

    NotificationHandler.mark_all_notifications_as_read(user, workspace=workspace)

    assert NotificationHandler.get_unread_notifications_count(user, workspace) == 0


@pytest.mark.django_db
def test_clear_all_direct_notifications(data_fixture):
    user = data_fixture.create_user()
    workspace = data_fixture.create_workspace(user=user)

    data_fixture.create_workspace_notification(recipients=[user], workspace=workspace)
    data_fixture.create_user_notification(recipients=[user])

    assert Notification.objects.count() == 2

    NotificationHandler.clear_all_notifications(user, workspace=workspace)

    assert Notification.objects.count() == 0


@pytest.mark.django_db
def test_clear_direct_notifications_should_delete_them(
    data_fixture,
):
    user = data_fixture.create_user()
    workspace = data_fixture.create_workspace(user=user)
    other_user = data_fixture.create_user(workspace=workspace)

    data_fixture.create_workspace_notification(
        recipients=[user, other_user], workspace=workspace
    )

    count_user_notifications = NotificationHandler.list_notifications(
        user, workspace=workspace
    ).count
    count_other_user_notifications = NotificationHandler.list_notifications(
        other_user, workspace=workspace
    ).count

    assert Notification.objects.all().count() == 1
    assert count_user_notifications() == 1
    assert count_other_user_notifications() == 1

    NotificationHandler.clear_all_notifications(user, workspace=workspace)

    assert Notification.objects.all().count() == 1
    assert count_user_notifications() == 0
    assert count_other_user_notifications() == 1

    NotificationHandler.clear_all_notifications(other_user, workspace=workspace)

    assert Notification.objects.all().count() == 0
    assert count_user_notifications() == 0
    assert count_other_user_notifications() == 0


@pytest.mark.django_db
def test_all_users_can_see_and_clear_broadcast_notifications(data_fixture):
    user = data_fixture.create_user()
    other_user = data_fixture.create_user()
    workspace = data_fixture.create_workspace(user=user)
    other_workspace = data_fixture.create_workspace(user=other_user)

    notification = data_fixture.create_broadcast_notification()

    user_notifications = NotificationHandler.list_notifications(
        user, workspace=workspace
    )
    user_unread_notifications_count = (
        lambda: NotificationHandler.get_unread_notifications_count(user)
    )
    other_user_notifications = NotificationHandler.list_notifications(
        other_user, workspace=workspace
    )
    other_user_unread_notifications_count = (
        lambda: NotificationHandler.get_unread_notifications_count(other_user)
    )

    assert Notification.objects.count() == 1
    assert user_unread_notifications_count() == 1
    assert other_user_unread_notifications_count() == 1

    NotificationHandler.mark_all_notifications_as_read(user, workspace=workspace)

    assert user_unread_notifications_count() == 0
    assert user_notifications[0].read is True

    assert other_user_unread_notifications_count() == 1
    assert other_user_notifications[0].read is False

    NotificationHandler.mark_notification_as_read(other_user, notification)

    assert other_user_unread_notifications_count() == 0

    # notifications have been read by are still there, let's clear them

    assert user_notifications.count() == 1
    assert other_user_notifications.count() == 1

    NotificationHandler.clear_all_notifications(user, workspace=workspace)

    assert user_notifications.count() == 0
    assert other_user_notifications.count() == 1

    NotificationHandler.clear_all_notifications(other_user, workspace=other_workspace)

    # broadcast notifications remain there until the notification is deleted
    assert NotificationRecipient.objects.filter(cleared=True).count() == 2
    assert Notification.objects.count() == 1

    Notification.objects.all().delete()
    assert NotificationRecipient.objects.count() == 0
