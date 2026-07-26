# 2026 Family AI Class - 3-4 Hour Teaching Plan

Draft date: 2026-06-22 CDT

Source document: Robert's "2026 Family AI Class" notes, exported from Google Docs through the National Outreach account with read permission. Robert's original notes are preserved at the end.

## Prep For Participants

Send this section before class. The first group is enough for everyone. The hands-on setup is only needed for people who want to follow along on their own Mac.

### Everyone Should Bring Or Prepare

- A laptop if you want to follow along. Watching is also fine.
- A charger.
- Access to your normal email account.
- A ChatGPT account. Free is enough for basic chat practice; paid plans may be needed for heavier Codex use depending on current product limits.
- One harmless example task, such as rewriting a recipe note, summarizing a public article, planning a trip, or making a small study guide.
- One question about AI safety, privacy, school, work, coding, or creative use.

### Hands-On Coding Prep

- Use a Mac if you want to follow the local web server and Codex demos.
- Install or confirm Python 3:

```bash
python3 --version
```

- Install GitHub Desktop:

```text
https://desktop.github.com/download/
```

- Create or confirm a GitHub account:

```text
https://github.com/
```

- Install Homebrew from the official site:

```text
https://brew.sh/
```

- Optional: install Codex from OpenAI's official quickstart:

```text
https://developers.openai.com/codex/quickstart
```

### Tools We Will Discuss

| Tool | Why It Matters | Needed For Class? |
| --- | --- | --- |
| ChatGPT | Easy chat, rewriting, explanations, planning, prompts. | Yes for hands-on chat |
| Gemini / Claude / Perplexity | Useful comparison tools and examples of the wider AI market. | No |
| GitHub account | Stores and shares code projects. | Helpful |
| GitHub Desktop | Visual Git checkpoints, diffs, commits, and sync. | Helpful for coding demo |
| Homebrew | Mac package manager for developer tools. | Helpful for setup |
| Terminal | Runs local commands and servers. | Yes for local server demo |
| Python 3 | Includes a simple local web server. | Yes for local server demo |
| Codex | Coding agent that can inspect files, edit, run commands, and verify. | Optional but recommended |
| Local web server | Shows how files become a working local website. | Yes for web demo |

### What We Will Not Do In Class

- We will not paste passwords, API keys, private 2FA codes, banking data, private medical information, confidential work documents, or customer records into AI tools.
- We will not require paid API keys for the first class.
- We will not expose a server publicly on the internet.
- We will not debug every individual laptop setup during the main teaching time.

### Quick Mac Self-Test

Open Terminal and run:

```bash
mkdir -p ~/Desktop/family-ai-class-test
cd ~/Desktop/family-ai-class-test
printf '<h1>Hello local web server</h1>\n' > index.html
python3 -m http.server 8000 --bind 127.0.0.1
```

Then open this in a browser:

```text
http://127.0.0.1:8000
```

If you see "Hello local web server", your Mac is ready for the local server demo. Press Control-C in Terminal to stop the server.

## Instructor Prep

- Decide whether participants are watching only or following along.
- Have one Mac ready with Terminal, browser, GitHub Desktop, Homebrew, Python 3, and Codex.
- Create a clean demo folder, for example `family-ai-class`.
- Prepare these demo files:
  - `index.html`
  - `style.css`
  - `app.js`
  - `prompt_harness.py`
  - `server.py`
- Test the local server:

```bash
python3 -m http.server 8000 --bind 127.0.0.1
```

- Test:

```text
http://127.0.0.1:8000
```

- Test Codex login before class if you will demo agent edits.
- Test GitHub Desktop with the demo folder before class if you will show diffs and commits.
- Keep a "no secrets" warning visible before live prompting.

## Class Goal

This is a 3-4 hour practical AI introduction. The point is to move from easy AI use to more powerful tool use in one sequence:

```text
Chat -> App -> Coding Tool -> Agent -> Loop -> Harness -> Server
```

By the end, participants should understand:

- What AI tools are useful for.
- Where AI tools are risky or unreliable.
- How to write clearer prompts.
- How privacy and data-sharing choices matter.
- How a simple local website works.
- How coding agents differ from normal chat.
- Why advanced AI workflows need loops, harnesses, logs, stop conditions, and human review.

## 4-Hour Class Plan

This is the primary version. Each module includes the time, teaching points, live demo, and participant activity.

### 0:00-0:10 - Module 1: Welcome And Safety Baseline
#### Instructor Script

Use this opening to reduce anxiety and make the class feel practical:

```text
This is not a class about becoming a professional programmer in one afternoon. It is a class about understanding the ladder of AI tools. We will start with chat because everyone can use it. Then we will move into files, local websites, coding agents, loops, harnesses, and servers so you can see where the power and risk increase.
```

Then draw or show:

```text
Chat -> App -> Coding Tool -> Agent -> Loop -> Harness -> Server
```

Explain the ladder in one sentence each:

- Chat: the AI answers or drafts.
- App: the AI works inside a product such as a document editor, spreadsheet, browser, or image tool.
- Coding tool: the AI helps with files and code.
- Agent: the AI can take actions, inspect files, run commands, and make changes.
- Loop: the work repeats until a condition is met.
- Harness: the work is wrapped in a repeatable test or scoring process.
- Server: the workflow is reachable through a URL or API.

