# Welcome to Myning

Myning is an idle game designed to be played in your terminal.
Mine for ore, battle enemies, manage your garden, upgrade your gear, and so much more!

![image of myning gameplay](https://github.com/TheRedPanda17/myning/blob/main/images/myning.png?raw=true)

## Prerequisites

### MacOS Setup

Install Homebrew:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Reload your environment (or just restart your terminal):

```bash
exec zsh
```

Add `brew` to your path:

```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
```

Install pyenv and virtualenv:

```bash
brew install pyenv pyenv-virtualenv
```

Initialize pyenv in your shell:

```bash
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.zshrc
```

Reload your environment (or just restart your terminal):

```bash
exec zsh
```

## Play the Game

Set up the environment:

```bash
make venv
```

Play the game:

```bash
make play
```

## Contributing

### Textual User Interface (TUI)

When developing a full-screen terminal application, the python debugger will not work. Instead, use
the textual debug console by running `textual console -x SYSTEM -x EVENT -x DEBUG -x INFO` in a
separate terminal and use `make dev` to run the app. You can then use `print` statements in the
code, and they will be displayed in the console window.

- [Textual documentation](https://textual.textualize.io) (TUI framework)
- [Textual devtools documentation](https://textual.textualize.io/guide/devtools/#console)
- [Rich documentation](https://rich.readthedocs.io/en/stable/) (library for styling and displaying rich text)

### Formatting and organizing imports

Format the code:

```bash
black .
```

Organize imports:

```bash
isort .
```

### Tests

Run tests:

```bash
make test
```

It may be helpful to visually debug TUI tests by running pytests with the `--headed` option:

```bash
pytest --headed
```

View test coverage:

```bash
open htmlcov/index.html
```
