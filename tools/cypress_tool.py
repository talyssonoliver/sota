"""
Cypress Tool - Helps agents generate and manage E2E tests using Cypress
"""

import json
import os
import subprocess
from typing import Any, Dict, List, Optional

from tools.base_tool import ArtesanatoBaseTool


class CypressTool(ArtesanatoBaseTool):
    """Tool for generating and managing Cypress E2E tests."""

    name: str = "cypress_tool"
    description: str = "Tool for generating and executing Cypress E2E tests for web interfaces"
    project_root: str
    cypress_dir: str
    test_output: str

    def __init__(self, project_root: str, **kwargs):
        """Initialize the Cypress tool."""
        super().__init__(**kwargs)
        self.project_root = project_root
        self.cypress_dir = os.path.join(self.project_root, "cypress")
        self.test_output = os.path.join(
            self.project_root, "cypress", "results")

    def _run(self, query: str) -> str:
        """Execute Cypress operations based on the query."""
        try:
            query_lower = query.lower()

            # Generate test case
            if "generate" in query_lower or "create" in query_lower:
                test_name = self._extract_param(query, "name")
                test_description = self._extract_param(query, "description")
                page_path = self._extract_param(query, "page")
                return self._generate_test(
                    test_name, test_description, page_path)

            # Execute tests
            elif "run" in query_lower or "execute" in query_lower:
                spec = self._extract_param(query, "spec")
                headless = "headless" in query_lower
                return self._run_tests(spec, headless)

            # List tests
            elif "list" in query_lower:
                return self._list_tests()

            # Generate fixture
            elif "fixture" in query_lower:
                fixture_name = self._extract_param(query, "name")
                data = self._extract_param(query, "data")
                return self._create_fixture(fixture_name, data)

            # Get test templates or examples
            elif "template" in query_lower or "example" in query_lower:
                test_type = self._extract_param(query, "type") or "basic"
                return self._get_test_template(test_type)

            else:
                return json.dumps(
                    self.format_response(
                        data=None,
                        error="Unsupported Cypress operation. Supported operations: generate test, run test, list tests, create fixture, get template"))

        except Exception as e:
            return json.dumps(self.handle_error(e, "CypressTool._run"))

    def _arun(self, query: str) -> str:
        """Async version of _run."""
        return self._run(query)

    def _extract_param(self, query: str, param_name: str) -> str:
        """Extract a parameter value from the query string."""
        import re
        pattern = rf"{param_name}[=:][\s]*[\"']([^\"']+)[\"']|{param_name}[=:][\s]*(\S+)"
        matches = re.search(pattern, query, re.IGNORECASE)
        if matches:
            return matches.group(1) or matches.group(2)
        return ""

    def _generate_test(
            self,
            test_name: str,
            test_description: str,
            page_path: str) -> str:
        """Generate a Cypress test file for the given page."""
        # In a real implementation, this would create actual test files
        # For now, return a mock response with test code

        if not test_name:
            test_name = "example"

        if not page_path:
            page_path = "/"

        if not test_description:
            test_description = f"Tests the {page_path} page functionality"

        # Generate a descriptive file name from test name
        file_name = f"{test_name.replace(' ', '_').lower()}.cy.js"

        # Generate the test content
        test_content = self._generate_test_content(
            test_name, test_description, page_path)

        return json.dumps(self.format_response(
            data={
                "message": f"Generated Cypress test: {file_name}",
                "file_name": file_name,
                "test_content": test_content
            }
        ))

    def _generate_test_content(
            self,
            test_name: str,
            test_description: str,
            page_path: str) -> str:
        """Generate test content based on the test type and page."""
        # Basic page test
        test_content = f"""// {test_description}
describe('{test_name}', () => {{
  beforeEach(() => {{
    cy.visit('{page_path}')
  }})

  it('successfully loads the page', () => {{
    cy.get('h1').should('be.visible')
    cy.url().should('include', '{page_path}')
  }})

  it('has all critical UI elements', () => {{
    cy.get('nav').should('exist')
    cy.get('footer').should('exist')
  }})

  // Add more specific tests based on the page functionality
}})
"""
        return test_content

    def _run_tests(self, spec: str, headless: bool = True) -> str:
        """Run Cypress tests and return results."""
        # In a real implementation, this would execute cypress run
        # For now, return a mock response

        mode = "headless" if headless else "headed"
        command = f"npx cypress run --spec '{spec}'" if spec else f"npx cypress run"
        command += " --headless" if headless else ""

        return json.dumps(self.format_response(
            data={
                "message": f"Executed Cypress tests in {mode} mode",
                "command": command,
                "results": {
                    "totalTests": 4,
                    "passing": 3,
                    "failing": 1,
                    "skipped": 0,
                    "duration": "2.5s"
                }
            }
        ))

    def _list_tests(self) -> str:
        """List all Cypress test files in the project."""
        # In a real implementation, this would scan the cypress/e2e directory
        # For now, return mock data

        return json.dumps(self.format_response(
            data={
                "message": "Listed all Cypress tests",
                "tests": [
                    {
                        "file": "home_page.cy.js",
                        "path": "cypress/e2e/home_page.cy.js"
                    },
                    {
                        "file": "product_listing.cy.js",
                        "path": "cypress/e2e/product_listing.cy.js"
                    },
                    {
                        "file": "checkout.cy.js",
                        "path": "cypress/e2e/checkout.cy.js"
                    },
                    {
                        "file": "auth_flow.cy.js",
                        "path": "cypress/e2e/auth_flow.cy.js"
                    }
                ]
            }
        ))

    def _create_fixture(self, fixture_name: str, data: str) -> str:
        """Create a Cypress fixture with the provided data."""
        # In a real implementation, this would write to cypress/fixtures
        # For now, return a mock response

        if not fixture_name:
            fixture_name = "example"

        file_name = f"{fixture_name}.json"

        # Parse data if provided as JSON string, otherwise use example data
        fixture_data = {}
        if data:
            try:
                fixture_data = json.loads(data)
            except BaseException:
                pass

        if not fixture_data:
            # Example fixture data
            fixture_data = {
                "products": [
                    {
                        "id": "1",
                        "name": "Handcrafted Ceramic Mug",
                        "price": 24.99
                    },
                    {
                        "id": "2",
                        "name": "Woven Wall Hanging",
                        "price": 89.99
                    }
                ]
            }

        return json.dumps(self.format_response(
            data={
                "message": f"Created Cypress fixture: {file_name}",
                "file_name": file_name,
                "fixture_data": fixture_data
            }
        ))

    def _get_test_template(self, test_type: str) -> str:
        """Return template code for different test types."""
        templates = {
            "basic": self._get_basic_test_template(),
            "auth": self._get_auth_test_template(),
            "api": self._get_api_test_template(),
            "form": self._get_form_test_template(),
            "cart": self._get_cart_test_template()
        }

        if test_type in templates:
            return json.dumps(self.format_response(
                data={
                    "message": f"Generated {test_type} test template",
                    "template": templates[test_type]
                }
            ))
        else:
            return json.dumps(
                self.format_response(
                    data={
                        "message": "Unknown template type, providing basic template",
                        "template": templates["basic"]}))

    def _get_basic_test_template(self) -> str:
        """Return a basic Cypress test template."""
        return """// Basic page test template
describe('Page Test', () => {
  beforeEach(() => {
    cy.visit('/path-to-page')
  })

  it('successfully loads the page', () => {
    cy.get('h1').should('be.visible')
    cy.contains('Expected Text').should('exist')
  })

  it('has working navigation', () => {
    cy.get('nav a').first().click()
    cy.url().should('include', '/expected-path')
  })
})
"""

    def _get_auth_test_template(self) -> str:
        """Return an authentication test template."""
        return """// Authentication test template
describe('Authentication Flow', () => {
  beforeEach(() => {
    cy.visit('/login')
  })

  it('shows validation errors with invalid credentials', () => {
    cy.get('input[name="email"]').type('invalid@example.com')
    cy.get('input[name="password"]').type('wrongpassword')
    cy.get('form').submit()
    cy.get('.error-message').should('be.visible')
  })

  it('successfully logs in with valid credentials', () => {
    cy.get('input[name="email"]').type('user@example.com')
    cy.get('input[name="password"]').type('correctpassword')
    cy.get('form').submit()
    cy.url().should('include', '/dashboard')
    cy.get('.user-welcome').should('contain', 'Welcome')
  })

  it('can log out', () => {
    // Log in first
    cy.get('input[name="email"]').type('user@example.com')
    cy.get('input[name="password"]').type('correctpassword')
    cy.get('form').submit()

    // Then log out
    cy.get('.logout-button').click()
    cy.url().should('include', '/login')
  })
})
"""

    def _get_api_test_template(self) -> str:
        """Return an API test template."""
        return """// API test template
describe('API Tests', () => {
  it('fetches data from API', () => {
    cy.request('/api/products')
      .its('status')
      .should('eq', 200)

    cy.request('/api/products')
      .its('body')
      .should('have.property', 'data')
      .and('have.length.greaterThan', 0)
  })

  it('handles API errors correctly', () => {
    cy.request({
      url: '/api/invalid-endpoint',
      failOnStatusCode: false
    })
      .its('status')
      .should('eq', 404)
  })

  it('can create a new resource', () => {
    cy.request({
      method: 'POST',
      url: '/api/products',
      body: {
        name: 'New Product',
        price: 29.99
      }
    })
      .its('status')
      .should('eq', 201)
  })
})
"""

    def _get_form_test_template(self) -> str:
        """Return a form test template."""
        return """// Form submission test template
describe('Form Submission', () => {
  beforeEach(() => {
    cy.visit('/contact')
  })

  it('validates form fields', () => {
    cy.get('form').submit()
    cy.get('.error-message').should('be.visible')
  })

  it('submits form with valid data', () => {
    cy.get('input[name="name"]').type('Test User')
    cy.get('input[name="email"]').type('test@example.com')
    cy.get('textarea[name="message"]').type('This is a test message.')
    cy.get('form').submit()
    cy.get('.success-message').should('be.visible')
    cy.get('.success-message').should('contain', 'Thank you')
  })

  it('populates form with fixture data', () => {
    cy.fixture('contact-form.json').then((data) => {
      cy.get('input[name="name"]').type(data.name)
      cy.get('input[name="email"]').type(data.email)
      cy.get('textarea[name="message"]').type(data.message)
    })
    cy.get('form').submit()
    cy.get('.success-message').should('be.visible')
  })
})
"""

    def _get_cart_test_template(self) -> str:
        """Return a shopping cart test template."""
        return """// Shopping cart test template
describe('Shopping Cart', () => {
  beforeEach(() => {
    cy.visit('/products')
  })

  it('adds item to cart', () => {
    cy.get('.product-card').first().find('.add-to-cart').click()
    cy.get('.cart-count').should('contain', '1')
  })

  it('updates quantity in cart', () => {
    // Add product to cart
    cy.get('.product-card').first().find('.add-to-cart').click()

    // Go to cart page
    cy.visit('/cart')

    // Update quantity
    cy.get('.quantity-input').clear().type('2')
    cy.get('.update-quantity').click()

    // Check if total is updated
    cy.get('.cart-total').should('contain', '49.98')
  })

  it('removes item from cart', () => {
    // Add product to cart
    cy.get('.product-card').first().find('.add-to-cart').click()

    // Go to cart page
    cy.visit('/cart')

    // Remove item
    cy.get('.remove-item').click()
    cy.get('.empty-cart-message').should('be.visible')
  })

  it('proceeds to checkout', () => {
    // Add product to cart
    cy.get('.product-card').first().find('.add-to-cart').click()

    // Go to cart page
    cy.visit('/cart')

    // Proceed to checkout
    cy.get('.checkout-button').click()
    cy.url().should('include', '/checkout')
  })
})
"""

    def handle_error(self, error: Any, context: str) -> Dict[str, Any]:
        """Handle errors in a consistent way."""
        error_message = str(error)
        self.log(f"Error in {context}: {error_message}")

        return {
            "data": None,
            "error": {
                "message": error_message,
                "context": context
            }
        }