#### Board Or Slide

Put this on the screen:

| Level | Student Question | Main Risk |
| --- | --- | --- |
| Chat | What should I ask? | Believing confident wrong answers |
| App | What context does the app have? | Sharing data without noticing |
| Coding tool | What file changed? | Not reviewing output |
| Agent | What actions can it take? | Too much autonomy without scope |
| Loop | When does it stop? | Runaway cost or bad iteration |
| Harness | How do we score it? | Measuring the wrong thing |
| Server | Who can access it? | Security and exposure |

#### Mini Activity

Ask each participant to choose one level they already understand and one level they want to understand by the end.

Expected answers:

- Many will know chat.
- Some will know apps.
- Few will know harness/server.

Use that to tell the room:

```text
It is fine if the last two levels feel abstract right now. They will make more sense after we build and serve a tiny local page.
```

#### Common Beginner Confusions

- "AI" is not one product.
- ChatGPT is not the same thing as Codex.
- A local server is not automatically a public website.
- A coding agent is not just a chatbot with better programming knowledge; it is connected to files and tools.
- A harness is not a fancy prompt; it is a repeatable wrapper around prompts, tests, and scoring.

#### Instructor Timing

- 2 minutes: welcome and goal.
- 3 minutes: ladder.
- 3 minutes: safety baseline.
- 2 minutes: room check.

If running behind, keep the ladder and safety baseline and skip the table.


Goal: Set the frame and make clear that AI is useful but not automatically trustworthy.

Teaching points:

- This class starts with chat and ends with local tools and small systems.
- AI is a fast draft partner, not an authority.
- The more power a tool has, the more important scope and verification become.
- Safety rule: do not paste secrets or sensitive private data.

Say:

```text
Today we are going from the simplest version of AI, which is chat, to the more powerful version, where AI can help change files, run local tools, and repeat work inside a controlled system. The goal is not to trust AI blindly. The goal is to learn how to use it with scope, verification, and good judgment.
```

Room check:

- Who has used ChatGPT, Gemini, Claude, or Perplexity?
- Who has opened Terminal?
- Who has used GitHub?
- Who has made a website before?

Do not spend more than two minutes on answers. Use the answers to tune the pace.

### 0:10-0:35 - Module 2: AI General - What It Is And What Is Out There
#### Deeper Explanation

Modern AI systems are useful because they turn context into structured output. The context can be a question, a draft email, a file, a screenshot, a codebase, a meeting note, or a set of instructions. The output can be text, code, a plan, a table, an image, a summary, a critique, or a proposed action.

Use three simple claims:

1. AI is good at patterns.
2. AI is not automatically good at truth.
3. AI becomes more useful when the task, context, and verification are clear.

Do not over-explain model architecture. For this audience, the practical mental model matters more:

```text
AI is a fast assistant that can draft, transform, explain, compare, and propose. It still needs a human to decide what matters and whether the answer is acceptable.
```

#### Offers Out There / Tools

Tie directly to Robert's note: Gemini, ChatGPT, apps, CLI, agents.

| Tool Type | Examples | Good For | Watch Out For |
| --- | --- | --- | --- |
| General chat | ChatGPT, Gemini, Claude | Learning, drafting, brainstorming | Hallucinated facts |
| Search-style AI | Perplexity, ChatGPT search, Gemini with search | Current info and source discovery | Weak source quality |
| Office/app AI | Google Workspace, Microsoft Copilot, Notion AI | Docs, email, slides, spreadsheets | Hidden data/context sharing |
| Coding agents | Codex, Copilot, Cursor, Windsurf | Editing files and running tests | Changes need review |
| Creative tools | image/video/audio AI tools | Mockups and creative drafts | Rights, realism, taste |
| Automation tools | Zapier, Make, scripts | Repeated workflows | Silent bad automation |
| Local tools | Terminal, Python, local servers | Private experiments and coding demos | Setup friction |

#### Use Cases

Everyday examples:

- Turn a messy note into a clean email.
- Summarize a public article.
- Create a study plan.
- Compare three products or trip options.
- Draft a checklist.
- Explain a technical term in plain language.

Work examples:

- Draft first-pass documentation.
- Turn meeting notes into action items.
- Create a table from unstructured text.
- Review a message for tone and clarity.
- Draft a spreadsheet formula.
- Convert a process into a checklist.

Programming examples:

- Explain a folder.
- Create a simple HTML page.
- Debug an error message.
- Add a small feature.
- Write a test.
- Run a local web server.

#### Live Demo Sequence

Use one prompt and then transform the output:

```text
Explain AI tools to a beginner in six categories: chat, search, apps, coding agents, creative tools, and automation. For each category, give one example, one good use, and one risk.
```

Follow up:

```text
Turn that into a table for a class handout.
```

Follow up:

```text
Now shorten it to the version I could explain out loud in two minutes.
```

Teaching point:

AI is useful not only because it answers, but because it can reshape the same material for different uses.

#### Discussion Prompt

Ask:

```text
Which of these categories feels most useful to you right now, and which feels most risky?
```

Expected discussion:

- Chat feels approachable.
- Coding agents feel powerful but scary.
- Search feels useful but participants may not know how to judge sources.
- Creative tools may raise questions about authenticity.

#### Instructor Cautions

Avoid saying "AI knows" or "AI understands" too casually. Use:

- "The model produces..."
- "The tool can help draft..."
- "The answer still needs checking..."

This creates the right mental habit for the rest of the class.


Goal: Give a grounded map of the AI landscape.

Teaching points:

- Modern AI tools generate likely useful outputs from context.
- They are strong at language, structure, examples, transformations, summaries, first drafts, and code patterns.
- They can be wrong, stale, overconfident, incomplete, or unsafe.
- Tool choice should follow the job.

Tool categories:

| Category | Examples | Use Cases |
| --- | --- | --- |
| Chat assistants | ChatGPT, Gemini, Claude | Explanations, rewriting, planning, brainstorming |
| Search/research assistants | ChatGPT search, Perplexity, Gemini search | Current information, source-backed summaries |
| App assistants | Google Workspace, Microsoft Copilot, Notion, Canva | Work inside existing documents and apps |
| Coding tools | Codex, GitHub Copilot, Cursor/Windsurf agents | Files, code, tests, local project work |
| Media tools | Image, video, voice, audio tools | Creative drafts and production assets |
| Automation tools | Scripts, Zapier, Make, internal agents | Repetitive workflows |

Live demo:

Ask ChatGPT:

```text
Explain the difference between a chat assistant, an app assistant, a coding agent, and a local server. Use one short paragraph and one practical example for each.
```

Participant activity:

Write down one low-risk task where AI could help you this week.

Teaching point:

"The best first AI task is one where the cost of being wrong is low and you can easily check the answer."

### 0:35-1:05 - Module 3: Easy AI - Chat, Prompts, Personas
#### Prompt Anatomy

Give participants a concrete model:

| Part | Question It Answers | Example |
| --- | --- | --- |
| Role | Who should the AI act like? | Act as a patient tutor |
| Task | What do I want? | Explain local web servers |
| Context | What does it need to know? | I am on a Mac and new to Terminal |
| Constraints | What should it avoid or limit? | Use plain language, no jargon |
| Output format | What should the answer look like? | 5 bullets and one command |
| Verification | How should uncertainty be handled? | Separate facts from assumptions |

#### Prompt Progression Exercise

Start bad:

```text
Tell me about AI.
```

Make it better:

```text
Explain AI to a beginner who has used ChatGPT once. Use 5 bullets, include 2 risks, and end with one safe practice exercise.
```

Make it task-specific:

```text
Act as a patient tutor. I am preparing for a family AI class. Explain the difference between ChatGPT, Codex, GitHub Desktop, Homebrew, and a local web server. Use a table with one row per tool and one beginner-friendly example.
```

Make it safer:

```text
Before answering, list any assumptions you are making. Do not ask me to paste passwords, private data, API keys, customer data, or medical information.
```

#### Persona Examples

Use personas as lenses, not costumes:

| Persona | Useful When | Prompt Starter |
| --- | --- | --- |
| Tutor | Learning a concept | Act as a patient tutor... |
| Editor | Improving writing | Act as a concise editor... |
| Skeptic | Finding flaws | Act as a skeptical reviewer... |
| Project manager | Turning ideas into tasks | Act as a project manager... |
| Security reviewer | Checking risk | Act as a security-minded reviewer... |
| Coding assistant | Working with files/code | Act as a coding assistant... |

#### Live Demo: Same Material, Different Personas

Prompt:

```text
Here is my rough plan: teach AI basics, prompts, safety, Codex, GitHub, Homebrew, local web server, loops, harnesses, and servers. Turn this into a class outline.
```

Then:

```text
Now act as a skeptical beginner. What would confuse you?
```

Then:

```text
Now act as a safety reviewer. What should I warn participants not to do?
```

Then:

```text
Now act as a practical instructor. What should I demonstrate live?
```

Teaching point:

The same source material can be transformed by changing the role and review lens.

#### Common Prompt Failures

- Too vague: "Make this better."
- No audience: the answer does not know who it is for.
- No constraints: the answer gets too long or too formal.
- No source boundary: the answer may invent facts.
- No output format: the answer is hard to use.
- No verification: the answer hides uncertainty.

#### Participant Exercise

Ask participants to write a prompt for one harmless task. Then have them add:

1. Audience.
2. Format.
3. One safety constraint.
4. One verification request.

Example:

```text
Act as a concise editor. Rewrite this note as a friendly text message to a family member. Keep it under 80 words. Do not add facts I did not provide. If anything is unclear, ask one question first.
```

#### Instructor Timing

- 5 minutes: prompt anatomy.
- 8 minutes: live demo.
- 8 minutes: participant prompt rewrite.
- 5 minutes: persona examples.
- 4 minutes: debrief.


Goal: Teach basic prompting and iteration.

Teaching points:

- A prompt is a work order.
- Better prompts include role, task, context, constraints, output format, and verification.
- Personas are useful when they create a concrete review lens.
- The first answer is usually a draft.

