from pydantic import BaseModel, Field

from .endpoint import Endpoint


class Info(BaseModel):
    """Response model for the info route."""

    app_name: str = Field(..., description="The name of the app")
    app_image_url: str | None = Field(
        default=None, description="URL to the app's image"
    )
    app_description: str | None = Field(
        default=None, description="Description of the app"
    )
    app_title: str | None = Field(default=None, description="Title of the app")
    endpoints: list[Endpoint] = Field(
        default_factory=list, description="List of available endpoints"
    )

    def make_markdown_documentation(self) -> str:
        lines = [f"# {self.app_title or self.app_name}", ""]

        lines.extend(["## Endpoints", ""])

        for endpoint in self.endpoints:
            lines.append(endpoint.make_markdown_documentation())
            lines.append("")

        return "\n".join(lines)

    def print_markdown_documentation(self) -> None:
        print(self.make_markdown_documentation())

    def export_markdown_documentation(self, filename: str) -> None:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(self.make_markdown_documentation())
