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

      in {
        lib = {
          # Create an attrset representing a flake for a Lifesaver bot. It is
          # intended to be used with `flake-utils.lib.eachDefaultSystem`.
          mkFlake = gen:
            let
              bot = gen {
                python = py;
                inherit jishaku lifesaver pkgs;
                lib = pkgs.lib;
              };

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
            };

          mkDiscordBotModule = import ./nix/mkDiscordBot.nix {
            inherit lifesaver;
            python = py;
          };
        };

        devShells.default = mkDevShell { };
        packages.default = lifesaver;
      });
}
