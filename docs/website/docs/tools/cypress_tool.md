# cypress_tool.py

The **CypressTool** enables agents to generate and run end-to-end tests using
the Cypress test runner. It can create test templates, execute test suites, and
manage fixtures under the project `cypress/` directory.

## CypressTool class

Key methods:

- ` _generate_test(name, description, page)` – create a basic test file.
- ` _run_tests(spec, headless)` – run Cypress for a given spec or all tests.
- ` _list_tests()` – list available spec files in the project.
- ` _create_fixture(name, data)` – generate fixture JSON files.
- ` _get_test_template(type)` – return sample code for a template.

Typical call from an agent:

```python
from tools.cypress_tool import CypressTool

cypress = CypressTool(project_root="./frontend")
result = cypress.call("run spec:checkout.cy.js headless")
```
