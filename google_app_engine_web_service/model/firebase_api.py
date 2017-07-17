try:
    from functools import lru_cache
except ImportError:
    from functools32 import lru_cache
# [START rest_writing_data]
import json
import httplib2
from oauth2client.client import GoogleCredentials
import logging

logger = logging.getLogger('')

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

@lru_cache()
def _get_http():
    """Provides an authed http object."""
    http = httplib2.Http()
    # Use application default credentials to make the Firebase calls
    # https://firebase.google.com/docs/reference/rest/database/user-auth
    creds = GoogleCredentials.get_application_default().create_scoped(
        _FIREBASE_SCOPES)
    creds.authorize(http)
    return http


def firebase_put(path, value=None):
    """Writes data to Firebase.
    An HTTP PUT writes an entire object at the given database path. Updates to
    fields cannot be performed without overwriting the entire object
    Args:
        path - the url to the Firebase object to write.
        value - a json string.
    """
    response, content = _get_http().request(path, method='PUT', body=value)
    logger.info(content)
    return json.loads(content)

def firebase_patch(path, value=None):
    """Update specific children or fields
    An HTTP PATCH allows specific children or fields to be updated without
    overwriting the entire object.
    Args:
        path - the url to the Firebase object to write.
        value - a json string.
    """
    response, content = _get_http().request(path, method='PATCH', body=value)
    logger.debug(content)
    return json.loads(content)

def firebase_get(path):
    """Read the data at the given path.
    An HTTP GET request allows reading of data at a particular path.
    A successful request will be indicated by a 200 OK HTTP status code.
    The response will contain the data being retrieved.
    Args:
        path - the url to the Firebase object to read.
    """
    response, content = _get_http().request(path, method='GET')
    logger.debug(content)
    return json.loads(content)
