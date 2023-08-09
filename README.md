# Welcome to Myning

Myning is an idle game designed to be played in your terminal.
Mine for ore, battle enemies, manage your garden, upgrade your gear, and so much more!

![image of myning gameplay](https://github.com/TheRedPanda17/myning/blob/main/images/myning.png?raw=true)

## Prerequisites

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

Feel free to. I think you can probably figure out how
