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
        py = pkgs.python310.override { inherit packageOverrides; };

        jishaku = pkgs.callPackage ./nix/jishaku.nix { python3 = py; };

        lifesaver = py.pkgs.buildPythonPackage rec {
          pname = "lifesaver";
          version = "0.0.0";

          src = builtins.path {
            path = nix-filter.lib {
              root = self.outPath;
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
      in {
        lib.mkDiscordBotModule = import ./nix/mkDiscordBot.nix {
          inherit lifesaver;
          python = py;
        };

        devShells.default = pkgs.mkShell {
          nativeBuildInputs = [
            (builtins.attrValues {
              inherit (py.pkgs) black sphinx sphinxcontrib-asyncio;
            })
            pkgs.nodePackages.pyright
            (py.withPackages (p: [ lifesaver ]))
          ];
        };

        packages.default = lifesaver;
      });
}
