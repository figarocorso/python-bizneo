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

The project dependencies are specified in a `pyproject.toml` file, which adheres to several Python PEPs, making it easy to manage and maintain the project. The tool we are using in this project is [uv](https://docs.astral.sh/uv/), which simplifies dependency management and setup.

To get started with development:

1. Activate the venv shell:

```sh
uv venv
```

2. Run the CLI tool within the environment:

```sh
uv run bizneo
```

3. Build and package the tool:

```sh
uv build
```

This will generate a dist/ folder with the sdist and the wheel.

## License

This project is licensed under the [GPL-3.0 License](LICENSE).

