# Git Cheat Sheet (Student Repo)

Setup
- git config --global user.name "Your Name"
- git config --global user.email "you@example.com"

Basics
- git status
- git add <files>
- git commit -m "message"
- git log --oneline --graph --decorate --all

Branching
- git branch
- git checkout -b group0X/feature-name
- git switch group0X/feature-name

Remote
- git push -u origin group0X/feature-name
- git pull --rebase

Conflicts
- Resolve markers <<<<<<< ======= >>>>>>>
- git add <resolved files>
- git rebase --continue (or commit if merging)
