# python-bizneo

This is a Command Line Interface (CLI) tool designed as an integration with the Bizneo API. It allows administrators to manage employee absences within an organization efficiently. Currently, the primary feature of this tool is to add absences for one or more users, specifying details such as the type of absence, start and end dates, and additional comments.
Key Features

* **Add Absences**: Easily add absences for individual users or all users at once.
* **Specify Absence Details**: Include the type of absence, start and end dates, and optional comments for more context.
* **Automated Absence Assignment**: Automatically assign specified absences to all users if no specific user is indicated.

## Usage

The CLI provides a straightforward way to manage absences. The primary command structure includes an absences group with an add command to add new absences.

For detailed command usage, simply run the CLI with the --help flag to see all available options and their descriptions.

## Getting Started

Ensure you have Python 3 installed and the required dependencies. Execute the CLI commands in your terminal or command prompt to start managing absences efficiently.

## Hacking

The project dependencies are specified in a `pyproject.toml` file, which adheres to several Python PEPs, making it easy to manage and maintain the project. The most commonly used tool to handle this kind of projects is [Poetry](https://python-poetry.org/), which simplifies dependency management and setup.

To get started with development:

1. Install the project dependencies:

```sh
poetry install
```

2. Activate the Poetry shell:

```sh
poetry shell
```

Run the CLI tool within the Poetry environment:

```sh
python <your_script_name>.py
```

## Explanation of Key Files

#### bizneo.py

This file is still under active development. It handles the core functionality of the CLI tool, specifically integrating with the Bizneo API to manage absences. To use this script, you need to add your Bizneo API token by looking for the `TOKEN` within the file and inserting your token value there.

#### bizneo_browser.py

This file is a temporary solution for supporting Google login to Bizneo. It uses a Firefox browser profile to maintain a logged-in session with Bizneo. You need to set the `PROFILE_PATH` to one of your existing Firefox profiles. Initially, you must log in to Bizneo manually. You might want to use `time.sleep(100000)` or insert a `breakpoint()` to pause the script and complete the manual login before proceeding. Note that this script is not yet headless, meaning it will open a visible browser window during execution.

## License

This project is licensed under the [GPL-3.0 License](LICENSE).