Prompt pattern:

```text
Role:
Task:
Context:
Constraints:
Output format:
Verification:
```

Live demo prompt:

```text
Act as a patient tutor. I am teaching a family class about AI. Explain chat, app assistant, coding agent, loop, harness, and server. Use one short paragraph for each and include one beginner-friendly example.
```

Follow-up:

```text
Now make this less abstract and add one thing beginners should be careful about for each level.
```

Persona demo:

```text
Act as a skeptical editor. Review this class outline for places where a beginner might get confused or where the demo could become risky. Give the top 5 fixes.
```

Participant activity:

Improve this weak prompt:

```text
Tell me about AI.
```

Example improved prompt:

```text
Explain AI to a beginner who has used ChatGPT once. Use 5 bullets, include 2 risks, and end with one safe practice exercise.
```

Teaching point:

"A prompt is not a magic spell. It is a work order. The clearer the work order, the easier it is to check the result."

### 1:05-1:25 - Module 4: Safety, Privacy, Retention, Verification
#### Data Sharing Rules

Say this clearly:

```text
If you would not put it in an email to a stranger, do not paste it into a general AI tool for practice.
```

Never paste:

- Passwords.
- API keys.
- Private 2FA codes.
- Session cookies.
- Bank account information.
- Social Security numbers.
- Private medical information.
- Private legal documents.
- Customer lists.
- Confidential work files.
- Private family information that someone else would not want shared.

Safer alternatives:

- Use fake names.
- Remove account numbers.
- Summarize the situation instead of pasting the document.
- Use public examples.
- Ask the AI how to sanitize the data before sharing, without sharing the sensitive data itself.

#### Retention And Training Settings

Explain carefully:

- Settings vary by tool, plan, account type, and date.
- Do not rely on something a friend said months ago.
- Open the product settings and check the current privacy/training controls.
- Business or enterprise accounts may have different data handling from personal accounts.
- API usage may have different retention and training rules from consumer chat.

Do not promise that a setting exists unless you are showing it live.

#### Verification Habits

Teach these habits:

| Situation | Verification |
| --- | --- |
| Current fact | Check source/date |
| Medical/legal/financial | Ask a qualified professional or official source |
| Code change | Run it and review diff |
| Email/text | Read aloud before sending |
| Summary | Spot-check against original |
| Citation | Click the source |
| Command line | Understand before running |

#### Hallucination Demo

Ask:

```text
Give me three sources about a topic and include links.
```

Then show that links and citations must be clicked and checked. Do not dwell on embarrassing the tool. The lesson is:

```text
AI output is a lead, not proof.
```

#### Safe Prompt Pattern

```text
Use only the information I provide. If you are unsure, say what is uncertain. Do not invent sources, dates, names, or quotes. Separate confirmed facts from assumptions.
```

#### Participant Activity

Give these examples and ask safe/unsafe:

- Public recipe.
- Private medical bill.
- Fake customer complaint.
- Real customer complaint with name and phone number.
- Password reset code.
- Public article link.
- Family conflict text thread.
- Sanitized summary of a family conflict.

Debrief:

The question is not "Can AI help?" It is "What can I safely share, and how will I check the result?"


Goal: Give practical rules for safe AI use.

Teaching points:

- Do not paste secrets or sensitive personal data.
- Product settings differ. Check the current tool's privacy and training controls.
- AI can hallucinate facts, citations, commands, and code explanations.
- A confident answer is not proof.
- Use fake or sanitized data for practice.
- Verify important facts against a real source.

Safe/unsafe examples:

| Example | Safe? | Why |
| --- | --- | --- |
| A public recipe | Usually safe | Public and low-risk |
| A password reset code | Unsafe | Secret credential material |
| A private medical bill | Unsafe | Sensitive personal data |
| A fake customer complaint | Usually safe | Synthetic practice data |
| A public article URL | Usually safe | Public source |
| A customer list | Unsafe | Private business data |

Participant activity:

For each example, ask: "Could I safely email this to a stranger?" If not, do not paste it into a general AI chat.

Teaching point:

"Share less than you think, verify more than you want, and use AI for leverage rather than blind delegation."

### 1:25-1:35 - Break

Instructor job:

- Answer quick setup questions.
- Keep the main demo machine ready.
- Do not let one laptop problem consume the class.

### 1:35-2:05 - Module 5: Setup And Tool Map On A Mac
#### Setup Philosophy

Tell participants:

```text
Setup is not the class. Setup is only useful because it lets us do small controlled experiments.
```

The toolchain:

```text
Finder folder -> Terminal commands -> Local server -> Browser preview -> Git checkpoint -> Codex agent edit -> Review diff
```

#### Terminal Basics In More Detail

Show each command slowly:

```bash
pwd
```

Meaning: print working directory. This answers, "Where am I?"

```bash
ls
```

Meaning: list files. This answers, "What is here?"

```bash
cd Desktop
```

Meaning: change directory. This moves into the Desktop folder.

```bash
mkdir family-ai-class
```

Meaning: make a folder.

```bash
cd family-ai-class
```

Meaning: move into the new folder.

