Title: Automating Python code quality
Date: 2023-06-23
Lang: en
Category: Software
Tags: programming,python,automation,howto,free-software
Slug: python-code-quality

In this article I explain what I mean by code quality and how it benefits developers.

In the first half I discuss general concepts and workflows that apply to most software projects.
Even if you are not writing Python code you might learn something from it.

In the second half I offer a step-by-step guide to setting up tooling to improve the code quality of Python projects.
I focus on tools I have used and favor after 15 years of professional experience with Python.
I list some available alternatives to each of my proposals.

[TOC]

# Code quality

All coders develop a (subjective) sense of nice or ugly code, and it gets stronger the more experienced we get with a particular technology.

Sometimes it's hard to put into words, but it's usually a combination of:

- Formatting rules.
- Hard errors, e.g. referencing an undeclared variable or dereferencing a null pointer.
- Soft errors or warnings, e.g. having an unused import or variable.
- Language idioms.
- Comments.
- Documentation.

All these have one aspect in common: they are not part of the strict definition of the programming language, so developers are free to do things in different ways.
Whenever there is room to do things differently, people will do it in any way possible, and fight for their reasons to do it their way.

I define *code quality* as the set of metrics that apply directly over the source code artifacts (i.e. the source files).
These metrics are a subset of [non-functional requirements](https://en.wikipedia.org/wiki/Non-functional_requirement).
Different projects will care more or less about each metric, and might ignore some of them.

## Why care about code quality?

Even if end users of the software might not directly notice, higher code quality has clear benefits:

- Reduced count of bugs per line of code (LoC).
- Consistent formatting leads to more [readable code](https://en.wikipedia.org/wiki/Computer_programming#Readability_of_source_code), which improves [maintainability](https://en.wikipedia.org/wiki/Maintainability).
- Better code introspection by having richer type information. Explicit function parameter types, jumping to definitions, browsing documentation...
- Happier developers. This is more important than it sounds, because current developers will be more productive and likelier to stay longer with the project, and it also makes it more attractive to new recruits. "Quality of your projects" ranks #2 in developer happiness, and "quality of development tools" is #4, according to [Zenhub's 2022 report on developer happiness](https://web.archive.org/web/20230429193820/https://www.zenhub.com/reports/software-developer-happiness).

But nothing is free, and the downside is obvious: time and effort have to be invested to keep code quality high.

Fortunately we have a way out: automation.

## Why automate code quality?

Manually keeping code quality high has a constant level of effort.
By automating these processes, most of the effort is paid upfront when setting up the tooling.

These tools have some maintenance cost, like upgrading versions or onboarding new developers, but for big or long-running software projects the benefits should outweigh the costs.

The benefits stack:

- Detect errors earlier in the software life cycle (ideally as the developer is writing the code).
- Less or no time spent formatting code. Even better: less mental overhead as you stop paying attention to formatting and focus more on what the code is doing.
- No time spent discussing with other developers about how *exactly* to format the code. And besides time, also avoid negative feelings that can arise in those discussions.
- Happier developers. Yes, I mentioned this before, but if a high-quality codebase makes programmers happy, an automated one even more so.

## Categories under consideration

These are the specific code quality categories that will automated for Python in the second half of the article.

### Linting

Linting is the detection of errors and warnings of all kind by static code analysis, i.e. parsing code without actually executing it.

Linting hints cover a wide range of issues, from "referenced an undeclared variable" to "unused import" or "potentially insecure string interpolation".
Some linting warnings can quickly get pedantic and unhelpful, but the hard errors are definitely good to know about as early as possible, before your code runs for real.

In a compiled language (e.g. C, C++, Rust, Go...) the compiler catches the errors so the program will not even build until they are fixed.
In an interpreted language such as Python or Javascript many of these errors happen at runtime.
That is where a linter shines by detecting them before the program runs.

### Formatting

Code format is every stylistic aspect that can be changed without making the code fail.
Different developers have different preferences on how to style code, so much so that there are discussions that span decades:

- Tabs or spaces?
- How many spaces per indent level? 2? 4? 8?
- Single quotes (`'`) or double quotes (`"`)?
- Opening brace at the function declaration/flow-control statement or at the following line?
- How to format function definitions? Parameters on same or separate lines? One parameter per line or up to the maximum line width?
- How many blank lines between module declarations?
- How to sort imports?
- Etcetera.

A codebase with consistent formatting makes it faster to read and understand the code, which is why many developers care about formatting.
The problem is that opinions vary, and different developers want to format things in different ways.
These discussions are not just a time sink but also they can mine morale by pitting developers against each other, sometimes splitting them into winners and losers.

When formatting is automated those discussions go away.
At most there would be initial discussion on the exact configuration to use for the formatting tool, but once set it will rarely change, as that would cause a reformatting of the whole codebase.

Another common counter-argument by some developers is that they are too attached to their way of formatting and no tool matches it exactly.
If you think like that I encourage you to give automated formatting a serious try.
For me the pure joy of auto-formatting gets over any personal preferences I might have.
After a while I wondered why I even cared in the first place.

### Type-hinting

This is specific to Python and Javascript/Typescript (as the most popular languages with optional type-hinting, I'm not saying there are no others!).

Both Python and Javascript are _dynamically typed_ languages, which means that the type of a given variable can change at runtime, as opposed to _statically typed_ languages, where all types are set and checked at compilation time and cannot change at runtime.

Python is _strongly typed_, so every variable has a specific type at any point in time during the execution of the program.
On the other hand Javascript is _weakly typed_, as variables can change type depending on the context sometimes (e.g. `'1' + 1` will cause a cast of `1` into a string for a surprising final result of `'11'`). Typescript is _strongly typed_ which is a good reason to prefer it over Javascript.

As with almost everything in programming there are pros and cons to each approach, and discussing them goes beyond the goal of this article.

In the case of Python it wasn't until [PEP 484](https://peps.python.org/pep-0484/) and Python 3.5 that it became possible to annotate the code with the expected type of variables, arguments and function returns.
Many years later now there are tools to not only check the code according to the type hints, but also to do other cool stuff like runtime data validation, like [Pydantic](https://pydantic-docs.helpmanual.io/) does.

Type-hinting would be worth a full blog post about its benefits, but for this article I will focus on type checks, which can detect a variety of bugs that linting alone cannot.

### What about tests?

First of all: _of course you should have tests_!
However they are out of scope for this blog post as they can hardly be fully automated, in the sense of setting them up once and they will cover future code without any additional work.
Also tests are usually application-specific, so they are not directly shareable between projects like the proposed tools in the article are.

### What about code coverage?

Code coverage, i.e. counting how much code is covered by tests and how much isn't, is also a common code quality metric.
I am not including it in this article for two reasons:

1. It wraps the unit test runner, which is outside of the scope of this article.
2. Code coverage arguably contains a perverse incentive for developers: to avoid adding code that would be hard to test.
For example detecting error cases implies extra code and specific test cases, and therefore extra effort to maintain the code coverage, so a developer might think of not handling some errors and let them bubble up the stack trace.

Code coverage can be a good quality metric for some projects and teams.
Pay special attention so it doesn't actually become a detriment to code quality.

If you are interested, the most common way of measuring code coverage in Python is through the [coverage package](https://pypi.org/project/coverage/).

# Python code quality tools

## flake8

[flake8](https://flake8.pycqa.org/en/latest/) is a linter, it will check for a wide variety of issues ranging from errors (e.g. mention to an undeclared variable) to warnings (e.g. unused import) to styling (e.g. long lines or excessive whitespace).

This is a good starting configuration, place it in a *.flake8* file in the project root:

```
[flake8]
max-line-length = 90
extend-ignore = E501, E203, W503
per-file-ignores =
    settings*.py:E402,F403,F405
exclude =
    .git,
    __pycache__,
    .tox,
    .eggs,
    *.egg,
    .venv
```

`max-line-length` should match whatever you configure in *Black* (see next section).
I like 90, but feel free to use less or more.
*Black*'s default is 88.
I wouldn't recommend going over 100, as long lines can be harder to read in diff tools such as Github's split view:

[
![Example of split diff with long lines]({static}/images/automating_python_code_quality/github_split_diff.png "Click to see full size"){: .align-center}
]({static}/images/automating_python_code_quality/github_split_diff.png "Click to see full size")

`per-file-ignores` is useful to ignore some errors or warnings in some files.
In this example I'm ignoring the warning about using `import *` in Django settings files, as that is a common pattern.
Feel free to tailor it to your specific case.

Some alternatives to *flake8*:

- [pylint](https://pylint.pycqa.org/en/latest/): a configurable linter with plugin support.
- [pyflakes](https://github.com/PyCQA/pyflakes): a simpler linter that ignores styling.
Faster as it parses source files instead of importing them.
No per-project configurability.
No plugins.
It can be a good choice for projects using automated formatting tools like *Black* and *isort* and that don't use plugins.

## Black

[Black](https://black.readthedocs.io/en/stable/) is a Python code formatter.
It will take any Python file (as long as it doesn't have syntax errors) and change it to conform to [Black's code style](https://black.readthedocs.io/en/stable/the_black_code_style/current_style.html): split long lines; use double quotes in strings; remove spurious whitespace and empty lines; and a lot more.
In short, Black will make files [PEP 8](https://peps.python.org/pep-0008/) compatible.

Many programmers are very opinionated about style, and don't want a tool to enforce a style they don't like.
However automating code formatting not only saves a ton of time but it also frees us from **not having to discuss styling with other developers**.
If you are like me, once you let go of whatever specific style you prefer you will feel the bliss and never go back.
Saving a Python file in the editor and seeing it autoformat instantaneously still feels magical.

So to use *Black*, just install it with *pip* then add this to *pyproject.toml* file in the project root:

``` toml
[tool.black]
line-length = 90
target-version = ['py310']
extend-exclude = '''
(
  migrations   # Django DB migrations
)
'''
```

Configuration is straightforward and uses good defaults.
You could run *Black* without any configuration at all and it would work great, just be aware that `line-length` defaults to 88.
I like explicit configuration so I recommend adding a configuration file even if minimal.

Notice the use of `extend-exclude` instead of `exclude`.
*Black*'s `exclude` setting has a [sane default](https://github.com/psf/black/blob/main/src/black/const.py#L2) that will exclude most files that you would usually want (`.git` and `.hg`, `build`, `dist`, etc.).
So unless there are files in `exclude` that you *actually want to include* then better stick to `extend-exclude` to append to the default `exclude` values.

When introducing *Black* into an existing codebase you can [use this trick to avoid ruining git blame](https://black.readthedocs.io/en/stable/guides/introducing_black_to_your_project.html#avoiding-ruining-git-blame).

*Black* documentation also includes a guide on [configuring other tools to be compatible with black](https://black.readthedocs.io/en/stable/guides/using_black_with_other_tools.html).

When running *Black* in CI without *pre-commit* use `--check` option so files are not actually reformatted, it will just give a pass/fail result with the faulty files.

Some alternatives to *Black*:

- [yapf](https://github.com/google/yapf): created by Google.
Still considered beta as of the time of this writing, while *Black* released its [first stable version](https://github.com/psf/black/releases/tag/22.1.0) on Jan 29, 2022.
- [autopep8](https://github.com/hhatto/autopep8): uses [pycodestyle](https://github.com/PyCQA/pycodestyle). It can correct deprecated code, so it can be useful for migrating codebases from Python 2 to 3.x.

## isort

[*isort*](https://pycqa.github.io/isort/index.html) will automatically sort all imports in your Python files following a given configuration, or as they say in their home page: *isort your imports, so you don't have to*.

The imports will be split into groups and sorted alphabetically.
The groups are:

1. Python standard library.
2. Third-party dependencies.
3. Current project dependencies.

Configuration goes into the same *pyproject.toml* file that *Black* uses.
This is an starting point:

``` toml
[tool.isort]
profile = "black"
line_length = 90
multi_line_output = 3
skip_gitignore = true
skip_glob = ["**/migrations/*", "**/settings/*"]
src_paths = ["<your_code_dir>"]
```

The key is to use `profile = "black"` to make it compatible with how *Black* expects imports to be sorted.
This gets us the best of both tools: *Black* will format the files and *isort* will sort the imports, without interfering with each other.
*isort* has [many other profiles available](https://pycqa.github.io/isort/docs/configuration/profiles.html).

Of course make `line_length` match the same setting from *Black* and *flake8*.

In `skip_globs` you can put files that shouldn't be automatically processed by *isort*.
In the example I'm excluding Django DB migrations, as they are automatically generated, and setting files, that in some projects have bad-style *import*s, like star imports.

*isort* has a `--check` flag same as *Black*, use it in CI if running without *pre-commit*.

## mypy

Type hints are a relatively new addition to the Python language, starting with [PEP 484](https://peps.python.org/pep-0484/) in Python 3.5.
Since Python has always been a dynamically-typed language, any typing extension is something optional that developers can choose whether to use or not.

[Mypy](https://mypy-lang.org/index.html) is a static type checker for Python.
It will parse the type hints and determine whether the program is correct or whether there are inconsistencies.
For example if a variable can be a `string` or `null` and you try to invoke a string method on it, *mypy* will throw an error.
At that point you can check the code and control for the `null` case appropriately, thus avoiding a potential runtime bug.

Type checking being optional in Python, it actually requires quite a bit of effort from the developer to add the type hints.
It will reduce the number of bugs and make the code easier to read and understand, but it's not clear whether this effort is worth it from a productivity standpoint.
I think it's worth it for long-running projects, especially those starting from scratch.
There are also type-aware libraries like [Pydantic](https://docs.pydantic.dev/latest/) that make type hints useful for other use cases, and combined with type checking can make it worthwhile for more projects.

So on to setting up *mypy*, it has [extensive configuration](https://mypy.readthedocs.io/en/stable/config_file.html).
It supports either a *mypy.ini* file or it can use *pyproject.toml*.
I recommend using *pyproject.toml* as it's becoming the standard file for all Python tooling, I consider other configuration files as deprecated.

This is an example *mypy* configuration in *pyproject.toml*:

```toml
[tool.mypy]
mypy_path = "./src"
follow_imports = "silent"
strict_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
disallow_any_generics = true
check_untyped_defs = true
no_implicit_reexport = true

[mypy-pyproj.*]
# use for dependencies that don't have typing stubs
ignore_missing_imports = True

[tool.pytest.ini_options]
addopts = [
    "--import-mode=importlib",
]
pythonpath = "src"
```

For external dependencies that don't have type hints you should check and install the type stubs, they usually have the [types- prefix](https://pypi.org/search/?q=types-).
They will provide type hints that *mypy* can use.
For packages with no type hints and no stubs available you can use the `ignore_missing_imports` option as in the example above to silence *mypy* errors.

For larger codebases you want to check out the [mypy daemon](https://mypy.readthedocs.io/en/stable/mypy_daemon.html) to speed up checking.

Do check [mypy documentation on adding to an existing codebase](https://mypy.readthedocs.io/en/stable/existing_code.html) if that is your case.

Alternatives to *mypy*:

- [pyright](https://github.com/microsoft/pyright): A Microsoft project.
Combines a type checker with a language server.
*pyright* is open-source but there is also [pylance](https://github.com/microsoft/pylance-release) which is closed-source but leverages *pyright*.
- [pyre](https://pyre-check.org/): a type checker with a focus on performance.
Claims to be "performant on large codebases with millions of lines of Python".
Created by Facebook.

## Other tools to consider

[bandit](https://github.com/PyCQA/bandit) checks for potential security bugs.
It [integrates with pre-commit](https://bandit.readthedocs.io/en/latest/start.html#version-control-integration).
There is a [flake8-bandit plugin](https://github.com/tylerwince/flake8-bandit).

[flake8-bugbear](https://github.com/PyCQA/flake8-bugbear) is a flake8 plugin that adds additional checks for some Python pitfalls, i.e. code that can have unexpected results.

[pydocstyle](https://github.com/pycqa/pydocstyle) automatically formats docstrings.
If you are using flake8 check out the [flake8-docstrings plugin](https://github.com/PyCQA/flake8-docstrings).

# Integrations

The tools I have presented can be invoked in a CLI, but that is not how you want to use them most of the time.
Remember, the goal is automation.

This section is split into 3 parts:

- IDE (Integrated Development Environment), i.e. your code editor.
- CI (Continuous Integration).
- pre-commit hooks.

## IDE

If you are reading this article and are already a programmer, chances are you are already using an IDE of some kind.
Whichever IDE it is, you should learn how to set up all these tools in your IDE.
If your code editor doesn't allow for running all the necessary tools then it might be time to look for another one.
It's a bit out of scope for the article, but talking IDEs is always fun, so I will leave just some thoughts and recommendations for whoever wants to listen.

Before jumping onto specific IDE recommendations, I want to mention the [Language Server Protocol](https://microsoft.github.io/language-server-protocol/), or LSP.
Modern IDEs don't implement features like auto-complete, jump to definition, find references, refactor operations, etc.
They communicate with a language server that offers those operations.
For example for Python there is [python-lsp-server](https://github.com/python-lsp/python-lsp-server/), which has a variety of plugins to integrate with different tools.
This way your editor doesn't need to worry about using *Black* for formatting or *flake8* for linting, just to communicate with a LSP server that supports them.

About IDE recommendations, I personally use [Emacs](https://www.gnu.org/software/emacs/) and don't think I will ever change.
The learning curve is like no other, but for that same reason it can take you higher than any other editor (flamewar!).
To connect to a LSP server you want to use either [lsp-mode](https://emacs-lsp.github.io/lsp-mode/) or [eglot](https://joaotavora.github.io/eglot/) (which is part of Emacs itself as of Emacs 29).
If you are curious about my Emacs configuration it's [published here](https://github.com/haplo/dotemacs).

A lot of people like Vim.
It is a great editor, fast and available in virtually every UNIX-like operating system in the form of the venerable *vi*.
I used it for years until I decided to give Emacs a try after hearing so much about it.
I have heard that [Neovim](https://neovim.io/) is amazing, definitely check it out if you are into Vim.

Nowadays [Visual Studio Code](https://code.visualstudio.com/), or VSCode, is the popular new kid on the block.
And for good reason: the developer experience is great, easy to set up and add plugins to do all kinds of stuff.
I dislike it because it's closed-source software, so I would bet it's a matter of time until Microsoft pulls the rug under its users in some nasty way, like it's happened [time](https://en.wikipedia.org/wiki/BitKeeper) [and](https://en.wikipedia.org/wiki/Flickr#Deletion_of_files_of_non-paying_users) [time](https://www.office.com/) [again](https://web.archive.org/web/20220703064153/https://discussion.evernote.com/forums/topic/97299-two-device-limit-is-a-bad-idea/) with closed-source software.
At least there is [VSCodium](https://github.com/VSCodium/vscodium) which is a free-software version with the proprietary bits removed, like Chromium is to Chrome, but who knows how long it will last.

If you are a young developer, or someone willing to put in the effort, I recommend choosing between Emacs and Vim/Neovim and committing to it for a few months.
You won't regret it, they will last you a lifetime.

## Continuous Integration (CI)

It's important to notice that all these tools and checks on a codebase can be undone by an uncollaborative or uncaring developer.
For this reason it's a good idea (some would say a requirement) to enforce the checks, keeping developers from merging any breaking changes.
Usually this is done by a system that runs the necessary checks on the code before it is merged to the main branch.
That system is called a Continuous Integration system, or CI.

The workflow for getting changes into the project then becomes:

1. Developer commits changes to a branch and creates a Pull Request (PR) in the code hosting service (e.g. Github or Gitlab).
2. Code hosting notifies the CI tool, which starts a new job to check the branch at its current commit.
3. Developer cannot merge until the job finishes successfully (usually there are special permissions for some users to override this and merge anyway).
4. On a successful job, developer can merge the changes. If new changes are added another CI job will be triggered and flow will restart.
5. On errors the developer can look at the job log to figure out what is wrong, fix it and push the new changes. This will trigger a new CI job and restart the flow.

There are dozens of CI platforms out there, but I will list a few that I have worked with:

- [Jenkins](https://jenkins.io/)
- [CircleCI](https://circleci.com/)
- [TravisCI](https://travis-ci.org/)
- [Github Actions](https://github.com/features/actions)
- [Gitlab CI](https://about.gitlab.com/features/continuous-integration/)
- [AWS CodeBuild](https://aws.amazon.com/codebuild/)

## pre-commit

When introducing CI-enforced checks it becomes painful for developers to push some changes and then seeing an error several minutes later.
The feedback loop between errors and their fix should be as short as possible for maximum developer productivity (and happiness!).
For this reason it's a good idea to not just allow the developers to run the checks locally, but to make it easy and fast to do so.

[pre-commit](https://pre-commit.com/) is <quote>a framework for managing and maintaining multi-language pre-commit hooks</quote>.
[git hooks](https://git-scm.com/docs/githooks) are just programs that can be set up in *git* repositories to be executed when *git* triggers certain actions.
As *pre-commit*'s name suggests it commonly runs before a commit is created, but [it can be set up to run before git push](https://pre-commit.com/#pre-commit-during-push) or at some other point if necessary.

Benefits of *pre-commit*:

1. Same checks run by developers and CI, reducing the chances of the developer encountering CI errors later in the development pipeline.
This is the more valuable the slower the CI checks are, as it reduces the feedback loop for developers.
2. Quick and easy to add third-party hooks and keep them updated (`pre-commit autoupdate`).
3. Opt-in for developers.
They can either not use *pre-commit* at all (by just not installing the hooks) or skip the checks for specific commits (by using `git commit -n`).
But then don't complain about CI failing! ;-)

Cons of *pre-commit*:

1. Yet another dependency/tool to manage.
2. *pre-commit* installs hooks in a separate environment, which can be wasteful if you are already installing some tools in the project's virtualenv.

This is an example *pre-commit* configuration that integrates my recommended tools, just put it in *.pre-commit-config.yaml*:

```yaml
repos:
- repo: https://github.com/pre-commit/pre-commit-hooks
  rev: v4.4.0
  hooks:
  - id: check-json
  - id: check-toml
  - id: check-yaml
  - id: check-merge-conflict
  - id: debug-statements
- repo: https://github.com/PyCQA/isort
  rev: 5.12.0
  hooks:
  - id: isort
    args: [--filter-files, src/]
- repo: https://github.com/psf/black
  rev: 23.3.0
  hooks:
  - id: black
    exclude: migrations
    args: [--check,--config=pyproject.toml]
- repo: https://github.com/PyCQA/flake8
  rev: 6.0.0
  hooks:
  - id: flake8
    args: [--config=pyproject.toml]
- repo: local
  hooks:
    - id: mypy
      name: mypy
      entry: "sh mypy_run.sh"
      language: system
      # run if any Python file is changed
      types: [python]
      # mypy will always check all files
      pass_filenames: false
      # use require_serial so that script is only called once per commit
      require_serial: true
```

`pre-commit autoupdate` finds new versions of the pre-commit hooks you use and automatically updates the *.pre-commit-config.yaml* file to use them.

### Mypy and pre-commit

Making *mypy* work in *pre-commit* can be challenging, because *pre-commit* runs on its own environment, so it won't see any of the installed dependencies for the project.
This is the reason why the [official mypy hook for pre-commit](https://github.com/pre-commit/mirrors-mypy) has limited usefulness in my opinion.

My usual hack is to define a shell script that activates the project's virtualenv and invokes *mypy*, and have *pre-commit* run it whenever a Python file changes.
This is a sample *mypy_run.sh* file as referenced in the *.pre-commit-config.yaml* example from above:

```shell
./venv/bin/mypy src/
```

If you know of a better way of running *mypy* with *pre-commit* I would love to hear it, please send me a message.

# Conclusion

I first gave a short generic introduction to code quality and why it's important for software projects.

Then I presented ready-to-use configurations using my tools of choice for Python programming, and instructions on how to automate the necessary checks to maximize developer productivity and happiness.

> **Need a Python expert?**
>
> With over 15 years of experience building large web projects and a proven track record on Silicon Valley start-ups I can help you take your project to the next level.
>
> Read all the details in my [Consultancy]({filename}/pages/consultancy.md) page.
>
> Contact me at <a href="mailto:fidel@openwebconsulting.com">fidel@openwebconsulting.com</a>.
