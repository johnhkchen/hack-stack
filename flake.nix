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
            # Python ecosystem (backend)
            python311  # Match backend requirements (>=3.11)
            uv
            
            # Node.js ecosystem (frontend)
            nodejs_22
            npm  # Frontend uses npm, not pnpm
            
            # Development tools
            just        # For justfile commands
            curl
            jq
            git
            
            # Docker for containerized deployment
            docker
            docker-buildx  # Modern docker compose plugin
          ];

          shellHook = ''
            echo "🚀 Hack Stack Development Environment"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo "📦 Available tools:"
            echo "  • python: $(python --version)"
            echo "  • uv: $(uv --version)"
            echo "  • node: $(node --version)"
            echo "  • npm: $(npm --version)"
            echo "  • just: $(just --version)"
            echo "  • docker: $(docker --version)"
            echo ""
            echo "🏃 Quick commands:"
            echo "  • just demo           # Build and start all services"
            echo "  • just start          # Start services (Docker)"
            echo "  • just logs           # View service logs"
            echo "  • just clean          # Clean up containers"
            echo ""
            echo "🛠️  Development workflow:"
            echo "  • cd backend && uv run fastapi dev api/routes.py"
            echo "  • cd frontend && npm run dev"
            echo ""
            echo "🌐 URLs (when running):"
            echo "  • App: http://localhost:2872"
            echo "  • Backend API: http://localhost:8000"
            echo "  • Frontend: http://localhost:4321"
            echo "  • API docs: http://localhost:8000/docs"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
          '';
        };
      });
}