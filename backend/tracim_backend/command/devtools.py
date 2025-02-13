import argparse
import json

from pyramid.scripting import AppEnvironment

from tracim_backend.command import AppContextCommand
from tracim_backend.config import CFG
from tracim_backend.config import ConfigParam
from tracim_backend.lib.core.live_messages import LiveMessagesLib
from tracim_backend.lib.core.user_custom_properties import UserCustomPropertiesApi
from tracim_backend.lib.mail_notifier.sender import EmailSender
from tracim_backend.lib.mail_notifier.utils import EmailAddress
from tracim_backend.lib.mail_notifier.utils import EmailNotificationMessage
from tracim_backend.lib.mail_notifier.utils import SmtpConfiguration
from tracim_backend.lib.utils.utils import CustomPropertiesValidator


class ParametersListCommand(AppContextCommand):
    def get_description(self) -> str:
        return (
            "list of all parameters available for tracim (in DEFAULT section of config file) excluding"
            "radicale config"
        )

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "--template",
            help="template used for parameters list print",
            dest="template",
            required=False,
            default="|{env_var_name: <30}|{config_file_name: <30}|{config_name: <30}|",
        )
        return parser

    def take_app_action(self, parsed_args: argparse.Namespace, app_context: AppEnvironment) -> None:
        # TODO - G.M - 05-04-2018 -Refactor this in order
        # to not setup object var outside of __init__ .
        self._session = app_context["request"].dbsession
        self._app_config = app_context["registry"].settings["CFG"]  # type: CFG
        print(
            parsed_args.template.format(
                config_name="<config_name>",
                config_file_name="<config_file_name>",
                env_var_name="<env_var_name>",
            )
        )
        for config in self._app_config.config_info:
            print(
                parsed_args.template.format(
                    config_name=config.config_name,
                    config_file_name=config.config_file_name,
                    env_var_name=config.env_var_name,
                )
            )


class ParametersValueCommand(AppContextCommand):
    def get_description(self) -> str:
        return "get applied value of parameter with current context"

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "-n",
            "--name",
            help="parameter name: env_var_name,config_file_name and config_name syntax allowed",
            dest="parameter_name",
            required=False,
        )
        parser.add_argument(
            "--template",
            help="template used for parameters value print, not compatible with raw mode",
            dest="template",
            required=False,
            default="|{config_name: <30}| {config_value: <50}|",
        )
        parser.add_argument(
            "-r",
            "--raw-mode",
            help="return only parameter name",
            dest="raw",
            default=False,
            action="store_true",
        )
        parser.add_argument(
            "-f",
            "--full-information_mode",
            help="return most information possible, replace default template",
            dest="full",
            default=False,
            action="store_true",
        )

        parser.add_argument(
            "--show-deprecated",
            help="return also deprecated parameters",
            dest="show_deprecated",
            default=False,
            action="store_true",
        )
        parser.add_argument(
            "--show-secret",
            help="return secret value",
            dest="show_secret",
            default=False,
            action="store_true",
        )
        return parser

    def take_app_action(self, parsed_args: argparse.Namespace, app_context: AppEnvironment) -> None:
        # TODO - G.M - 05-04-2018 -Refactor this in order
        # to not setup object var outside of __init__ .
        self._session = app_context["request"].dbsession
        self._app_config = app_context["registry"].settings["CFG"]  # type: CFG
        if parsed_args.full:
            parsed_args.template = "|{config_name}|{config_value}|{default_value}|{secret}|{config_source}|{config_file_name}|{config_file_value}|{config_env_var_name}|{config_env_var_value}|{deprecated}|"
        if not parsed_args.raw:
            print(
                parsed_args.template.format(
                    config_name="<config_name>",
                    config_value="<config_value>",
                    default_value="<default_value>",
                    secret="<secret>",
                    config_source="<config_source>",
                    config_file_name="<config_file_name>",
                    config_file_value="<config_file_value>",
                    config_env_var_name="<config_env_var_name>",
                    config_env_var_value="<config_env_var_value>",
                    deprecated="<deprecated>",
                )
            )
        for config_param in self._app_config.config_info:
            # INFO - G.M - 2020-04-17 - filter deprecated parameters
            if config_param.deprecated and not parsed_args.show_deprecated:
                continue
            if parsed_args.show_secret:
                config_param.show_secret = True
            if parsed_args.parameter_name:
                if parsed_args.parameter_name in [
                    config_param.config_name,
                    config_param.config_file_name,
                    config_param.env_var_name,
                ]:
                    self.print_config_parameter(config_param=config_param, parsed_args=parsed_args)
            else:
                self.print_config_parameter(config_param=config_param, parsed_args=parsed_args)

    def print_config_parameter(self, parsed_args: argparse.Namespace, config_param: ConfigParam):
        if parsed_args.raw:
            print(config_param.config_value, end="")
        else:
            print(
                parsed_args.template.format(
                    config_name=config_param.config_name,
                    config_value=str(config_param.config_value),
                    default_value=str(config_param.default_value),
                    secret=str(config_param.secret),
                    config_source=config_param.config_source,
                    config_file_name=config_param.config_file_name,
                    config_file_value=str(config_param.config_file_value),
                    config_env_var_name=config_param.env_var_name,
                    config_env_var_value=str(config_param.env_var_value),
                    deprecated=config_param.deprecated,
                )
            )


