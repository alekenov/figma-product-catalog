# Design System Rules - Figma Product Catalog

## Project Overview
**Framework**: React 18.2.0 + Vite 4.3.9
**Styling**: Tailwind CSS 3.3.2
**Target**: Mobile-first catalog application (320px width)

---

## 1. Token Definitions

### Current Token Location
**File**: `/tailwind.config.js` - Complete Design Token System
```javascript
theme: {
  extend: {
    fontFamily: {
      'sans': ['Open Sans', 'Noto Sans', 'sans-serif'],
    },
    colors: {
      // Brand colors
      'purple-primary': '#8A49F3',
      'purple-light': '#EFEBF6',
      'purple-hover': '#7A39E3',

      // State colors
      'green-success': '#34C759',
      'success': '#0BBC87',
      'status-new': '#EB5757',
      'status-assembled': '#F8C20B',
      'status-blue': '#5E81DC',
      'status-pink': '#DC5EC0',
      'status-green': '#7FC663',
      'error-primary': '#DF1D4C',
      'whatsapp': '#25D366',

      // Neutral colors
      'gray-disabled': '#6B6773',
      'gray-placeholder': '#828282',
      'gray-neutral': '#C4C4C4',
      'gray-border': '#E0E0E0',
      'gray-secondary': '#8E8E93',

      // Background colors
      'gray-input': '#F2F2F2',
      'gray-input-alt': '#EEEDF2',
      'gray-input-hover': '#E5E4EA',
      'background-light': '#F2F2F7',
      'background-hover': '#F5F5F5',
      'background-section': '#EEEDF2',

      // System colors
      'system-blue': '#007AFF',

      // Border colors
      'border-input': '#E2E2E2',
      'border-dashed': '#C7C7CC'
    }
  }
}
```

### ✅ Token Standardization Complete
**Status**: All inline hex colors have been replaced with design tokens
**Coverage**: 100% of React components now use standardized tokens
**Implementation**: CSS variables created for SVG stroke/fill colors

### Token Format
- **Structure**: Tailwind CSS extended theme
- **Transformation**: PostCSS with Autoprefixer
- **Usage**: ✅ **STANDARDIZED** - All components use design tokens
- **SVG Support**: CSS variables in App.css for stroke/fill colors

---

## 2. Component Library

### Current Architecture
**Location**: Flat structure in `/src/` directory
**Pattern**: Functional components with React Hooks

### Component Inventory
```
ProductCatalogFixed.jsx  - Main product grid with filtering
ReadyProducts.jsx       - Ready products variant (unified styling)
AddProduct.jsx          - Product creation form with validation
EditProduct.jsx         - Product editing interface
FilterPage.jsx          - Filter modal/page
```

### Repeated UI Patterns (Need Extraction)

#### Toggle Switch Component ✅ **EXTRACTED & STANDARDIZED**
```javascript
// Location: /src/components/ToggleSwitch.jsx
// Uses design tokens: bg-green-success, bg-gray-neutral
<ToggleSwitch isEnabled={isEnabled} onToggle={() => toggleProduct(product.id)} />
```

#### Add Button Component ✅ **STANDARDIZED**
```javascript
// Now uses design tokens across all components
<button className="w-6 h-6 bg-purple-primary rounded-md flex items-center justify-center">
  <span className="text-white text-lg leading-none">+</span>
</button>
```

#### Product Card Layout
```javascript
// Standard product item structure across both catalog pages
<div className="flex items-center gap-3">
  <div className="relative w-[88px] h-[88px] flex-shrink-0">
    {/* Image */}
  </div>
  <div className="flex-1">
    {/* Product info */}
  </div>
  {/* Toggle switch */}
</div>
```

---

## 3. Frameworks & Libraries

