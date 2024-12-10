from .base_researcher import BaseResearcher
from config import ELASTICACHE_RESEARCHER_NAME

class ElastiCacheResearcher(BaseResearcher):
    def __init__(self, openai_config):
        super().__init__(openai_config)
        self.name = ELASTICACHE_RESEARCHER_NAME
        self.description = "I am an ElastiCache research specialist."
        self.expertise = [
            "Redis configuration",
            "Memcached setup",
            "Cluster scaling",
            "Cache strategies",
            "Performance tuning"
        ]
        example_questions = """
        Example technical questions to consider:
        1. Are you using Redis or Memcached?
        2. What's your expected cache data size?
        3. Do you need persistence or replication?
        4. What are your latency requirements?
        5. Do you need cluster mode enabled (Redis)?
        6. What's your cache eviction strategy?
        7. Do you require encryption at rest/transit?
        8. What's your cache hit ratio target?
        """
        self.system_message = self.base_system_message.format(
            service_area="Amazon ElastiCache",
            expertise="\n- ".join(self.expertise)
        ) + example_questions 