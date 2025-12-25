# Wes Porter - Writing Style Guide

A reference for capturing my authentic voice in blog posts on geoalchemist.com.

---

## Voice Summary

Casual, reflective, and direct—balancing practical questions with humor, introspection, and a grounded curiosity that mixes warmth and precision.

---

## Core Characteristics

### 1. Conversational & Direct
- Write like you're explaining something to a smart colleague over coffee
- Use contractions freely ("I'm", "you're", "that's", "can't")
- Address the reader as "you" when appropriate
- Rhetorical questions to pull the reader in: "Weird, right?", "Sounds simple enough, right?"
- Short, punchy sentences for emphasis: "Yikes." / "Win win." / "This is **HUGE** problem."
- Occasional one-word or one-line paragraphs for impact
- Use em-dashes liberally for asides and emphasis: "—an AI coding agent—", "—and what I learned about..."
- Favor active, personal framing: "As part of my day-to-day" over formal descriptions

### 2. Problem-Solution Narrative
- Frame posts around a real problem encountered at work or in a project
- Establish context/background before diving into the problem
- Walk through the journey: problem → research → solution → results
- Show the "before" state and the pain points clearly
- Celebrate wins with enthusiasm when earned
- Often structure around numbered options or approaches considered

### 3. Humor (Strategic & Self-Aware)
- Use GIFs from GIPHY to punctuate emotional beats (confusion, frustration, triumph)
- Same GIF can be reused across posts if it fits (the "mind blown" GIF appears multiple times)
- Occasional pop culture references (Eddie Vedder SQL joke, Star Wars "A New Hope" section header)
- Light self-deprecation: "If you're like me when you get a new dataset..."
- Understated jokes dropped casually, not forced
- Wry asides about money/retirement are optional—not required for every post
- Keep GIFs to 1-2 per post; don't overdo it

### 4. Technical Depth with Accessibility
- Don't shy away from code blocks and technical details
- Explain the "why" before the "how"
- Use analogies when helpful (cmd-c, cmd-x for database operations; TI-83 calculator reference)
- Define jargon in context or with callout boxes
- Show concrete numbers and stats: "42,000 zip codes", "6,000 farms", "207 NDVI images"
- Let the data speak—quantify improvements dramatically

### 5. Personal Stakes & Vulnerability
- Share genuine struggles and uncertainties: "Am I good enough?"
- Acknowledge past mistakes: "I did myself a disservice by shying away from some of those challenges"
- Frame learning as a journey, not a lecture
- "Unfortunately, like most things in life, you just don't know what to search for when you're new to something"

### 6. Reflective Closing
- End with takeaways or "Closing Thoughts" section (can be topic-specific: "Closing Thoughts on AI")
- Often circles back to a broader insight beyond the technical details
- Can end with a simple, grounded statement: "A little prompt engineering and curiosity pays off."
- Wry money/retirement jokes are optional—use sparingly, not as a formula
- Sometimes poses future possibilities: "(future blog post?)"

---

## Structural Patterns

### Post Opening
1. **Italicized teaser** immediately after frontmatter—one punchy sentence that hooks
2. `<!--more-->` excerpt break right after the teaser
3. Optional horizontal rule (`---`) before diving into content
4. Often starts with context/background before the core problem

**Example:**
```markdown
*How I achieved a 38,000% boost in execution speed while calculating Zonal Statistics in Python.*

<!--more-->

---

You might be wondering - why write a Python script...
```

### Section Headers
- Use `# Header #` for major sections (Background, The Problem, Results)
- Use `## Header ##` for subsections
- Use `### Header ##` for options/alternatives within a section
- Use `##### Header #####` for sub-points within lists
- Keep headers short and scannable
- Occasional creative headers: "A New Hope", "The DG Problem"

### Paragraph Structure
- Mix longer explanatory paragraphs with short punchy ones
- Use single-sentence paragraphs for emphasis
- Liberal use of line breaks to create visual rhythm
- Horizontal rules (`---`) to separate major sections

### Code & Technical Content
- Use fenced code blocks with language hints (```Python, ```SQL)
- Show output/results directly after code as comments or separate blocks
- Tables in Markdown for structured data
- Include timing/performance metrics when relevant