### Tech Stack
```json
// package.json dependencies
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "react-router-dom": "^7.9.2"
}

// devDependencies
{
  "tailwindcss": "^3.3.2",
  "autoprefixer": "^10.4.14",
  "postcss": "^8.4.24",
  "vite": "^4.3.9"
}
```

### Build Configuration
- **Bundler**: Vite with HMR
- **CSS Processing**: PostCSS + Tailwind + Autoprefixer
- **Content Sources**: `"./index.html", "./src/**/*.{js,ts,jsx,tsx}"`

---

## 4. Asset Management

### Current Approach
**Method**: Direct Figma signed URLs
```javascript
// ProductCatalogFixed.jsx:6-7
const imgRectangle = "https://s3-alpha-sig.figma.com/img/d1e4/a43d/fd35275968d7a4b44aa8a93a79982faa?Expires=1759708800...";
```

### Issues & Requirements
- ❌ **Temporary URLs**: Figma links expire
- ❌ **No optimization**: Raw image sizes
- ❌ **No responsive variants**: Single image size only
- ✅ **Should implement**: Asset optimization + CDN strategy

### Image Specifications
- **Product thumbnails**: 88x88px (based on className analysis)
- **Format**: Mixed (needs standardization to WebP/AVIF)

---

## 5. Icon System

### Current Implementation
**Storage**: Inline SVG within JSX components
**Standardization**: Recently unified across pages

### Standardized Icons

#### Search Icon ✅ **STANDARDIZED WITH CSS VARIABLES**
```javascript
// Uses CSS utility classes instead of inline hex colors
<svg className="absolute right-3 top-1/2 transform -translate-y-1/2 w-4 h-4 stroke-gray-placeholder"
     fill="none" viewBox="0 0 24 24">
  <circle cx="11" cy="11" r="8" strokeWidth="2"/>
  <path strokeLinecap="round" strokeWidth="2" d="m21 21-4.35-4.35"/>
</svg>
```

#### Shop/Filter Icons
```javascript
// viewBox="0 0 20 20" for consistency
<svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 20 20">
  {/* Standardized paths */}
</svg>
```

### Icon System Rules ✅ **IMPLEMENTED**
- **Size Classes**: `w-4 h-4` (16px) standard
- **ViewBox**: `0 0 24 24` for search, `0 0 20 20` for UI icons
- **Colors**: CSS utility classes (`stroke-gray-placeholder`, `stroke-purple-primary`)
- **Stroke Width**: `strokeWidth="1.5"` or `strokeWidth="2"`
- **CSS Variables**: Defined in App.css for consistent SVG styling

---

## 6. Styling Approach

### Primary Method: Tailwind Utility Classes
```javascript
// Standard layout pattern
className="flex items-center justify-between px-4 mt-6"
```

### Custom CSS Classes
**File**: `/src/App.css`
```css
/* CSS Variables for SVG colors mapped to design tokens */
:root {
  --svg-purple-primary: #8A49F3;
  --svg-gray-disabled: #6B6773;
  --svg-gray-placeholder: #828282;
  --svg-black: #000000;
}

/* SVG stroke utility classes */
.stroke-purple-primary { stroke: var(--svg-purple-primary); }
.stroke-gray-disabled { stroke: var(--svg-gray-disabled); }
.stroke-gray-placeholder { stroke: var(--svg-gray-placeholder); }
.stroke-black { stroke: var(--svg-black); }

/* Mobile container constraint */
.figma-container {
  width: 320px;           /* Fixed mobile width */
  min-height: 100vh;      /* Full viewport height */
  margin: 0 auto;         /* Center alignment */
  background: white;      /* Base background */
}
```

### Global Styles
**File**: `/src/index.css`
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### Responsive Strategy
- **Approach**: Mobile-first (320px fixed width)
- **Breakpoints**: Currently none (single mobile layout)
- **Future**: Needs responsive breakpoint system

---

## 7. Project Structure

