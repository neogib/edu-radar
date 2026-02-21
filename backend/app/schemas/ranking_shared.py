from app.models.ranking import RankingBase
from app.schemas.base import CustomBaseModel


class RankingPublic(CustomBaseModel, RankingBase):
    id: int