### Emphasis & Callouts
- **Bold** for key terms, emphasis, and stats: "**42,000**", "**HUGE**"
- *Italics* for asides, internal thoughts, or subtle emphasis
- **_Bold italic_** for extra emphasis: "**_but..._**", "_**all stores**_"
- Hugo shortcodes for alerts: `{{< alert success no-icon >}}` for tips/definitions
- `{{< alert warning >}}` for important caveats
- `{{< blockquote >}}` for external sources with attribution
- Inline code for technical terms: `WHERE`, `SELECT`, `Coffee_ID`

### Visual Elements
- GIFs: embed via `![Alt text](giphy-url)` to add personality at emotional beats
- Images: use Cloudinary URLs, typically with `{{< image >}}` shortcode
- Interactive maps: embed via iframe when relevant
- Embedded tweets for social proof/external voices

---

## Tone Calibration

| Situation | Tone |
|-----------|------|
| Introducing a problem | Slightly frustrated, curious, relatable |
| Explaining technical details | Clear, patient, precise |
| Considering alternatives | Thoughtful, weighing pros/cons honestly |
| Sharing results/wins | Enthusiastic, occasionally emphatic ("That's a 98% decrease!!!") |
| Closing thoughts | Reflective, grounded, sometimes wry |
| Admitting uncertainty | Honest, unbothered ("I'm still tinkering with it...") |
| Giving advice | Warm but direct, speaking from experience |

---

## Common Phrases & Patterns

### Transitions & Framing
- "So what was going on?"
- "Enter [X]." (to introduce the subject)
- "Okay, so..." / "Okay so..."
- "Before I dive into..."
- "I couldn't be the first person to encounter this problem right?"
- "Sounds [adjective] enough, right?" — to set up complexity
- "Turns out, [answer]." — for reveals after questions
- "This reflects a key lesson:" — to highlight takeaways mid-post

### Emphasis
- "Win win."
- "Yikes."
- "This is **HUGE** problem."
- "That's [X]% [faster/better/etc]!" — celebrate quantifiable wins
- Italicize key phrases for emphasis: "**_With the right context_**", "**_messy_**"
- Use "still" to acknowledge nuance: "that's still **400-900 hours per year**"

### Closings
- "Closing Thoughts..." (or topic-specific: "Closing Thoughts on AI")
- "A little [X] and curiosity pays off." — adaptable formula
- "If you've made it this far..."
- Posing future work as questions: "(future blog post?)"

### Reader Connection
- "If you're like me..."
- "You might be wondering..."
- "Was this the table you were expecting?"
- "Weird, right?"

---

## What to Avoid

- Overly formal academic language
- Excessive hedging ("I think maybe perhaps...")
- Clickbait hyperbole without substance to back it up
- Walls of text without visual breaks
- Apologizing for the post's existence
- Over-explaining obvious things
- Passive voice when active is clearer
- Being preachy—share experience, don't lecture
- Overusing formulaic endings (e.g., retirement joke on every post)
- Proof-that-it-works sections without actual evidence—if you claim impact, show it (screenshots, Slack posts, etc.)
- Fluffy filler language: "Here's where it gets interesting" can stay, but don't pad unnecessarily

---

## Frontmatter Template

```yaml
---
title: "Post Title Here"
author: "Wes"
date: YYYY-MM-DD

autoThumbnailImage: false
thumbnailImagePosition: "left"
thumbnailImage: https://res.cloudinary.com/wessport/image/upload/...
coverImage: https://res.cloudinary.com/wessport/image/upload/...
metaAlignment: center
coverMeta: in
comments: true

keywords:
- keyword1
- keyword2

categories:
- Category1
- Category2

tags:
- tag1
- tag2
---
```

---

## Audience Reminder

Primary audience: **professional peers, coworkers, future employers, recruiters, hiring managers**

This blog is a digital portfolio. Posts should demonstrate:
- Technical competence and problem-solving ability
- Clear communication skills
- Initiative and curiosity
- Ability to learn and apply new tools/methods
- Willingness to share knowledge with others

Balance approachability with credibility. Show the work, celebrate the wins, acknowledge the journey.
