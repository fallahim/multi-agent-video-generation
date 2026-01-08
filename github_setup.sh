#!/bin/bash

# GitHub Repository Setup Script for Multi-Agent Video Generation PoC
# This script helps set up the GitHub repository for the project

echo "🚀 شروع تنظیم GitHub Repository..."
echo "================================="

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📝 Initializing Git repository..."
    git init
    git branch -M main
else
    echo "✅ Git repository already initialized"
fi

# Create .gitignore
echo "📄 Creating .gitignore..."
cat > .gitignore << EOF
# Environment variables
.env
.env.local
.env.*.local

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/
.venv/
.env/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Test outputs
test_outputs/
demo_outputs/

# Temporary files
*.tmp
*.temp
EOF

# Add all files
echo "📦 Adding files to Git..."
git add .

# Initial commit
echo "💾 Creating initial commit..."
git commit -m "Initial commit: Multi-Agent Video Generation PoC

- Research on multi-agent orchestration challenges
- Character consistency PoC implementation
- Edge case testing and validation
- Comprehensive documentation

Features:
✅ Character extraction and consistency validation
✅ Scene planning with shared memory
✅ Multi-agent coordination using LangChain
✅ Edge case handling and testing
✅ Persian language support

Time breakdown:
- Research: 4 hours
- Model evaluation: 2 hours
- PoC implementation: 6 hours
- Testing: 2 hours
- Documentation: 2 hours
Total: 16 hours"

# Instructions for GitHub setup
echo ""
echo "📋 GitHub Setup Instructions:"
echo "=============================="
echo ""
echo "1. Create a new repository on GitHub:"
echo "   https://github.com/new"
echo ""
echo "2. Repository name suggestion: multi-agent-video-orchestration-poc"
echo ""
echo "3. Description:"
echo "   PoC for solving character consistency challenges in multi-agent video generation systems using LangChain"
echo ""
echo "4. Make it public repository"
echo ""
echo "5. Do NOT initialize with README (we already have one)"
echo ""
echo "6. After creating repository, run these commands:"
echo ""
echo "   # Add remote origin (replace YOUR_USERNAME with your GitHub username)"
echo "   git remote add origin https://github.com/YOUR_USERNAME/multi-agent-video-orchestration-poc.git"
echo ""
echo "   # Push to GitHub"
echo "   git push -u origin main"
echo ""
echo "7. Alternative using GitHub CLI (if installed):"
echo "   gh repo create multi-agent-video-orchestration-poc --public --source=. --push"
echo ""

# Repository structure
echo "📁 Repository Structure:"
echo "======================="
echo ""
echo "multi-agent-video-orchestration-poc/"
echo "├── character_consistency_poc.py      # Main PoC implementation"
echo "├── test_edge_cases.py                # Edge case testing"
echo "├── requirements.txt                  # Python dependencies"
echo "├── README.md                         # Comprehensive documentation"
echo "├── multi_agent_video_challenges_research.md  # Research findings"
echo "├── video_generation_models_evaluation.md     # Model evaluation"
echo "├── demo_output.json                  # Sample output"
echo "├── edge_case_results.json           # Test results"
echo "├── github_setup.sh                  # This setup script"
echo "└── .gitignore                       # Git ignore rules"
echo ""

echo "🎯 Repository Topics (GitHub):"
echo "=============================="
echo "multi-agent, video-generation, langchain, orchestration,"
echo "character-consistency, ai-agents, machine-learning"
echo ""

echo "✅ Setup script completed!"
echo "📚 Check README.md for detailed usage instructions"
