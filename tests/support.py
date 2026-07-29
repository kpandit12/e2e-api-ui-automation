"""Reusable test-support helpers shared across the pyramid layers."""
from __future__ import annotations

import json

import allure

from clients.rest_client import ApiResponse


def attach_api_response(name: str, response: ApiResponse) -> None:
    """Attach a request/response summary to the Allure report.

    Ensures a failure is debuggable from the report alone: the status code,
    correlation id and (truncated) body land as an attachment on the step.
    """
    payload = {
        "request_id": response.request_id,
        "status_code": response.status_code,
        "body": response.json if response.json is not None else response.text[:1000],
    }
    allure.attach(
        json.dumps(payload, indent=2, default=str),
        name=name,
        attachment_type=allure.attachment_type.JSON,
    )
