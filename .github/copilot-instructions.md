# Project Overview
This project is a Wagtail CMS site using Django as its backend and a modern frontend build process with Vite for managing assets. Tailwind CSS is used for all styling.

# Technology Stack
- **Backend**: Django, Wagtail CMS
- **Frontend**: Tailwind CSS 4+, Vite, JavaScript (ES6+)
- **Templating**: Django Templates, with Wagtail-specific template tags.

# Project Structure
- Django and Wagtail files are organized in the standard Django layout.
<!-- - All frontend assets (JavaScript, CSS) are located in the `frontend/` directory. -->
- Compiled static assets are served from the `static/` directory.

# Coding Guidelines

## Django & Wagtail
- Follow Django and Wagtail best practices for models, views, and templates.
- Use `StreamField` for flexible content creation on pages.
- Create custom template tags and filters when template logic becomes complex.
- Use the `wagtail start` template as a base for standard directory layout.

## Tailwind CSS
- **Utility-first approach**: Prefer Tailwind's utility classes over writing custom CSS where possible.
- **No unnecessary prefixes**: Tailwind 4+ does not require `postcss` or `autoprefixer`.
- **Content path**: Ensure `tailwind.config.js` is configured to find template files (`.html`) in all relevant Django/Wagtail app directories to correctly generate CSS.
- **Tailwind Plugins**: Use the `@tailwindcss/typography` plugin for styling rich text content within Wagtail's rich text editor, as standard Tailwind resets heading and list styles.
- **Consistent styling**: Adhere to the established styling conventions found in existing components and templates.

## Templates
- **Frontend Assets**: Load compiled static assets (e.g., `main.min.css`, `main.min.js`) using the `{% static %}` template tag in the `base.html` file.
- **HTML structure**: Use semantic HTML5 elements.

## Frontend Build Process (Vite)
- **Vite configuration**: The `vite.config.js` file is configured to output compiled assets to the `static/` directory to be served by Django.
- **npm scripts**: The project uses `npm run dev` for watching and compiling assets during development, and `npm run build` for a production build.

# Important File References
- `tailwind.config.js`: Tailwind CSS configuration file.
- `vite.config.js`: Vite build tool configuration.
- `frontend/`: Contains raw, uncompiled frontend assets.
- `static/`: Contains compiled CSS and JS assets.
- `templates/`: Contains Django and Wagtail template files.
