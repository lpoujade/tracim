# -*- coding: utf-8 -*-
from tracim import model
from tracim.fixtures import Fixture
from tracim.fixtures.users_and_groups import Test
from tracim.lib.content import ContentApi
from tracim.lib.userworkspace import RoleApi
from tracim.lib.workspace import WorkspaceApi
from tracim.model.data import ContentType
from tracim.model.data import UserRoleInWorkspace


class Content(Fixture):
    require = [Test]

    def insert(self):
        admin = self._session.query(model.User) \
            .filter(model.User.email == 'admin@admin.admin') \
            .one()
        bob = self._session.query(model.User) \
            .filter(model.User.email == 'bob@fsf.local') \
            .one()
        workspace_api = WorkspaceApi(admin)
        content_api = ContentApi(admin)
        role_api = RoleApi(admin)

        # Workspaces
        w1 = workspace_api.create_workspace('w1', save_now=True)
        w2 = workspace_api.create_workspace('w2', save_now=True)
        w3 = workspace_api.create_workspace('w3', save_now=True)

        # Workspaces roles
        role_api.create_one(
            user=bob,
            workspace=w1,
            role_level=UserRoleInWorkspace.CONTENT_MANAGER,
            with_notif=False,
        )
        role_api.create_one(
            user=bob,
            workspace=w2,
            role_level=UserRoleInWorkspace.CONTENT_MANAGER,
            with_notif=False,
        )

        w1f1 = content_api.create(
            content_type=ContentType.Folder,
            workspace=w1,
            label='w1f1',
            do_save=True,
        )
        w1f2 = content_api.create(
            content_type=ContentType.Folder,
            workspace=w1,
            label='w1f2',
            do_save=True,
        )

        # Folders
        w2f1 = content_api.create(
            content_type=ContentType.Folder,
            workspace=w2,
            label='w1f1',
            do_save=True,
        )
        w2f2 = content_api.create(
            content_type=ContentType.Folder,
            workspace=w2,
            label='w2f2',
            do_save=True,
        )

        w3f1 = content_api.create(
            content_type=ContentType.Folder,
            workspace=w3,
            label='w3f3',
            do_save=True,
        )

        # Pages, threads, ..
        w1f1p1 = content_api.create(
            content_type=ContentType.Page,
            workspace=w1,
            parent=w1f1,
            label='w1f1p1',
            do_save=True,
        )
        w1f1t1 = content_api.create(
            content_type=ContentType.Thread,
            workspace=w1,
            parent=w1f1,
            label='w1f1t1',
            do_save=False,
        )
        w1f1t1.description = 'w1f1t1 description'
        self._session.add(w1f1t1)
        w1f1d1 = content_api.create(
            content_type=ContentType.File,
            workspace=w1,
            parent=w1f1,
            label='w1f1d1',
            do_save=False,
        )
        w1f1d1.file_extension = '.txt'
        w1f1d1.file_content = b'w1f1d1 content'
        self._session.add(w1f1d1)

        w2f1p1 = content_api.create(
            content_type=ContentType.Page,
            workspace=w2,
            parent=w2f1,
            label='w2f1p1',
            do_save=True,
        )
        self._session.flush()
