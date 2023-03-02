{
  description = "An opinionated Discord bot framework";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs";
    flake-utils.url = "github:numtide/flake-utils";
    nix-filter.url = "github:numtide/nix-filter";
  };

  outputs = { self, nixpkgs, flake-utils, nix-filter, ... }@attrs:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        packageOverrides = self: super: {
          discordpy = super.discordpy.overridePythonAttrs (old: {
            # Include packages that speed up the library.
            propagatedBuildInputs = old.propagatedBuildInputs
              ++ [ self.brotli self.aiodns self.orjson ];
          });
        };
        py = pkgs.python310.override {
          inherit packageOverrides;

          # This is needed or else we'll get conflict errors.
          self = py;
        };

        jishaku = pkgs.callPackage ./nix/jishaku.nix { python3 = py; };

        filterPath = root:
          nix-filter.lib {
            inherit root;
            exclude = [
              ./flake.nix
              ./flake.lock
              ./result
              ./README.md
              ./LICENSE
              (nix-filter.lib.matchExt "egg-info")
              (nix-filter.lib.matchExt "yml")
              (nix-filter.lib.matchExt "yaml")
            ];
          };

        lifesaver = py.pkgs.buildPythonPackage rec {
          pname = "lifesaver";
          version = "0.0.0";

          src = builtins.path {
            path = filterPath self.outPath;
            name = "lifesaver";
          };

          doCheck = false;
          pythonImportsCheck = [ "lifesaver" ];

          propagatedBuildInputs = builtins.attrValues {
            inherit (py.pkgs)
              typing-extensions ruamel-yaml click discordpy asyncpg uvloop;
            inherit jishaku;
          };
        };

        mkDevShell = { nativeBuildInputs ? [ ], extraPythonPackages ? [ ] }:
          pkgs.mkShell {
            nativeBuildInputs = [
              (builtins.attrValues {
                inherit (py.pkgs) black sphinx sphinxcontrib-asyncio;
              })
              pkgs.nodePackages.pyright
              (py.withPackages (p: [ lifesaver ] ++ extraPythonPackages))
            ] ++ nativeBuildInputs;
          };

        mkDiscordBot = import ./nix/mkDiscordBot.nix {
          inherit lifesaver;
          python = py;
        };
      in {
        lib = {
          # Create an attrset representing a flake for a Lifesaver bot. It is
          # intended to be used with `flake-utils.lib.eachDefaultSystem`.
          mkFlake = generateBotMetadata:
            let
              # The caller receives the Nixpkgs, Python, etc. that we are using,
              # and returns some metadata for the bot needed to generate a
              # corresponding Python package and NixOS module.
              bot = generateBotMetadata {
                python = py;
                inherit jishaku lifesaver pkgs;
                lib = pkgs.lib;
              };

              # Generate a Python package to have as a flake output, and to use
              # in the NixOS module for deployment.
              generatedPackage = py.pkgs.buildPythonPackage ({
                pname = bot.name;
                version = bot.version or "0.0.0";
                src = builtins.path {
                  path = filterPath bot.path;
                  name = bot.name;
                };
                doCheck = false;
                propagatedBuildInputs = [ lifesaver ]
                  ++ (bot.propagatedBuildInputs or [ ]);
              } // (bot.pythonPackageOptions or { }));
            in {
              packages.default = generatedPackage;

              devShells.default = mkDevShell {
                nativeBuildInputs = bot.devShellInputs or [ ];
                extraPythonPackages = (bot.devShellPythonPackages or [ ])
                  ++ (bot.propagatedBuildInputs or [ ]);
              };

              nixosModules.default = (import ./nix/mkDiscordBot.nix) {
                inherit lifesaver;
                python = py.withPackages (pkgs: [ generatedPackage ]);
              } {
                name = bot.name;

                # XXX: This is a bit of a hack, because `mkDiscordBot` can an
                # "ad-hoc" approach to bots - only accepting a directory that
                # contains source code, and leaving dependencies to be handled
                # by overriding the Python interpreter package. This is
                # consistent with how Lifesaver bots used to be deployed in the
                # real world.
                #
                # However, now that we're actually generating a _real_ Python
                # package, we have to figure out how to give that to
                # `mkDiscordBot` and have it work. This is important because the
                # `extensions_path` configuration option goes hand in hand with
                # this "ad hoc" deployment style - it takes a filesystem path,
                # iterates over everything in that directory, and converts it to
                # Python module names to import at startup. It isn't equipped
                # to handle real Python packages.
                #
                # We'll be able to handle this better once we force Lifesaver
                # bots to be Python packages, but I'm not entirely sure if
                # that's a good idea. Ad-hoc can be nice sometimes.
                src = "${generatedPackage}/lib/${py.libPrefix}/site-packages";

                description =
                  bot.description or "Lifesaver flake bot ${bot.name}";

                hardConfig = (bot.hardConfig or { });

                # We always generate a real Python package, so we are never
                # ad-hoc. See the comment in `mkDiscordBot.nix`.
                adhoc = false;
                loadList = bot.loadList or [ ];
              };
            };

          mkDiscordBotModule = mkDiscordBot;
        };

        devShells.default = mkDevShell { };
        packages.default = lifesaver;
      });
}
