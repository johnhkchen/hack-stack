{
  description = "Hackathon-optimized demo stack with FastAPI + Astro + Svelte";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            # Python ecosystem
            python313
            uv
            
            # Node.js ecosystem for Astro
            nodejs_22
            pnpm
            
            # Development tools
            curl
            jq
            
            # Optional: Docker for deployment
            docker
            docker-compose
          ];

          shellHook = ''
            echo "🚀 Hack Stack Development Environment"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo "📦 Available tools:"
            echo "  • python: $(python --version)"
            echo "  • uv: $(uv --version)"
            echo "  • node: $(node --version)"
            echo "  • pnpm: $(pnpm --version)"
            echo ""
            echo "🏃 Quick commands:"
            echo "  • uv run python main.py     # Start backend"
            echo "  • cd frontend && pnpm dev   # Start frontend"
            echo "  • uv run --with fastapi fastapi dev main.py  # Dev mode"
            echo ""
            echo "🌐 URLs:"
            echo "  • Backend: http://localhost:8000"
            echo "  • Frontend: http://localhost:4321"
            echo "  • API docs: http://localhost:8000/docs"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
          '';
        };
      });
}