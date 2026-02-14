{
  description = "rbwm - Bitwarden menu for dmenu/bemenu/rofi";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      systems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
      forAllSystems = nixpkgs.lib.genAttrs systems;
    in
    {
      packages = forAllSystems (system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
        in
        {
          default = pkgs.python3Packages.buildPythonApplication {
            pname = "rbwm";
            version = "0.1.0";
            
            src = ./.;
            
            format = "other";
            
            installPhase = ''
              mkdir -p $out/bin
              mkdir -p $out/lib/rbwm
              
              # Copy Python package
              cp -r rbwm $out/lib/
              
              # Create wrapper script
              cat > $out/bin/rbwm << 'EOF'
              #!/usr/bin/env bash
              exec ${pkgs.python3}/bin/python3 -m rbwm "$@"
              EOF
              
              chmod +x $out/bin/rbwm
            '';
            
            # Runtime dependencies
            propagatedBuildInputs = with pkgs; [
              rbw  # Bitwarden CLI
              # Menu programs (at least one required)
              dmenu  # or bemenu, rofi, etc.
              # Clipboard/input tools
              xclip
              xdotool
            ];
            
            meta = with pkgs.lib; {
              description = "Bitwarden menu for dmenu/bemenu/rofi";
              homepage = "https://github.com/kanielrkirby/rbwm";
              license = licenses.mit;
              platforms = platforms.linux;
            };
          };
        });
      
      # Development shell
      devShells = forAllSystems (system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
        in
        {
          default = pkgs.mkShell {
            buildInputs = with pkgs; [
              python3
              rbw
              dmenu
              xclip
              xdotool
            ];
          };
        });
    };
}
