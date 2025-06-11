"""
Design System Tool - Provides utilities for working with the Artesanato design system
"""

import json
import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from langchain_core.tools import BaseTool
from pydantic import BaseModel, ValidationError

from tools.base_tool import ArtesanatoBaseTool

load_dotenv()


class DesignSystemTool(ArtesanatoBaseTool):
    """Tool for working with the Artesanato design system."""

    name: str = "design_system_tool"
    description: str = "Tool for generating and retrieving design system components and specifications"

    design_system: Dict[str, Any] = {
        "colors": {
            "brazilian-sun": "#FFC12B",
            "amazon-green": "#036B52",
            "artesanato-clay": "#A44A3F",
            "midnight-black": "#1A1A1A",
            "charcoal": "#404040",
            "slate": "#707070",
            "mist": "#E0E0E0",
            "cloud": "#F5F5F5",
            "white": "#FFFFFF",
            "success": "#0D8A6A",
            "warning": "#FFA726",
            "error": "#D32F2F",
            "info": "#2196F3",
        },
        "typography": {
            "families": {
                "heading": "Montserrat",
                "body": "Open Sans",
            },
            "sizes": {
                "heading-1": {"size": "32px", "lineHeight": "40px", "weight": "bold"},
                "heading-2": {"size": "24px", "lineHeight": "32px", "weight": "bold"},
                "heading-3": {"size": "20px", "lineHeight": "28px", "weight": "semibold"},
                "heading-4": {"size": "18px", "lineHeight": "24px", "weight": "semibold"},
                "heading-5": {"size": "16px", "lineHeight": "24px", "weight": "semibold"},
                "body-large": {"size": "18px", "lineHeight": "28px", "weight": "regular"},
                "body": {"size": "16px", "lineHeight": "24px", "weight": "regular"},
                "body-small": {"size": "14px", "lineHeight": "20px", "weight": "regular"},
                "caption": {"size": "12px", "lineHeight": "16px", "weight": "medium"},
                "button": {"size": "16px", "lineHeight": "24px", "weight": "semibold"},
            },
        },
        "spacing": {
            "0": "0px",
            "1": "4px",
            "2": "8px",
            "3": "12px",
            "4": "16px",
            "5": "20px",
            "6": "24px",
            "8": "32px",
            "10": "40px",
            "12": "48px",
            "16": "64px",
            "20": "80px",
            "24": "96px",
        },
        "borderRadius": {
            "none": "0px",
            "sm": "2px",
            "md": "4px",
            "lg": "8px",
            "xl": "12px",
            "2xl": "16px",
            "full": "9999px",
        },
        "components": {
            "button": {
                "variants": ["primary", "secondary", "tertiary", "ghost", "link"],
                "sizes": ["sm", "md", "lg", "icon"],
                "states": ["default", "hover", "active", "focus", "disabled"],
            },
            "card": {
                "variants": ["default", "interactive", "highlighted"],
                "parts": ["header", "content", "footer"],
                "shadows": ["none", "sm", "md", "lg", "xl"],
            },
            "input": {
                "variants": ["default", "error", "success"],
                "states": ["default", "focus", "disabled"],
            },
        },
    }

    class InputSchema(BaseModel):
        query: str

    def _run(self, query: str) -> str:
        """Execute Design System operations with input validation and error handling."""
        try:
            # Input validation
            validated = self.InputSchema(query=query)
            query = validated.query

            if "color" in query.lower() or "palette" in query.lower():
                return self._get_color_palette()

            elif "typography" in query.lower() or "font" in query.lower():
                return self._get_typography_specs()

            elif "spacing" in query.lower():
                return self._get_spacing_specs()

            elif "component" in query.lower():
                if "button" in query.lower():
                    return self._get_button_specs()
                elif "card" in query.lower():
                    return self._get_card_specs()
                elif "input" in query.lower() or "form" in query.lower():
                    return self._get_input_specs()
                else:
                    return self._get_component_overview()

            elif "icon" in query.lower():
                return self._get_icon_specs()

            elif "design token" in query.lower():
                return self._get_design_tokens()

            elif "overview" in query.lower() or "all" in query.lower():
                return self._get_design_system_overview()

            # Generic response
            return (
                "Design System operation processed. Please specify if you need information about "
                "colors, typography, spacing, components, icons, or design tokens.")
        except ValidationError as ve:
            return self.handle_error(ve, f"{self.name}._run.input_validation")
        except Exception as e:
            return self.handle_error(e, f"{self.name}._run")

    def _arun(self, query: str) -> str:
        """Async version of _run."""
        return self._run(query)

    def _get_color_palette(self) -> str:
        """Get the color palette."""
        colors = self.design_system["colors"]

        result = "# Artesanato Design System: Color Palette\n\n"

        result += "## Primary Colors\n\n"
        result += "| Name | Hex | RGB | Usage |\n"
        result += "|------|-----|-----|-------|\n"
        result += f"| Brazilian Sun | {
            colors['brazilian-sun']} | rgb(255, 193, 43) | Primary buttons, call-to-actions, highlights |\n"
        result += f"| Amazon Green | {
            colors['amazon-green']} | rgb(3, 107, 82) | Secondary elements, success states, accents |\n"
        result += f"| Artesanato Clay | {
            colors['artesanato-clay']} | rgb(164, 74, 63) | Tertiary elements, decorative accents |\n\n"

        result += "## Neutral Colors\n\n"
        result += "| Name | Hex | RGB | Usage |\n"
        result += "|------|-----|-----|-------|\n"
        result += f"| Midnight Black | {
            colors['midnight-black']} | rgb(26, 26, 26) | Primary text, high-emphasis elements |\n"
        result += f"| Charcoal | {
            colors['charcoal']} | rgb(64, 64, 64) | Secondary text, medium-emphasis elements |\n"
        result += f"| Slate | {
            colors['slate']} | rgb(112, 112, 112) | Tertiary text, low-emphasis elements |\n"
        result += f"| Mist | {
            colors['mist']} | rgb(224, 224, 224) | Borders, dividers, subtle elements |\n"
        result += f"| Cloud | {
            colors['cloud']} | rgb(245, 245, 245) | Backgrounds, cards, containers |\n"
        result += f"| White | {
            colors['white']} | rgb(255, 255, 255) | Page backgrounds, high-contrast elements |\n\n"

        result += "## Semantic Colors\n\n"
        result += "| Name | Hex | RGB | Usage |\n"
        result += "|------|-----|-----|-------|\n"
        result += f"| Success | {
            colors['success']} | rgb(13, 138, 106) | Success messages, positive actions |\n"
        result += f"| Warning | {
            colors['warning']} | rgb(255, 167, 38) | Warning messages, caution states |\n"
        result += f"| Error | {
            colors['error']} | rgb(211, 47, 47) | Error messages, destructive actions |\n"
        result += f"| Info | {
            colors['info']} | rgb(33, 150, 243) | Information messages, neutral states |\n\n"

        result += "## Color Usage Guidelines\n\n"
        result += "- Use Brazilian Sun for primary buttons and important call-to-actions\n"
        result += "- Use Amazon Green for secondary interactive elements and success states\n"
        result += "- Use Artesanato Clay for decorative elements and tertiary actions\n"
        result += "- Use neutral colors for text, backgrounds, and UI containers\n"
        result += "- Use semantic colors consistently for their designated purposes\n"

        return result

    def _get_typography_specs(self) -> str:
        """Get typography specifications."""
        typography = self.design_system["typography"]

        result = "# Artesanato Design System: Typography\n\n"

        result += "## Font Families\n\n"
        result += "| Usage | Font Family |\n"
        result += "|-------|------------|\n"
        result += f"| Headings | {typography['families']['heading']} |\n"
        result += f"| Body Text | {typography['families']['body']} |\n\n"

        result += "## Type Scale\n\n"
        result += "| Name | Size | Line Height | Font Weight | Usage |\n"
        result += "|------|------|-------------|------------|-------|\n"

        sizes = typography["sizes"]
        for name, specs in sizes.items():
            result += f"| {name} | {
                specs['size']} | {
                specs['lineHeight']} | {
                specs['weight']} | "

            if "heading" in name:
                result += f"Section headings, level {name[-1]} |\n"
            elif name == "body-large":
                result += "Lead paragraphs, important text |\n"
            elif name == "body":
                result += "Standard paragraph text |\n"
            elif name == "body-small":
                result += "Secondary text, captions, metadata |\n"
            elif name == "caption":
                result += "Small labels, timestamps, footnotes |\n"
            elif name == "button":
                result += "Button labels, interactive elements |\n"
            else:
                result += "- |\n"

        result += "\n## Typography Usage Guidelines\n\n"
        result += "- Use Montserrat for all headings and maintain consistent hierarchy\n"
        result += "- Use Open Sans for all body text, labels, and UI text\n"
        result += "- Maintain a minimum 16px font size for body text to ensure readability\n"
        result += "- Use appropriate line heights to ensure proper readability\n"
        result += "- Limit line length to 60-80 characters for optimal reading experience\n"
        result += "- Always ensure sufficient color contrast for accessibility\n"

        return result

    def _get_spacing_specs(self) -> str:
        """Get spacing specifications."""
        spacing = self.design_system["spacing"]
        border_radius = self.design_system["borderRadius"]

        result = "# Artesanato Design System: Spacing & Layout\n\n"

        result += "## Spacing Scale\n\n"
        result += "| Token | Value | Usage |\n"
        result += "|-------|-------|-------|\n"

        spacing_usage = {
            "0": "No spacing, flush elements",
            "1": "Tiny spacing between very close elements",
            "2": "Small spacing between related elements",
            "3": "Spacing between related elements",
            "4": "Standard spacing between elements",
            "5": "Medium spacing between groups of elements",
            "6": "Default section padding",
            "8": "Large section padding",
            "10": "Extra large section padding",
            "12": "Spacing between major sections",
            "16": "Large spacing between major sections",
            "20": "Extra large spacing between major sections",
            "24": "Maximum spacing for page layout",
        }

        for token, value in spacing.items():
            usage = spacing_usage.get(token, "-")
            result += f"| {token} | {value} | {usage} |\n"

        result += "\n## Border Radius\n\n"
        result += "| Token | Value | Usage |\n"
        result += "|-------|-------|-------|\n"

        radius_usage = {
            "none": "No border radius, square corners",
            "sm": "Subtle rounded corners",
            "md": "Standard rounded corners for most UI elements",
            "lg": "More pronounced rounded corners for cards, modals",
            "xl": "Large rounded corners for floating elements",
            "2xl": "Very large rounded corners for promotional elements",
            "full": "Circular or pill-shaped elements",
        }

        for token, value in border_radius.items():
            usage = radius_usage.get(token, "-")
            result += f"| {token} | {value} | {usage} |\n"

        result += "\n## Spacing Guidelines\n\n"
        result += "- Use the spacing scale consistently throughout the application\n"
        result += "- Maintain consistent spacing between similar elements\n"
        result += "- Use larger spacing values to separate different sections\n"
        result += "- Ensure adequate whitespace for readability\n"
        result += "- Scale spacing proportionally on different device sizes\n"

        return result

    def _get_button_specs(self) -> str:
        """Get button component specifications."""
        button = self.design_system["components"]["button"]

        result = "# Artesanato Design System: Button Components\n\n"

        result += "## Button Variants\n\n"
        result += "| Variant | Usage | Visual Style |\n"
        result += "|---------|-------|-------------|\n"
        result += "| primary | Main actions, form submissions | Solid Brazilian Sun background, dark text |\n"
        result += "| secondary | Alternative actions, secondary flows | Solid Amazon Green background, white text |\n"
        result += "| tertiary | Less prominent actions | Artesanato Clay outline, Artesanato Clay text |\n"
        result += "| ghost | Subtle actions within context | No background, colored text only |\n"
        result += "| link | Navigational elements styled as links | No background, underlined text |\n"

        result += "\n## Button Sizes\n\n"
        result += "| Size | Usage | Dimensions |\n"
        result += "|------|-------|------------|\n"
        result += "| sm | Compact UI areas, inline actions | Height: 32px, Padding: 12px |\n"
        result += "| md | Standard button size for most uses | Height: 40px, Padding: 16px |\n"
        result += "| lg | Prominent calls-to-action | Height: 48px, Padding: 20px |\n"
        result += "| icon | Icon-only buttons | Square with equal height/width |\n"

        result += "\n## Button States\n\n"
        result += "Buttons respond to the following states with visual feedback:\n\n"
        result += "- **default**: Normal resting state\n"
        result += "- **hover**: When cursor is positioned over the button\n"
        result += "- **active**: During click/tap interaction\n"
        result += "- **focus**: When the button has keyboard focus\n"
        result += "- **disabled**: When the button is not interactive\n"

        result += "\n## Example Button Implementation\n\n"
        result += "```html\n"
        result += '<button class="btn btn-primary btn-md">\n'
        result += '  <span class="btn-text">Button Label</span>\n'
        result += "</button>\n"
        result += "```\n\n"

        result += "## Button Usage Guidelines\n\n"
        result += "- Use primary buttons for the main action in a section\n"
        result += "- Limit the number of primary buttons on a single page\n"
        result += "- Use secondary or tertiary buttons for alternative actions\n"
        result += "- Maintain consistent button sizing within the same context\n"
        result += "- Use clear, actionable labels (start with verbs)\n"
        result += "- Ensure buttons have adequate touch targets (minimum 44x44px)\n"

        return result

    def _get_card_specs(self) -> str:
        """Get card component specifications."""
        card = self.design_system["components"]["card"]

        result = "# Artesanato Design System: Card Components\n\n"

        result += "## Card Variants\n\n"
        result += "| Variant | Usage | Visual Style |\n"
        result += "|---------|-------|-------------|\n"
        result += "| default | Standard information display | White background, subtle border or shadow |\n"
        result += "| interactive | Clickable/tappable cards | Hover effects, cursor changes |\n"
        result += "| highlighted | Featured or promoted content | Brazilian Sun border or accent color |\n"

        result += "\n## Card Parts\n\n"
        result += "Cards can include the following sections:\n\n"
        result += "- **header**: Title bar, often with actions or metadata\n"
        result += "- **content**: Main card content area\n"
        result += "- **footer**: Additional actions or information\n"

        result += "\n## Card Shadow Variants\n\n"
        result += "| Shadow | Usage | Elevation |\n"
        result += "|--------|-------|----------|\n"
        result += "| none | Flat cards with borders only | No elevation |\n"
        result += "| sm | Subtle elevation | Low elevation (2dp) |\n"
        result += "| md | Standard card elevation | Medium elevation (4dp) |\n"
        result += "| lg | Emphasized cards, modals | High elevation (8dp) |\n"
        result += "| xl | Floating cards, popovers | Highest elevation (16dp) |\n"

        result += "\n## Example Card Implementation\n\n"
        result += "```html\n"
        result += '<div class="card card-default shadow-md">\n'
        result += '  <div class="card-header">\n'
        result += '    <h3 class="card-title">Card Title</h3>\n'
        result += '  </div>\n'
        result += '  <div class="card-content">\n'
        result += '    <p>Card content goes here.</p>\n'
        result += '  </div>\n'
        result += '  <div class="card-footer">\n'
        result += '    <button class="btn btn-secondary btn-sm">Action</button>\n'
        result += '  </div>\n'
        result += '</div>\n'
        result += "```\n\n"

        result += "## Card Usage Guidelines\n\n"
        result += "- Use cards to group related information\n"
        result += "- Maintain consistent card sizes within the same view\n"
        result += "- Use appropriate spacing within and between cards\n"
        result += "- Consider responsive behavior of card layouts\n"
        result += "- Use shadows to indicate elevation hierarchy\n"
        result += "- Ensure cards are distinguishable from the background\n"

        return result

    def _get_input_specs(self) -> str:
        """Get input component specifications."""
        input_specs = self.design_system["components"]["input"]

        result = "# Artesanato Design System: Form Input Components\n\n"

        result += "## Input Variants\n\n"
        result += "| Variant | Usage |\n"
        result += "|---------|-------|\n"
        result += "| default | Standard input fields |\n"
        result += "| error | Inputs with validation errors |\n"
        result += "| success | Successfully validated inputs |\n"

        result += "\n## Input States\n\n"
        result += "Inputs respond to the following states with visual feedback:\n\n"
        result += "- **default**: Normal resting state\n"
        result += "- **focus**: When the input has focus\n"
        result += "- **disabled**: When the input is not interactive\n"

        result += "\n## Form Components\n\n"
        result += "### Text Input\n\n"
        result += "```html\n"
        result += '<div class="form-field">\n'
        result += '  <label for="field-id" class="form-label">Field Label</label>\n'
        result += '  <input \n'
        result += '    type="text"\n'
        result += '    id="field-id"\n'
        result += '    class="input-default"\n'
        result += '    placeholder="Enter text"\n'
        result += '  />\n'
        result += '  <p class="form-helper">Helper text goes here</p>\n'
        result += '</div>\n'
        result += "```\n\n"

        result += "### Text Input with Error\n\n"
        result += "```html\n"
        result += '<div class="form-field">\n'
        result += '  <label for="field-id" class="form-label">Field Label</label>\n'
        result += '  <input \n'
        result += '    type="text"\n'
        result += '    id="field-id"\n'
        result += '    class="input-error"\n'
        result += '    placeholder="Enter text"\n'
        result += '  />\n'
        result += '  <p class="form-error">Error message goes here</p>\n'
        result += '</div>\n'
        result += "```\n\n"

        result += "### Select Dropdown\n\n"
        result += "```html\n"
        result += '<div class="form-field">\n'
        result += '  <label for="select-id" class="form-label">Select Label</label>\n'
        result += '  <select id="select-id" class="select-default">\n'
        result += '    <option value="">Select an option</option>\n'
        result += '    <option value="option1">Option 1</option>\n'
        result += '    <option value="option2">Option 2</option>\n'
        result += '  </select>\n'
        result += '</div>\n'
        result += "```\n\n"

        result += "## Form Layout Guidelines\n\n"
        result += "- Group related form fields together\n"
        result += "- Use consistent label positioning (above inputs)\n"
        result += "- Show validation errors inline, near the relevant field\n"
        result += "- Use helper text to provide additional guidance\n"
        result += "- Maintain consistent spacing between form fields\n"
        result += "- Consider mobile-friendly form designs with touch targets\n"
        result += "- Use fieldsets for logical form sections\n"

        return result

    def _get_component_overview(self) -> str:
        """Get overview of all components."""
        components = self.design_system["components"]

        result = "# Artesanato Design System: Component Overview\n\n"

        result += "## Available Components\n\n"
        result += "| Component | Description | Variants |\n"
        result += "|-----------|-------------|----------|\n"
        result += f"| Button | Interactive clickable elements | {
            ', '.join(
                components['button']['variants'])} |\n"
        result += f"| Card | Containers for grouped content | {
            ', '.join(
                components['card']['variants'])} |\n"
        result += f"| Input | Form input elements | {
            ', '.join(
                components['input']['variants'])} |\n"
        result += "| Typography | Text elements | heading-1 through heading-5, body variants |\n"
        result += "| Table | Structured data display | default, compact, bordered |\n"
        result += "| Modal | Overlay dialogs | default, alert, fullscreen |\n"
        result += "| Navigation | Site navigation components | navbar, sidebar, breadcrumb, tabs |\n"
        result += "| Dropdown | Expandable option menus | default, contextual |\n"
        result += "| Badge | Small status indicators | default, notification |\n"
        result += "| Alert | Status messages | info, success, warning, error |\n"
        result += "| Tooltips | Contextual help text | default, rich |\n"
        result += "| Pagination | Page navigation controls | default, compact |\n"

        result += "\n## Component Usage Guidelines\n\n"
        result += "- Use components consistently throughout the application\n"
        result += "- Combine components following established patterns\n"
        result += "- Maintain appropriate spacing between components\n"
        result += "- Ensure accessibility for all interactive components\n"
        result += "- Consider responsive behavior for all components\n"
        result += "- Use the appropriate component variant for each context\n"

        return result

    def _get_icon_specs(self) -> str:
        """Get icon specifications."""
        result = "# Artesanato Design System: Icons\n\n"

        result += "## Icon System\n\n"
        result += "Artesanato uses a custom icon system based on SVG icons with consistent styling.\n\n"

        result += "## Icon Sizes\n\n"
        result += "| Size | Dimensions | Usage |\n"
        result += "|------|------------|-------|\n"
        result += "| xs | 12x12px | Very small UI elements |\n"
        result += "| sm | 16x16px | Small UI elements, inline with text |\n"
        result += "| md | 24x24px | Default size for most UI contexts |\n"
        result += "| lg | 32x32px | Larger UI elements, navigation |\n"
        result += "| xl | 48x48px | Featured UI elements, illustrations |\n"

        result += "\n## Icon Categories\n\n"
        result += "- **Navigation**: Arrows, hamburger menu, close\n"
        result += "- **Actions**: Add, edit, delete, save, download\n"
        result += "- **Communication**: Email, chat, phone, notification\n"
        result += "- **E-commerce**: Cart, wishlist, checkout, payment\n"
        result += "- **Media**: Play, pause, volume, fullscreen\n"
        result += "- **Social**: Share, like, comment, follow\n"
        result += "- **Status**: Success, error, warning, info\n"

        result += "\n## Icon Implementation\n\n"
        result += "```html\n"
        result += '<svg class="icon icon-md" aria-hidden="true" focusable="false">\n'
        result += '  <use href="/icons/sprite.svg#icon-name"></use>\n'
        result += '</svg>\n'
        result += "```\n\n"

        result += "For semantic icon usage (when the icon conveys meaning):\n\n"

        result += "```html\n"
        result += '<svg class="icon icon-md" aria-label="Descriptive label" role="img" focusable="false">\n'
        result += '  <use href="/icons/sprite.svg#icon-name"></use>\n'
        result += '</svg>\n'
        result += "```\n\n"

        result += "## Icon Usage Guidelines\n\n"
        result += "- Use icons consistently for the same actions/concepts\n"
        result += "- Combine icons with text for clearer communication\n"
        result += "- Maintain consistent sizing within the same context\n"
        result += "- Use appropriate ARIA attributes for accessibility\n"
        result += "- Consider color variations for different states\n"
        result += "- Optimize SVGs for performance\n"

        return result

    def _get_design_tokens(self) -> str:
        """Get design token specifications."""
        colors = self.design_system["colors"]
        spacing = self.design_system["spacing"]
        border_radius = self.design_system["borderRadius"]

        result = "# Artesanato Design System: Design Tokens\n\n"

        result += "Design tokens are the visual design atoms of the design system—specifically, they are named entities that store visual design attributes.\n\n"

        result += "## Color Tokens\n\n"
        result += "```css\n"
        for name, value in colors.items():
            result += f"--color-{name}: {value};\n"
        result += "```\n\n"

        result += "## Spacing Tokens\n\n"
        result += "```css\n"
        for name, value in spacing.items():
            result += f"--spacing-{name}: {value};\n"
        result += "```\n\n"

        result += "## Border Radius Tokens\n\n"
        result += "```css\n"
        for name, value in border_radius.items():
            result += f"--radius-{name}: {value};\n"
        result += "```\n\n"

        result += "## Typography Tokens\n\n"
        result += "```css\n"
        result += "--font-family-heading: Montserrat, sans-serif;\n"
        result += "--font-family-body: 'Open Sans', sans-serif;\n"
        result += "--font-size-h1: 32px;\n"
        result += "--font-size-h2: 24px;\n"
        result += "--font-size-h3: 20px;\n"
        result += "--font-size-h4: 18px;\n"
        result += "--font-size-h5: 16px;\n"
        result += "--font-size-body-large: 18px;\n"
        result += "--font-size-body: 16px;\n"
        result += "--font-size-body-small: 14px;\n"
        result += "--font-size-caption: 12px;\n"
        result += "--line-height-heading: 1.25;\n"
        result += "--line-height-body: 1.5;\n"
        result += "```\n\n"

        result += "## Shadow Tokens\n\n"
        result += "```css\n"
        result += "--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);\n"
        result += "--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);\n"
        result += "--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);\n"
        result += "--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);\n"
        result += "```\n\n"

        result += "## Transition Tokens\n\n"
        result += "```css\n"
        result += "--transition-fast: 150ms ease;\n"
        result += "--transition-normal: 300ms ease;\n"
        result += "--transition-slow: 500ms ease;\n"
        result += "```\n\n"

        result += "## Usage Guidelines\n\n"
        result += "- Always use design tokens instead of hard-coded values\n"
        result += "- Use the appropriate token for each context\n"
        result += "- Compose complex values from existing tokens when possible\n"
        result += "- Use CSS variables or a preprocessor for implementing tokens\n"
        result += "- Tokens should be documented and shared across platforms\n"

        return result

    def _get_design_system_overview(self) -> str:
        """Get a complete overview of the design system."""
        result = "# Artesanato Design System: Complete Overview\n\n"

        result += "## Introduction\n\n"
        result += "The Artesanato Design System is a comprehensive collection of design standards, components, and guidelines that ensure a consistent, accessible, and high-quality user experience across the Artesanato e-commerce platform. This system reflects Brazilian artisanal heritage while providing modern e-commerce functionality.\n\n"

        result += "## Core Elements\n\n"
        result += "### 1. Color System\n\n"
        result += "- **Primary Colors**: Brazilian Sun, Amazon Green, Artesanato Clay\n"
        result += "- **Neutral Colors**: Midnight Black, Charcoal, Slate, Mist, Cloud, White\n"
        result += "- **Semantic Colors**: Success, Warning, Error, Info\n\n"

        result += "### 2. Typography\n\n"
        result += "- **Headings**: Montserrat (bold, semibold)\n"
        result += "- **Body**: Open Sans (regular, medium, semibold)\n"
        result += "- **Hierarchical scale**: Heading 1-5, Body Large, Body, Body Small, Caption\n\n"

        result += "### 3. Spacing & Layout\n\n"
        result += "- **Spacing scale**: 0-24 tokens for consistent spacing\n"
        result += "- **Border radius**: None to Full scale for different UI elements\n"
        result += "- **Grid system**: 12-column responsive grid\n\n"

        result += "### 4. Components\n\n"
        result += "- **Core UI**: Buttons, Cards, Inputs, Tables\n"
        result += "- **Navigation**: Navbar, Sidebar, Breadcrumbs, Tabs\n"
        result += "- **Feedback**: Alerts, Modals, Toasts\n"
        result += "- **E-commerce**: Product Cards, Cart Items, Checkout Forms\n\n"

        result += "## Design Principles\n\n"
        result += "1. **Authentic**: Celebrate Brazilian artisanal heritage\n"
        result += "2. **Accessible**: Follow WCAG 2.1 AA standards\n"
        result += "3. **Responsive**: Design for all device sizes\n"
        result += "4. **Consistent**: Maintain visual and behavioral consistency\n"
        result += "5. **Efficient**: Optimize for user task completion\n\n"

        result += "## Implementation\n\n"
        result += "The design system is implemented using:\n\n"
        result += "- Figma design libraries and components\n"
        result += "- React component library with TypeScript\n"
        result += "- Tailwind CSS for styling with custom design tokens\n"
        result += "- Storybook for component documentation\n"
        result += "- Automated accessibility and visual regression testing\n\n"

        result += "## Resources\n\n"
        result += "- Design System Documentation\n"
        result += "- Component Library\n"
        result += "- Design Token Reference\n"
        result += "- Figma UI Kit\n"
        result += "- Accessibility Guidelines\n"

        return result
