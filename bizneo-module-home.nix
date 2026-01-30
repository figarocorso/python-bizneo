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
    getExe
    ;
  cfg = config.services.bizneo;
  isDarwin = pkgs.stdenv.isDarwin;
in
{
  options = {
    services.bizneo = {
      enable = mkEnableOption "Enable bizneo timer service.";

      browser = mkOption {
        type = types.enum [
          "firefox"
          "chromium"
        ];
        default = "firefox";
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

      package = mkOption {
        type = types.package;
        default = flake.packages.${pkgs.system}.bizneo;
        description = "The bizneo package to use.";
      };
    };
  };

  config = mkIf cfg.enable {
    home.packages = [ cfg.package ];

    # Linux: systemd user services
    systemd.user.services.bizneo = mkIf (!isDarwin) {
      Unit.Description = "Execute bizneo browser command";
      Service = {
        Type = "oneshot";
        ExecStart = ''
          ${cfg.package}/bin/bizneo browser expected --browser ${cfg.browser} ${
            if cfg.headless then "--headless" else ""
          }
        '';
      };
    };

    systemd.user.timers.bizneo-timer = mkIf (!isDarwin) {
      Unit.Description = "Execute bizneo browser command every time this has been scheduled.";
      Timer = {
        OnCalendar = cfg.schedule;
        Unit = "bizneo.service";
      };
      Install.WantedBy = [ "default.target" ];
    };

    # macOS: launchd agent
    launchd.agents.bizneo = mkIf isDarwin {
      enable = true;
      config = {
        Label = "com.bizneo.browser";
        ProgramArguments = [
          (getExe cfg.package)
          "browser"
          "expected"
          "--browser"
          cfg.browser
        ] ++ (if cfg.headless then [ "--headless" ] else [ ]);
        StartCalendarInterval = lib.hm.darwin.mkCalendarInterval cfg.schedule;
        StandardOutPath = "${config.home.homeDirectory}/Library/Logs/bizneo/stdout.log";
        StandardErrorPath = "${config.home.homeDirectory}/Library/Logs/bizneo/stderr.log";
      };
    };
  };
}
