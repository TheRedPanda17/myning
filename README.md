# Welcome to Myning

## Prerequisits

Install Brew:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Add Brew to your path.

```bash
echo 'eval $(/opt/homebrew/bin/brew shellenv)' >> ~/.zshrc
```

Use Brew to install pyenv and virtualenv:

```bash
brew install pyenv pyenv-virtualenv
```

Add pyenv and virtualenv to your `~/.zshrc`

```bash
echo 'eval $(pyenv init -)' >> ~/.zshrc
eval 'eval $(pyenv virtualenv-init -)' >> ~/.zshrc
```

## Play the Game

Set up the environment

```bash
make venv
```

Play the game

```bash
make play
```

## Contributing

Feel free to. I think you can probably figure out how
