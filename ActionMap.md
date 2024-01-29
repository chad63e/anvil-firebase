# ActionMap

## Table of Contents
- [**Class Description**](#class-description)
- [**Constructor**](#constructor)
- [**Public Methods**](#public-methods)
- [**Private Methods**](#private-methods)
- [**Code Examples**](#code-examples)

## Class Description
`ActionMap` is a class designed to map an action name to an endpoint or a full URL along with additional details such as parameters, data, and authorization information. It provides a simple way to register Notification Actions that can either open webpages or make POST requests to APIs, without the need for custom coding a Service Worker. 

This is particularly useful in scenarios where actions need to be dynamically linked to different API endpoints or URLs. However, if additional actions beyond opening webpages or making POST requests are required, a custom Service Worker will be needed.

## Constructor
#### `__init__(self, action_name, endpoint=None, full_url=None, params=None, data=None, auth_key=None, is_api_endpoint=False)`
Initializes a new instance of the `ActionMap` class.

#### Parameters:
- `action_name (str)`: The name of the action.
- `endpoint (str, optional)`: The endpoint for the action.
- `full_url (str, optional)`: The full URL for the action.
- `params (dict, optional)`: Parameters for the URL (if not an API endpoint).
- `data (dict, optional)`: Data for the POST request body (if an API endpoint).
- `auth_key (str, optional)`: Authorization token (if an API endpoint).
- `is_api_endpoint (bool, optional)`: Indicates if the URL is an API endpoint.

## Public Methods
#### Property: `full_url`
- Getter: Returns the full URL if set; otherwise, constructs a full URL from the provided endpoint. This construction is derived from your application's origin and the specified endpoint. If `is_api_endpoint` is set to `True`, it will utilize `anvil.server.get_api_origin()`. Conversely, if it's set to `False`, it will use `anvil.server.get_app_origin()`. If a `full_url` and `endpoint` are both provided, the `full_url` will be returned.
- Setter: Sets the `full_url` attribute.

## Code Examples
### Example 1: Creating an ActionMap Instance
```python
from Firebase.client import ActionMap


action_map = ActionMap(
    action_name="getData",
    endpoint="/data",
    params={"id": "123"},
    is_api_endpoint=True
)
```

### Example 2: Accessing the Full URL
```python
print(action_map.full_url)
# Output depends on the base URL and the specified endpoint
```

### Example 3: Modifying the Full URL
```python
action_map.full_url = "https://example.com/api/data"
print(action_map.full_url)
# Output: https://example.com/api/data
```

In these examples, the `ActionMap` class is used to create mappings between action names and endpoints/URLs, with support for additional parameters such as POST data and authentication tokens. This approach is useful for managing and organizing API endpoints or URLs in a structured way, especially in applications with dynamic action handling.
