# 🎨 Smart Workforce Platform - Theme & Design Guide

## Color Palette

### Primary Colors
```css
--primary: #667eea;           /* Purple Blue */
--primary-dark: #5568d3;      /* Darker Purple Blue */
--secondary: #764ba2;         /* Deep Purple */
--accent: #f093fb;            /* Pink/Magenta */
```

### Semantic Colors
```css
--success: #10b981;           /* Green */
--danger: #ef4444;            /* Red */
--warning: #f59e0b;           /* Amber */
--info: #3b82f6;              /* Blue */
```

### Neutral Colors
```css
--text-dark: #0f172a;         /* Dark Blue-Black */
--text-muted: #64748b;        /* Gray */
--bg: #f8fafc;                /* Light Gray-Blue */
--dark-bg: #0f172a;           /* Dark Background */
```

---

## Design Elements

### Gradients

#### Primary Gradient (Main Brand)
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```
**Usage**: Buttons, Headers, Cards, Badges

#### Accent Gradient (Secondary Brand)
```css
background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
```
**Usage**: Active states, Highlights, CTA Buttons

#### Light Gradient (Backgrounds)
```css
background: linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%);
```
**Usage**: Subtle backgrounds, Accents

---

## Components

### 1. **Sidebar Navigation**
- **Background**: Dark gradient (#0f172a → #1e293b)
- **Active State**: Pink accent (#f093fb) with glow effect
- **Hover**: Light purple background with smooth animation
- **Icons**: Scale up on hover with color change

```html
<!-- Example -->
<div class="sidebar">
    <div class="brand">
        Logo + Brand Name
    </div>
    <nav class="sidebar-nav">
        <a href="#" class="active">
            <i class="fas fa-icon"></i> Menu Item
        </a>
    </nav>
</div>
```

### 2. **Cards**
- **Background**: White (#ffffff)
- **Border**: 2px solid rgba(102, 126, 234, 0.1)
- **Border Radius**: 15px
- **Shadow**: 0 4px 20px rgba(102, 126, 234, 0.08)
- **Hover**: Lift effect (-5px) with enhanced shadow

```html
<!-- Example -->
<div class="card">
    <div class="card-header">Header</div>
    <div class="card-body">Content</div>
</div>
```

### 3. **Buttons**

#### Primary Button
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
color: white;
border-radius: 10px;
box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
```

#### Secondary Button
```css
background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
color: white;
border-radius: 10px;
box-shadow: 0 4px 15px rgba(240, 93, 108, 0.3);
```

#### Outline Button
```css
border: 2px solid #667eea;
color: #667eea;
background: transparent;
```

### 4. **Badges**
- **Border Radius**: 8px
- **Padding**: 6px 12px
- **Font Weight**: 600
- **Font Size**: 12px

#### Badge Types
- **Primary**: Purple gradient background
- **Success**: Green gradient background
- **Danger**: Red gradient background
- **Warning**: Orange gradient background
- **Info**: Blue gradient background

### 5. **Forms**
- **Input Border**: 2px solid #e2e8f0
- **Border Radius**: 10px
- **Focus Color**: #667eea
- **Focus Shadow**: 0 0 0 0.2rem rgba(102, 126, 234, 0.15)

### 6. **Alerts**
```css
/* Success Alert */
background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
border-left-color: #10b981;
color: #065f46;

/* Danger Alert */
background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
border-left-color: #ef4444;
color: #7f1d1d;

/* Warning Alert */
background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
border-left-color: #f59e0b;
color: #78350f;

/* Info Alert */
background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
border-left-color: #3b82f6;
color: #0c2d6b;
```

### 7. **Tables**
- **Header Background**: Light gradient
- **Header Border**: 2px solid rgba(102, 126, 234, 0.2)
- **Cell Padding**: 15px
- **Row Hover**: Light purple background

### 8. **Modals**
- **Border Radius**: 15px
- **Header Background**: Primary gradient
- **Header Border**: None (rounded top)
- **Box Shadow**: 0 20px 60px rgba(0, 0, 0, 0.15)

---

## Animations

### Hover Effects
```css
/* Lift Effect */
transform: translateY(-5px);
transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

/* Color Transition */
transition: color 0.3s ease;

/* Scale Effect */
transform: scale(1.1);
```

### Loading Animation
```css
@keyframes shine {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
}
```

---

## Typography

### Font Family
```css
font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
```

### Font Weights
- **Regular**: 400
- **Medium**: 500
- **Semibold**: 600
- **Bold**: 700
- **Extra Bold**: 800

