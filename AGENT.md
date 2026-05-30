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

## Git Configuration

**Author info for this repo:**
- Name: `wessport`
- Email: `wesporter92@gmail.com`

When committing, always use:
```bash
GIT_AUTHOR_NAME="wessport" GIT_AUTHOR_EMAIL="wesporter92@gmail.com" \
GIT_COMMITTER_NAME="wessport" GIT_COMMITTER_EMAIL="wesporter92@gmail.com" \
git commit --no-verify -m "message"
```

**IMPORTANT:** Do NOT include any AI assistant trailers or co-author lines in commits:
- No `Co-authored-by: Amp` or similar
- No `Amp-Thread-ID` or similar thread references
- No mentions of `ampcode.com` or `ampcode-com`

Before pushing any branch, verify new commits do not contain forbidden AI metadata:
```bash
git log origin/$(git branch --show-current)..HEAD --format=%B | \
  grep -E 'Co-authored-by: Amp|Amp-Thread-ID|ampcode' && \
  echo "ERROR: forbidden AI metadata found"
```

If forbidden metadata appears, rewrite the affected commit message before pushing. Do not rely on `git commit --amend` if the local environment is auto-inserting trailers; recreate the commit with an explicit clean message instead, then re-run the verification above.

Pull request descriptions must also avoid AI assistant metadata and should not mention Amp, ampcode.com, thread IDs, or co-authoring by an AI assistant.

## Workflow

- Use feature branches for major changes (e.g., `site-revival-2025`)
- Test that `hugo` builds successfully before committing
- Direct commits to `main` acceptable for minor fixes
- Do not merge pull requests without explicit user approval. It is okay to open, update, review, and summarize PRs, but stop before merge and ask for confirmation unless the user has clearly said to merge that specific PR.

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