### Current Organization
```
figma-product-catalog/
├── src/
│   ├── App.jsx                 # Router configuration
│   ├── main.jsx               # React entry point
│   ├── ProductCatalogFixed.jsx # Main products page
│   ├── ReadyProducts.jsx       # Ready products page
│   ├── AddProduct.jsx          # Add product form
│   ├── EditProduct.jsx         # Edit product form
│   ├── FilterPage.jsx          # Filter interface
│   ├── App.css                 # Custom styles
│   └── index.css               # Tailwind imports
├── tailwind.config.js          # Design tokens
├── package.json                # Dependencies
└── vite.config.js              # Build config
```

### Architectural Patterns
- **Routing**: React Router DOM with path-based navigation
- **State Management**: Local component state (useState hooks)
- **Data Flow**: Props and local state only
- **File Organization**: Flat structure (needs component folders)

---

## Design System Opportunities

### Immediate Improvements Needed

1. **Centralize Design Tokens**
```javascript
// Proposed: /src/design-tokens.js
export const tokens = {
  colors: {
    brand: {
      primary: '#8A49F3',      // purple-primary
      success: '#34C759',      // toggle enabled
    },
    neutral: {
      border: '#E0E0E0',       // dividers
      disabled: '#6B6773',     // gray-disabled
      placeholder: '#828282',  // gray-placeholder
      background: '#F2F2F2',   // input backgrounds
    }
  },
  spacing: {
    xs: '4px',   // gap-1
    sm: '8px',   // gap-2
    md: '16px',  // mt-4
    lg: '24px',  // mt-6 (standardized)
    xl: '32px',  // mt-8
  }
}
```

2. **Extract Reusable Components**
- `<ToggleSwitch>` - For product enable/disable
- `<AddButton>` - Plus icon button pattern
- `<ProductCard>` - Product list item layout
- `<SearchInput>` - Search field with icon
- `<TabNavigation>` - Products/Ready Products tabs

3. **Implement Icon Library**
```javascript
// Proposed: /src/components/icons/
export { SearchIcon, ShopIcon, FilterIcon, PlusIcon }
```

### Design System Compliance Rules ✅ **IMPLEMENTED**

#### Color Usage **ENFORCED**
- ✅ **USE**: Tailwind custom tokens (`text-purple-primary`, `bg-gray-input-alt`)
- ✅ **USE**: CSS utility classes for SVG (`stroke-gray-placeholder`)
- ❌ **PROHIBITED**: Direct hex values (`text-[#8A49F3]`, `stroke="#828282"`)
- 📋 **STATUS**: 100% compliance achieved across all components

#### Spacing Consistency **STANDARDIZED**
- ✅ **USE**: Standardized spacing (`mt-6` for section spacing)
- ✅ **USE**: Consistent gaps (`gap-3` for product layouts)
- ❌ **AVOID**: Mixed spacing scales

#### Component Patterns **ESTABLISHED**
- ✅ **EXTRACTED**: ToggleSwitch component from repeated patterns
- ✅ **STANDARDIZED**: Icon sizes and viewBox dimensions
- ✅ **UNIFIED**: Button, form styling, and SVG color handling
- 📋 **NEXT**: ESLint rule configuration to prevent regression

---

## Integration Guidelines for Figma MCP

### When Converting Figma Designs:

1. **Extract color values** → Map to existing tokens or create new ones
2. **Identify spacing patterns** → Use established spacing scale
3. **Recognize component patterns** → Reference existing component library
4. **Standardize icon usage** → Follow established icon system rules
5. **Maintain mobile-first approach** → 320px container constraint

### File Generation Patterns:
- **New components** → `/src/components/[ComponentName].jsx`
- **Design tokens** → Update `/tailwind.config.js` theme.extend
- **Global styles** → Add to `/src/App.css` if needed
- **Icons** → Inline SVG following established viewBox patterns

This documentation serves as the foundation for systematic design system implementation and Figma-to-code conversion using MCP protocols.