# Landing Page Components

This directory contains reusable React components for the DovvyBuddy landing page.

## Components

### Hero
The above-the-fold hero section with headline, subheadline, and primary CTA.

**Props:**
- `headline` (string): Main headline text
- `subheadline` (string): Supporting text below headline
- `ctaText` (string): Text for the call-to-action button
- `ctaLink` (string): URL for the CTA button
- `onCtaClick` (function, optional): Callback for analytics tracking

**Usage:**
```tsx
<Hero
  headline="Your AI Diving Companion"
  subheadline="Get judgment-free guidance on certifications..."
  ctaText="Start Chatting"
  ctaLink="/chat"
  onCtaClick={() => trackEvent('cta_click', { location: 'hero' })}
/>
```

### ValueProposition
Three-column feature highlights showing key benefits.

**Props:**
- `features` (array): Array of feature objects with `icon`, `title`, and `description`

**Usage:**
```tsx
<ValueProposition
  features={[
    {
      icon: '🎓',
      title: 'Certification Navigator',
      description: 'Understand PADI, SSI, and other certification pathways...',
    },
    // ... more features
  ]}
/>
```

### HowItWorks
Step-by-step explanation of how to use the product.

**Props:**
- `steps` (array): Array of step objects with `number`, `title`, and `description`

**Usage:**
```tsx
<HowItWorks
  steps={[
    {
      number: 1,
      title: 'Ask Your Question',
      description: 'Type anything about certifications...',
    },
    // ... more steps
  ]}
/>
```

### SocialProof
Trust indicators and social proof section.

**Props:**
- `title` (string, optional): Main heading (default: "Built by Divers, for Divers")
- `subtitle` (string, optional): Supporting text

**Usage:**
```tsx
<SocialProof />
// or with custom text:
<SocialProof
  title="Trusted by Divers Worldwide"
  subtitle="Join thousands of diving enthusiasts"
/>
```

### Footer
Site footer with links and copyright information.

**Props:** None (uses current year automatically)

**Usage:**
```tsx
<Footer />
```

## Styling

All components use Tailwind CSS classes for styling. The design system includes:

- **Colors:** Primary (ocean blue), Accent (tropical teal), Neutral (grays)
- **Typography:** Inter font family, responsive text sizes
- **Spacing:** Consistent padding/margin scale
- **Shadows:** Soft, medium, and hard shadow utilities

See `tailwind.config.ts` for the complete design system.

## Responsive Design

All components are mobile-responsive:
- **Mobile (< 768px):** Single column layout, smaller text, stacked elements
- **Tablet (768-1024px):** Two-column layout where appropriate
- **Desktop (> 1024px):** Full multi-column layout

## Accessibility

Components follow accessibility best practices:
- Semantic HTML (header, section, footer)
- ARIA labels for icons
- Keyboard navigation support
- Sufficient color contrast (WCAG AA)
- Focus indicators on interactive elements

## Testing

Landing page components are tested via:
- E2E smoke test (`tests/e2e/smoke.spec.ts`)
- Visual inspection on multiple viewports
- Lighthouse accessibility audit

## Future Enhancements

Potential improvements for V1.1+:
- Testimonials component (requires real user testimonials)
- FAQ accordion component
- Partners/logos section (when partnerships established)
- Animation on scroll (intersection observer)
- Video hero background (if video assets available)
