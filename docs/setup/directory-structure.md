# Directory Structure

Generated on: 2025-07-19 13:58:09

```
ai-system/
├── .claude/
│   └── commands/
├── .vscode/
│   └── snippets/
├── archives/
│   ├── cold/
│   └── warm/
├── build/
│   ├── dashboard/
│   │   └── notifications/
│   ├── runtime/
│   ├── storage/
│   │   ├── cold/
│   │   ├── hitl/
│   │   ├── hot/
│   │   └── warm/
│   └── test_outputs/
├── config/
│   └── schemas/
├── dashboard/
├── data/
│   └── storage/
│       └── escalations/
├── docs/
│   ├── admin/
│   ├── api/
│   ├── architecture/
│   │   └── agents/
│   ├── cicd/
│   ├── completions/
│   ├── development/
│   │   ├── debugging/
│   │   ├── generation/
│   │   ├── mocking/
│   │   ├── testing/
│   │   └── visualization/
│   ├── integrations/
│   ├── operations/
│   │   ├── automation/
│   │   ├── monitoring/
│   │   └── workflows/
│   ├── optimizations/
│   ├── reports/
│   │   ├── memory-engine/
│   │   └── phase7-hitl/
│   ├── security/
│   │   └── validation/
│   ├── setup/
│   ├── sprint/
│   │   ├── briefings/
│   │   └── daily_reports/
│   ├── tools/
│   │   └── validation/
│   └── user-guides/
│       └── demos/
├── outputs/
│   ├── BE-01/
│   ├── BE-02/
│   ├── BE-03/
│   ├── BE-04/
│   ├── BE-05/
│   ├── BE-06/
│   ├── BE-07/
│   ├── BE-08/
│   ├── BE-09/
│   ├── BE-10/
│   ├── BE-11/
│   ├── BE-12/
│   ├── BE-13/
│   ├── BE-14/
│   ├── briefings/
│   ├── DEPENDENT-01/
│   ├── FE-01/
│   ├── FE-02/
│   ├── FE-03/
│   ├── FE-04/
│   ├── FE-05/
│   ├── FE-06/
│   ├── INTEGRATION-01/
│   ├── LC-01/
│   ├── PM-01/
│   ├── PM-02/
│   ├── PM-03/
│   ├── PM-04/
│   ├── PM-05/
│   ├── PM-06/
│   ├── PM-07/
│   ├── PM-08/
│   ├── PM-09/
│   ├── PM-10/
│   ├── PM-11/
│   ├── PM-12/
│   ├── QA-01/
│   ├── QA-02/
│   ├── QA-03/
│   ├── QA-INTEGRATION-01/
│   ├── TL-01/
│   ├── TL-02/
│   ├── TL-03/
│   ├── TL-04/
│   ├── TL-05/
│   ├── TL-06/
│   ├── TL-07/
│   ├── TL-08/
│   ├── TL-09/
│   ├── TL-10/
│   ├── TL-11/
│   ├── TL-12/
│   ├── TL-13/
│   ├── TL-14/
│   ├── TL-15/
│   ├── TL-16/
│   ├── TL-17/
│   ├── TL-18/
│   ├── TL-19/
│   ├── TL-20/
│   ├── TL-21/
│   ├── TL-22/
│   ├── TL-23/
│   ├── TL-24/
│   ├── TL-25/
│   ├── TL-26/
│   ├── TL-27/
│   ├── TL-28/
│   ├── TL-29/
│   ├── TL-30/
│   ├── UX-01/
│   ├── UX-02/
│   ├── UX-03/
│   ├── UX-04/
│   ├── UX-05/
│   ├── UX-06/
│   ├── UX-07/
│   ├── UX-08/
│   ├── UX-09/
│   ├── UX-10/
│   ├── UX-11/
│   ├── UX-12/
│   ├── UX-13/
│   ├── UX-14/
│   ├── UX-15/
│   ├── UX-16/
│   ├── UX-17/
│   ├── UX-18/
│   ├── UX-19/
│   ├── UX-21/
│   ├── UX-21b/
│   ├── UX-22/
│   ├── UX-23/
│   ├── UX-24/
│   └── UX-25/
├── progress_reports/
├── reports/
│   └── qa/
├── scripts/
├── src/
│   ├── core/
│   │   ├── agents/
│   │   ├── domain/
│   │   ├── services/
│   │   ├── states/
│   │   ├── tasks/
│   │   │   ├── backend/
│   │   │   ├── frontend/
│   │   │   ├── general/
│   │   │   ├── qa/
│   │   │   └── technical_lead/
│   │   └── workflows/
│   │       ├── graph/
│   │       │   └── config/
│   │       └── hitl/
│   ├── examples/
│   ├── infrastructure/
│   │   ├── .approved/
│   │   ├── data/
│   │   │   ├── context/
│   │   │   │   ├── backend/
│   │   │   │   ├── db/
│   │   │   │   ├── design/
│   │   │   │   ├── infra/
│   │   │   │   ├── patterns/
│   │   │   │   ├── sprint/
│   │   │   │   └── technical/
│   │   │   ├── sprints/
│   │   │   │   └── audit/
│   │   │   │       └── report/
│   │   │   └── storage/
│   │   │       ├── cold/
│   │   │       │   └── context/
│   │   │       ├── hot/
│   │   │       │   └── context/
│   │   │       └── warm/
│   │   │           └── context/
│   │   ├── memory/
│   │   │   ├── config/
│   │   │   ├── engines/
│   │   │   ├── knowledge/
│   │   │   └── security/
│   │   ├── prompts/
│   │   ├── reviews/
│   │   ├── runtime/
│   │   │   └── chroma_db/
│   │   ├── scripts/
│   │   │   ├── generation/
│   │   │   ├── monitoring/
│   │   │   ├── testing/
│   │   │   │   └── validation/
│   │   │   └── utilities/
│   │   │       └── db/
│   │   ├── security/
│   │   ├── storage/
│   │   │   └── feedback/
│   │   ├── templates/
│   │   │   ├── agent/
│   │   │   └── email/
│   │   ├── tools/
│   │   │   ├── core/
│   │   │   ├── external/
│   │   │   ├── handlers/
│   │   │   └── validation/
│   │   │       ├── ai/
│   │   │       ├── core/
│   │   │       ├── dashboard/
│   │   │       └── persistence/
│   │   └── utils/
│   │       └── security/
│   ├── integrations/
│   │   ├── analytics/
│   │   │   └── results/
│   │   ├── external/
│   │   └── notifications/
│   └── interfaces/
│       ├── api/
│       ├── cli/
│       ├── dashboard/
│       │   ├── api/
│       │   │   └── components/
│       │   ├── components/
│       │   ├── static/
│       │   └── templates/
│       ├── logs/
│       ├── outputs/
│       │   └── BE-07/
│       ├── reports/
│       ├── visualization/
│       └── webhooks/
├── storage/
│   ├── feedback/
│   └── hitl_tasks/
├── tasks/
├── templates/
│   └── email/
├── test_outputs/
└── tests/
    ├── components/
    ├── e2e/
    │   ├── performance/
    │   ├── system/
    │   ├── user_journeys/
    │   └── workflows/
    ├── fixtures/
    │   ├── data/
    │   ├── factories/
    │   ├── mocks/
    │   └── test_data/
    ├── integration/
    │   ├── api/
    │   ├── dashboard/
    │   ├── memory/
    │   └── workflows/
    ├── unit/
    │   ├── core/
    │   │   ├── agents/
    │   │   ├── states/
    │   │   ├── tasks/
    │   │   └── workflows/
    │   ├── infrastructure/
    │   │   └── tools/
    │   │       └── validation/
    │   ├── integrations/
    │   │   ├── analytics/
    │   │   └── external/
    │   ├── interfaces/
    │   │   ├── api/
    │   │   ├── cli/
    │   │   └── dashboard/
    │   └── platform/
    │       ├── memory/
    │       ├── security/
    │       ├── storage/
    │       └── tools/
    ├── utils/
    └── validation/
```

## Summary

- **Total directories**: 293 (directories only - partial view)
- **Generation method**: Depth-First Search (DFS) traversal
- **Tree algorithm**: Recursive directory iteration with ASCII formatting

## Complete Tree Structure

📋 **For the complete tree structure including all files**, see: [`complete-directory-structure.md`](./complete-directory-structure.md)

The complete structure includes:
- **1,369 files** across the entire project
- **269 directories** with full hierarchy
- **132,529 total lines** of code and documentation
- **File sizes** in appropriate units (B/K/M)
- **DFS traversal algorithm** with detailed insights
