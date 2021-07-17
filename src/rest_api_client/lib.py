import logging
import re
from typing import Iterable, Dict, Optional, List
from makefun import create_function
from pydantic import BaseModel, HttpUrl
from enum import Enum
import httpx


logger = logging.getLogger("LIB_LOGGER")
logger.setLevel(logging.ERROR)

JSON_MIMETYPE = "application/json"
SUPPORTED_METHODS = {"get", "post", "put", "patch", "delete"}
ALIASES = {"create": "post", "update": "put"}


class HttpDriver:
    session: httpx.Client


class HTTPMethod(Enum):
    GET = "get"
    DELETE = "delete"
    POST = "post"
    PUT = "put"
    PATCH = "patch"


class Url(BaseModel):
    full_string: HttpUrl


class Endpoint(BaseModel):
    name: str
    path: str
    method: Optional[HTTPMethod]
    model: Optional[type]
    query_parameters: Optional[Dict[str, type]]
    path_parameters: Optional[List[str]] = None


class EndpointNotFound(Exception):
    """Endpoint not found in Rest API class."""


class MissingMethodName(Exception):
    "HTTP Method is missing from endpoint."

    def __init__(self, endpoint_name):
        self.msg = f"""
Missing method name for endpoint {endpoint_name}.
Pass it as an argument or declare it in the format:

- get_your_resource_name
- post_something
- put_asd
- patch_another
- delete_snake_case
""".format(
            endpoint_name
        )


class RestAPI:
    def __init__(
        self,
        api_url: str,
        driver: HttpDriver,
        endpoints: Optional[Iterable[Endpoint]] = None,
    ):
        self.api_url = Url(full_string=api_url)
        self.driver = driver
        self._headers = {
            "Accept": JSON_MIMETYPE,
        }
        self.endpoints: Dict[str, Endpoint] = {}
        if endpoints:
            self.register_endpoints(endpoints)

    def register_endpoints(self, endpoints: Iterable[Endpoint]):
        for endpoint in endpoints:
            if not endpoint.method:
                missing_method = False
                sections = endpoint.name.split("_")
                if not sections:
                    missing_method = True

                method = sections[0]
                if method in ALIASES:
                    method = ALIASES[method]

                if method not in SUPPORTED_METHODS:
                    missing_method = True

                if missing_method:
                    raise MissingMethodName(endpoint_name=endpoint.name)

                # Inferred type from endpoint name.
                endpoint.method = HTTPMethod(method)

            # Check for path parameters
            endpoint.path_parameters = self.get_path_parameters(endpoint.path)

            self.endpoints[endpoint.name] = endpoint
            self._create_sync_method(endpoint)

    def call_endpoint(self, name, *args, data: Optional[BaseModel] = None, **kwargs):
        endpoint = self.endpoints.get(name)
        if not endpoint:
            raise EndpointNotFound(f"Endpoint {name} not found!")

        return self._sync_call_endpoint(endpoint, data, **kwargs)

    def _sync_call_endpoint(
        self, endpoint: Endpoint, data: Optional[BaseModel] = None, **kwargs
    ):
        if not endpoint.method:
            raise MissingMethodName(endpoint_name=endpoint.name)

        method = endpoint.method.value
        driver_function = getattr(self.driver, method)
        url = f"{str(self.api_url.full_string)}{endpoint.path}"
        driver_kwargs = {}
        headers = self._headers.copy()
        if data:
            driver_kwargs["json"] = data
            headers["Content-Type"] = JSON_MIMETYPE

        if endpoint.query_parameters:
            parameters = []
            for key, item in kwargs.items():
                if item and key in endpoint.query_parameters:
                    parameters.append(f"{key}={item}")
            query = "?" + "&".join(parameters)

            url += query

        if endpoint.path_parameters:
            path_kwargs = {}
            for key, item in kwargs.items():
                if key in endpoint.path_parameters:
                    path_kwargs[key] = item
            url = url.format(**path_kwargs)

        driver_kwargs["url"] = url  # type: ignore
        logger.debug(driver_kwargs)
        response = driver_function(**driver_kwargs)
        response.raise_for_status()
        try:
            json_response = response.json()
            if endpoint.model:
                return endpoint.model(**json_response)
            return json_response
        except Exception:
            return response.text

    def _create_sync_method(self, endpoint: Endpoint):
        parameters = []
        if endpoint.method in [HTTPMethod.POST, HTTPMethod.PUT, HTTPMethod.PATCH]:
            parameters.append("data: BaseModel = None")

        if endpoint.path_parameters:
            for p in endpoint.path_parameters:
                parameters.append(f"{p}: str = None")

        if endpoint.query_parameters:
            for p_name, p_type in endpoint.query_parameters.items():
                parameters.append(f"{p_name}:{p_type.__name__} = None")

        parameters_string = ",".join(parameters)
        logger.debug(parameters_string)

        func_sig = f"{endpoint.name}({parameters_string})"

        def func_impl(*args, **kwargs):
            """This docstring will be used in the generated function by default"""
            return self.call_endpoint(name=endpoint.name, **kwargs)
            return args, kwargs

        dynamic_function = create_function(func_sig, func_impl)

        setattr(self, endpoint.name, dynamic_function)  # noqa

    def get_path_parameters(self, path: str) -> Optional[List[str]]:
        _query_parameters: List[str] = []
        params = re.findall(r"({[a-z_]+})", path)
        if not params:
            return None
        for param in params:
            _query_parameters.append(re.sub("{|}", "", str(param)))
        return _query_parameters
