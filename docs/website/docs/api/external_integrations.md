# api/external_integrations.py

## Classes
- **ExternalSystemType** (line 23)
- **IntegrationStatus** (line 33)
- **ExternalSystemConfig** (line 44)
- **ExternalReviewRequest** (line 59)
- **ExternalSystemIntegration** (line 80)
  - Methods: __init__, _check_rate_limit, _increment_rate_limit
- **GitHubIntegration** (line 127)
- **SlackIntegration** (line 265)
- **JIRAIntegration** (line 424)
- **ExternalAPIManager** (line 545)
  - Methods: __init__, _load_config, _create_integration, get_request, list_requests, get_system_stats

## Functions
- **get_external_api_manager()** (line 828)
