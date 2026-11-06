@echo off
REM Connects this folder to https://github.com/balum211/DealRoom so you can pull and push.
REM Run once. Afterwards use: git pull   /   git add -A ^&^& git commit -m "msg" ^&^& git push
cd /d "%~dp0"
if exist .git (
  echo Already a git repository.
  git remote -v
  goto :eof
)
git init -b main
git remote add origin https://github.com/balum211/DealRoom.git
git fetch origin main
git reset --mixed origin/main
git branch --set-upstream-to=origin/main main
git status
echo Linked to GitHub. Local files match the repo.
