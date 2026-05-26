Title: Vibe Coding Escapades: pelican-copy-code plugin
Date: 2026-05-26
Lang: en
Category: Software
Tags: ai,blog,pelican,programming,python
Slug: vibe-coding-escapades-pelican-copy-code
Series: Vibe Coding Escapades

## The Problem

I realized that this blog uses a lot of code blocks, but it’s not easy to copy them because there’s no *Copy* button on each block.

I looked for a plugin for [Pelican](https://getpelican.com/) that would do this, convinced that there must be one already out there, but I was surprised to find nothing!

It seemed like an ideal project to solve quickly with AI.
I could fix my issue and create a useful project for the community.

## Execution

My goal was to create a new project publishable to PyPI, with these requirements:

- Compatible with stable Pelican.
- Installable with `pip` and featuring auto-discovery. In other words, it must be a next-generation Pelican plugin; it doesn’t need to be added to the Pelican configuration (`pelicanconf.py`), it installs with `pip` and runs right away.
- Static JavaScript and CSS files, without `npm` or similar.
- No external JavaScript or CSS dependencies, only standard APIs.
- Should not require changes to the templates. Once activated, the plugin automatically inserts the button into all blocks.
- No DOM manipulation; the button is inserted when the Pelican site is generated.
- Configurable.

I used OpenCode (in a sandbox, [I describe it in this other article]({filename}/software/2026-05-14_how_i_sandbox_ai_agents_es.md)), initially with Kimi 2.6, then with Deepseek V4 Pro, and later with Claude Opus 4.7.
I’ll discuss the details in the *Lessons* section.

Development took place in fits and starts over the course of an afternoon.
While I was doing other things, I’d go to the computer, ask it to prepare the next change in planning mode, then come back, quickly review it, and give the go-ahead to implement it.

I tested the changes locally on this blog.
I simply installed the plugin with `uv` in editable mode: `uv add --editable ~/Code/pelican-copy-code`

It’s a tiny project, so I didn’t bother generating or maintaining tests, *linting*, or GitHub actions.

## Results

The plugin is `pelican-copy-code`, published on [Github](https://github.com/haplo/pelican-copy-code) and [PyPI](https://pypi.org/project/pelican-copy-code/).

It can be installed directly as intended; it’s just a `pip install pelican-copy-code` away.

Instead of a screenshot, here’s a code block so you can try it out live, just hover over it and click “Copy”:

```python
def swallow_airspeed(laden=False):
   return 24 if not laden else RuntimeError("African or European?")

class BlackKnight:
   def __init__(self):
       self.flesh_wounds = ["'Tis but a scratch!"]
   def is_defeated(self):
       return len(self.flesh_wounds) >= 4

print(swallow_airspeed(laden="coconut"))
```

## Lessons

At first, I used Kimi 2.6 because it’s my default model on [Venice.ai](https://venice.ai/).
It’s cheap, fast, and private (Venice.ai doesn’t keep logs of conversations in its own models).

I tried switching to Deepseek V4 Pro because it was new and they said it was better for programming, comparable to Claude Opus 4.5.
I didn’t notice much of a difference; for such a small project, either one would probably have worked well.

It is true that Kimi 2.6 made some mistakes in its initial implementation; for example, some of the configuration settings I asked it to include had no effect, that is, the code never used them.
It was easy to fix in separate sessions, but it opened my eyes to how important the testing phase is.

I also ended up doing some manual refactoring that I probably could have avoided if I had been more specific in the instructions in `AGENTS.md`.
For example, keeping configuration variables in alphabetical order should have been a style requirement in `AGENTS.md`.
The agent also placed some configuration variables outside [the dictionary](https://github.com/haplo/pelican-copy-code/blob/f0a625b85caa3ff134ab85bfdf006abad4bd505c/pelican/plugins/copy_code/settings.py#L2).
A style error that a human probably wouldn’t have made.


When it came time to test the plugin for the first time on a real site, it turned out that it wasn't working; it threw an error at build time due to incorrect use of [signals and generators](https://github.com/haplo/pelican-copy-code/blob/f0a625b85caa3ff134ab85bfdf006abad4bd505c/pelican/plugins/copy_code/__init__.py#L8).
I asked Deepseek V4 Pro to fix it but it couldn’t figure it out with a couple attempts.
That’s when I switched to Claude Opus 4.7, which found the problem on the first try and fixed it correctly.
I then remembered the advice I’d read here and there about using a smart model as a planner and another cheaper model to implement the changes.
You can tell Opus is the most advanced model, but it’s also much more expensive than Kimi or Deepseek.

When I implemented [translation support](https://github.com/haplo/pelican-copy-code/commit/b76cff671550231135ced60dbd598993a160ebcf), I did it with Deepseek V4 Pro, and it worked well.
However, it duplicated code (the strings “Copy” and “Copied!” were duplicated across two different files).
I asked it to refactor to remove the duplication, but the proposal wasn’t good at all, it eliminated the duplication but added more poorly styled code.
Once again, I switched to Opus 4.7, which proposed a much better solution that actually simplified the code.