```bash
python3 --version
```

Meaning: check whether Python 3 is installed.

#### Homebrew

Explain:

Homebrew is a Mac package manager. It helps install developer tools that do not come with macOS or are easier to manage outside the App Store.

Official site:

```text
https://brew.sh/
```

Teaching line:

```text
For command-line install commands, prefer official docs. Random blog posts can be outdated or unsafe.
```

Do not require everyone to install Homebrew live unless there is enough time. Show where it fits.

#### GitHub And GitHub Desktop

Explain:

- Git is version history.
- GitHub is online project hosting.
- GitHub Desktop is a visual app for Git.
- A commit is a checkpoint.
- A diff shows what changed.

Live demo:

1. Open GitHub Desktop.
2. Add or select the demo folder.
3. Show the Changes tab.
4. Change a file.
5. Show the diff.
6. Write a commit message.
7. Explain that committing makes a checkpoint.

Beginner analogy:

```text
Git is like a timeline of saved versions. GitHub Desktop is the visual remote control for that timeline.
```

#### Codex

Explain:

Codex is a coding agent. Unlike a normal chat, it can work with a folder, read files, edit files, run commands, and report evidence.

Say:

```text
That power is why we give it scope: which files it may touch, what it should not do, and how it should prove the change worked.
```

#### Setup Troubleshooting

Common issues:

| Issue | What To Do |
| --- | --- |
| Python missing | Watch the demo; install later from official source or Homebrew |
| GitHub login slow | Skip live login; use instructor demo |
| Codex not installed | Watch the agent demo |
| Terminal in wrong folder | Run `pwd`, then `cd` carefully |
| Permission prompt appears | Pause and explain before accepting |

Do not let setup turn into private tech support for one machine.


Goal: Show the basic local development setup.

Teaching points:

- The folder is the workbench.
- Terminal runs commands.
- Python serves local files.
- GitHub Desktop saves checkpoints and shows diffs.
- Codex can work in a project folder as a coding agent.
- Homebrew helps install developer tools on a Mac.

Terminal commands:

```bash
pwd
ls
cd Desktop
mkdir family-ai-class
cd family-ai-class
python3 --version
```

Explain:

| Command | Meaning |
| --- | --- |
| `pwd` | Show where you are |
| `ls` | List files |
| `cd` | Change folder |
| `mkdir` | Make a folder |
| `python3 --version` | Check Python |

Show GitHub Desktop:

- Current folder.
- Changes tab.
- Diff view.
- Commit message.

Show Codex:

- It works in a folder.
- It can read and edit files.
- It can run commands.
- It should receive scope and verification instructions.

Teaching point:

"The folder is the workbench. The server shows the work. Git saves checkpoints. The agent helps make changes."

### 2:05-2:45 - Module 6: Local Web Server Lab
#### Why This Matters

The local web server is the bridge between normal computer use and coding tools. It makes files visible in the browser and gives students a concrete model for how a web app works.

Key idea:

```text
The browser asks the server for files. In this demo, the server is running on your own Mac.
```

#### File Roles

| File | Role | What To Show |
| --- | --- | --- |
| `index.html` | Page structure | Headings, paragraphs, buttons |
| `style.css` | Visual design | Color, spacing, borders, fonts |
| `app.js` | Behavior | Button click, prompt generator |
| `server.py` | Local server | Serves the folder on localhost |
| `prompt_harness.py` | Harness demo | Scores prompt structure |

#### Local Server Explanation

Explain:

- `127.0.0.1` means your own computer.
- `localhost` also means your own computer.
- `8000` is the port.
- Binding to `127.0.0.1` keeps the demo local to your machine.

Command:

```bash
python3 -m http.server 8000 --bind 127.0.0.1
```

Break it down:

| Part | Meaning |
| --- | --- |
| `python3` | Run Python |
| `-m http.server` | Use Python's built-in web server module |
| `8000` | Listen on port 8000 |
| `--bind 127.0.0.1` | Local machine only |

#### Demo Script

1. Show the folder in Finder.
2. Show the same folder in Terminal.
3. Run `ls`.
4. Open `index.html`.
5. Start the server.
6. Open the browser URL.
7. Change one heading in `index.html`.
8. Refresh the browser.
9. Change a color in `style.css`.
10. Refresh the browser.
11. Click the JavaScript button.
12. Open `app.js` and show the prompt list.

#### Participant Activity

Ask participants to make three tiny changes:

1. Change the title text.
2. Change one safety sentence.
3. Change one color or button label.

Then ask:

```text
What changed in the file, and what changed in the browser?
```

This trains the edit/observe loop.

#### Common Problems

| Symptom | Cause | Fix |
| --- | --- | --- |
| Browser shows directory listing | No `index.html` in current folder | `cd` into the right folder |
| Address already in use | Something else uses port 8000 | Use 8001 |
| Page does not change | Browser cached or wrong file edited | Refresh and check folder |
| Terminal seems frozen | Server is running normally | Press Control-C to stop |
| Permission popup appears | macOS security prompt | Stop and explain the permission |

#### Extension If Time Allows

Ask ChatGPT:

```text
Explain this HTML file line by line for a beginner.
```

