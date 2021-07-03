import logging
import os

from flask import Flask

from src.driver.file_driver import LocalFileDriverImpl
from src.rest.status import StatusResource
from src.rest.web import WebResource
from src.usecase.ability import AbilityInteractor
from src.usecase.character import CharacterInteractor
from src.usecase.status_interactor import StatusInteractor


class Config:
    host: str
    port: int
    root_path: str
    log_level: int
    max_content_length: int
    debug: bool

    def __init__(self):
        # default setting
        self.host = '0.0.0.0'
        self.port = int(os.environ.get('PORT', 8080))
        self.root_path = os.environ.get('ROOT_PATH', '../')
        self.log_level = logging.DEBUG
        self.max_content_length = os.environ.get(
            'MAX_CONTENT_LENGTH', 5 * 1024 * 1024)  # default is 5MB
        self.debug = os.environ.get('ENABLE_DEBUG', False)


class App:
    config: Config

    def __init__(self, config: Config):
        self.config = config

    def run(self):
        logging.basicConfig(level=self.config.log_level)

        app = Flask(
            __name__,
            static_folder=os.path.join(self.config.root_path, 'static'),
            template_folder=os.path.join(self.config.root_path, 'templates'),
        )
        app.config['MAX_CONTENT_LENGTH'] = self.config.max_content_length

        root_path = self.config.root_path

        web_resource = WebResource()
        status_resource = StatusResource(
            StatusInteractor(
                LocalFileDriverImpl(root_path),
                app.logger,
                debug=self.config.debug,
            ),
            CharacterInteractor(
                LocalFileDriverImpl(root_path),
                app.logger,
                debug=self.config.debug,
            ),
            AbilityInteractor(
                LocalFileDriverImpl(root_path),
                app.logger,
                debug=self.config.debug,
            )
        )

        app.add_url_rule('/', view_func=web_resource.as_view('web_resource'))
        app.add_url_rule(
            '/api/v1/ocr/status',
            view_func=status_resource.index,
            methods=['POST'])

        app.run(
            host=self.config.host,
            port=self.config.port,
            debug=self.config.debug,
            threaded=True,
        )
