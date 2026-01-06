---
title: "Developing with AI Agents"
author: "Wes"
date: 2025-12-30

autoThumbnailImage: false
thumbnailImagePosition: "left"
thumbnailImage: https://res.cloudinary.com/wessport/image/upload/v1767647909/atomic-776857940_odfe0t.png
coverImage: https://res.cloudinary.com/wessport/image/upload/v1767648076/IMG_1049_alt_qmro27.jpg
metaAlignment: center
coverMeta: in
comments: true

keywords:
- AI
- Python
- Amp
- Developer Tools
- Productivity

categories:
- AI
- Python

tags:
- amp-sdk
- automation
- developer-tools
---

*How I built a Streamlit App from Scratch using Amp AI agents.*

<!--more-->

---

# Background #

Over the past few weeks, I've been building a new app **LocDB Tools** — an internal facing Streamlit app with three main tools for my team:

1. [A Python Powered SQL Validator & SQL Generator](/2025/12/building-a-streamlit-app-to-scale-my-teams-output/)
2. [AI Enhanced Regression Reports](/2025/12/adding-claude-to-a-streamlit-app/)


The fun part - I developed the entire app using [Claude](https://www.anthropic.com/claude/opus) and [Amp by Sourcegraph](https://ampcode.com/).

---

# Development Velocity #

A few years ago, building these three tools would have taken me a week or two of focused work squeezed between other core projects. 

Instead, I built them in a few days — including hitting a few road bumps - buffer limits, debugging async/sync conflicts (not my cup of tea), and restructuring the original steamlit app.

I built these tools with detailed prompts via Amp.

### Claude Opus 4.5

This is the model I'm currently working with. Prior to using Opus, I was using Sonnet up to this point, but I've found Opus handles complexity better and is less prone to making mistakes (looking at you Gemini 3).

Opus has a smaller context window than Sonnet, but I haven't really found this to be a major issue. When I approach the limit, I use the `handoff` feature of Amp to spinoff a new thread. I've also found this helps make sessions more targeted and requires me (in a good way) to do more upfront planning.

Then I step back and let the model cook.

### Example Prompt:

```
Please review the AGENT.md document before getting started for general guidelines on how to proceed in this project. Read the project README.md.

Today's goal is to add a new tool to the streamlit app that generates a sql file for the user when they upload a csv of their proposed data changes.

Please use the Atlassian mcp server to read this wiki page regarding bulk updates to the location database: <link-to-wiki-page>

It has examples for bulk edits (updating existing records), uploads (inserting new records), and deletes (soft deletes).

We use the following python scripts to create the sql files:
* <link-to-bulk-delete-script>
* <link-to-bulk-edit-script>
* <link-to-bulk-insert-script>

The goal is to abstract the use of python away so that analysts don't have to run these scripts locally, they just upload their csv and get back the sql file they want to then upload to the validation tool to check for data quality issues.

Ask clarifying questions as needed.
```

### Example Followup prompts:

- "The Amp SDK is hitting a buffer limit. Here's the error. <\long-error-message-here>. What are our potential options for reducing the buffer limit - plan before writing any code."

- "I want to add a streaming progress window to the app. How can we feed messages from the SDK into the streamlit app to show progress to end users?"

_*I shortened the above prompts for readability here. I usually write a fairly detailed prompt with links to important project specific context._

---

# AI Context Strategy #

Each time I implement a new feature or cross a development milestone, I ask the agent to write a new "ai log file" documenting all of the work (and struggles):

| Session | What We Built |
|---------|---------------|
| 01 | SQL Validator core implementation |
| 02 | Landing page and project restructure |
| 03 | AI feature UI improvements |
| 04 | Amp SDK integration fixes |
| 05 | LLM integration challenges (buffer limits) |
| 06 | Aggregation approach success |
| 07 | Streaming progress UI |
| 08 | SQL Generator tool |

Each session picks up context from previous ones. This allows each session to reference past work rather than starting from scratch each time - similar to Amp's thread handoff feature. 

Adding a new tool becomes easier since I just have to explain *what* I want, and not re-teaching *how* the entire project works and past efforts.

---

# A Glimpse at the Future of Coding #

A few things made this development style effective:

**1. Domain knowledge matters.** 

I maintain `AGENT.md` files that explain project structure, conventions, and domain concepts. I routinely ask the agent to update the AGENT file as the project evolves.

**2. Iterative short conversations beat large one-shot prompts.** 

Complex features emerge through back-and-forth on focused tasks. Wide scoped tasks usually get too complex fast, leading to the agent unraveling, so keeping the prompt focused and on succinct tasks seems to yield the best results in my experience. 

For example, I might ask it to create a feature vs a whole app and then provide feedback: "That's close, but the history file should only show which values explicitly were changed." 

**3. Validation.** 

There's a lot of back and forth validation of what the AI agent is doing. It's important to not blindly rely on the agent, but check and validate their work.

This involves manually testing each new feature to ensure it works as expected - AI is like a junior collegue, sometimes they interpret instructions in unexpected ways. It's **critical** to check how they implemented a feature and if it's reliable.

**4. Prior sessions build on one another.** 

Early sessions built the SQL validator. Later sessions referenced that work to build the SQL generator. The AI understood what `LocDB` was, what the `locations_table` contains, how I prefer to structure Streamlit pages.

**5. Let the AI Agent run the build.** 

After making changes, I have the AI agent run `streamlit run` in a separate tmux session to check for errors. This helps it catch its own errors and make fixes - automating some of the simple validation work i.e. does it build successfully.

---

# Closing Thoughts #

AI is a powerful tool **_if used in the right context_**. 

It unlocks the ability to create efficiency wins quickly - but its only as good as the user's domain knowledge. Without that, it has the poential to have the opposite effect.

Personally, I don't see AI replacing human analysts in the near term. I think it's most useful when used in a collaborative method like this to quickly develop tooling or explore data. It still needs a guide.

Cost of AI powered development sessions is another major factor that I think impacts its ROI at the moment - maybe a topic for another post.

Currently see its value in mainly freeing up our time from manual work to focus on bigger picture challenges - automating and scaling our impact beyond what we normally could. 

With AI tooling evolving at what feels like a daily pace, it's going to be an interesting new year with plenty of opportunity to continue experimenting and learning.
