{
  description = "Instantiate directories from templates.";

  inputs.nixpkgs.url = github:NixOS/nixpkgs/nixos-20.09;

  outputs = { self, nixpkgs }: 
    let
      supportedSystems = [ "x86_64-linux" "x86_64-darwin" ];
      forAllSystems = f: nixpkgs.lib.genAttrs supportedSystems (system: f system);
    in
      {
        instantiate = forAllSystems (system:
          with import nixpkgs { system = "${system}"; };
            python37Packages.buildPythonPackage rec {
              name = "instantiate";
              src = ./.;
              propagatedBuildInputs = with python37Packages; [ jinja2 pyyaml ];
              nativeBuildInputs = with python37Packages;[ black pytest ipython ];
            }
          );

        defaultPackage = forAllSystems (system:
            self.instantiate.${system}
          );
      };

}