Then ask:

```text
What is one small change I could make without breaking the page?
```

Teaching point:

AI can explain the code, but the browser proves whether the code works.


Goal: Make local web development concrete.

Teaching points:

- HTML is structure.
- CSS is appearance.
- JavaScript is behavior.
- A server responds to browser requests.
- `127.0.0.1` means your own computer.
- A local server is safe for practice when bound to `127.0.0.1`.

Start the server:

```bash
python3 -m http.server 8000 --bind 127.0.0.1
```

Open:

```text
http://127.0.0.1:8000
```

Demo steps:

1. Open `index.html`.
2. Change one visible line.
3. Refresh the browser.
4. Open `style.css`.
5. Change one color or spacing value.
6. Refresh again.
7. Open `app.js`.
8. Click the page button and connect the behavior to the file.

Participant activity:

- Change the page title.
- Change one paragraph.
- Change one color.
- Refresh and confirm.

Common problems:

| Problem | Fix |
| --- | --- |
| Address already in use | Use port 8001 |
| Directory listing appears | Make sure `index.html` exists |
| Changes do not appear | Refresh or hard refresh |
| Terminal looks stuck | The server is running; press Control-C to stop |

Teaching point:

"This is the smallest useful web development loop: edit, serve, refresh, observe."

### 2:45-3:20 - Module 7: Medium AI - Agent Workflow With Codex
#### Agent Mental Model

Explain:

```text
Chat suggests. An agent acts. That is the difference.
```

A coding agent can:

- Inspect the folder.
- Read files.
- Edit files.
- Run commands.
- Start tests or servers.
- Summarize changes.
- Report verification.

Because it can act, the prompt needs boundaries.

#### Before Using The Agent

Checklist:

- Are we in the right folder?
- Do we know what files may change?
- Is the task small?
- Is there a Git checkpoint or at least a visible diff tool?
- Do we know how to test the result?

#### Agent Prompt Template

```text
Work in this folder.
Goal:
Allowed files:
Do not change:
Do not add:
Before editing:
After editing:
Verification:
```

#### Live Agent Prompt

```text
Inspect this demo folder.
Goal: add one beginner-friendly feature to the page: a button that cycles through three AI use cases.
Scope: index.html, style.css, and app.js only.
Do not add dependencies.
Do not change server.py or prompt_harness.py.
Before editing, summarize the existing files.
After editing, tell me which files changed and how to test the result at http://127.0.0.1:8000.
```

#### Review The Result

After the agent finishes:

1. Read the summary.
2. Open GitHub Desktop.
3. Show changed files.
4. Read the diff.
5. Refresh the browser.
6. Test the feature.
7. Commit if acceptable.

Do not skip the diff. This is the core habit.

#### Good Agent Tasks

- Add one button.
- Change one layout section.
- Explain a small folder.
- Write a small test.
- Fix a specific visible bug.
- Convert repeated text into a table.

#### Bad First Agent Tasks

- "Make this whole app better."
- "Refactor everything."
- "Connect my email."
- "Use my real customer data."
- "Deploy this publicly."
- "Install whatever you need."

#### Participant Activity

Have participants draft a scoped agent task:

```text
Goal: Change the demo page heading.
Allowed files: index.html only.
Do not change: style.css, app.js, server.py.
Verification: Tell me exactly what text changed and where I should refresh the page.
```

Then discuss why this is safer than:

```text
Make the site better.
```

#### Teaching Point

Agent work is not just "better AI." It is a workflow:

```text
Scope -> Change -> Diff -> Test -> Commit
```


Goal: Show how an agent differs from chat.

Teaching points:

- Chat gives answers.
- An agent can inspect files, edit files, run commands, and verify work.
- Agents need scope.
- Review diffs before trusting changes.
- Use Git checkpoints before and after agent work.

Good agent prompt:

```text
Inspect this demo folder.
Goal: add one beginner-friendly feature to the page: a button that cycles through three AI use cases.
Scope: index.html, style.css, and app.js only.
Do not add dependencies.
Do not change the server script.
After editing, tell me which files changed and how to test the result at http://127.0.0.1:8000.
```

Demo steps:

1. Show current page.
2. Show clean or known GitHub Desktop state.
3. Give Codex the scoped prompt.
4. Let Codex inspect and edit.
5. Read Codex's summary.
6. Review changed files in GitHub Desktop.
7. Refresh browser and test.
8. Commit if the change is good.

Participant activity:

Write a scoped agent prompt for one tiny change:

```text
Goal:
Allowed files:
Forbidden changes:
Verification:
```

Teaching point:

"The agent is powerful because it can act. That is also why it needs boundaries, diffs, and verification."

### 3:20-3:30 - Break

Instructor job:

- Reset the room.
- If the agent demo ran long, shorten the harness section.

### 3:30-3:50 - Module 8: Advanced AI - Loop, Harness, Token Usage
#### Why This Is Advanced

The advanced section should not feel like a new unrelated topic. Tie it back to what participants already did:

- In chat, they revised prompts manually.
- In the local server demo, they edited and refreshed.
- In the agent demo, they changed and verified.
- A loop makes that repetition explicit.
- A harness makes it measurable.

