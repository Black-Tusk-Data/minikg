from typing import Type
from pydantic import BaseModel
from minikg.extractor.base_extractor import BaseExtractor
from minikg.models import EntityRelationship


class EntityRelationshipExtractor(BaseExtractor[EntityRelationship]):
    pass
