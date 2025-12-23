from microservices.libs.services.tags import TagsService

tags_service = TagsService()


def get_tags_service() -> TagsService:
    return TagsService()
