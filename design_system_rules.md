# Design System Rules - Figma Product Catalog

## Project Overview
**Framework**: React 18.2.0 + Vite 4.3.9
**Styling**: Tailwind CSS 3.3.2
**Target**: Mobile-first catalog application (320px width)

---

## 1. Token Definitions

### Current Token Location
**File**: `/tailwind.config.js` lines 7-17
```javascript
theme: {
  extend: {
    fontFamily: {
      'sans': ['Open Sans', 'Noto Sans', 'sans-serif'],
    },
    colors: {
      'purple-primary': '#8A49F3',    // Brand primary
      'gray-disabled': '#6B6773',     // Disabled text
      'gray-placeholder': '#828282',  // Placeholder text
    }
  }
}
```

### Missing Critical Tokens
```javascript
// Colors found in codebase but not tokenized:
'#34C759' // Success/enabled state (toggles)
'#C4C4C4' // Disabled/neutral gray
'#E0E0E0' // Border color
'#F2F2F2' // Search input background
'#EEEDF2' // Alternative input background

// Spacing inconsistencies found:
mt-4 (16px) vs mt-6 (24px) // Fixed: now standardized to mt-6
```

### Token Format
- **Structure**: Tailwind CSS extended theme
- **Transformation**: PostCSS with Autoprefixer
- **Usage**: Mix of custom tokens and hardcoded hex values (needs standardization)

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

#### Toggle Switch Component
```javascript
// Found in: ProductCatalogFixed.jsx:179-188, ReadyProducts.jsx:189-198
<button className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
  isEnabled ? 'bg-[#34C759]' : 'bg-[#C4C4C4]'
}`}>
  <span className={`inline-block h-5 w-5 transform rounded-full bg-white transition-transform ${
    isEnabled ? 'translate-x-6' : 'translate-x-1'
  }`} />
</button>
```

#### Add Button Component
```javascript
// Found in: ProductCatalogFixed.jsx:91-95, ReadyProducts.jsx:105-109
<button className="w-6 h-6 bg-[#8A49F3] rounded-md flex items-center justify-center">
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

#### Search Icon
```javascript
// Standard across ProductCatalogFixed.jsx:106-109, ReadyProducts.jsx:122-125
<svg className="absolute right-3 top-1/2 transform -translate-y-1/2 w-4 h-4"
     fill="none" stroke="#828282" viewBox="0 0 24 24">
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

### Icon System Rules
- **Size Classes**: `w-4 h-4` (16px) standard
- **ViewBox**: `0 0 24 24` for search, `0 0 20 20` for UI icons
- **Colors**: `currentColor` or `#828282` for neutral icons
- **Stroke Width**: `strokeWidth="1.5"` or `strokeWidth="2"`

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

### Design System Compliance Rules

#### Color Usage
- ✅ **USE**: Tailwind custom tokens (`text-purple-primary`)
- ❌ **AVOID**: Direct hex values (`text-[#8A49F3]`)

#### Spacing Consistency
- ✅ **USE**: Standardized spacing (`mt-6` for section spacing)
- ❌ **AVOID**: Mixed spacing scales

#### Component Patterns
- ✅ **EXTRACT**: Repeated UI patterns into reusable components
- ✅ **STANDARDIZE**: Icon sizes and viewBox dimensions
- ✅ **UNIFY**: Toggle switch, button, and form styling

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