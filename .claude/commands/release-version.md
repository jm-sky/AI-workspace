Release a new version
- Run `pnpm lint && pnpm type-check` (if didn't run recently)
- Check latest changes (files staged in git, or latest commit if there are no changed files)
- Bump version in package.json (we're using semantic versioning)
- Add version description to CHANGELOG.md
- Mark feature as done in ROADMAP if applies
- Create a git commit & push
- Create a git tag & push
