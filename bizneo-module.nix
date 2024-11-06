# modules/bizneo.nix
flake:
{
  lib,
  pkgs,
  config,
  ...
}:
let
  inherit (lib)
    mkOption
    mkIf
    types
    mkEnableOption
    mkPackageOption
    ;
  cfg = config.services.bizneo;
in
{
  options = {
    services.bizneo = {
      enable = mkEnableOption "Enable bizneo timer service.";

      browser = mkOption {
        type = types.enum [
          "chromium"
          "firefox"
        ];
        default = "chromium";
        description = "Browser to be used for the bizneo command.";
      };

      headless = mkOption {
        type = types.bool;
        default = true;
        description = "Run the browser in headless mode.";
      };

      schedule = mkOption {
        type = types.str;
        default = "Mon..Fri 08..18:00:00"; # Each hour from 8 to 18 on weekdays.
        description = "Schedule of when to launch the bizneo command.";
      };

      package = mkPackageOption pkgs "bizneo" { };
    };
  };

  config = mkIf cfg.enable {
    nixpkgs.overlays = [ (final: prev: { bizneo = flake.packages.${prev.system}.bizneo; }) ];

    environment.systemPackages = [ cfg.package ];

    systemd.user.services."bizneo@" = {
      description = "Execute bizneo browser command";
      serviceConfig = {
        Type = "oneshot";
        ExecStart = ''
          ${cfg.package}/bin/bizneo browser expected --browser ${cfg.browser} ${
            if cfg.headless then "--headless" else ""
          }
        '';
      };
    };

    # To enable with `systemctl enable --now --user bizneo-timer@<USERNAME>.timer`
    systemd.user.timers."bizneo-timer@" = {
      description = "Execute bizneo browser command every time this has been scheduled.";
      wantedBy = [ "timers.target" ];
      timerConfig = {
        OnCalendar = cfg.schedule;
        Unit = "bizneo@%i.service";
      };
    };
  };
}
