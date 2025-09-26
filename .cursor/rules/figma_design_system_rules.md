# Design System Rules for Figma Remote MCP Integration

## Project Overview
**Project**: Figma Product Catalog - React-based mobile-first flower shop management system
**Target**: 320px fixed width mobile interface
**Tech Stack**: React 18.2.0 + Tailwind CSS 3.3.2 + Vite 4.3.9

## 1. Token Definitions

### Location & Structure
Tokens are defined in `/tailwind.config.js` under `theme.extend.colors`:

```javascript
// /tailwind.config.js
colors: {
  // Brand colors
  'purple-primary': '#8A49F3',

  // State colors
  'green-success': '#34C759',

  // Neutral colors
  'gray-disabled': '#6B6773',
  'gray-placeholder': '#828282',
  'gray-neutral': '#C4C4C4',
  'gray-border': '#E0E0E0',

  // Background colors
  'gray-input': '#F2F2F2',
  'gray-input-alt': '#EEEDF2'
}
```

### Typography Tokens
```javascript
fontFamily: {
  'sans': ['Open Sans', 'Noto Sans', 'sans-serif']
}
```

### Spacing System
- Container width: `320px` (fixed)
- Section spacing: `mt-6` (24px)
- Component gap: `gap-3` (12px)
- Horizontal padding: `px-4` (16px)

## 2. Component Library

### Current Structure
```
src/
├── components/
│   ├── BottomNavBar.jsx      # Fixed bottom navigation (5 tabs)
│   └── ToggleSwitch.jsx      # Reusable toggle component
├── ProductCatalogFixed.jsx   # Main products page
├── Orders.jsx               # Orders management page
├── ReadyProducts.jsx        # Ready products variant
└── App.jsx                  # Router configuration
```

### Component Patterns
- **Functional components** with hooks (useState, useNavigate)
- **Props-based configuration** (size variants, state management)
- **Accessibility-first** (ARIA attributes, semantic HTML)

## 3. Frameworks & Libraries

### Core Stack
- **UI Framework**: React 18.2.0 (functional components + hooks)
- **Styling**: Tailwind CSS 3.3.2 (utility-first approach)
- **Routing**: React Router DOM 7.9.2
- **Build System**: Vite 4.3.9 (ES modules, HMR)

### Build Configuration
```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  }
}
```

## 4. Asset Management

### Current State
- **Images**: Direct Figma signed URLs (temporary solution)
- **Format**: 88x88px product thumbnails
- **Critical Issue**: URLs expire, needs asset optimization system

### Recommended Structure
```
src/assets/
├── images/
│   ├── products/
│   └── icons/
└── index.js  # Asset exports
```

## 5. Icon System

### Current Implementation
- **Format**: Inline SVG components
- **Standardization**: Mixed viewBox sizes (20x20, 24x24)
- **Dynamic coloring**: `stroke={isActive ? "#8A49F3" : "#6B6773"}`

### Icon Standards
```javascript
// Search icons: viewBox="0 0 24 24", w-4 h-4
// UI icons: viewBox="0 0 20 20", w-4 h-4
// Stroke width: 1.5 or 2
// Colors: currentColor or #828282
```

### BottomNavBar Icon Pattern
```javascript
const IconComponent = ({ isActive }) => (
  <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24">
    <path stroke={isActive ? "#8A49F3" : "#6B6773"} />
  </svg>
);
```

## 6. Styling Approach

### CSS Methodology
- **Primary**: Tailwind CSS utility classes
- **Container**: `.figma-container` custom class (320px constraint)
- **Responsive**: Mobile-first (single breakpoint)

### Global Styles (`src/App.css`)
```css
.figma-container {
  width: 320px;
  min-height: 100vh;
  margin: 0 auto;
  position: relative;
  background: white;
  overflow-x: visible;
  overflow-y: visible;
}
```

### Component Style Patterns
```javascript
// Header pattern
<div className="flex items-center justify-between px-4 mt-5">
  <h1 className="text-2xl font-['Open_Sans'] font-normal">Title</h1>
  <button className="w-6 h-6 bg-purple-primary rounded-md">+</button>
</div>

// Search input pattern
<div className="px-4 mt-6">
  <div className="relative">
    <input className="w-full px-4 py-3 bg-gray-input rounded-lg" />
    <svg className="absolute right-3 top-1/2 transform -translate-y-1/2" />
  </div>
</div>
```

## 7. Project Structure

### Current Organization
```
figma-product-catalog/
├── public/                  # Static assets
├── src/
│   ├── components/         # Reusable components
│   ├── *.jsx              # Page components (flat structure)
│   ├── App.jsx            # Router setup
│   ├── main.jsx           # React entry point
│   └── App.css            # Global styles
├── tailwind.config.js      # Design tokens
├── package.json           # Dependencies
└── vite.config.js         # Build configuration
```

### Component Naming Convention
- **Pages**: PascalCase descriptive names (`ProductCatalogFixed.jsx`)
- **Components**: PascalCase with clear purpose (`BottomNavBar.jsx`)
- **Props**: camelCase with semantic meaning (`activeTab`, `onTabChange`)

## 8. Design System Violations & Fixes Needed

### Critical Inconsistencies
1. **Filter Section Icons**: Different between Products/Orders pages
2. **Search Placeholders**: "Найти" vs "Поиск по заказам"
3. **Filter Labels**: "Магазин Cvety.kz" vs "Все заказы"

### Recommended Components to Create
```javascript
// Unified filter header
<FilterHeader
  icon="shop|orders"
  label="Магазин Cvety.kz|Все заказы"
  onFiltersClick={handleFilters}
/>

// Standardized search input
<SearchInput
  placeholder="Поиск товаров|Поиск заказов"
  value={searchQuery}
  onChange={setSearchQuery}
/>

// Icon system
<Icon
  name="search|filter|shop|orders"
  size="sm|md|lg"
  color="primary|secondary|neutral"
/>
```

## 9. Figma Integration Guidelines

### Component Mapping Strategy
- **Extract atomic components** first (buttons, inputs, toggles)
- **Build molecular components** (filter headers, product cards)
- **Compose page templates** using established patterns

### Token Synchronization
- Map Figma color styles to Tailwind tokens
- Maintain 1:1 relationship between design and code tokens
- Use semantic naming (not descriptive)

### Asset Pipeline
- Extract assets at 2x resolution for sharp mobile display
- Implement CDN strategy for production
- Create automated asset optimization workflow

This structure provides a foundation for systematic Figma-to-code integration while maintaining the existing architecture and patterns.