# Geoalchemist - Agent Instructions

Personal blog/portfolio site for GIS and programming topics.

**Site:** https://www.geoalchemist.com/  
**Framework:** Hugo (static site generator)  
**Theme:** Tranquilpeak (v0.5.3-BETA)  
**Hosting:** Netlify

## Commands

```bash
# Local development server
hugo server

# Production build (verify before committing)
hugo
```

## Workflow

- Use feature branches for major changes (e.g., `site-revival-2025`)
- Test that `hugo` builds successfully before committing
- Direct commits to `main` acceptable for minor fixes

## Content

- Posts live in `content/post/`
- Use `.md` files for new posts (not `.html`)
- Images should be hosted on Cloudinary (see existing posts for URL patterns)
- Frontmatter fields: title, date, categories, tags, thumbnailImage, coverImage

## Theme

- Theme files are in `themes/tranquilpeak/`
- The upstream theme is no longer actively maintained
- Patching theme files directly is acceptable when needed
- Theme was updated to work with Hugo v0.153.0+

### Known Theme Patches Applied

- `.Site.Author` → `.Site.Params.author` in templates
- Custom `google-analytics.html` partial for modern GA support
- Raw HTML rendering enabled in `config.toml`

## Configuration

- Main config: `config.toml`
- Author info is under `[params.author]`
- Google Analytics is currently commented out (needs GA4 migration)

## Code Snippets

- Python is the primary language used in tutorials
- Syntax highlighting uses highlight.js
