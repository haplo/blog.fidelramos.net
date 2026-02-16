# AGENTS.md

Guidance for AI agents working on this codebase.

## Project Overview

Personal blog built with [Pelican](http://getpelican.com/) (Python static site generator) using the [Reflex theme](https://github.com/haplo/reflex). Content is written in Markdown.

## Setup

Requires [uv](https://github.com/astral-sh/uv) package manager.

```bash
uv sync
```

## Commands

Run from the `src/` directory:

| Command | Description |
|---------|-------------|
| `make html` | Generate static site |
| `make clean` | Remove generated files |
| `make devserver` | Serve at localhost:8000 with auto-regeneration |
| `make serve` | Serve at localhost:8000 (no auto-regen) |
| `make publish` | Build for production |
| `make regenerate` | Auto-regenerate on file changes |

## Project Structure

```
src/
├── content/           # Markdown articles
│   ├── pages/         # Static pages (about, projects, etc.)
│   ├── images/        # Blog images
│   ├── software/      # Software articles
│   ├── personal/      # Personal articles
│   ├── photography/   # Photography articles
│   └── cryptocurrency/# Cryptocurrency articles
├── output/            # Generated HTML (gitignored)
├── pelicanconf.py     # Development config
└── publishconf.py     # Production config
```

## Content Conventions

### Article Naming
- Format: `YYYY-MM-DD_article_title.md`
- Spanish versions: `YYYY-MM-DD_article_title_es.md`

### Frontmatter
```yaml
Title: Article Title
Date: YYYY-MM-DD
Lang: en  # or 'es' for Spanish
Category: Software
Tags: tag1,tag2
Slug: article-slug
```

### URL Structure
- Articles: `/{category}/{slug}.html`
- Categories: `/categories/{slug}.html`
- Tags: `/tags/{slug}.html`

## Configuration

- `pelicanconf.py` - Development settings (localhost URLs, no feeds)
- `publishconf.py` - Production settings (live URL, RSS/Atom feeds, analytics)

## Deployment

```bash
./deploy.sh  # Must be on master branch
```

## Dependencies

Key packages from `pyproject.toml`:
- `pelican[markdown]>=4.11.0`
- `markdown-captions>=2.1.2`
- `pelican-i18n-subsites>=1.0.0`
- `pelican-theme-reflex>=3.0.3`
