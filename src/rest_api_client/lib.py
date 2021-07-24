import logging
import re
from dataclasses import dataclass
from typing import Iterable, Dict, Optional, List, Callable, Generator
from makefun import create_function
from pydantic import BaseModel, HttpUrl
from enum import Enum
import httpx
import httpx_auth  # type: ignore


logger = logging.getLogger("LIB_LOGGER")
logger.setLevel(logging.ERROR)

JSON_MIMETYPE = "application/json"
SUPPORTED_METHODS = {"get", "post", "put", "patch", "delete"}
ALIASES = {"create": "post", "update": "put"}


@dataclass
class PreparedCall:
    driver_function: Callable
    driver_kwargs: dict
    model: Optional[type]


class ExecutionMode(Enum):
    SYNC = "SYNC"
    ASYNC = "ASYNC"


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
        custom_headers: Optional[Dict[str, str]] = None,
    ):
        self.api_url = Url(full_string=api_url)
        self.driver = driver
        self._headers = {
            "Accept": JSON_MIMETYPE,
        }
        self._custom_headers = custom_headers
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
            self._create_methods(endpoint)

    def call_endpoint(
        self, endpoint_name, *args, data: Optional[BaseModel] = None, **kwargs
    ):
        call: PreparedCall = self._prepare_call(
            endpoint_name, data, **kwargs, mode=ExecutionMode.SYNC
        )
        return self._call_sync_endpoint(call)

    async def call_async_endpoint(
        self, endpoint_name, *args, data: Optional[BaseModel] = None, **kwargs
    ):
        call: PreparedCall = self._prepare_call(
            endpoint_name, data, **kwargs, mode=ExecutionMode.ASYNC
        )
        return await self._call_async_endpoint(call)

    def _prepare_call(
        self,
        name: str,
        data: Optional[BaseModel] = None,
        mode=ExecutionMode.SYNC,
        **kwargs,
    ) -> PreparedCall:

        endpoint = self.endpoints.get(name)
        if not endpoint:
            raise EndpointNotFound(f"Endpoint {name} not found!")

        if not endpoint.method:
            raise MissingMethodName(endpoint_name=endpoint.name)

        method = endpoint.method.value
        driver_function = getattr(self.driver, method)
        url = f"{str(self.api_url.full_string)}{endpoint.path}"
        driver_kwargs = {}
        headers = self._headers.copy()

        if self._custom_headers:
            headers.update(self._custom_headers)
        if data:
            driver_kwargs["json"] = data
            headers["Content-Type"] = JSON_MIMETYPE

        driver_kwargs["headers"] = headers  # type: ignore
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
        return PreparedCall(driver_function, driver_kwargs, endpoint.model)

    def _call_sync_endpoint(self, call: PreparedCall):
        response = call.driver_function(**call.driver_kwargs)
        return self._process_endpoint_response(call, response)

    async def _call_async_endpoint(self, call: PreparedCall):
        response = await call.driver_function(**call.driver_kwargs)
        return self._process_endpoint_response(call, response)

    def _process_endpoint_response(self, call: PreparedCall, response):
        logger.debug(response.content)
        response.raise_for_status()
        try:
            json_response = response.json()
            if call.model:
                return call.model(**json_response)
            return json_response
        except Exception:
            return response.text

    def _create_methods(self, endpoint: Endpoint):
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
            """Synchronous endpoint call."""
            return self.call_endpoint(endpoint_name=endpoint.name, **kwargs)

        async def async_func_impl(*args, **kwargs):
            """Asynchronous endpoint call."""
            return await self.call_async_endpoint(endpoint_name=endpoint.name, **kwargs)

        dynamic_sync_function = create_function(func_sig, func_impl)
        dynamic_async_function = create_function(func_sig, async_func_impl)

        setattr(self, endpoint.name, dynamic_sync_function)  # noqa
        setattr(self, "async_" + endpoint.name, dynamic_async_function)  # noqa

    def get_path_parameters(self, path: str) -> Optional[List[str]]:
        _query_parameters: List[str] = []
        params = re.findall(r"({[a-z_]+})", path)
        if not params:
            return None
        for param in params:
            _query_parameters.append(re.sub("{|}", "", str(param)))
        return _query_parameters


class BearerHeaderToken(httpx.Auth, httpx_auth.authentication.SupportMultiAuth):
    """Describes a bearer token used in the header requests authentication."""

    def __init__(self, bearer_token: str):
        """
        :param api_key: The API key that will be sent.
        """
        self.bearer_token = bearer_token
        if not bearer_token:
            raise Exception("Bearer token is mandatory.")
        self.header_name = "Authorization"

    def auth_flow(
        self, request: httpx.Request
    ) -> Generator[httpx.Request, httpx.Response, None]:
        request.headers[self.header_name] = f"Bearer {self.bearer_token}"
        yield request
