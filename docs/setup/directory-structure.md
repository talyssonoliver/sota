# Directory Structure

Generated on: 2025-06-14 08:12:01

```
ai-system/
├── .approved/
├── .claude/
│   └── claude-code/
│       └── .vscode/
├── .vscode/
├── agents/
├── analytics/
│   └── results/
├── api/
├── build/
│   ├── archives/
│   │   ├── cold/
│   │   └── warm/
│   ├── dashboard/
│   │   ├── dashboard/
│   │   ├── docs/
│   │   │   └── sprint/
│   │   │       └── briefings/
│   │   ├── logs/
│   │   ├── notifications/
│   │   ├── reports/
│   │   └── visualizations/
│   ├── data/
│   │   └── storage/
│   ├── reports/
│   ├── runtime/
│   │   ├── logs/
│   │   │   ├── daily_cycle/
│   │   │   └── langgraph/
│   │   ├── outputs/
│   │   └── temp/
│   ├── static/
│   ├── storage/
│   │   ├── cold/
│   │   ├── feedback/
│   │   ├── hitl/
│   │   ├── hitl_tasks/
│   │   ├── hot/
│   │   └── warm/
│   ├── templates/
│   │   └── email/
│   └── test_outputs/
├── cli/
├── config/
│   └── schemas/
├── dashboard/
│   └── notifications/
├── data/
│   ├── context/
│   │   ├── backend/
│   │   ├── db/
│   │   ├── design/
│   │   ├── frontend/
│   │   ├── infra/
│   │   ├── patterns/
│   │   ├── product/
│   │   ├── sprint/
│   │   └── technical/
│   ├── sprints/
│   │   └── audit/
│   │       └── report/
│   ├── storage/
│   │   ├── cold/
│   │   │   └── context/
│   │   ├── escalations/
│   │   ├── hot/
│   │   │   └── context/
│   │   └── warm/
│   │       └── context/
│   └── templates/
│       └── email/
├── deployment/
│   ├── build/
│   │   ├── archives/
│   │   │   ├── cold/
│   │   │   └── warm/
│   │   ├── dashboard/
│   │   │   ├── dashboard/
│   │   │   ├── docs/
│   │   │   │   └── sprint/
│   │   │   │       └── briefings/
│   │   │   ├── logs/
│   │   │   ├── notifications/
│   │   │   ├── reports/
│   │   │   └── visualizations/
│   │   ├── data/
│   │   │   └── storage/
│   │   ├── reports/
│   │   ├── runtime/
│   │   │   ├── logs/
│   │   │   │   ├── daily_cycle/
│   │   │   │   └── langgraph/
│   │   │   ├── outputs/
│   │   │   └── temp/
│   │   ├── static/
│   │   ├── storage/
│   │   │   ├── cold/
│   │   │   ├── feedback/
│   │   │   ├── hitl/
│   │   │   ├── hitl_tasks/
│   │   │   ├── hot/
│   │   │   └── warm/
│   │   ├── templates/
│   │   │   └── email/
│   │   └── test_outputs/
│   ├── logs/
│   │   ├── daily_cycle/
│   │   └── langgraph/
│   ├── outputs/
│   ├── reports/
│   ├── runtime/
│   │   ├── cache/
│   │   │   └── memory_disk_cache/
│   │   ├── chroma_db/
│   │   ├── logs/
│   │   │   ├── context_usage/
│   │   │   ├── daily_cycle/
│   │   │   └── langgraph/
│   │   ├── outputs/
│   │   ├── progress_reports/
│   │   ├── reports/
│   │   │   └── qa/
│   │   ├── temp/
│   │   │   └── mock-api-key/
│   │   ├── test_logs/
│   │   │   └── daily_cycle/
│   │   └── test_outputs/
│   └── storage/
│       ├── cold/
│       ├── feedback/
│       ├── hitl/
│       ├── hitl_tasks/
│       ├── hot/
│       └── warm/
├── docs/
│   ├── admin/
│   ├── architecture/
│   ├── completions/
│   ├── optimizations/
│   ├── setup/
│   ├── sprint/
│   │   ├── briefings/
│   │   └── daily_reports/
│   └── tools/
├── examples/
├── graph/
├── handlers/
├── logs/
│   ├── daily_cycle/
│   └── langgraph/
├── memory-bank/
├── orchestration/
├── outputs/
├── patches/
├── pending_reviews/
├── progress_reports/
├── prompts/
├── reports/
├── reviews/
├── runtime/
│   ├── cache/
│   │   └── memory_disk_cache/
│   ├── chroma_db/
│   ├── logs/
│   │   ├── context_usage/
│   │   ├── daily_cycle/
│   │   └── langgraph/
│   ├── outputs/
│   ├── progress_reports/
│   ├── reports/
│   │   └── qa/
│   ├── temp/
│   │   └── mock-api-key/
│   ├── test_logs/
│   │   └── daily_cycle/
│   └── test_outputs/
├── scripts/
│   └── validation/
├── src/
│   ├── core/
│   │   ├── agents/
│   │   ├── states/
│   │   ├── tasks/
│   │   │   ├── backend/
│   │   │   ├── frontend/
│   │   │   ├── general/
│   │   │   ├── qa/
│   │   │   └── technical_lead/
│   │   └── workflows/
│   ├── integrations/
│   │   ├── analytics/
│   │   │   └── results/
│   │   ├── external/
│   │   └── notifications/
│   ├── interfaces/
│   │   ├── api/
│   │   ├── cli/
│   │   ├── dashboard/
│   │   │   ├── api/
│   │   │   ├── components/
│   │   │   ├── static/
│   │   │   └── templates/
│   │   └── webhooks/
│   └── platform/
│       ├── memory/
│       │   ├── config/
│       │   ├── engines/
│       │   ├── knowledge/
│       │   └── security/
│       ├── security/
│       ├── storage/
│       ├── tools/
│       └── utils/
├── storage/
│   ├── cold/
│   ├── feedback/
│   ├── hitl/
│   ├── hitl_tasks/
│   ├── hot/
│   └── warm/
├── tasks/
│   ├── backend/
│   ├── frontend/
│   ├── general/
│   ├── qa/
│   └── technical_lead/
├── templates/
│   └── email/
├── tests/
│   ├── e2e/
│   │   ├── performance/
│   │   ├── system/
│   │   ├── user_journeys/
│   │   └── workflows/
│   ├── fixtures/
│   │   ├── data/
│   │   ├── factories/
│   │   ├── mocks/
│   │   └── test_data/
│   ├── integration/
│   │   ├── api/
│   │   ├── dashboard/
│   │   ├── memory/
│   │   └── workflows/
│   ├── test_data/
│   │   └── context-store/
│   ├── test_outputs/
│   └── unit/
│       ├── core/
│       │   ├── agents/
│       │   ├── states/
│       │   ├── tasks/
│       │   └── workflows/
│       ├── integrations/
│       │   ├── analytics/
│       │   └── external/
│       ├── interfaces/
│       │   ├── api/
│       │   ├── cli/
│       │   └── dashboard/
│       └── platform/
│           ├── memory/
│           ├── security/
│           ├── storage/
│           └── tools/
├── tools/
│   └── memory/
└── visualization/
```

## Summary

- **Total directories**: 268 (directories only - partial view)
- **Generation method**: Depth-First Search (DFS) traversal
- **Tree algorithm**: Recursive directory iteration with ASCII formatting

## Complete Tree Structure

📋 **For the complete tree structure including all files**, see: [`complete-directory-structure.md`](./complete-directory-structure.md)

The complete structure includes:
- **1,248 files** across the entire project
- **268 directories** with full hierarchy
- **226,383 total lines** of code and documentation
- **File sizes** in appropriate units (B/K/M)
- **DFS traversal algorithm** with detailed insights
