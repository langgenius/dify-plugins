import jenkins
from typing import Dict, Any

class JenkinsClient:
    def __init__(self, jenkins_url: str, username: str, api_token: str):
        """
        Initializes the Jenkins client using the python-jenkins library.
        """
        try:
            self.api_token = api_token
            self.server = jenkins.Jenkins(jenkins_url, username=username, password=api_token, timeout=10)
            # Check connection and authentication on initialization
            self.server.get_whoami()
        except jenkins.JenkinsException as e:
            # Raise a standard exception to be caught by the tool
            raise Exception(f"Failed to connect or authenticate with Jenkins: {e}")

    def get_build_info(self, job_name: str, build_number_str: str, depth: int=0) -> Dict[str, Any]:
        """Gets detailed information for a specific build."""
        try:
            build_number = int(build_number_str)
            return self.server.get_build_info(job_name, build_number, depth=depth)
        except ValueError:
            raise Exception(f"Invalid build number: '{build_number_str}'. It must be a number.")
        except jenkins.NotFoundException:
            raise Exception(f"Job '{job_name}' or build '{build_number_str}' not found.")
        except jenkins.JenkinsException as e:
            raise Exception(f"Jenkins API error getting build info: {e}")

    def get_build_log(self, job_name: str, build_number_str: str) -> str:
        """Gets the console output for a specific build."""
        try:
            build_number = int(build_number_str)
            return self.server.get_build_console_output(job_name, build_number)
        except ValueError:
            raise Exception(f"Invalid build number: '{build_number_str}'. It must be a number.")
        except jenkins.NotFoundException:
            raise Exception(f"Job '{job_name}' or build '{build_number_str}' not found.")
        except jenkins.JenkinsException as e:
            raise Exception(f"Jenkins API error getting build log: {e}")

    def trigger_build(self, job_name: str, parameters=None) -> str:
        """Triggers a build for a specific job."""
        if parameters is None:
            parameters = {}
        try:
            # The build_job method doesn't return anything on success, it raises on failure.
            id = self.server.build_job(job_name, parameters=parameters, token=self.api_token)
            return f"Build for job '{job_name}' has been successfully triggered : {id}."
        except jenkins.NotFoundException:
            raise Exception(f"Job '{job_name}' not found.")
        except jenkins.JenkinsException as e:
            raise Exception(f"Jenkins API error triggering build: {e}")