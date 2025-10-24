# Design System - CRM Bitrix Admin Panel

This document defines the complete design system for the CRM Bitrix admin interface, extracted from Figma designs (nodes 263:1711 and 626:206). All components must follow these rules to maintain pixel-perfect consistency.

---

## Table of Contents

1. [Color System](#color-system)
2. [Typography](#typography)
3. [Spacing & Layout](#spacing--layout)
4. [Component Library](#component-library)
5. [Patterns & Guidelines](#patterns--guidelines)
6. [Implementation Rules](#implementation-rules)

---

## Color System

### Primary Colors

```javascript
// Primary UI Color
#8A49F3 - Purple (primary brand color, active states, buttons)

// Neutral Colors
#000000 - Black (text, headings)
#FFFFFF - White (backgrounds, surfaces)
```

### Grey Scale

```javascript
// Grey Scale (for secondary text and UI elements)
#6B6773 - Grey 1 (disabled/inactive text, secondary labels)
#828282 - Grey 2 (placeholder text, help text)
#E2E2E2 - Grey 3 (borders, dividers)
#E8E8E8 - Grey 4 (light backgrounds)
#EFEBF6 - Grey 5 / Violet 1 (inactive pill backgrounds, light backgrounds)
#F2F2F2 - Grey 6 (input backgrounds)
```

### Status Colors

Used for order status badges and state indicators:

```javascript
// Status Badge Colors
#EB5757 - Red (НОВЫЙ - New orders)
#5E81DC - Blue (ОПЛАЧЕН - Paid)
#DC5EC0 - Pink/Magenta (ПРИНЯТ - Accepted)
#F8C20B - Yellow (СОБРАН - Assembled)
#7FC663 - Green (В ПУТИ - In transit)
```

### Color Usage Guidelines

| Color | Usage |
|-------|-------|
| Purple (#8A49F3) | Active tabs, primary buttons, selected states, active toggles |
| Black (#000000) | Primary text, headings, body text |
| White (#FFFFFF) | Main backgrounds, button backgrounds, surface overlays |
| Grey 1 (#6B6773) | Disabled product names, disabled text |
| Grey 2 (#828282) | Placeholder text in inputs, helper text |
| Grey 3 (#E2E2E2) | Borders around buttons, divider lines |
| Violet 1 (#EFEBF6) | Inactive pill backgrounds, inactive badge backgrounds |
| Red (#EB5757) | Status: New/Pending |
| Blue (#5E81DC) | Status: Paid/Completed |
| Pink (#DC5EC0) | Status: Accepted/In Progress |
| Yellow (#F8C20B) | Status: Assembled/Ready |
| Green (#7FC663) | Status: In Transit/Shipping |

---

## Typography

### Font Family

```css
font-family: 'Open Sans', sans-serif;
```

All text uses Open Sans. No other fonts should be used.

### Type Scale

```javascript
// Heading 1 (Page Titles)
{
  fontSize: 24px,
  fontWeight: 400,  // Regular
  lineHeight: '100%',
  fontFamily: 'Open Sans'
}

// Heading 2 / Body Bold (Section Titles, Product Names)
{
  fontSize: 16px,
  fontWeight: 700,  // Bold
  lineHeight: '100%',
  fontFamily: 'Open Sans'
}

// Body Regular (Default Text)
{
  fontSize: 16px,
  fontWeight: 400,  // Regular
  lineHeight: '100%',
  fontFamily: 'Open Sans'
}

// Body SemiBold (Emphasis within body)
{
  fontSize: 16px,
  fontWeight: 600,  // SemiBold
  lineHeight: '100%',
  fontFamily: 'Open Sans'
}

// Label (Small pills, badges)
{
  fontSize: 14px,
  fontWeight: 400,  // Regular
  lineHeight: '100%',
  fontFamily: 'Open Sans'
}

// Caption / Small Text
{
  fontSize: 12px,
  fontWeight: 400,  // Regular
  lineHeight: '100%',
  fontFamily: 'Open Sans'
}

// Status Labels (uppercase)
{
  fontSize: 12px,
  fontWeight: 400,
  lineHeight: '100%',
  fontFamily: 'Open Sans',
  textTransform: 'uppercase',
  letterSpacing: '1.2px'
}
```

### Typography Usage

| Style | Size | Weight | Usage |
|-------|------|--------|-------|
| H1 | 24px | 400 | Page titles ("Товары", "Заказы") |
| H2/Bold | 16px | 700 | Section titles, product names, order numbers |
| Body | 16px | 400 | Default text, descriptions, dates |
| SemiBold | 16px | 600 | Emphasized text within body |
| Label | 14px | 400 | Filter pills, secondary labels |
| Caption | 12px | 400 | Status badges, small helper text |
| Caption Uppercase | 12px | 400 | Status badge text (must use uppercase + 1.2px tracking) |

---

## Spacing & Layout

### Container & Padding

```css
/* Main content container */
width: 320px;
max-width: 320px;
margin: 0 auto;

/* Standard padding */
padding: 16px;  /* Left/right padding for all sections */

/* Bottom padding (for scrollable areas) */
padding-bottom: 32px;  /* Extra space for action buttons */
```

### Spacing Scale

```javascript
// Standard spacing increments
4px   - Minimal spacing (icon padding)
6px   - Small spacing (badge/pill padding)
10px  - Component gap (flex gaps between items)
12px  - Medium spacing (input padding)
16px  - Standard padding (container, sections)
24px  - Large spacing (section spacing)
32px  - Extra large (bottom padding)
```

### Component Spacing

```javascript
// Tabs/Segmented Control
gap: 0  // No gap, elements touch

// Filter Pills
gap: 10px  // Horizontal spacing between pills

// Product Cards / Order Cards
separator: 1px solid #E2E2E2  // Between items in list

// Flex Components
gap: 10px  // Standard component gap

// Section Dividers
margin-top: 16px
margin-bottom: 16px
border-top: 1px solid #E2E2E2
```

### Layout Patterns

1. **Vertical List Layout**
   - 16px padding on sides
   - 1px grey separator between items
   - No margin/padding between separator and content

2. **Horizontal Tabs**
   - Full-width container
   - Segments are 144px each
   - No gaps between segments
   - White background for selected

3. **Grid/Flex Layouts**
   - Standard gap: 10px
   - Flex wrap for responsive behavior

---

## Component Library

### 1. Segmented Control / Tabs

**Usage**: Product feed tabs ("Товары" / "Готовые товары"), Order filters

**Specifications**:
```javascript
{
  height: 34px,
  container: {
    width: '100%',
    display: 'flex',
    gap: 0,
    borderRadius: '4px',  // Slight rounding for container
    overflow: 'hidden'
  },
  segment: {
    flex: 1,
    minWidth: '144px',
    height: '34px',
    padding: '0',
    fontSize: '14px',
    fontWeight: '400',
    border: 'none',
    cursor: 'pointer',
    transition: 'all 0.2s ease'
  },
  active: {
    backgroundColor: '#8A49F3',  // Purple
    color: '#FFFFFF',  // White text
  },
  inactive: {
    backgroundColor: '#FFFFFF',
    color: '#8A49F3',  // Purple text
  }
}
```

**Implementation**:
```jsx
<div className="flex h-[34px] rounded overflow-hidden w-full">
  <button className="flex-1 bg-white text-purple-primary text-[14px]">Товары</button>
  <button className="flex-1 bg-purple-primary text-white text-[14px]">Готовые товары</button>
</div>
```

---

### 2. Pills / Filter Badges

**Usage**: Filter tags, category tags, status badges

**Specifications (Large Pills)**:
```javascript
{
  height: 'auto',
  padding: '6px 12px',
  fontSize: '16px',
  fontWeight: '400',
  borderRadius: '50px',  // Full rounded
  border: 'none',
  cursor: 'pointer',
  whiteSpace: 'nowrap',
  transition: 'all 0.2s ease'
}

// Active state
{
  backgroundColor: '#8A49F3',  // Purple
  color: '#FFFFFF'
}

// Inactive state
{
  backgroundColor: '#EFEBF6',  // Violet 1
  color: '#000000'  // Black text
}
```

**Specifications (Small Status Badges)**:
```javascript
{
  height: 'auto',
  padding: '3px 6px',
  fontSize: '12px',
  fontWeight: '400',
  textTransform: 'uppercase',
  letterSpacing: '1.2px',
  borderRadius: '21px',
  border: 'none',
  color: '#FFFFFF',
  whiteSpace: 'nowrap'
}

// Color variants by status
// See Status Colors section
```

**Implementation**:
```jsx
// Large pill
<button className="px-3 py-1.5 rounded-full bg-purple-primary text-white text-[16px]">
  Все
</button>

// Small status badge
<div className="px-1.5 py-0.75 rounded-[21px] bg-red-500 text-white text-[12px] uppercase tracking-[1.2px]">
  НОВЫЙ
</div>
```

---

### 3. Search Input

**Usage**: Product search, order search

**Specifications**:
```javascript
{
  height: '46px',
  padding: '12px 16px',
  fontSize: '16px',
  fontWeight: '400',
  backgroundColor: '#F2F2F2',  // Light grey background
  border: 'none',
  borderRadius: '4px',
  color: '#000000',
  placeholder: {
    color: '#828282'  // Grey 2
  },
  icon: {
    position: 'absolute',
    right: '12px',
    width: '16px',
    height: '16px',
    color: '#828282'
  }
}
```

**Implementation**:
```jsx
<div className="relative">
  <input
    type="text"
    placeholder="Найти"
    className="w-full h-[46px] px-4 bg-gray-input rounded text-[16px]"
  />
  <svg className="absolute right-4 top-3 w-4 h-4 text-gray-placeholder">
    {/* Search icon SVG */}
  </svg>
</div>
```

---

### 4. Product Card

**Usage**: Product listings

**Specifications**:
```javascript
{
  layout: 'vertical list',
  itemStructure: {
    image: {
      width: '88px',
      height: '88px',
      objectFit: 'cover'
    },
    content: {
      title: {
        fontSize: '14px',
        fontWeight: '700',
        color: '#000000'
      },
      price: {
        fontSize: '14px',
        fontWeight: '400',
        color: '#000000'
      }
    },
    toggle: {
      // See Toggle Switch component
    }
  },
  separator: '1px solid #E2E2E2',
  disabledState: {
    title: {
      color: '#6B6773'  // Grey 1
    },
    price: {
      color: '#6B6773'
    },
    overlay: {
      backgroundColor: 'rgba(255, 255, 255, 0.6)'
    }
  }
}
```

---

### 5. Action Button

**Usage**: Order actions ("Оплачен", "Принять", "Завершить", etc.)

**Specifications**:
```javascript
{
  height: '38px',
  padding: '8px 16px',
  fontSize: '16px',
  fontWeight: '400',
  backgroundColor: '#FFFFFF',
  border: '1px solid #E2E2E2',
  borderRadius: '4px',
  color: '#000000',
  cursor: 'pointer',
  transition: 'all 0.2s ease',
  hover: {
    backgroundColor: '#F9F9F9'
  },
  active: {
    backgroundColor: '#F2F2F2'
  }
}
```

**Implementation**:
```jsx
<button className="h-[38px] px-4 bg-white border border-gray-border rounded text-[16px] text-black">
  Оплачен
</button>
```

---

### 6. Toggle Switch

**Usage**: Enable/disable products

**Already implemented in existing codebase** (`/src/components/ToggleSwitch.jsx`)

Specifications:
- Sizes: sm (12px), md (16px), lg (20px)
- Colors: Purple for active state
- Smooth animation on toggle

---

### 7. Avatar Group

**Usage**: Order staff/florist avatars, product thumbnails

**Specifications**:
```javascript
{
  avatar: {
    width: '48px',
    height: '48px',
    borderRadius: '50%',
    border: '2px solid #FFFFFF',
    objectFit: 'cover'
  },
  group: {
    display: 'flex',
    layout: 'overlapping',
    marginBetween: '-12px'  // Negative margin for overlap
  }
}
```

**Implementation**:
```jsx
<div className="flex" style={{ marginLeft: -12 }}>
  {avatars.map((avatar, i) => (
    <img
      key={i}
      src={avatar.src}
      alt={avatar.name}
      className="w-12 h-12 rounded-full border-2 border-white"
      style={{ marginLeft: i > 0 ? -12 : 0 }}
    />
  ))}
</div>
```

---

### 8. Status Badge

**Usage**: Order status indicators

**Specifications**:
```javascript
{
  layout: 'small pill',
  padding: '3px 6px',
  fontSize: '12px',
  fontWeight: '400',
  textTransform: 'uppercase',
  letterSpacing: '1.2px',
  borderRadius: '21px',
  border: 'none',
  whiteSpace: 'nowrap',
  colors: {
    'НОВЫЙ': '#EB5757',       // Red
    'ОПЛАЧЕН': '#5E81DC',      // Blue
    'ПРИНЯТ': '#DC5EC0',       // Pink
    'СОБРАН': '#F8C20B',       // Yellow
    'В ПУТИ': '#7FC663',       // Green
    'ДОСТАВЛЕН': '#7FC663'     // Green
  }
}
```

---

### 9. Divider / Separator

**Usage**: Between list items, section dividers

**Specifications**:
```javascript
{
  height: '1px',
  backgroundColor: '#E2E2E2',  // Grey 3
  width: '100%',
  margin: '0'
}
```

**Implementation**:
```jsx
<div className="w-full h-px bg-gray-border" />
```

---

## Patterns & Guidelines

### 1. Form Inputs

All input fields should use:
```css
padding: 8px 12px;
border: 1px solid #E2E2E2;
border-radius: 4px;
background-color: #F2F2F2;
font-size: 16px;
font-family: 'Open Sans';
```

### 2. Focus States

```css
focus {
  outline: none;
  ring: 2px #8A49F3;
  ring-offset: 0;
}
```

### 3. Disabled States

```css
disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
```

### 4. Loading States

Use placeholder skeletons or spinner overlays with `rgba(255, 255, 255, 0.6)` overlay.

### 5. Mobile Constraints

```css
max-width: 320px;
margin-left: auto;
margin-right: auto;
```

---

## Implementation Rules

### React/JSX Guidelines

1. **Always use design tokens, never hardcoded colors**
   ```jsx
   // ✅ Good
   <button className="bg-purple-primary text-white">

   // ❌ Bad
   <button style={{ backgroundColor: '#8A49F3' }}>
   ```

2. **Component Composition**
   - Extract reusable components to `/src/components/`
   - Use props for variants (size, color, disabled state)
   - Maintain consistent naming conventions

3. **Spacing**
   - Use Tailwind spacing scale: `px-4`, `py-2`, `gap-2`, etc.
   - Align with spacing system (16px standard)
   - Never use arbitrary pixel values except when matching Figma exactly

4. **Typography**
   - Always use Open Sans font family
   - Match font sizes and weights to type scale
   - Line height should be 100% (tight) for most components

5. **Accessibility**
   - Include `aria-label` for icon buttons
   - Use semantic HTML (`<button>`, `<input>`, etc.)
   - Ensure focus states are visible
   - Maintain sufficient color contrast

### Figma to Code Workflow

1. Get design context from Figma using MCP
2. Extract all color values and typography
3. Map to existing design tokens
4. Create component with proper variant support
5. Test pixel-perfect match against Figma screenshot

### Common Conversions

| Figma | Tailwind | CSS |
|-------|----------|-----|
| 16px padding | `px-4` | `padding: 16px` |
| 24px margin | `my-6` | `margin-top/bottom: 24px` |
| Open Sans 16px | `font-open-sans text-base` | `font-family: 'Open Sans'; font-size: 16px` |
| Purple #8A49F3 | `bg-purple-primary` | `background-color: #8A49F3` |
| 1px border grey | `border-gray-border` | `border: 1px solid #E2E2E2` |
| 4px radius | `rounded` | `border-radius: 4px` |

---

## Tailwind Configuration

Ensure `tailwind.config.js` includes:

```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        'purple-primary': '#8A49F3',
        'gray-disabled': '#6B6773',
        'gray-placeholder': '#828282',
        'gray-border': '#E2E2E2',
        'gray-light': '#F2F2F2',
        'violet-light': '#EFEBF6',
        'status-red': '#EB5757',
        'status-blue': '#5E81DC',
        'status-pink': '#DC5EC0',
        'status-yellow': '#F8C20B',
        'status-green': '#7FC663',
      },
      fontFamily: {
        'open-sans': ['Open Sans', 'sans-serif'],
      }
    }
  }
};
```

---

## Last Updated

Generated from Figma node designs:
- Node 263:1711 - "Лента товаров" (Product Feed)
- Node 626:206 - "0 (старший флорист / админ)" (Orders Management)

This document is the single source of truth for all design decisions in the CRM Bitrix admin interface.
