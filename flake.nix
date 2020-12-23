{
  description = "Instantiate directories from templates.";

  inputs.nixpkgs.url = github:NixOS/nixpkgs/nixos-20.09;

  outputs = { self, nixpkgs }: {
    instantiate = with import nixpkgs { system = "x86_64-darwin"; };
      python37Packages.buildPythonPackage rec {
        name = "instantiate";
        src = ./.;
        propagatedBuildInputs = with python37Packages; [ jinja2 pyyaml ];
        nativeBuildInputs = with python37Packages;[ black pytest ipython ];
      };
    defaultPackage.x86_64-darwin = self.instantiate;
  };

}
