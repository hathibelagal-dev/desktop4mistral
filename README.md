# desktop4mistral

A powerful desktop client for interacting with Mistral Large Language Models (LLMs)

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

## Overview

desktop4mistral is a Python-based desktop application that provides a user-friendly interface for chatting with Mistral AI models. Built with PySide6, it offers a modern GUI with features like model selection, chat history, and command support.

## Features

- Interactive chat interface with Mistral LLMs
- Support for multiple Mistral models with easy switching
- Custom FiraCode font for better code readability
- Markdown support for formatted responses
- Command system (e.g., `/read` to fetch and display file contents)
- Threaded responses to maintain UI responsiveness
- Keyboard shortcuts (Ctrl+Enter to send messages)
- Dark theme with color-coded messages (User, System, Assistant)

## Screenshots

<img src="https://raw.githubusercontent.com/hathibelagal-dev/desktop4mistral/refs/heads/main/sshots/0.png" style="width:800px;"/>

<img src="https://raw.githubusercontent.com/hathibelagal-dev/desktop4mistral/refs/heads/main/sshots/1.png" style="width:800px;"/>

## Installation

### Prerequisites

- Python 3.11 or 3.12
- Mistral API key (get it from [Mistral AI](https://mistral.ai/))

## Quickstart

Install using `pip`.
```bash
pip install desktop4mistral
```

And run...
```bash
export MISTRAL_API_KEY='your-api-key-here'
desktop4mistral
```

or

```bash
python3 -m desktop4mistral.main
```

### Setup for development

1. Clone the repository:
```bash
git clone https://github.com/hathibelagal-dev/desktop4mistral.git
cd desktop4mistral
```

2. Install the app and its dependencies:
```bash
pip3 install .
```

## Usage

- Launch the application
- Select a Mistral model from the "Models" menu
- Type your message in the input field
- Press Ctrl+Enter or click "Send" to submit
- View responses in the chat window

## Commands

Desktop4Mistral supports several commands.

- `/read` to read a local or remote file
- `/git` to read a github repository
- `/wiki_search` to search Wikipedia
- `/wiki_id` to look up the contents of a Wikipedia page
- `/save` to save the entire chat session as a JSON file
- `/talk` to turn talking `on` or `off`. Uses Kokoro as the TTS model. You can expect reasonable performance on most hardware.

## Support
For issues and feature requests, please use the GitHub [Issues](https://github.com/hathibelagal-dev/desktop4mistral/issues) page.

## License

This project is licensed under the GNU General Public License v3 (GPLv3) - see the LICENSE file for details.

