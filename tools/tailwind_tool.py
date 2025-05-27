"""
Tailwind Tool - Provides utilities for Tailwind CSS configuration and usage
"""

import json
import os
import re
from typing import Any, Dict

from dotenv import load_dotenv
from langchain.tools import BaseTool
from pydantic import BaseModel, Field, ValidationError

from tools.base_tool import ArtesanatoBaseTool

load_dotenv()


class TailwindTool(ArtesanatoBaseTool):
    """Tool for working with Tailwind CSS."""

    name: str = "tailwind_tool"
    description: str = "Tool for generating Tailwind CSS classes and utilities"
    config_cache: Dict[str, Any] = Field(default_factory=dict)

    class InputSchema(BaseModel):
        query: str

    def _load_config(self):
        """Load configuration from file if available, otherwise use defaults."""
        config_path = os.environ.get("TAILWIND_CONFIG_PATH", None)
        if (config_path and os.path.exists(config_path)):
            try:
                with open(config_path, 'r') as f:
                    self.config_cache = json.load(f)
            except Exception as e:
                print(f"Error loading Tailwind config: {e}")

    def _run(self, query: str) -> str:
        try:
            validated = self.InputSchema(query=query)
            query = validated.query
            query_lower = query.lower()

            if "config" in query_lower:
                return self._get_tailwind_config()

            elif any(term in query_lower for term in ["color", "palette", "theme"]):
                return self._get_color_palette()

            elif any(term in query_lower for term in ["typography", "font", "text"]):
                return self._get_typography_config()

            elif "spacing" in query_lower:
                return self._get_spacing_config()

            elif any(term in query_lower for term in ["responsive", "breakpoint", "mobile", "desktop"]):
                return self._get_responsive_config()

            elif any(term in query_lower for term in ["layout", "flex", "grid", "container"]):
                return self._get_layout_utilities(query)

            elif any(term in query_lower for term in ["class", "utility", "component"]):
                return self._generate_utility_classes(query)

            return (
                "Tailwind operation processed. Please specify if you need information about:\n"
                "- configuration (tailwind.config.js)\n"
                "- colors (color palette)\n"
                "- typography (fonts, text sizing)\n"
                "- spacing (padding, margin)\n"
                "- responsive (breakpoints)\n"
                "- layout (flex, grid, container)\n"
                "- utility classes (buttons, cards, forms, etc.)")
        except ValidationError as ve:
            return self.handle_error(ve, f"{self.name}._run.input_validation")
        except Exception as e:
            return self.handle_error(e, f"{self.name}._run")

    def _arun(self, query: str) -> str:
        """Async version of _run."""
        return self._run(query)

    def _get_tailwind_config(self) -> str:
        """Get the Tailwind configuration."""
        return """
Tailwind Configuration:

```javascript
// tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'brazilian-sun': '#FFC12B',
        'amazon-green': '#036B52',
        'artesanato-clay': '#A44A3F',
        'midnight-black': '#1A1A1A',
        'charcoal': '#404040',
        'slate': '#707070',
        'mist': '#E0E0E0',
        'cloud': '#F5F5F5',
        'success': '#0D8A6A',
        'warning': '#FFA726',
        'error': '#D32F2F',
        'info': '#2196F3',
      },
      fontFamily: {
        heading: ['var(--font-montserrat)', 'sans-serif'],
        body: ['var(--font-open-sans)', 'sans-serif'],
      },
      fontSize: {
        'heading-1': ['32px', '40px'],
        'heading-2': ['24px', '32px'],
        'heading-3': ['20px', '28px'],
        'heading-4': ['18px', '24px'],
        'heading-5': ['16px', '24px'],
        'body-large': ['18px', '28px'],
        'body': ['16px', '24px'],
        'body-small': ['14px', '20px'],
        'caption': ['12px', '16px'],
        'button': ['16px', '24px'],
      },
    },
  },
  plugins: [],
}
```
"""

    def _get_color_palette(self) -> str:
        """Get the color palette."""
        return """
Color Palette:

Primary Colors:
- Brazilian Sun: #FFC12B - Use for primary buttons, call-to-action elements, and highlights
- Amazon Green: #036B52 - Use for secondary interactive elements, success states, and accents
- Artesanato Clay: #A44A3F - Use for tertiary elements, decorative accents, and specialized UI components

Neutral Colors:
- Midnight Black: #1A1A1A - Use for primary text and high-emphasis UI elements
- Charcoal: #404040 - Use for secondary text and medium-emphasis UI elements
- Slate: #707070 - Use for tertiary text, disabled states, and low-emphasis UI elements
- Mist: #E0E0E0 - Use for borders, dividers, and subtle UI elements
- Cloud: #F5F5F5 - Use for backgrounds, cards, and container elements
- White: #FFFFFF - Use for page backgrounds and high-contrast elements

Semantic Colors:
- Success: #0D8A6A - Indicates successful actions or positive status
- Warning: #FFA726 - Indicates warnings or actions requiring attention
- Error: #D32F2F - Indicates errors or destructive actions
- Info: #2196F3 - Indicates informational messages or neutral status

Usage Examples:
- Button Primary: bg-brazilian-sun text-midnight-black
- Button Secondary: border border-amazon-green text-amazon-green
- Success Alert: bg-success text-white
- Error Message: text-error
"""

    def _get_typography_config(self) -> str:
        """Get the typography configuration."""
        return """
Typography Configuration:

Font Families:
- Headings: Montserrat (Bold, SemiBold) - font-heading
- Body: Open Sans (Regular, Medium, SemiBold) - font-body

Type Scale:
- Heading 1: 32px/40px, Montserrat Bold - text-heading-1 font-heading font-bold
- Heading 2: 24px/32px, Montserrat Bold - text-heading-2 font-heading font-bold
- Heading 3: 20px/28px, Montserrat SemiBold - text-heading-3 font-heading font-semibold
- Heading 4: 18px/24px, Montserrat SemiBold - text-heading-4 font-heading font-semibold
- Heading 5: 16px/24px, Montserrat SemiBold - text-heading-5 font-heading font-semibold
- Body Large: 18px/28px, Open Sans Regular - text-body-large font-body
- Body: 16px/24px, Open Sans Regular - text-body font-body
- Body Small: 14px/20px, Open Sans Regular - text-body-small font-body
- Caption: 12px/16px, Open Sans Medium - text-caption font-body font-medium
- Button: 16px/24px, Open Sans SemiBold - text-button font-body font-semibold

Usage Examples:
- Page Title: <h1 class="text-heading-1 font-heading font-bold text-midnight-black">Page Title</h1>
- Section Header: <h2 class="text-heading-2 font-heading font-bold text-midnight-black">Section Header</h2>
- Card Title: <h3 class="text-heading-4 font-heading font-semibold text-midnight-black">Card Title</h3>
- Body Text: <p class="text-body font-body text-charcoal">Body text content...</p>
- Small Text: <p class="text-body-small font-body text-slate">Small text content...</p>
"""

    def _get_spacing_config(self) -> str:
        """Get the spacing configuration."""
        return """
Spacing Configuration:

Our spacing system uses a 4px base unit to maintain consistent spacing throughout the interface.

- space-0: 0px - p-0, m-0
- space-1: 4px - p-1, m-1
- space-2: 8px - p-2, m-2
- space-3: 12px - p-3, m-3
- space-4: 16px - p-4, m-4
- space-5: 20px - p-5, m-5
- space-6: 24px - p-6, m-6
- space-8: 32px - p-8, m-8
- space-10: 40px - p-10, m-10
- space-12: 48px - p-12, m-12
- space-16: 64px - p-16, m-16
- space-20: 80px - p-20, m-20
- space-24: 96px - p-24, m-24

Direction-specific spacing:
- Padding: p-4 (all sides), pt-4 (top), pr-4 (right), pb-4 (bottom), pl-4 (left), px-4 (horizontal), py-4 (vertical)
- Margin: m-4 (all sides), mt-4 (top), mr-4 (right), mb-4 (bottom), ml-4 (left), mx-4 (horizontal), my-4 (vertical)

Usage Examples:
- Card Padding: <div class="p-6">...</div>
- Section Margin: <section class="my-12">...</section>
- Button Padding: <button class="px-6 py-3">...</button>
- Form Field Spacing: <div class="space-y-4">...</div>
"""

    def _get_responsive_config(self) -> str:
        """Get the responsive configuration."""
        return """
Responsive Configuration:

Breakpoints:
- xs: < 640px (Default)
- sm: ≥ 640px - sm:
- md: ≥ 768px - md:
- lg: ≥ 1024px - lg:
- xl: ≥ 1280px - xl:
- 2xl: ≥ 1536px - 2xl:

Container:
- Default: width: 100%
- sm: max-width: 640px
- md: max-width: 768px
- lg: max-width: 1024px
- xl: max-width: 1280px
- 2xl: max-width: 1536px

Usage Examples:
- Responsive Grid: <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">...</div>
- Responsive Spacing: <div class="p-4 md:p-6 lg:p-8">...</div>
- Responsive Typography: <h1 class="text-heading-3 md:text-heading-2 lg:text-heading-1">...</h1>
- Responsive Display: <div class="hidden md:block">Desktop Only</div>
- Responsive Flex Direction: <div class="flex flex-col md:flex-row">...</div>

Mobile-first Approach:
We follow a mobile-first approach, which means styles are applied to mobile by default and then overridden for larger screens using breakpoint prefixes.
"""

    def _get_layout_utilities(self, query: str) -> str:
        """Get layout utilities based on the query."""
        result = "Layout Utilities:\n\n"

        if "flex" in query.lower():
            result += """
Flexbox Layout:

Basic Flex Container:
```html
<div class="flex">
  <!-- Flex items go here -->
</div>
```

Common Flex Properties:
- Direction: flex-row, flex-col, flex-row-reverse, flex-col-reverse
- Wrap: flex-wrap, flex-nowrap, flex-wrap-reverse
- Justify Content: justify-start, justify-end, justify-center, justify-between, justify-around, justify-evenly
- Align Items: items-start, items-end, items-center, items-baseline, items-stretch
- Align Content: content-start, content-end, content-center, content-between, content-around, content-evenly
- Gap: gap-4, gap-x-4, gap-y-4

Example: Centered content both horizontally and vertically:
```html
<div class="flex items-center justify-center h-screen">
  <div>Centered Content</div>
</div>
```
"""

        if "grid" in query.lower():
            result += """
Grid Layout:

Basic Grid:
```html
<div class="grid grid-cols-3 gap-4">
  <div>Item 1</div>
  <div>Item 2</div>
  <div>Item 3</div>
  <div>Item 4</div>
  <div>Item 5</div>
  <div>Item 6</div>
</div>
```

Common Grid Properties:
- Grid Template Columns: grid-cols-1, grid-cols-2, grid-cols-3, grid-cols-4, grid-cols-12
- Grid Column Span: col-span-1, col-span-2, col-span-full
- Grid Template Rows: grid-rows-1, grid-rows-2, grid-rows-3
- Grid Row Span: row-span-1, row-span-2, row-span-full
- Grid Auto Flow: grid-flow-row, grid-flow-col
- Gap: gap-4, gap-x-4, gap-y-4

Example: Responsive grid with different column counts:
```html
<div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
  <!-- Grid items go here -->
</div>
```
"""

        if "container" in query.lower():
            result += """
Container:

Standard Container:
```html
<div class="container mx-auto px-4">
  <!-- Content goes here -->
</div>
```

Centered Container with max-width at different breakpoints:
```html
<div class="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl">
  <!-- Content goes here -->
</div>
```

Common Container Utilities:
- Width constraints: max-w-xs, max-w-sm, max-w-md, max-w-lg, max-w-xl, max-w-2xl, max-w-3xl, max-w-4xl, max-w-5xl, max-w-6xl, max-w-7xl
- Responsive padding: px-4 sm:px-6 lg:px-8
"""

        return result

    def _generate_utility_classes(self, query: str) -> str:
        """Generate utility classes based on the query."""
        # Analyze the query to determine which utility classes to generate
        result = "Tailwind Utility Classes:\n\n"

        if "button" in query.lower():
            result += """
Button Classes:

Primary Button:
```html
<button class="inline-flex items-center justify-center rounded-md bg-brazilian-sun text-midnight-black px-4 py-2 text-button font-medium hover:bg-brazilian-sun/90 active:bg-brazilian-sun/80 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amazon-green focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none">
  Button Text
</button>
```

Secondary Button:
```html
<button class="inline-flex items-center justify-center rounded-md border border-amazon-green text-amazon-green px-4 py-2 text-button font-medium hover:bg-amazon-green/10 active:bg-amazon-green/15 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amazon-green focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none">
  Button Text
</button>
```

Small Button:
```html
<button class="inline-flex items-center justify-center rounded-md bg-brazilian-sun text-midnight-black px-3 py-2 text-body-small font-medium hover:bg-brazilian-sun/90 active:bg-brazilian-sun/80 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amazon-green focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none">
  Button Text
</button>
```

Full-width Button:
```html
<button class="w-full inline-flex items-center justify-center rounded-md bg-brazilian-sun text-midnight-black px-4 py-2 text-button font-medium hover:bg-brazilian-sun/90 active:bg-brazilian-sun/80 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amazon-green focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none">
  Button Text
</button>
```

Icon Button:
```html
<button class="inline-flex items-center justify-center rounded-md bg-brazilian-sun text-midnight-black p-2 hover:bg-brazilian-sun/90 active:bg-brazilian-sun/80 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amazon-green focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none">
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M5 12h14"></path>
    <path d="M12 5v14"></path>
  </svg>
</button>
```
"""

        elif "card" in query.lower():
            result += """
Card Classes:

Basic Card:
```html
<div class="bg-white border border-mist rounded-lg shadow-md p-6">
  Card Content
</div>
```

Card with Header and Footer:
```html
<div class="bg-white border border-mist rounded-lg shadow-md">
  <div class="p-6 border-b border-mist">
    <h3 class="text-heading-4 font-heading font-semibold text-midnight-black">Card Title</h3>
    <p class="text-body-small text-slate">Card description</p>
  </div>
  <div class="p-6">
    Card Content
  </div>
  <div class="p-6 border-t border-mist flex justify-end">
    <button class="bg-brazilian-sun text-midnight-black px-4 py-2 rounded-md">Action</button>
  </div>
</div>
```

Product Card:
```html
<div class="bg-white border border-mist rounded-lg shadow-md overflow-hidden transition-all hover:shadow-lg">
  <div class="aspect-square relative">
    <img src="/path/to/image.jpg" alt="Product" class="object-cover w-full h-full transition-transform hover:scale-105" />
  </div>
  <div class="p-4">
    <p class="text-body-small text-slate mb-1">Category</p>
    <h3 class="text-heading-5 font-heading mb-2 line-clamp-2">Product Name</h3>
    <div class="flex items-center justify-between mt-2">
      <p class="text-body font-semibold">$99.99</p>
      <button class="bg-brazilian-sun text-midnight-black px-3 py-2 text-body-small rounded-md">Add to Cart</button>
    </div>
  </div>
</div>
```

Interactive Card with Hover Effect:
```html
<div class="bg-white border border-mist rounded-lg shadow-md p-6 transition-all duration-300 hover:shadow-lg hover:border-amazon-green hover:-translate-y-1 cursor-pointer">
  <h3 class="text-heading-5 font-heading font-semibold text-midnight-black mb-2">Interactive Card</h3>
  <p class="text-body text-charcoal">Card content that responds to hover state.</p>
</div>
```
"""

        elif "form" in query.lower() or "input" in query.lower():
            result += """
Form Elements Classes:

Text Input:
```html
<input
  type="text"
  class="flex h-10 w-full rounded-md border border-mist bg-white px-3 py-2 text-body text-midnight-black placeholder:text-slate focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amazon-green disabled:cursor-not-allowed disabled:bg-cloud disabled:text-slate"
  placeholder="Enter text"
/>
```

Text Input with Label:
```html
<div class="space-y-2">
  <label class="text-body-small font-medium text-midnight-black">Label</label>
  <input
    type="text"
    class="flex h-10 w-full rounded-md border border-mist bg-white px-3 py-2 text-body text-midnight-black placeholder:text-slate focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amazon-green disabled:cursor-not-allowed disabled:bg-cloud disabled:text-slate"
    placeholder="Enter text"
  />
</div>
```

Text Input with Error:
```html
<div class="space-y-2">
  <label class="text-body-small font-medium text-midnight-black">Label</label>
  <input
    type="text"
    class="flex h-10 w-full rounded-md border border-error bg-white px-3 py-2 text-body text-midnight-black placeholder:text-slate focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-error disabled:cursor-not-allowed disabled:bg-cloud disabled:text-slate"
    placeholder="Enter text"
  />
  <p class="text-body-small text-error">Error message</p>
</div>
```

Textarea:
```html
<textarea
  class="flex min-h-[80px] w-full rounded-md border border-mist bg-white px-3 py-2 text-body text-midnight-black placeholder:text-slate focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amazon-green disabled:cursor-not-allowed disabled:bg-cloud disabled:text-slate"
  placeholder="Enter text"
></textarea>
```

Select:
```html
<select class="flex h-10 w-full rounded-md border border-mist bg-white px-3 py-2 text-body text-midnight-black focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amazon-green disabled:cursor-not-allowed disabled:bg-cloud disabled:text-slate">
  <option value="" disabled selected>Select an option</option>
  <option value="option1">Option 1</option>
  <option value="option2">Option 2</option>
  <option value="option3">Option 3</option>
</select>
```

Checkbox:
```html
<div class="flex items-center space-x-2">
  <input
    type="checkbox"
    id="checkbox"
    class="h-4 w-4 rounded border-mist text-amazon-green focus:ring-amazon-green"
  />
  <label for="checkbox" class="text-body text-midnight-black">Checkbox Label</label>
</div>
```

Radio:
```html
<div class="flex items-center space-x-2">
  <input
    type="radio"
    id="radio"
    name="radio-group"
    class="h-4 w-4 border-mist text-amazon-green focus:ring-amazon-green"
  />
  <label for="radio" class="text-body text-midnight-black">Radio Label</label>
</div>
```

Input Group with Icon:
```html
<div class="relative">
  <div class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-slate">
      <circle cx="11" cy="11" r="8"></circle>
      <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
    </svg>
  </div>
  <input
    type="text"
    class="flex h-10 w-full rounded-md border border-mist bg-white pl-10 pr-3 py-2 text-body text-midnight-black placeholder:text-slate"
    placeholder="Search..."
  />
</div>
```

Complete Form:
```html
<form class="space-y-6">
  <div class="space-y-2">
    <label class="text-body-small font-medium text-midnight-black">Full Name</label>
    <input
      type="text"
      class="flex h-10 w-full rounded-md border border-mist bg-white px-3 py-2 text-body text-midnight-black"
      placeholder="Enter your name"
    />
  </div>

  <div class="space-y-2">
    <label class="text-body-small font-medium text-midnight-black">Email Address</label>
    <input
      type="email"
      class="flex h-10 w-full rounded-md border border-mist bg-white px-3 py-2 text-body text-midnight-black"
      placeholder="Enter your email"
    />
  </div>

  <div class="space-y-2">
    <label class="text-body-small font-medium text-midnight-black">Message</label>
    <textarea
      class="flex min-h-[120px] w-full rounded-md border border-mist bg-white px-3 py-2 text-body text-midnight-black"
      placeholder="Enter your message"
    ></textarea>
  </div>

  <div class="flex items-center space-x-2">
    <input
      type="checkbox"
      id="terms"
      class="h-4 w-4 rounded border-mist text-amazon-green focus:ring-amazon-green"
    />
    <label for="terms" class="text-body-small text-charcoal">I agree to the terms and conditions</label>
  </div>

  <button type="submit" class="w-full inline-flex items-center justify-center rounded-md bg-brazilian-sun text-midnight-black px-4 py-2 text-button font-medium">
    Submit Form
  </button>
</form>
```
"""

        elif "alert" in query.lower() or "notification" in query.lower():
            result += """
Alert/Notification Classes:

Success Alert:
```html
<div class="bg-success/10 border border-success text-success px-4 py-3 rounded-md flex items-start">
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-2 mt-0.5">
    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
    <polyline points="22 4 12 14.01 9 11.01"></polyline>
  </svg>
  <div>
    <h4 class="font-semibold text-body">Success!</h4>
    <p class="text-body-small">Your changes have been saved successfully.</p>
  </div>
</div>
```
"""

        elif "nav" in query.lower() or "navigation" in query.lower():
            result += """
Navigation Classes:

Navbar:
```html
<nav class="bg-white shadow-md px-4 py-4">
  <div class="container mx-auto flex justify-between items-center">
    <div class="flex items-center">
      <span class="text-heading-4 font-heading font-bold text-midnight-black">Logo</span>
    </div>

    <div class="hidden md:flex space-x-6">
      <a href="#" class="text-body font-medium text-midnight-black border-b-2 border-brazilian-sun">Home</a>
      <a href="#" class="text-body font-medium text-charcoal hover:text-midnight-black">About</a>
      <a href="#" class="text-body font-medium text-charcoal hover:text-midnight-black">Services</a>
      <a href="#" class="text-body font-medium text-charcoal hover:text-midnight-black">Contact</a>
    </div>

    <div>
      <button class="inline-flex items-center justify-center rounded-md bg-brazilian-sun text-midnight-black px-4 py-2 text-button font-medium">
        Sign In
      </button>
    </div>

    <button class="md:hidden">
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="3" y1="12" x2="21" y2="12"></line>
        <line x1="3" y1="6" x2="21" y2="6"></line>
        <line x1="3" y1="18" x2="21" y2="18"></line>
      </svg>
    </button>
  </div>
</nav>
```

Tabs:
```html
<div class="border-b border-mist">
  <nav class="flex space-x-8">
    <a href="#" class="border-b-2 border-brazilian-sun py-4 px-1 text-body font-medium text-midnight-black">
      Dashboard
    </a>
    <a href="#" class="border-b-2 border-transparent py-4 px-1 text-body font-medium text-slate hover:text-charcoal hover:border-mist">
      Team
    </a>
    <a href="#" class="border-b-2 border-transparent py-4 px-1 text-body font-medium text-slate hover:text-charcoal hover:border-mist">
      Projects
    </a>
    <a href="#" class="border-b-2 border-transparent py-4 px-1 text-body font-medium text-slate hover:text-charcoal hover:border-mist">
      Calendar
    </a>
  </nav>
</div>
```

Pagination:
```html
<nav class="flex items-center justify-center space-x-2 mt-8">
  <a href="#" class="px-3 py-2 rounded-md border border-mist text-slate hover:bg-cloud">
    <span class="sr-only">Previous</span>
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <polyline points="15 18 9 12 15 6"></polyline>
    </svg>
  </a>
  <a href="#" class="px-3 py-1 rounded-md bg-brazilian-sun text-midnight-black font-medium">1</a>
  <a href="#" class="px-3 py-1 rounded-md text-charcoal hover:bg-cloud">2</a>
  <a href="#" class="px-3 py-1 rounded-md text-charcoal hover:bg-cloud">3</a>
  <span class="px-3 py-1 text-slate">...</span>
  <a href="#" class="px-3 py-1 rounded-md text-charcoal hover:bg-cloud">8</a>
  <a href="#" class="px-3 py-1 rounded-md text-charcoal hover:bg-cloud">9</a>
  <a href="#" class="px-3 py-2 rounded-md border border-mist text-slate hover:bg-cloud">
    <span class="sr-only">Next</span>
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <polyline points="9 18 15 12 9 6"></polyline>
    </svg>
  </a>
</nav>
```
"""

        return result

    def generate_component(
            self,
            component_type: str,
            variant: str = "default",
            props: Dict = None) -> str:
        """
        Generate a specific Tailwind component with customizable props.

        Args:
            component_type: Type of component (button, card, input, etc.)
            variant: Variant of the component (primary, secondary, etc.)
            props: Dictionary of properties to customize the component

        Returns:
            HTML string of the generated component
        """
        props = props or {}

        # Implementation would create HTML with Tailwind classes based on
        # parameters
        query = f"{component_type} {variant}"
        component_html = self._generate_utility_classes(query)

        # In a real implementation, we'd parse the HTML and inject props
        # For now, we'll just return the component HTML
        return component_html

    def analyze_tailwind_classes(self, html_snippet: str) -> str:
        """
        Analyze Tailwind classes in an HTML snippet and provide explanations.

        Args:
            html_snippet: HTML code containing Tailwind classes

        Returns:
            Explanation of the Tailwind classes used
        """
        # In a real implementation, we would:
        # 1. Extract all classes from the HTML
        # 2. Group them by category (layout, color, typography, etc.)
        # 3. Provide explanations for each class

        # Example implementation (simplified):
        class_pattern = re.compile(r'class="([^"]*)"')
        matches = class_pattern.findall(html_snippet)

        if not matches:
            return "No Tailwind classes found in the HTML snippet."

        all_classes = []
        for match in matches:
            all_classes.extend(match.split())

        # Group classes by category (simplified)
        categories = {
            "Layout": [],
            "Typography": [],
            "Colors": [],
            "Spacing": [],
            "Flexbox/Grid": [],
            "Borders": [],
            "Effects": [],
            "Interactions": [],
            "Other": []
        }

        for cls in all_classes:
            if cls.startswith(("w-", "h-", "max-w-", "min-h-")):
                categories["Layout"].append(cls)
            elif cls.startswith(("text-", "font-")):
                categories["Typography"].append(cls)
            elif cls.startswith(("bg-", "text-", "border-")) and "-" in cls:
                categories["Colors"].append(cls)
            elif cls.startswith(("m-", "p-", "gap-", "space-")):
                categories["Spacing"].append(cls)
            elif cls.startswith(("flex", "grid", "items-", "justify-")):
                categories["Flexbox/Grid"].append(cls)
            elif cls.startswith(("border", "rounded")):
                categories["Borders"].append(cls)
            elif cls.startswith(("shadow", "opacity")):
                categories["Effects"].append(cls)
            elif cls.startswith(("hover:", "focus:", "active:", "disabled:")):
                categories["Interactions"].append(cls)
            else:
                categories["Other"].append(cls)

        # Build explanation
        explanation = "Tailwind Class Analysis:\n\n"

        for category, classes in categories.items():
            if classes:
                explanation += f"{category}:\n"
                explanation += ", ".join(classes) + "\n\n"

        return explanation
