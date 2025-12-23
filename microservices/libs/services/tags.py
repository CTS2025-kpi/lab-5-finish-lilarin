from microservices.libs.schemas.tags import TagValidationRequest


class TagsService:
    def __init__(self):
        self._fake_tags_db = [
            "sci-fi", "action", "drama", "classic", "adventure", "comedy", "thriller"
        ]

    def get_all(self) -> list[str]:
        return self._fake_tags_db

    def validate_tag(self, payload: TagValidationRequest) -> str:
        if payload.tag_name not in self._fake_tags_db:
            self._fake_tags_db.append(payload.tag_name)

        return payload.tag_name
