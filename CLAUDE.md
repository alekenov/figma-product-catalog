# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Quick Start (Recommended)
- `./scripts/start.sh` - Start both frontend and backend
- `./scripts/start-frontend.sh` - Start frontend only
- `./scripts/start-backend.sh` - Start backend only

### Frontend Development (from frontend/ directory)
- `npm run dev` - Start development server on port 5176
- `npm run build` - Build production bundle
- `npm run preview` - Preview production build locally

### Backend Development (from backend/ directory)
- `python3 main.py` - Start FastAPI server on port 8014
- `uvicorn main:app --reload` - Start with auto-reload

### Architecture Overview

This is a React-based mobile-first product catalog application implementing a design system approach. The application is structured as a single-page application with client-side routing for managing flower shop products.

## Project Structure

```
figma-product-catalog/
├── frontend/          # React frontend application
│   ├── src/          # React components and services
│   ├── package.json  # Frontend dependencies
│   └── vite.config.js # Vite configuration
├── backend/          # FastAPI backend application
│   ├── main.py      # API entry point
│   ├── api/         # API endpoints
│   └── requirements.txt # Backend dependencies
├── scripts/         # Development scripts
│   ├── start.sh     # Start both services
│   ├── start-frontend.sh
│   └── start-backend.sh
└── .env.local       # Local environment variables
```

## Technical Stack & Architecture

**Frontend**: React 18.2.0 + Vite 4.3.9 (Port 5176)
**Backend**: FastAPI + SQLAlchemy (Port 8014)
**Styling**: Tailwind CSS 3.3.2 with custom design tokens
**Routing**: React Router DOM 7.9.2
**Target**: Mobile-first (320px fixed width container)

### Design System Implementation

The project implements a systematic design token approach in `/frontend/tailwind.config.js`:

```javascript
colors: {
  'purple-primary': '#8A49F3',    // Brand primary
  'green-success': '#34C759',     // Success states
  'gray-disabled': '#6B6773',     // Disabled text
  'gray-placeholder': '#828282',  // Placeholder text
  'gray-neutral': '#C4C4C4',      // Neutral backgrounds
  'gray-border': '#E0E0E0',       // Border colors
  'gray-input': '#F2F2F2',        // Input backgrounds
  'gray-input-alt': '#EEEDF2'     // Alternative input backgrounds
}
```

**Critical Rule**: Always use design tokens (e.g., `bg-purple-primary`) rather than hardcoded hex values (e.g., `bg-[#8A49F3]`).

### Component Architecture

The application uses a hybrid structure transitioning from flat organization to component-based:

- **Pages**: Main route components in `/src/` root (ProductCatalogFixed, ReadyProducts, AddProduct, etc.)
- **Reusable Components**: Located in `/src/components/` (ToggleSwitch)
- **Styling**: Custom mobile container via `.figma-container` class (320px width constraint)

### Key Architectural Patterns

#### Mobile Container Constraint
All pages must use the `.figma-container` class which enforces:
```css
.figma-container {
  width: 320px;
  min-height: 100vh;
  margin: 0 auto;
  background: white;
}
```

#### State Management Pattern
Uses local React state with useState hooks. Product states are managed per-page with this pattern:
```javascript
const [productStates, setProductStates] = useState(
  products.reduce((acc, product) => ({ ...acc, [product.id]: product.enabled }), {})
);
```

#### Toggle Switch Component
Extracted reusable component supporting multiple sizes (sm/md/lg) with accessibility features:
- Uses design tokens for colors
- Implements proper ARIA attributes (`role="switch"`, `aria-checked`)
- Supports disabled state

#### Routing Structure
- `/` - Main products catalog (ProductCatalogFixed)
- `/ready-products` - Ready products variant (ReadyProducts)
- `/add-product` - Product creation form
- `/edit-product/:id` - Product editing
- `/filters` - Filter interface

### Asset Management Strategy

**Current Approach**: Direct Figma signed URLs (temporary solution)
**Image Specifications**: 88x88px product thumbnails
**Critical Issue**: Figma URLs expire and need asset optimization system

### Icon System Standards

Icons are implemented as inline SVG with standardized dimensions:
- **Search icons**: `viewBox="0 0 24 24"`, `w-4 h-4` classes
- **UI icons**: `viewBox="0 0 20 20"`, `w-4 h-4` classes
- **Colors**: Use `currentColor` or `#828282` for neutral icons
- **Stroke width**: `strokeWidth="1.5"` or `strokeWidth="2"`

### Spacing Consistency Rules

**Standardized Values**:
- Section spacing: `mt-6` (24px) - used for consistent vertical rhythm
- Component gaps: `gap-3` for product card layouts
- Horizontal padding: `px-4` for page-level content

**Critical**: Avoid mixing `mt-4` and `mt-6` - use `mt-6` for section-level spacing consistency.

### Form Input Patterns

Forms use controlled components with validation patterns:
- Price inputs: `inputMode="numeric"` with thousand-separator formatting
- Search inputs: Include SVG search icon positioned absolutely
- Color tags: Predefined array of color objects with id/name/color properties

### Component Extraction Guidelines

When identifying repeated patterns, extract to `/src/components/` with these naming conventions:
- PascalCase component names
- Props interface supporting size variants where applicable
- Accessibility features included by default
- Design token usage enforced

## Design System Integration

### Figma MCP Integration Rules

When converting Figma designs:
1. Map colors to existing design tokens or create new semantic tokens
2. Use established spacing scale (`mt-6`, `gap-3`, `px-4`)
3. Follow mobile-first 320px container constraint
4. Extract reusable patterns into components
5. Maintain consistent icon sizing and viewBox standards

### Token Extension Process

Add new design tokens to `/tailwind.config.js` under `theme.extend.colors` with semantic naming:
```javascript
'semantic-name': '#HEX_VALUE',  // Usage description
```

## Development Patterns

### State Management Approach
- Use local state for component-specific data
- Implement reducer pattern for complex state (products with enable/disable toggles)
- Persist filter state in localStorage when needed

### Navigation Patterns
Use React Router's `useNavigate` hook consistently:
```javascript
const navigate = useNavigate();
navigate('/path'); // Programmatic navigation
```

### Component Import Structure
```javascript
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import ComponentName from './components/ComponentName';
import './App.css';
```

This architecture supports systematic design system implementation while maintaining development velocity and consistent user experience across the mobile catalog interface.