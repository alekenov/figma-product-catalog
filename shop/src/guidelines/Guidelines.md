# Cvety.kz Design System Guidelines

## General Rules

* Always use the Cvety design system components located in `/components/ui/cvety-*`
* Follow the mobile-first design approach - all layouts should work on 375px width
* Use CSS variables from our design system instead of hardcoded colors
* Maintain consistent spacing using our 8px grid system
* Always use Open Sans font family
* Prefer clean, borderless designs with white backgrounds and subtle shadows
* Use coral (#FF6666) checkmarks for selected states across all selection elements

## Brand Identity

* **Primary Brand Color**: #FF6666 (coral/red) - use for primary actions, CTAs, selected states, and brand elements
* **Success Color**: #01BC6F (green) - use for success states, completed orders, positive feedback
* **Warning Color**: #FFB300 (amber) - use for warnings and important notices
* **Error Color**: #FF4444 (red) - use for errors and destructive actions

## Typography System

Our typography system is mobile-first, optimized for 375px screens with a clean, readable hierarchy.

### Font Family
* **Primary**: Open Sans with system font fallbacks
* Automatically applied to all elements - no need to specify font-family

### Font Sizes (Mobile-First)
* **--text-xs** (12px): Small text, badges, micro-labels
* **--text-sm** (14px): Secondary text, captions, form labels
* **--text-base** (16px): Body text, buttons, inputs (default)
* **--text-lg** (18px): Subheadings, important text, prices
* **--text-xl** (22px): Section headers, card titles
* **--text-2xl** (26px): Page headers, main titles
* **--text-3xl** (30px): Hero text, display text

### Font Weights
* **Normal (400)**: Body text, descriptions, inputs
* **Medium (500)**: Labels, buttons, emphasized text
* **Semibold (600)**: Headers, important titles
* **Bold (700)**: Prices, hero text, primary emphasis

### Typography Utility Classes
Use these semantic classes instead of raw Tailwind typography:

```tsx
/* Display & Headers */
<h1 className="text-display">Hero Text</h1>
<h2 className="text-headline">Page Title</h2>
<h3 className="text-title">Section Header</h3>
<h4 className="text-subtitle">Card Title</h4>

/* Body Text */
<p className="text-body">Regular paragraph text</p>
<span className="text-body-emphasis">Emphasized text</span>
<small className="text-caption">Secondary information</small>
<span className="text-micro">Very small text</span>

/* Specialized */
<span className="text-price">7 900 ₸</span>
<span className="text-price-large">15 900 ₸</span>
<span className="text-overline">Category</span>
<span className="text-label">Form Label</span>
<button className="text-button">Button Text</button>
```

### Typography Best Practices

1. **Use semantic classes** instead of raw Tailwind text utilities
2. **Let globals.css handle defaults** - only override when necessary
3. **Maintain hierarchy** - larger text for more important content
4. **Consider line length** - optimal 45-75 characters per line
5. **Use consistent spacing** - follow our 8px grid system

### Text Colors
Always use CSS variables for consistent theming:
```tsx
/* Text Colors */
className="text-[var(--text-primary)]"    // Main text
className="text-[var(--text-secondary)]"  // Secondary text  
className="text-[var(--text-muted)]"      // Disabled/subtle text
className="text-[var(--brand-primary)]"   // Brand color text
```

### Line Clamping
Use utility classes for truncating text:
```tsx
<p className="text-body line-clamp-2">Long text that will be truncated...</p>
```

## Design Principles

### Clean & Minimal Design
* **Avoid heavy borders** - use subtle backgrounds and shadows instead
* **White backgrounds** with `rounded-[var(--radius-md)]` for content blocks
* **Consistent selection indicators** - coral checkmarks in top-right corner of selected items
* **Unified button styles** - borderless with subtle styling, no heavy filled buttons unless primary action

### Selection Elements Standard
All selection elements (buttons, options, tabs) should follow this pattern:
```tsx
// Selected state
className="relative px-4 py-2 rounded-2xl bg-white text-[var(--text-primary)] border border-[var(--border)]"

// With coral checkmark for selected
{isSelected && (
  <div className="absolute -top-1 -right-1 w-4 h-4 bg-[var(--brand-primary)] rounded-full flex items-center justify-center">
    <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
      <path 
        d="M2 5L4 7L8 3" 
        stroke="white" 
        strokeWidth="1.5" 
        strokeLinecap="round" 
        strokeLinejoin="round"
      />
    </svg>
  </div>
)}
```

## Component Guidelines

### Layout Containers
Use clean div containers instead of heavy card components:
```tsx
// Preferred - Clean container
<div className="p-[var(--spacing-4)] bg-white rounded-[var(--radius-md)]">
  {/* Content */}
</div>

// Avoid - Heavy card borders
<CvetyCard variant="outlined">
  {/* Content */}
</CvetyCard>
```

### Button Patterns
#### Standard Selection Buttons
```tsx
<button
  type="button"
  className="relative px-4 py-2 rounded-2xl transition-all text-sm font-medium border bg-white border-[var(--border)] flex-shrink-0"
>
  Button Text
  {/* Coral checkmark for active/selected state */}
</button>
```

#### Primary Action Buttons
Use CvetyButton only for main CTAs:
```tsx
<CvetyButton variant="primary" fullWidth>
  Оформить заказ
</CvetyButton>
```

### Form Elements
#### Input Fields
```tsx
<CvetyInput
  label="Имя получателя"
  value={name}
  onChange={(e) => setName(e.target.value)}
  placeholder="Введите имя"
/>
```

#### Textarea Fields
```tsx
<CvetyTextarea
  value={text}
  onChange={(e) => setText(e.target.value)}
  placeholder="Введите текст"
  maxLength={200}
  className="min-h-[80px]"
/>
```

### Selection Components
#### Radio-style Selection
Use for date/time, delivery options, etc.:
```tsx
<div className="flex gap-2">
  {options.map((option) => (
    <button
      key={option.id}
      className={`relative px-4 py-2 rounded-2xl border transition-all ${
        selected === option.id 
          ? 'bg-white text-[var(--text-primary)] border-[var(--border)]'
          : 'bg-white text-[var(--text-secondary)] border-[var(--border)]'
      }`}
    >
      {option.label}
      {selected === option.id && (
        <div className="absolute -top-1 -right-1 w-4 h-4 bg-[var(--brand-primary)] rounded-full flex items-center justify-center">
          <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
            <path d="M2 5L4 7L8 3" stroke="white" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </div>
      )}
    </button>
  ))}
</div>
```

### Interactive Elements
#### Expandable Sections
```tsx
<div 
  className="p-[var(--spacing-4)] bg-white rounded-[var(--radius-md)] cursor-pointer"
  onClick={toggleExpanded}
>
  {/* Content */}
</div>
```

## Layout Patterns

### Page Container
```tsx
<div className="bg-[var(--background-secondary)] min-h-screen">
  <div className="w-full max-w-sm mx-auto bg-white min-h-screen">
    <Header />
    
    <div className="p-[var(--spacing-4)] space-y-[var(--spacing-6)]">
      {/* Page content */}
    </div>
    
    <Footer />
  </div>
</div>
```

### Content Sections
```tsx
<div className="space-y-[var(--spacing-4)]">
  <h2 className="text-[var(--text-primary)] font-medium">Section Title</h2>
  
  <div className="p-[var(--spacing-4)] bg-white rounded-[var(--radius-md)]">
    {/* Section content */}
  </div>
</div>
```

### Spacing System
* `var(--spacing-2)` (8px): Tight spacing between related elements
* `var(--spacing-3)` (12px): Small gaps in button groups
* `var(--spacing-4)` (16px): Default spacing, padding
* `var(--spacing-6)` (24px): Section spacing
* `var(--spacing-8)` (32px): Large spacing between major sections

### Color Usage
Always use CSS variables:
```css
/* Text colors */
color: var(--text-primary);    /* Main text */
color: var(--text-secondary);  /* Secondary text */
color: var(--text-muted);      /* Disabled/muted text */

/* Backgrounds */
background: var(--background);           /* Main white */
background: var(--background-secondary); /* Light gray */
background: var(--brand-primary);       /* Coral for highlights */

/* Borders */
border-color: var(--border);    /* Subtle borders */
```

## State Management

### Loading States
Use skeleton components or simple loading text:
```tsx
<div className="animate-pulse bg-[var(--background-secondary)] h-8 rounded-[var(--radius-md)]" />
```

### Error States
```tsx
<div className="p-[var(--spacing-3)] bg-red-50 border border-red-200 rounded-[var(--radius-md)]">
  <p className="text-red-600 text-sm">Error message</p>
</div>
```

### Success States
```tsx
<div className="p-[var(--spacing-3)] bg-green-50 border border-green-200 rounded-[var(--radius-md)]">
  <p className="text-green-600 text-sm">Success message</p>
</div>
```

## Accessibility

* All interactive elements must have proper ARIA labels
* Use semantic HTML elements
* Ensure color contrast meets WCAG guidelines
* Provide keyboard navigation support
* Include focus states for all interactive elements
* Use descriptive button and link text

## File Organization

* Page components: `/components/PageName.tsx`
* UI components: `/components/ui/cvety-component.tsx`
* Reusable sections: `/components/SectionName.tsx`
* Import structure: First external, then internal, then relative imports

## Best Practices

1. **Consistency**: All selection elements should have the same visual treatment
2. **Simplicity**: Avoid unnecessary borders and heavy visual elements
3. **Accessibility**: Always include proper labels and ARIA attributes
4. **Performance**: Use CSS variables for theming and easy maintenance
5. **Mobile-first**: Design for 375px width first, then enhance for larger screens
6. **Typography**: Let the globals.css handle base typography, only override when necessary