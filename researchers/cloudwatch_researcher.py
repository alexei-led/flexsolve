from .base_researcher import BaseResearcher

class CloudWatchResearcher(BaseResearcher):
    def __init__(self, openai_config):
        super().__init__(openai_config)
        self.name = "CloudWatch_Researcher"
        self.expertise = [
            "Metrics and Alarms",
            "Log Analysis",
            "Events/EventBridge",
            "Container Insights",
            "Application Insights"
        ]
        self.system_message = """You are a CloudWatch research specialist. Your role is to:
        1. Analyze monitoring-related questions
        2. Identify missing observability details
        3. Suggest clarifying questions about:
           - Monitoring needs
           - Alerting requirements
           - Log analysis
           - Performance metrics
           - Event patterns
        
        Focus on gathering:
        - Current monitoring setup
        - Alert requirements
        - Log retention needs
        - Performance thresholds
        - Event handling needs
        
        Format questions to be:
        - Monitoring-focused
        - Performance-aware
        - Clear and specific
        - SLA/SLO-conscious""" 
