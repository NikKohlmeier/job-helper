# Nik Kohlmeier - Portfolio

Frontend-focused web developer portfolio built with vanilla JavaScript, modern CSS (BEM methodology), and GSAP animations.

## Tech Stack

- **HTML5** - Semantic markup
- **CSS3** - Modern CSS with BEM naming, CSS nesting, custom properties (design tokens)
- **JavaScript (Vanilla)** - No frameworks, pure ES6+
- **GSAP** - Smooth scroll animations via CDN
- **Vite** - Modern dev server and build tool
- **GitHub Actions** - Automated CI/CD

## Features

- ✨ Dark/light mode toggle with localStorage persistence
- 🎨 Clean BEM CSS architecture (2-3 levels nesting max)
- 🎭 GSAP scroll animations
- 📱 Fully responsive design
- ♿ Accessible and semantic HTML
- ⚡ Fast loading (no framework overhead)
- 🚀 Auto-deployment via GitHub Actions

## Development

```bash
# Install dependencies
npm install

# Start dev server (http://localhost:5173)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Deployment

Push to `main` branch and GitHub Actions automatically:
1. Installs dependencies
2. Builds the project
3. Deploys to GitHub Pages

## Project Structure

```
portfolio/
├── index.html              # Main HTML file
├── css/
│   └── style.css          # BEM CSS with nesting
├── js/
│   └── main.js            # Vanilla JS + GSAP
├── assets/
│   └── images/            # Images (if needed)
├── .github/
│   └── workflows/
│       └── deploy.yml     # GitHub Actions workflow
├── vite.config.js         # Vite configuration
├── package.json           # Dependencies
└── README.md              # This file
```

## CSS Architecture

- **Design Tokens** - CSS custom properties in `:root`
- **BEM Methodology** - Block__Element--Modifier naming
- **CSS Nesting** - Modern native nesting (2-3 levels max)
- **Responsive** - Mobile-first approach

## License

MIT

---

Built with ❤️ using vanilla JavaScript, BEM CSS, GSAP, and Vite.
