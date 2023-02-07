{ lifesaver, python }:

{ name, src, description ? "Lifesaver bot ${name}", ... }:

{ config, lib, pkgs, ... }:

let
  cfg = config.lifesaver.${name};
  yaml = pkgs.formats.yaml { };
in {
  options.lifesaver.${name} = with lib; {
    enable = mkEnableOption ''Enables Lifesaver-powered Discord bot "${name}"'';

    token = mkOption {
      type = types.str;
      description = "The token of the bot. Used to authenticate with Discord.";
    };

    python = mkOption {
      type = types.package;
      default = python;
      description = "The Python package to use for the bot.";
    };

    dataDir = mkOption {
      type = types.path;
      default = "/var/lib/lifesaver-${name}";
      description = "The data directory that the bot runs in.";
    };

    loadDefaultCogs = mkOption {
      type = types.bool;
      default = true;
      description = "Whether to pass `--no-default-cogs` to the Lifesaver CLI.";
    };

    user = mkOption {
      type = types.str;
      default = "lifesaver";
      description = "The user account to run the bot under.";
    };

    group = mkOption {
      type = types.str;
      default = "lifesaver";
      description = "The group to run the bot under.";
    };

    settings = mkOption {
      type = types.submodule {
        freeformType = yaml.type;

        options = let opt = type: default: mkOption { inherit type default; };
        in {
          bot_class = opt (types.nullOr types.str) null;
          config_class = opt (types.nullOr types.str) null;
          extensions_path = opt types.str "./exts";
          cog_config_path = opt types.str "./config";
          ignore_bots = opt types.bool true;
          command_prefix =
            opt (types.either (types.listOf types.str) types.str) "!";
          intents =
            opt (types.either (types.listOf types.str) types.str) "default";
          description = opt types.str description;
          dm_help = opt (types.nullOr types.bool) null;
          command_prefix_include_mentions = opt (types.nullOr types.bool) null;
          hot_reload = opt types.bool false;
          emojis = opt (types.attrsOf types.anything) { };
          postgres = opt (types.nullOr (types.attrsOf types.anything)) null;
        };
      };

      description =
        "Extra configuration options to be serialized into the YAML file.";
      default = { };
      example = literalExpression ''{ command_prefix = ["?"]; }'';
    };

    cogConfig = mkOption {
      type = types.attrsOf yaml.type;
      description =
        "Configuration options for cogs that use `@lifesaver.Cog.with_config`.";
      default = { };
    };
  };

  config = lib.mkIf cfg.enable {
    users.users = lib.mkIf (cfg.user == "lifesaver") {
      lifesaver = {
        group = cfg.group;
        isSystemUser = true;
      };
    };
    users.groups = lib.mkIf (cfg.group == "lifesaver") { lifesaver = { }; };

    systemd.tmpfiles.rules =
      [ "d ${cfg.dataDir} 0750 ${cfg.user} ${cfg.group} -" ];

    systemd.services."lifesaver-${name}" = let
      python = cfg.python.withPackages
        (pythonPackages: [ lifesaver pythonPackages.discordpy ]);
      botYamlConfig = yaml.generate "lifesaver-${name}-config.yml" ({
        token = cfg.token;
        logging.file = "${cfg.dataDir}/bot.log";
      } // cfg.settings);
    in {
      wantedBy = [ "multi-user.target" ];
      script = ''
        echo "Starting Lifesaver Discord bot with source at: ${src}"
        cd ${src}
        ${python}/bin/python -mlifesaver.cli --config=${botYamlConfig}
      '';
      environment.NIX = "1";
      inherit description;
      serviceConfig = {
        Type = "simple";
        Restart = "on-failure";
        User = cfg.user;
        Group = cfg.group;
        WorkingDirectory = cfg.dataDir;
      };
    };
  };
}