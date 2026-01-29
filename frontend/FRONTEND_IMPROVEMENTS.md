# Frontend Improvements Roadmap

This document tracks planned UI/UX improvements for the Battery Valuator frontend.

---

## Completed (High Priority)

- [x] **Dark Mode Compatibility** - Replaced hardcoded `bg-white` with `bg-card` semantic token
- [x] **Design System Consistency** - Replaced hardcoded Tailwind colors (blue-50, green-50, amber-50, etc.) with semantic tokens (primary, profit, warning, destructive)
- [x] **Section/Card Styling** - Standardized card styling across all sections (rounded-xl, card-shadow, consistent borders)
- [x] **Section Headers** - Unified header pattern with icon + uppercase label across all components
- [x] **Spacing Consistency** - Standardized to space-y-6 for main sections, space-y-4 for internal groups

---

## Medium Priority (Next Phase)

### Visual Hierarchy Improvements
- [ ] **Results Section Redesign**
  - Add a summary "hero" card at top with key metrics (Net Profit, Margin)
  - Better visual grouping of related metrics
  - Consider side-by-side comparison for Revenue vs Cost

### Mobile Experience
- [ ] **Responsive Header**
  - Collapsible header on mobile with hamburger menu
  - Sticky "Run Valuation" button on mobile for easy access

- [ ] **Mobile-Optimized Inputs**
  - Transport mode buttons → dropdown on mobile
  - Better touch targets for sliders
  - Collapsible sections to reduce scroll depth

### Micro-interactions & Feedback
- [ ] **Loading States**
  - Add skeleton loading states instead of just disabled buttons
  - Progress indicator for calculation

- [ ] **Success Feedback**
  - Subtle animation on successful calculation
  - Confetti or highlight effect on profitable valuations

- [ ] **Hover States**
  - Add subtle lift/shadow on hoverable cards
  - Tooltip previews for complex metrics

---

## Low Priority (Polish Phase)

### Layout Options
- [ ] **Two-Column Desktop Layout**
  - Inputs panel on left (fixed/sticky)
  - Results panel on right (scrollable)
  - Reduces scrolling for power users
  - Could be a toggle preference

### Empty & Error States
- [ ] **Guided Empty States**
  - Step-by-step hints for first-time users
  - Sample data button to pre-fill form
  - Contextual tips for each section

- [ ] **Better Error Handling**
  - Inline validation messages
  - Field-level error highlighting
  - Recovery suggestions for API errors

### Accessibility
- [ ] **Keyboard Navigation**
  - Focus trap management for modals
  - Skip links for screen readers
  - Tab order optimization

- [ ] **ARIA Improvements**
  - Add aria-labels to icon-only buttons
  - Live region announcements for calculation results
  - Better screen reader descriptions for charts

### Performance
- [ ] **Code Splitting**
  - Lazy load results components
  - Defer regulatory advisory component

- [ ] **Bundle Optimization**
  - Tree-shake unused shadcn components
  - Optimize chart library imports

---

## Design Tokens Reference

The following semantic tokens are available in the design system:

| Token | Usage |
|-------|-------|
| `primary` | Main brand color (green), links, active states |
| `profit` | Positive values, success states |
| `cost` | Negative values, expenses |
| `warning` | Alerts, cautions |
| `destructive` | Errors, blocked states |
| `muted-foreground` | Secondary text |
| `card` | Card backgrounds (dark mode safe) |
| `border` | Consistent borders |

---

*Last updated: January 2026*
