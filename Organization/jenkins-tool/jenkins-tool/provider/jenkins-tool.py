import logging

import jenkins
import requests  # We must import requests to catch its specific exceptions
from dify_plugin import ToolProvider
from dify_plugin.config.logger_format import plugin_logger_handler
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(plugin_logger_handler)

class JenkinsToolProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, str]) -> None:
        """
        Validates the Jenkins credentials by using the python-jenkins library
        and correctly handling the underlying requests exceptions.
        """
        jenkins_url = credentials.get("jenkins_url", "").rstrip('/')
        username = credentials.get("username", "")
        api_token = credentials.get("api_token", "")

        if not all([jenkins_url, username, api_token]):
            raise ToolProviderCredentialValidationError("All fields (Jenkins URL, Username, API Token) are required.")

        try:
            # Instantiate the server object
            server = jenkins.Jenkins(jenkins_url, username=username, password=api_token, timeout=10)

            # get_whoami() will trigger the underlying HTTP request
            server.get_whoami()
            logger.info(f"Successfully authenticated with Jenkins at {jenkins_url}")

        except requests.exceptions.HTTPError as e:
            if e.response.status_code in [401, 403]:
                error_message = (
                    f"Authentication failed ({e.response.status_code}). This can be due to incorrect credentials "
                    "or Jenkins CSRF Protection. If credentials are correct, try disabling 'Prevent "
                    "Cross Site Request Forgery exploits' in Jenkins > Configure Global Security."
                )
                raise ToolProviderCredentialValidationError(error_message)
            else:
                raise ToolProviderCredentialValidationError(
                    f"HTTP error connecting to Jenkins: {e.response.status_code} {e.response.reason}")

        # Then, catch the general JenkinsException for other issues (e.g., bad URL format, connection timeout)
        except jenkins.JenkinsException as e:
            raise ToolProviderCredentialValidationError(
                f"Failed to connect to Jenkins. Please check the URL and network. Error: {e}")

        # Finally, catch any other unexpected errors
        except Exception as e:
            raise ToolProviderCredentialValidationError(f"An unexpected error occurred: {e}")

        # If no exceptions were raised, the validation is successful
        return

