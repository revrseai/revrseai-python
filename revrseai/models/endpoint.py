import json
from typing import TYPE_CHECKING, Any
from uuid import UUID

from pydantic import BaseModel, Field, PrivateAttr, field_validator

from .response import Response
from .schema import SchemaObject

if TYPE_CHECKING:
    from revrseai.client import RevrseAI


class Endpoint(BaseModel):
    """Information about an API endpoint."""

    _client: "RevrseAI | None" = PrivateAttr(default=None)

    id: UUID = Field(..., description="The unique identifier for the endpoint")
    name: str = Field(description="The name of the endpoint")
    description: str | None = Field(
        default=None, description="Description of what this endpoint does"
    )
    input_schema: SchemaObject = Field(
        description="JSON schema for the input parameters"
    )
    output_schema: SchemaObject = Field(
        description="JSON schema for the output response"
    )

    @field_validator("input_schema", "output_schema", mode="before")
    @classmethod
    def parse_schema(cls, v: Any) -> SchemaObject:
        if isinstance(v, dict):
            return SchemaObject.from_dict(v)
        if not isinstance(v, SchemaObject):
            raise ValueError(f"Expected dict or SchemaObject, got {type(v)}")
        return v

    def execute(self, data: dict[str, Any] | None = None) -> Response:
        if self._client is None:
            raise ValueError("Client not set. Cannot execute endpoint.")
        return self._client.execute_from_endpoint_id(str(self.id), data=data)

    def example_data(self) -> dict[str, Any]:
        return dict(self.input_schema.example_data())

    def example_response(self) -> dict[str, Any]:
        return dict(self.output_schema.example_data())

    def make_markdown_documentation(self) -> str:
        lines = [f"# {self.name}", ""]

        if self.description:
            lines.extend([f"> {self.description}", ""])

        # Input section
        lines.extend(["## Input", ""])
        lines.append(self.input_schema.to_markdown_table())

        # Build Python snippet for example request
        example_json = json.dumps(self.example_data(), indent=4)
        # Indent the data dict to align with the data= parameter
        indented_data = "\n".join(
            "    " + line if i > 0 else line
            for i, line in enumerate(example_json.split("\n"))
        )

        snippet = f'''from revrseai import RevrseAI

client = RevrseAI("YOUR_API_KEY")
resp = client.execute(
    endpoint_id="{self.id}",
    data={indented_data}
)
print(resp)'''

        lines.extend(["", "### Code Example", "", "```python"])
        lines.append(snippet)
        lines.extend(["```", ""])

        # Output section
        lines.extend(["## Output", ""])
        lines.append(self.output_schema.to_markdown_table())
        lines.extend(["", "### Example Response", "", "```json"])
        lines.append(json.dumps(self.example_response(), indent=2))
        lines.extend(["```"])

        return "\n".join(lines)

    def print_markdown_documentation(self) -> None:
        print(self.make_markdown_documentation())

    def export_markdown_documentation(self, filename: str) -> None:
        with open(filename, "w") as f:
            f.write(self.make_markdown_documentation())
