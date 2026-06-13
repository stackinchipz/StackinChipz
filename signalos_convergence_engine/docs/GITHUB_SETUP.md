# GitHub Setup

## Recommended Repo Name

```text
signalos
```

or

```text
signalos-convergence-engine
```

## Setup

```bash
cd signalos_convergence_engine

git init
git add .
git commit -m "Initial SignalOS options convergence MVP"

git branch -M main
git remote add origin <YOUR_GITHUB_REPO_URL>
git push -u origin main
```

## Branching

Use:

```text
main = stable
dev = active development
feature/* = new features
```

Examples:

```bash
git checkout -b feature/real-data-provider
git checkout -b feature/trade-journal
git checkout -b feature/mobile-dashboard
```

## Project Board Columns

- Backlog
- Ready
- In Progress
- Review
- Done

## Suggested Labels

- data
- scoring
- backtest
- ui
- risk
- journal
- tos
- bug
- enhancement
