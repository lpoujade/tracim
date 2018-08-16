import os

from pyramid.renderers import render_to_response
from pyramid.config import Configurator
from tracim_backend.extensions import APP_LIST
from tracim_backend.exceptions import PageNotFound
from tracim_backend.lib.core.application import ApplicationApi
from tracim_backend.lib.utils.utils import Color
from tracim_backend.views import BASE_API_V2
from tracim_backend.lib.utils.request import TracimRequest
from tracim_backend.views.controllers import Controller

INDEX_PAGE_NAME = 'index.mak'
APP_FRONTEND_PATH = 'app/{minislug}.app.js'


class FrontendController(Controller):

    def __init__(self, dist_folder_path: str):
        self.dist_folder_path = dist_folder_path

    def _get_index_file_path(self):
        index_file_path = os.path.join(self.dist_folder_path, INDEX_PAGE_NAME)
        if not os.path.exists(index_file_path):
            raise FileNotFoundError()
        return index_file_path

    def not_found_view(self, context, request: TracimRequest):

        if request.path.startswith(BASE_API_V2):
            raise PageNotFound('{} is not a valid path'.format(request.path)) from context  # nopep8
        return self.index(context, request)

    def index(self, context, request: TracimRequest):
        app_config = request.registry.settings['CFG']
        # TODO - G.M - 2018-08-07 - Refactor autogen valid app list for frontend
        frontend_apps = []
        app_api = ApplicationApi(
            app_list=APP_LIST,
        )
        applications = app_api.get_all()
        for app in applications:
            app_frontend_path = APP_FRONTEND_PATH.replace('{minislug}',
                                                          app.minislug)  # nopep8
            app_path = os.path.join(self.dist_folder_path,
                                    app_frontend_path)  # nopep8
            if os.path.exists(app_path):
                frontend_apps.append(app)

        return render_to_response(
            self._get_index_file_path(),
            {
                'colors': {
                    'primary': Color(app_config.APPS_COLORS['primary']),
                },
                'applications': frontend_apps,
            }
        )

    def bind(self, configurator: Configurator) -> None:

        configurator.add_notfound_view(self.not_found_view)
        # index.html for /index.html and /
        configurator.add_route('root', '/', request_method='GET')
        configurator.add_view(self.index, route_name='root')
        configurator.add_route('index', INDEX_PAGE_NAME, request_method='GET')
        configurator.add_view(self.index, route_name='index')

        for dirname in os.listdir(self.dist_folder_path):
            configurator.add_static_view(
                name=dirname,
                path=os.path.join(self.dist_folder_path, dirname)
            )
