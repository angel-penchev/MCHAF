# Moodle Choice Auto-filler (MCHAF)
Moodle Choice Auto-filler (MCHAF) is a tool for automatic Moodle single-choice survey filling. It can be used to automatically fill/notify you about newly created course forms, such as test signups.

### Table of contents

1. [Setup](#-setup)
    1. [Linux and macOS shells](#linux-and-macos-shells)
    2. [Windows PowerShell](#windows-powershell)
    3. [Run from source](#run-from-source)
2. [Configuration](#-configuration)
    1. [Command-line arguments](#command-line-arguments)
    2. [Environment variables](#environment-variables)
    3. [Environment file](#environment-file)
3. [Contributions](#-contributions)
4. [License](#-license)

---

## 👨‍💻 Setup

### Linux and macOS shells
Go to the [MCHAF release page](https://github.com/angel-penchev/mchaf/releases) and download the latest executable for Unix.

### Windows PowerShell
Visit the [MCHAF release page](https://github.com/angel-penchev/mchaf/releases) and download the latest executable for Windows.

### Run from source
Before running the code directly from source, please ensure that you have `Python 3`, `pipenv` and `git` installed. Afterwards, run the following commands:

```
git clone https://github.com/angel-penchev/mchaf
cd mchaf
pipenv install
python.py main.py
```

## ⚙ Configuration
### Command-line arguments
| Argument | Meaning |
|---------:|---------|
| `-u`, `--username`           | moodle authentication username      |
| `-p`, `--password`           | moodle authentication password      |
| `-d`, `--domain`             | moodle server domain                |
| `-c`, `--course`             | moodle course id                    |
| `-r`, `--regex`              | choice form title regex filter      |
| `-n`, `--notification-level` | notification level. 0 = no notifications, 1 = unfilled multiple choice forms notification, 2 = successfully filled and unfilled forms notifications, 3 = closed, filled and unfilled forms notifications |
| `-o`, `--run-once`           | whether to check only once and exit |
| `-h`, `--help`               | show this help message and exit     |

### Environment variables
On Unix based systems, the variable can be exported in `.bashrc`, `.zshrc`, etc. usually located in the home directory.

```
... other shell configuration ...

export MCHAF_USERNAME=*username*
export MCHAF_PASSWORD=*password*
export MCHAF_MOODLE_DOMAIN=https://learn.fmi.uni-sofia.bg/
export MCHAF_COURSE_ID=7473
export MCHAF_CHOICE_TITLE_REGEX=(З|з)аписване за*
```

On Windows this can be done by selecting `Settings > System > Advanced > Environment Variables... > New`.

### Environment file
MCHAF can be also configured using a .env file. Such file can contain the same values as the ones exported in shell.

```
export MCHAF_USERNAME=*username*
export MCHAF_PASSWORD=*password*
MCHAF_MOODLE_DOMAIN=https://learn.fmi.uni-sofia.bg/
MCHAF_COURSE_ID=7473
MCHAF_CHOICE_TITLE_REGEX=(З|з)аписване за*
```

## 💖 Contributions
1. Fork it (<https://github.com/angel-penchev/mchaf/fork>)
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -a`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request
6. Upon review, it will be merged.

## ⚖️ License
Distributed under the BSD-3 Cause license. See [LICENSE](LICENSE) for more information.