# Accessibility Quick Reference Guide

## Quick Start

### Import Accessibility Features

```typescript
// Focus trap
import { FocusTrap, useFocusTrap } from '@/lib/a11y';

// Announcer
import { useAnnounce, announce } from '@/lib/a11y';

// Settings hook
import { useAccessibility } from '@/hooks/useAccessibility';

// Components
import { AccessibilityPanel } from '@/components/a11y/AccessibilityPanel';
import { SkipLink } from '@/components/a11y/SkipLink';
```

## Common Patterns

### 1. Modal Dialog with Focus Trap

```typescript
'use client';

import { useRef, useEffect } from 'react';
import { FocusTrap } from '@/lib/a11y';

function Dialog({ open, onClose }) {
  const dialogRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (!open || !dialogRef.current) return;

    const trap = new FocusTrap({
      element: dialogRef.current,
      triggerElement: buttonRef.current,
      allowEscape: true,
      onDeactivate: onClose
    });

    trap.activate();
    return () => trap.deactivate();
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div
      ref={dialogRef}
      role="dialog"
      aria-modal="true"
      aria-labelledby="dialog-title"
    >
      <h2 id="dialog-title">Dialog Title</h2>
      <button onClick={onClose}>Close</button>
    </div>
  );
}
```

### 2. Announce Dynamic Content

```typescript
'use client';

import { useAnnounce } from '@/lib/a11y';
import { useState } from 'react';

function SearchResults() {
  const { announce } = useAnnounce();
  const [results, setResults] = useState([]);

  const handleSearch = async (query: string) => {
    const data = await searchAPI(query);
    setResults(data);
    announce(`${data.length} Ergebnisse gefunden`);
  };

  return (
    <div>
      <input onChange={(e) => handleSearch(e.target.value)} />
      <div role="region" aria-live="polite" aria-atomic="true">
        {results.length} Ergebnisse
      </div>
    </div>
  );
}
```

### 3. Form with Proper Labels

```typescript
function AccessibleForm() {
  return (
    <form>
      {/* Text input */}
      <div>
        <label htmlFor="name">Name</label>
        <input
          id="name"
          type="text"
          aria-required="true"
          aria-describedby="name-hint"
        />
        <span id="name-hint">Bitte geben Sie Ihren vollständigen Namen ein</span>
      </div>

      {/* Checkbox */}
      <div>
        <input
          type="checkbox"
          id="terms"
          aria-required="true"
        />
        <label htmlFor="terms">Ich akzeptiere die Bedingungen</label>
      </div>

      {/* Radio group */}
      <fieldset>
        <legend>Wählen Sie eine Option</legend>
        <div>
          <input type="radio" id="opt1" name="option" value="1" />
          <label htmlFor="opt1">Option 1</label>
        </div>
        <div>
          <input type="radio" id="opt2" name="option" value="2" />
          <label htmlFor="opt2">Option 2</label>
        </div>
      </fieldset>

      <button type="submit">Absenden</button>
    </form>
  );
}
```

### 4. Loading States

```typescript
function LoadingContent() {
  const [loading, setLoading] = useState(true);

  return (
    <div>
      {loading ? (
        <div
          role="status"
          aria-live="polite"
          aria-label="Wird geladen"
        >
          <Spinner />
          <span className="sr-only">Inhalt wird geladen...</span>
        </div>
      ) : (
        <div>Content loaded</div>
      )}
    </div>
  );
}
```

### 5. Error Messages

```typescript
function FormWithErrors() {
  const [error, setError] = useState('');
  const { announce } = useAnnounce();

  const handleSubmit = async (data) => {
    try {
      await submitForm(data);
    } catch (err) {
      setError(err.message);
      announce(err.message, { priority: 'assertive' });
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {error && (
        <div
          role="alert"
          aria-live="assertive"
          className="error"
        >
          {error}
        </div>
      )}
      {/* form fields */}
    </form>
  );
}
```

### 6. Custom Focus Indicators

```typescript
function FocusableCard() {
  return (
    <div
      tabIndex={0}
      role="button"
      className="focus-visible:outline focus-visible:outline-2 focus-visible:outline-primary"
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          // Handle activation
        }
      }}
    >
      Card content
    </div>
  );
}
```

## Essential ARIA Attributes

### Roles
```typescript
role="button"           // Interactive element
role="dialog"          // Modal dialog
role="alert"           // Important message
role="status"          // Status update
role="navigation"      // Navigation section
role="main"            // Main content
role="complementary"   // Sidebar content
role="search"          // Search form
```

