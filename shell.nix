with import <nixpkgs> {};
with python37Packages;

buildPythonPackage rec {
  name = "instantiate";
  src = ./.;
  propagatedBuildInputs = [ jinja2 pyyaml ];
  nativeBuildInputs = [ black pytest ipython ];
}