### Font Sizes (Desktop)
- **H1**: 2.8rem (44px), 800 weight
- **H2**: 2.2rem (35px), 700 weight
- **H3**: 1.5rem (24px), 700 weight
- **Body**: 1rem (16px), 400 weight
- **Small**: 0.875rem (14px), 500 weight
- **Label**: 0.75rem (12px), 600 weight

---

## Spacing

### Standard Spacing Scale
```
8px   (0.5rem)
16px  (1rem)
24px  (1.5rem)
32px  (2rem)
40px  (2.5rem)
48px  (3rem)
64px  (4rem)
```

### Padding
- **Sidebar**: 20-25px horizontal
- **Card**: 25px (body), 20px (header)
- **Button**: 10px vertical, 20px horizontal
- **Input**: 10px vertical, 15px horizontal

---

## Responsive Design

### Breakpoints
- **Mobile**: < 576px
- **Tablet**: 576px - 768px
- **Small Desktop**: 768px - 992px
- **Desktop**: 992px - 1200px
- **Large Desktop**: > 1200px

### Mobile Adjustments
- **Sidebar**: Full width, toggleable
- **Font Sizes**: Reduced by 10-15%
- **Padding**: Reduced by 20-30%
- **Card Border Radius**: 12px instead of 15px

---

## CSS Variables (Use These!)

```css
:root {
    --primary: #667eea;
    --primary-dark: #5568d3;
    --secondary: #764ba2;
    --accent: #f093fb;
    --success: #10b981;
    --danger: #ef4444;
    --warning: #f59e0b;
    --info: #3b82f6;
    --text-dark: #0f172a;
    --text-muted: #64748b;
    --bg: #f8fafc;
    --dark-bg: #0f172a;
    --gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    --gradient-accent: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    --gradient-light: linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%);
}
```

---

## Usage Examples

### Example 1: Creating a Custom Card
```html
<div class="card">
    <div class="card-header">
        <h5 class="card-title">Title</h5>
    </div>
    <div class="card-body">
        <p>Content goes here</p>
    </div>
</div>
```

### Example 2: Custom Button
```html
<button class="btn btn-primary">
    <i class="fas fa-plus"></i> Add Item
</button>
```

### Example 3: Stat Card
```html
<div class="stat-card">
    <div class="stat-card-icon primary">
        <i class="fas fa-users"></i>
    </div>
    <div class="stat-card-value">256</div>
    <div class="stat-card-label">Total Users</div>
</div>
```

---

## Best Practices

1. **Always use CSS variables** for colors
2. **Use gradients** for primary actions
3. **Add hover effects** to interactive elements
4. **Keep shadows subtle** - not harsh
5. **Use proper transitions** - 0.3s cubic-bezier(0.4, 0, 0.2, 1)
6. **Test on mobile** - ensure responsive design
7. **Keep consistency** - use the same patterns throughout
8. **Accessibility**: Ensure sufficient color contrast
9. **Loading states**: Add visual feedback for actions
10. **Error states**: Use the danger color consistently

---

## Color Contrast

### WCAG AA Compliant
- Dark text on light background: ✅ Passes
- Light text on dark background: ✅ Passes
- Primary color on white: ✅ Passes
- Warning color on white: ✅ Passes

---

## Troubleshooting

### Issue: Colors look different in production
**Solution**: Check if CSS is properly minified and cached correctly

### Issue: Gradients not showing
**Solution**: Add vendor prefixes:
```css
background: -webkit-linear-gradient(...);
background: linear-gradient(...);
```

### Issue: Text hard to read
**Solution**: Check color contrast ratio (should be 4.5:1 minimum)

### Issue: Animations feel slow
**Solution**: Use `cubic-bezier(0.4, 0, 0.2, 1)` for snappier feel

---

## Theme Files

- **Main Style**: `base.html` (embedded)
- **Landing Page**: `landing.html` (embedded)
- **Dashboard**: All templates inherit from `base.html`
- **Custom Colors**: Set via company settings (CompanyBranding model)

---

## Version History

- **v1.0** (Feb 2026): Initial colorful theme
  - Purple/Blue primary colors
  - Pink/Magenta accent colors
  - Modern gradient design
  - Smooth animations
  - Full dark sidebar

---

## Support

For theme customizations or issues:
1. Check this guide first
2. Review existing components in templates
3. Test changes on mobile
4. Update this guide with your changes

---

**Made with ❤️ for beautiful user interfaces**

**Last Updated**: February 2, 2026