### Properties
```typescript
aria-label="Close"              // Label for element
aria-labelledby="heading-id"    // Reference to label element
aria-describedby="desc-id"      // Reference to description
aria-required="true"            // Required field
aria-invalid="true"             // Invalid input
aria-hidden="true"              // Hide from screen readers
aria-live="polite"              // Live region update (polite)
aria-live="assertive"           // Live region update (urgent)
aria-atomic="true"              // Announce entire region
aria-modal="true"               // Modal dialog
aria-expanded="false"           // Expandable section state
aria-pressed="true"             // Toggle button state
aria-checked="true"             // Checkbox/radio state
aria-current="page"             // Current navigation item
```

## CSS Classes

### Screen Reader Only
```typescript
<span className="sr-only">Text only for screen readers</span>
```

### Focus Indicators
```typescript
<button className="focus-visible:ring-2 focus-visible:ring-primary">
  Click me
</button>
```

### Skip Link
```typescript
<a href="#main" className="skip-link">
  Skip to main content
</a>
```

## Keyboard Navigation

### Standard Keys
- `Tab` - Next focusable element
- `Shift + Tab` - Previous focusable element
- `Enter` - Activate button/link
- `Space` - Activate button, toggle checkbox
- `Escape` - Close modal/dropdown
- `Arrow Keys` - Navigate within component

### Implementation
```typescript
function KeyboardComponent() {
  const handleKeyDown = (e: React.KeyboardEvent) => {
    switch (e.key) {
      case 'Enter':
      case ' ':
        e.preventDefault();
        // Activate
        break;
      case 'Escape':
        // Close
        break;
      case 'ArrowDown':
        // Navigate down
        break;
      case 'ArrowUp':
        // Navigate up
        break;
    }
  };

  return <div onKeyDown={handleKeyDown} tabIndex={0}>...</div>;
}
```

## Testing Checklist

### Keyboard Navigation
- [ ] All interactive elements reachable via Tab
- [ ] Focus order is logical
- [ ] Focus visible on all elements
- [ ] No keyboard traps (can always Tab away)
- [ ] Escape closes modals

### Screen Reader
- [ ] All images have alt text
- [ ] All form inputs have labels
- [ ] Live regions announce changes
- [ ] Skip links present
- [ ] Headings in logical order (h1, h2, h3...)

### Visual
- [ ] Color contrast meets WCAG AA (4.5:1)
- [ ] Text resizable to 200%
- [ ] No information by color alone
- [ ] Focus indicators visible

### Motion
- [ ] Animations respect prefers-reduced-motion
- [ ] No auto-playing videos with sound
- [ ] No flashing content (3+ flashes/sec)

## Browser DevTools

### Chrome/Edge
1. F12 to open DevTools
2. Lighthouse tab → Accessibility audit
3. Elements tab → Accessibility pane

### Firefox
1. F12 to open DevTools
2. Accessibility tab
3. Right-click element → Inspect Accessibility Properties

## Common Mistakes to Avoid

### 1. Missing Alt Text
```typescript
// Bad
<img src="logo.png" />

// Good
<img src="logo.png" alt="Company Logo" />

// Decorative (no alt needed)
<img src="decorative.png" alt="" />
```

### 2. Click Only Elements
```typescript
// Bad
<div onClick={handleClick}>Click me</div>

// Good
<button onClick={handleClick}>Click me</button>

// Or make div keyboard accessible
<div
  role="button"
  tabIndex={0}
  onClick={handleClick}
  onKeyDown={(e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      handleClick();
    }
  }}
>
  Click me
</div>
```

### 3. Form Without Labels
```typescript
// Bad
<input type="text" placeholder="Name" />

// Good
<label htmlFor="name">Name</label>
<input id="name" type="text" placeholder="Name" />
```

### 4. Low Contrast
```typescript
// Bad
<span className="text-gray-400">Important text</span>

// Good
<span className="text-gray-700">Important text</span>
```

### 5. Modal Without Focus Trap
```typescript
// Bad
<div role="dialog">
  <button onClick={close}>Close</button>
</div>

// Good - Use FocusTrap
<div ref={modalRef} role="dialog" aria-modal="true">
  <button onClick={close}>Close</button>
</div>
```

## Resources

- [WCAG Quick Reference](https://www.w3.org/WAI/WCAG21/quickref/)
- [MDN ARIA Guide](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA)
- [axe DevTools](https://www.deque.com/axe/devtools/)
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)

---

**Last Updated:** 2025-12-08