#### Loop Examples

Human loop:

```text
Ask -> Read -> Critique -> Revise -> Stop
```

Coding loop:

```text
Edit -> Run -> Fail -> Fix -> Run -> Pass
```

AI workflow loop:

```text
Generate -> Score -> Improve -> Compare -> Stop
```

#### Stop Conditions

Every loop needs one:

| Stop Condition | Example |
| --- | --- |
| Attempt limit | Stop after 3 tries |
| Score threshold | Stop when rubric score is 4/5 |
| Test result | Stop when tests pass |
| Human approval | Stop before sending email |
| Cost limit | Stop after a token or dollar budget |
| Time limit | Stop after 10 minutes |

#### Harness Explanation

A harness is a wrapper around work. It controls inputs, captures outputs, scores results, and records evidence.

Simple harness shape:

```text
Inputs
Prompt or rule
Output
Rubric
Score
Log
Decision
```

#### Prompt Harness Demo

Run:

```bash
python3 prompt_harness.py
```

Explain each prompt:

- Prompt 1 is vague and scores poorly.
- Prompt 2 has role, task, audience, constraints, and output.
- Prompt 3 is an agent prompt with scope and verification.

Teaching line:

```text
The harness does not make the AI smart. It makes the workflow observable.
```

#### Token Usage

Explain simply:

- Tokens are chunks of text.
- Long prompts use more tokens.
- Long outputs use more tokens.
- Repeated loops multiply token use.
- Uploaded files and long chat history can increase context.
- Agents may spend tokens inspecting files and explaining changes.

Practical advice:

- Start with a small task.
- Keep context relevant.
- Ask for concise output.
- Save reusable prompts.
- Stop loops early when the answer is good enough.

#### Advanced But Safe Example

No API key needed:

```text
Take three prompts. Score each for role, task, context, constraints, output format, and verification. Improve the weakest one.
```

This demonstrates evaluation without connecting a paid API.


Goal: Show what makes AI workflows repeatable.

Teaching points:

- A loop repeats work.
- A harness wraps a workflow so it can be tested.
- Rubrics make quality more explicit.
- Logs matter.
- Stop conditions prevent runaway work.
- Token usage grows with long prompts, long outputs, and repeated loops.

Loop:

```text
Generate -> Check -> Improve -> Stop
```

Harness:

```text
Inputs -> AI or rule -> Output -> Rubric -> Score -> Log
```

Run:

```bash
python3 prompt_harness.py
```

Explain:

- The vague prompt scores poorly.
- The structured prompt scores better.
- The agent prompt includes role, task, constraints, and verification.

Stop conditions:

- Stop after 3 attempts.
- Stop when score is high enough.
- Stop when a test passes.
- Stop when human approval is needed.

Teaching point:

"Advanced AI is less about one perfect prompt and more about repeatable process."

### 3:50-4:00 - Module 9: Server, Wrap, Next Steps
#### Server Concept

Tie server back to the earlier local server:

```text
The server we ran earlier served static files. A more advanced server can receive an input, run logic, call tools, and return a result.
```

Explain:

- Local server: only on your machine.
- Private internal server: accessible to a team or network.
- Public server: accessible on the internet.

The risk increases at each level.

#### What A Real AI Server Might Do

1. Receive a request.
2. Check who is allowed to use it.
3. Remove or reject unsafe data.
4. Call an AI model or local rule.
5. Log the input and output safely.
6. Return a result.
7. Apply rate limits and cost controls.

#### Safety Rules For Servers

- Do not put API keys in browser JavaScript.
- Do not expose local experiments publicly.
- Add authentication before real users.
- Log enough to debug but not secrets.
- Rate-limit expensive workflows.
- Keep human approval for high-stakes actions.

#### Wrap Script

Say:

```text
The point of today is not that everyone should build AI servers tomorrow. The point is that these tools form a ladder. You can stop at chat and still get value. If you climb toward agents, loops, harnesses, and servers, the same rules matter more: scope, safety, verification, and the ability to undo.
```

#### Practice Plan

Give participants a one-week plan:

Day 1:

- Use chat for one low-risk rewrite.
- Ask for assumptions and uncertainties.

Day 2:

- Turn a messy note into a checklist and table.

Day 3:

- Ask AI to explain a public article.
- Verify two facts.

Day 4:

- Run the local web server self-test.

Day 5:

- Edit the demo page and refresh.

Day 6:

- Use GitHub Desktop to make a checkpoint.

Day 7:

- Draft one scoped agent prompt, even if you do not run it yet.

#### Final Takeaway

```text
Use AI where you can check it. Add tools only when the job needs them. The more power the AI has, the more important scope and verification become.
```


Goal: Connect the local server idea to real systems and end with a practice plan.

Teaching points:

- A server makes a workflow reachable through a URL.
- Local servers are good for practice.
- Public servers need authentication, logging, limits, and security review.
- Never put API keys in browser JavaScript.

Show:

```bash
python3 server.py
```

Open:

```text
http://127.0.0.1:8765
```

Practice plan:

