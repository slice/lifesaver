{ pkgs, python3 ? pkgs.python310 }:

let
  import_expression = python3.pkgs.buildPythonPackage rec {
    pname = "import_expression";
    version = "1.1.4";
    src = python3.pkgs.fetchPypi {
      inherit pname version;
      sha256 = "sha256-BghqarO/pSixxHjmM9at8rOpkOMUQPZAGw8+oSsGWak=";
    };
    doCheck = false;
    pythonImportsCheck = [ "import_expression" ];
    propagatedBuildInputs = [ python3.pkgs.astunparse ];
  };
in python3.pkgs.buildPythonPackage rec {
  pname = "jishaku";
  version = "2.5.1";
  src = python3.pkgs.fetchPypi {
    inherit pname version;
    sha256 = "sha256-cQUxC7TgjT5nyEolx7+0YZ+kXKPb0TSuIZ+W9ftFENs=";
  };
  doCheck = false;
  pythonImportsCheck = [ "jishaku" ];
  propagatedBuildInputs = builtins.attrValues {
    inherit (python3.pkgs)
      braceexpand click importlib-metadata setuptools typing-extensions
      line_profiler discordpy;
    inherit import_expression;
  };
}