class LiveMessageTesterCommand(AppContextCommand):
    def get_description(self) -> str:
        return "send test live messages for testing"

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "-u", "--user_id", help="id of the user to test", dest="user_id", required=True,
        )
        return parser

    def take_app_action(self, parsed_args: argparse.Namespace, app_context: AppEnvironment) -> None:
        # TODO - G.M - 05-04-2018 -Refactor this in order
        # to not setup object var outside of __init__ .
        self._session = app_context["request"].dbsession
        self._app_config = app_context["registry"].settings["CFG"]  # type: CFG
        live_messages_lib = LiveMessagesLib(self._app_config)
        # TODO - G.M - 07-05-2020 - Should be a real tracim_message instead of dict
        test_message = {
            "event_id": -1,
            "event_type": "test",
        }
        live_messages_lib.publish_dict(
            "user_{}".format(parsed_args.user_id), message_as_dict=test_message
        )
        print("test message (id=-1) send to user {}".format(parsed_args.user_id))


class SMTPMailCheckerCommand(AppContextCommand):
    """ Check SMTP configuration by sending test email to given email address"""

    def get_description(self) -> str:
        return "check tracim smtp configuration by sending test email"

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "-r",
            "--receiver",
            help="email of the test mail receiver",
            dest="receiver",
            required=True,
        )
        return parser

    def take_app_action(self, parsed_args: argparse.Namespace, app_context: AppEnvironment) -> None:
        # TODO - G.M - 05-04-2018 -Refactor this in order
        # to not setup object var outside of __init__ .
        self._session = app_context["request"].dbsession
        self._app_config = app_context["registry"].settings["CFG"]  # type: CFG

        if not self._app_config.EMAIL__NOTIFICATION__ACTIVATED:
            print("Email notification are disabled")
            return
        smtp_config = SmtpConfiguration(
            self._app_config.EMAIL__NOTIFICATION__SMTP__SERVER,
            self._app_config.EMAIL__NOTIFICATION__SMTP__PORT,
            self._app_config.EMAIL__NOTIFICATION__SMTP__USER,
            self._app_config.EMAIL__NOTIFICATION__SMTP__PASSWORD,
            self._app_config.EMAIL__NOTIFICATION__SMTP__ENCRYPTION,
            self._app_config.EMAIL__NOTIFICATION__SMTP__AUTHENTICATION,
        )
        sender = EmailSender(self._app_config, smtp_config, True)
        html = """\
        <html>
          <head></head>
          <body>
            <p>This is just a test email from Tracim</p>
          </body>
        </html>
        """

        msg = EmailNotificationMessage(
            subject="Test Email from Tracim",
            from_header=EmailAddress("", self._app_config.EMAIL__NOTIFICATION__FROM__EMAIL),
            to_header=EmailAddress("", parsed_args.receiver),
            reply_to=EmailAddress("", self._app_config.EMAIL__NOTIFICATION__FROM__EMAIL),
            references=EmailAddress("", "references-test@localhost"),
            lang="en",
            body_html=html,
        )
        sender.send_mail(msg)
        sender.disconnect()
        print("Email sent")


class ExtractCustomPropertiesTranslationsCommand(AppContextCommand):
    """
    Tool to generate a json usable as template for translation of loaded user custom properties
    """

    def get_description(self) -> str:
        return "create translation template for user custom properties"

    def take_app_action(self, parsed_args: argparse.Namespace, app_context: AppEnvironment) -> None:
        # TODO - G.M - 05-04-2018 -Refactor this in order
        # to not setup object var outside of __init__ .
        self._session = app_context["request"].dbsession
        self._app_config = app_context["registry"].settings["CFG"]  # type: CFG
        custom_properties_api = UserCustomPropertiesApi(
            current_user=None, app_config=self._app_config, session=self._session
        )
        print(json.dumps(custom_properties_api.get_translation_template()))


class CustomPropertiesCheckerCommand(AppContextCommand):
    """
    Tool to validate custom properties
    """

    auto_setup_context = False

    def get_description(self) -> str:
        return "Check custom properties"

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "-s", "--json-schema", help="path of the json schema", dest="json_schema",
        )
        parser.add_argument(
            "-u", "--ui-schema", help="path of the ui schema", dest="ui_schema",
        )
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        super(CustomPropertiesCheckerCommand, self).take_action(parsed_args)
        custom_propertie_validator = CustomPropertiesValidator()
        if not parsed_args.json_schema and not parsed_args.ui_schema:
            print("No schema provided, skip checking.")
            return
        if parsed_args.json_schema:
            print("Checking json schema at {}".format(parsed_args.json_schema))
            json_content = custom_propertie_validator.validate_valid_json_file(
                parsed_args.json_schema
            )
            custom_propertie_validator.validate_json_schema(json_content)
        if parsed_args.ui_schema:
            print("Checking ui schema at {}".format(parsed_args.ui_schema))
            json_content = custom_propertie_validator.validate_valid_json_file(
                parsed_args.ui_schema
            )
        print("Schema validated without any issues")
