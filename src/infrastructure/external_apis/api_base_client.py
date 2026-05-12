from typing import Literal, TypedDict

import httpx


class HttpxRequest(TypedDict, total=False):
    url: str
    method: Literal['GET', 'POST', 'PUT', 'DELETE']
    headers: dict[str, str]
    json: dict
    timeout: float
    # False: não chama raise_for_status (tratamento manual do status HTTP)
    raise_for_status: bool


class DefaultHttpClientErrorMessages:
    def __init__(self, name: str) -> None:
        self.timeout = f'Request to {name} timed out'
        self.connection = f'Connection to {name} failed'
        self.http = f'HTTP error when calling {name}'
        self.unknown = f'Unknown error when calling {name}'


class ApiBaseClient:
    def __init__(
        self,
        *,
        name: str,
        base_url: str,
        timeout: float = 10.0,
        default_headers: dict[str, str] | None = None,
    ) -> None:
        self.name = name
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.default_headers = default_headers or {}
        self.errors = DefaultHttpClientErrorMessages(name)

    async def request(self, data: HttpxRequest) -> httpx.Response:
        try:
            async with httpx.AsyncClient(
                base_url=self.base_url,
                timeout=data.get('timeout', self.timeout),
                headers={**self.default_headers, **data.get('headers', {})},
            ) as client:
                response = await client.request(
                    method=data['method'],
                    url=data['url'],
                    json=data.get('json'),
                )
                if data.get('raise_for_status', True):
                    response.raise_for_status()
                return response

        except httpx.TimeoutException as exc:
            raise httpx.TimeoutException(self.errors.timeout) from exc

        except httpx.ConnectError as exc:
            raise httpx.ConnectError(self.errors.connection) from exc

        except httpx.HTTPStatusError as exc:
            raise httpx.HTTPStatusError(
                self.errors.http,
                request=exc.request,
                response=exc.response,
            ) from exc

        except httpx.RequestError as exc:
            raise httpx.RequestError(self.errors.http) from exc

        except Exception as exc:
            raise RuntimeError(self.errors.unknown) from exc
