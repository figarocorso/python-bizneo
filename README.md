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


## Install and Configuring

1. First login (manual browser login required the first time):

```sh
uvx --from git+https://github.com/figarocorso/python-bizneo.git bizneo browser login
```

2. Run the tool:

```sh
uvx --from git+https://github.com/figarocorso/python-bizneo.git bizneo browser expected
```

You can optionally specify the browser with `--browser chromium` or `--browser firefox`.

3. Add to cron:

```sh
crontab -e
```
then, add in the file:

```sh
15 10-13 * * 1-5 uvx --from git+https://github.com/figarocorso/python-bizneo.git bizneo browser expected --headless >> /tmp/bizneo-cron-output.log 2>&1
```

## Nix / NixOS / home-manager

The flake exposes a NixOS module and a home-manager module. Both set up a timer that runs `bizneo browser expected` automatically — a systemd user service + timer on Linux, or a launchd agent on macOS (home-manager only).

The service registers attendance automatically, but **the Bizneo session expires after ~30 days**. After each expiry you need to re-login manually:

```sh
bizneo browser login
```

This opens a real browser window. Once the login completes, the session is saved and the automated service continues working until the next expiry.

### NixOS

Add the flake as an input and import the module:

```nix
# flake.nix
inputs = {
  bizneo.url = "github:figarocorso/python-bizneo";
};
```

```nix
# nixos configuration
{ inputs, ... }:
{
  imports = [ inputs.bizneo.nixosModules.bizneo ];

  services.bizneo = {
    enable  = true;
    browser = "firefox"; # default; also accepts "chromium"
    # headless = true;   # default
    # schedule = "hourly"; # default; uses systemd OnCalendar syntax
  };
}
```

The module automatically registers the package overlay, adds `bizneo` to `environment.systemPackages`, and creates the systemd user service and timer.

### home-manager

```nix
# flake.nix
inputs = {
  bizneo.url = "github:figarocorso/python-bizneo";
};
```

```nix
# home-manager configuration
{ inputs, ... }:
{
  imports = [ inputs.bizneo.homeManagerModules.bizneo ];

  services.bizneo = {
    enable  = true;
    browser = "firefox"; # default; also accepts "chromium"
    # headless = true;     # default
    # schedule = "hourly"; # default; uses systemd OnCalendar syntax
  };
}
```

On Linux this creates a systemd user service + timer. On macOS it creates a launchd agent with logs at `~/Library/Logs/bizneo/`.

## License

This project is licensed under the [GPL-3.0 License](LICENSE).