1. Use chat for one low-risk personal task.
2. Rewrite the prompt with role, task, context, constraints, output format, and verification.
3. Run the local web server demo.
4. Make one small page edit.
5. Save a checkpoint in GitHub Desktop.
6. Try one scoped Codex task.
7. Run the prompt harness.

Final message:

```text
Use AI where you can check it. Add tools only when the job needs them. The more power the AI has, the more important scope and verification become.
```

## 3-Hour Fallback Plan

If time is short, keep the same module order but compress:

| Time | Module | What To Cut |
| --- | --- | --- |
| 0:00-0:10 | Welcome And Safety | Keep |
| 0:10-0:30 | AI General | Shorten tool comparison |
| 0:30-0:55 | Chat And Prompts | Keep one demo and one exercise |
| 0:55-1:10 | Privacy And Verification | Keep |
| 1:10-1:20 | Break | Keep |
| 1:20-1:45 | Setup Map | Show only, no installs |
| 1:45-2:20 | Local Web Server | Keep hands-on |
| 2:20-2:50 | Agent Workflow | Demo only |
| 2:50-3:00 | Harness And Wrap | Explain quickly |

## 90-Minute Fallback Plan

Use this only if the class becomes a talk instead of a workshop:

| Time | Module |
| --- | --- |
| 0:00-0:10 | Welcome, ladder, safety |
| 0:10-0:30 | AI general and use cases |
| 0:30-0:50 | Prompting and personas |
| 0:50-1:05 | Local web server concept |
| 1:05-1:20 | Agent workflow concept |
| 1:20-1:30 | Loop, harness, next steps |

## Handouts

### Prompt Basics

```text
Role:
Task:
Context:
Constraints:
Output format:
Verification:
```

### Agent Prompt Template

```text
Goal:
Folder:
Allowed files:
Do not change:
Before editing:
After editing:
Verification:
```

### AI Safety Checklist

- Did I share private information?
- Did I ask for sources or proof where facts matter?
- Did I separate assumptions from facts?
- Did I review changes before accepting them?
- Did I save a checkpoint?
- Can I undo this?
- Is this local-only or shared with a service?

### Coding Terms

| Term | Meaning |
| --- | --- |
| File | One saved document |
| Folder | A container of files |
| HTML | Page structure |
| CSS | Visual styling |
| JavaScript | Browser behavior |
| Python | General-purpose programming language |
| Terminal | Command-line app |
| Server | Program that responds to requests |
| Port | Number a server listens on |
| Git | Version history |
| GitHub | Online project hosting |
| Commit | Saved checkpoint |
| Agent | AI that can take actions in a tool or project |
| Harness | Repeatable test/evaluation wrapper |

## Good Sources To Read

- OpenAI Codex quickstart: https://developers.openai.com/codex/quickstart
- OpenAI Codex overview: https://developers.openai.com/codex
- ChatGPT help center: https://help.openai.com/
- GitHub Desktop download: https://desktop.github.com/download/
- GitHub Desktop docs: https://docs.github.com/en/desktop
- Homebrew: https://brew.sh/
- Python `http.server` docs: https://docs.python.org/3/library/http.server.html
- GitHub Skills: https://skills.github.com/

Prefer official docs for setup commands. Use blog posts for explanation, not as the source of install commands involving Terminal.

## Follow-Up Class Ideas

| Class | Topic |
| --- | --- |
| Class 2 | Build and publish a personal website |
| Class 3 | AI for notes, rewriting, summaries, and workflows |
| Class 4 | Coding agent basics with Git checkpoints |
| Class 5 | AI evaluation, rubrics, harnesses, and token usage |
| Class 6 | Safe API/server patterns |

## Open Questions For Robert

- Who exactly is attending: kids, adults, mixed, technical friends, nontechnical family?
- Is this one class or a series?
- Should everyone install tools, or is it mostly a live demonstration?
- Do you want to include paid ChatGPT/Codex setup live, or avoid account/payment friction?
- Should the class use only OpenAI tools, or compare Gemini/Claude/Perplexity too?
- Do you want to show real API usage, or keep the first class no-key/no-secret?
- Should the Ryan Klopf AI info be a separate handout?
- Should the two X/Twitter links become examples, reading assignments, or just inspiration?

## Preserved Original Notes

The following text is preserved from Robert's beginning draft and notes:

```text
2026 Family AI Class




1. Tools
   1. Codex
   2. GitHub Desktop (App Store)
   3. Local Web server


2. Accounts
   1. ChatGPT. ChatGPT Plus (we can try with free version, but I am not sure how much Codex usage is allowed for it)
   2. GitHub account
   3. ?


Robert To Do:
Send Ryan Klopf some AI info


https://x.com/hnshah/status/2067293695989465176?s=46


https://x.com/gabrielchua/status/2067263760088330450?s=46


Modules:


AI General


offers out there / tools
* Gemini, ChatGPT...
* Apps (Codex, Co-Work)
* CLI / agents


Use cases
* chat
* apps
* programming


data retention, usage... turn off
safety
what to share (personal info, passwords...)


AI risks, downsides... data centers


Setup ... GitHub, homebrew, web server


AI Persona's
prompts
harness, loop


token usage


Good sources to read
```
