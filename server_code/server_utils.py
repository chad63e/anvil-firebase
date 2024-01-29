import json
import re
import tempfile
from dataclasses import dataclass

from firebase_admin import credentials, initialize_app, messaging


@dataclass
class FCMServiceAccountCredentials:
    """
    Represents the credentials for a Firebase Cloud Messaging (FCM) service account.

    This class encapsulates the properties of an FCM service account, such as the project ID, private key, client email, etc.
    It provides methods to convert the credentials to a dictionary, get a temporary file path for the credentials, and create an instance of the class from a JSON string.

    Attributes:
        type (str): The type of the service account.
        project_id (str): The ID of the project that the service account is associated with.
        private_key_id (str): The ID of the private key for the service account.
        private_key (str): The private key for the service account.
        client_email (str): The email of the client that the service account is associated with.
        client_id (str): The ID of the client that the service account is associated with.
        auth_uri (str): The URI for authentication.
        token_uri (str): The URI for getting tokens.
        auth_provider_x509_cert_url (str): The URL of the auth provider's x509 certificate.
        client_x509_cert_url (str): The URL of the client's x509 certificate.
        universe_domain (str): The domain of the universe that the service account is associated with.
    """

    type: str
    project_id: str
    private_key_id: str
    private_key: str
    client_email: str
    client_id: str
    auth_uri: str
    token_uri: str
    auth_provider_x509_cert_url: str
    client_x509_cert_url: str
    universe_domain: str

    def to_dict(self):
        return {
            "type": self.type,
            "project_id": self.project_id,
            "private_key_id": self.private_key_id,
            "private_key": self.private_key,
            "client_email": self.client_email,
            "client_id": self.client_id,
            "auth_uri": self.auth_uri,
            "token_uri": self.token_uri,
            "auth_provider_x509_cert_url": self.auth_provider_x509_cert_url,
            "client_x509_cert_url": self.client_x509_cert_url,
            "universe_domain": self.universe_domain,
        }

    def get_temp_file_path(self) -> str:
        """
        Creates a temporary JSON file with the service account credentials and returns the file path.

        Raises:
            ValueError: If the credentials cannot be converted to a JSON string.
            Exception: If there is an error creating the temporary file.
        """
        try:
            # Create a temporary file
            temp_file = tempfile.NamedTemporaryFile(
                delete=False, mode="w", suffix=".json"
            )
            temp_file.write(json.dumps(self.to_dict()))
            temp_file.close()
            return temp_file.name
        except json.JSONDecodeError as e:
            raise ValueError("Invalid JSON string") from e
        except Exception as ex:
            raise Exception("Error creating temporary file") from ex

    @classmethod
    def from_json_string(cls, json_string) -> "FCMServiceAccountCredentials":
        """
        Creates an instance of the class from a JSON string.

        This method is particularly useful when saving the credentials in the Anvil Secrets as a string.

        Raises:
            ValueError: If the JSON string is invalid.
            Exception: If there is an error creating the instance.
        """

        try:
            # Remove all trailing commas using regex
            json_string = re.sub(r",\s*(?=}|])", "", json_string)
            json_dict = json.loads(json_string.strip())
            return cls(**json_dict)
        except json.JSONDecodeError as e:
            raise ValueError("Invalid JSON string") from e
        except Exception as ex:
            raise Exception("Error creating temporary file") from ex
