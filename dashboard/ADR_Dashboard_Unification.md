# ADR: Dashboard Unification

## Status
**APPROVED** - June 1, 2025

## Context
Multiple dashboards (ports 5000/8080) cause fragmentation, inconsistent metrics, and duplicated logic. Current state:

- `completion_charts.html` - Basic dashboard with chart functionality
- `enhanced_completion_charts.html` - Enhanced version with system health and timeline
- `realtime_dashboard.html` - Real-time monitoring dashboard
- Multiple API endpoints serving different data contracts
- Inconsistent UI/UX across dashboards
- No single source of truth for reporting

This leads to:
- Reporting confusion and maintenance overhead
- Divergent data showing different metrics
- Duplicated frontend and backend logic
- Poor user experience due to fragmentation

## Decision
**Migrate all features, widgets, and metrics into a single unified dashboard UI and API.**

### Technical Approach:
1. **Use `enhanced_completion_charts.html` as canonical base** - it has the most complete feature set
2. **Consolidate all API endpoints in `api_server_working.py`** - single backend serving all data
3. **Port missing features** from other dashboards into the unified version
4. **Standardize data contracts** - consistent metrics, health, QA, coverage models
5. **Single deployment endpoint** - serve unified dashboard from `/dashboard/` route
6. **Deprecate legacy dashboards** after successful migration

### Implementation Plan:
- ✅ Phase 1: API Consolidation (COMPLETE)
- 🔄 Phase 2: Frontend Unification (IN PROGRESS) 
- ⏳ Phase 3: Feature Integration
- ⏳ Phase 4: Testing & Validation
- ⏳ Phase 5: Legacy Deprecation

## Consequences
### Positive:
- Single source of truth for all reporting
- Easier maintenance, clearer CI pipeline
- Consistent UX for all users
- Reduced code duplication
- Better performance and reliability

### Negative:
- Short-term migration effort
- Risk of feature regression during consolidation
- Need to coordinate updates during transition

## Success Metrics
- [ ] Only one dashboard codebase in active use
- [ ] 100% of metrics/health/coverage data comes from single backend
- [ ] Zero dead/duplicate endpoints
- [ ] Automated tests for all charts/widgets
- [ ] No "Loading..." states > 2s with test data present
- [ ] All team members using unified dashboard

## Next Steps
1. Create unified dashboard (`unified_dashboard.html`)
2. Merge all frontend features and widgets
3. Update API server to serve unified dashboard at `/dashboard/`
4. Add deprecation banners to legacy dashboards
5. Update documentation and team processes
6. Remove legacy code after 30-day deprecation period

## Implementation Details
- **Primary Dashboard**: `unified_dashboard.html`
- **API Server**: `api_server_working.py` (port 5000)
- **Route**: `http://localhost:5000/dashboard/`
- **Data Sources**: All consolidated into single API
- **Features**: Real-time updates, system health, metrics, QA, coverage, timeline

---
*Approved by: AI Development Team*  
*Date: June 1, 2025*  
*Review Date: July 1, 2025*
