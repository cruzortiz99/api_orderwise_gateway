import json
import os
from pathlib import Path

import dotenv
import httpx
import uvicorn
from fastapi import FastAPI, Request, Response

dotenv.load_dotenv(dotenv_path=Path(__file__).parent / ".env")
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost")
API_PORT = int(os.environ.get("API_PORT", 8000))

APP = FastAPI()

with open("services.json") as f:
    services: dict = json.load(f)

    for service_name, service in services.items():
        for route in service["routes"]:
            path = route["path"]
            method = route["method"].lower()

            async def proxy(request: Request) -> Response:
                async with httpx.AsyncClient() as client:
                    match request.method.lower():
                        case "get":
                            resp = await client.get(
                                f"{API_BASE_URL}{request.url.path}",
                                headers=request.headers.raw,
                                params=request.query_params,
                            )
                            return Response(
                                content=resp.content,
                                headers=resp.headers,
                                media_type=resp.headers.get("Content-Type"),
                                status_code=resp.status_code,
                            )
                        case "post" | "put":
                            resp = await client.request(
                                request.method.upper(),
                                f"{API_BASE_URL}{request.url.path}",
                                content=await request.body(),
                                headers=request.headers.raw,
                                params=request.query_params,
                            )
                            return Response(
                                content=resp.content,
                                headers=resp.headers,
                                media_type=resp.headers.get("Content-Type"),
                                status_code=resp.status_code,
                            )
                        case "delete":
                            resp = await client.delete(
                                f"{API_BASE_URL}{request.url.path}",
                                headers=request.headers.raw,
                                params=request.query_params,
                            )
                            return Response(
                                content=resp.content,
                                headers=resp.headers,
                                media_type=resp.headers.get("Content-Type"),
                                status_code=resp.status_code,
                            )
                        case _:
                            resp = await client.request(
                                request.method.upper(),
                                f"{API_BASE_URL}{request.url.path}",
                                content=await request.body(),
                                headers=request.headers.raw,
                                params=request.query_params,
                            )
                            return Response(
                                content=resp.content,
                                headers=resp.headers,
                                media_type=resp.headers.get("Content-Type"),
                                status_code=resp.status_code,
                            )
                return Response(
                    content=json.dumps(
                        {
                            "message": f"Proxying {request.method.upper()} {request.url.path} to {API_BASE_URL}"
                        }
                    ),
                    media_type="application/json",
                )

            APP.add_api_route(
                path=path,
                endpoint=proxy,
                methods=[method.upper()],
                name=service_name,
                tags=[service_name],
                openapi_extra=route.get("docs", {}),
            )


def main():
    uvicorn.run("main:APP", port=API_PORT, log_level="info", reload=True)


if __name__ == "__main__":
    main()
