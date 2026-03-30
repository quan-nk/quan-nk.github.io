# CLAUDE.md — wp-qn47

## Project Overview
- **Site**: Quarto website hosted on GitHub Pages
- **Purpose**: Vietnamese-language data science learning platform for beginners ("learn by teaching")
- **Author**: Quan K Nguyen, MD (nguyenkhoiquan@gmail.com)
- **Repo**: Public [`wp-qn47`](https://github.com/quan-nk/wp-qn47) on GitHub
- **Sole author**: Quan K Nguyen — do NOT add `Co-Authored-By` to commits
- **Origin**: Migrated from qn47.wordpress.com (WordPress export archived in `wp-export/`)

## Quarto Workflow
```
edit .qmd → quarto preview → commit → push → GitHub Pages auto-deploys
```
- Output directory: `docs/` (GitHub Pages source)
- Always preview locally before pushing: `quarto preview`
- Render full site: `quarto render`

## Writing Agent
Use `.claude/agents/quan-wp-mask.md` for ALL content writing. This agent writes in Quan's voice.
- Invoke with: `@quan-wp-mask` in Claude Code
- Vietnamese is the primary language for data science tutorials
- English for personal essays or bilingual posts

## Content Rules
- **Language**: Vietnamese primary for tutorials. English terms in parentheses on first use: "độ lệch chuẩn (Standard Deviation, SD)"
- **Progressive disclosure**: hook → context → simple example → theory → code → common mistakes → summary
- **Always start with a hook** — personal anecdote, question, or real-world scenario. Never start with definitions.
- **End with**: "Hy vọng bài viết hữu ích!" or a reflective closing
- **Frame as**: "điều mình học được" (what I learned), never "bạn nên biết" (what you should know)
- **Code**: Use `{r}` executable code chunks. Always `code-fold: true`.
- **Math**: LaTeX with `$...$` for inline, `$$...$$` for display

## Site Structure
```
wp-qn47/
├── _quarto.yml              # Site config
├── index.qmd                # Landing page
├── about.qmd                # About Quan
├── resources.qmd            # Curated learning resources
├── data-science/            # Main learning section (left sidebar)
│   ├── index.qmd            # "Lộ trình học" (Learning Path)
│   ├── r-fundamentals/      # R Cơ bản
│   ├── statistics/          # Thống kê
│   ├── visualization/       # Trực quan hoá
│   └── epi-causal/          # Dịch tễ & Nhân quả
├── mind-wandering/          # Personal essays (preserved from WP)
│   ├── posts/               # Migrated blog posts as .qmd
│   └── book-reviews/
├── wp-export/               # WordPress archive (reference only, not rendered)
├── .claude/agents/
│   └── quan-wp-mask.md      # Writing agent
└── docs/                    # Quarto output (GitHub Pages serves this)
```

## File Naming Conventions
- Tutorials: `data-science/{section}/{slug}.qmd`
- Essays: `mind-wandering/posts/{YYYY-MM-DD}-{slug}.qmd`
- All .qmd files need YAML frontmatter with: title, date, categories, description

## Key References
- WordPress blog_id: 173374270 (for MCP operations on legacy site)
- WordPress MCP tools still available for managing qn47.wordpress.com
- WP content archive: `wp-export/posts/` (34 posts), `wp-export/pages/` (5 pages)
- Plan file: `.claude/plans/unified-wandering-nest.md`
