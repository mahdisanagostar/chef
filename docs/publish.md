# GitHub Publish

## Local Repo

CHEF repository root:

`chef/`

## Suggested Flow

```bash
cd chef
git init
git add .
git commit -m "Initial CHEF scaffold"
gh repo create <owner>/chef --public --source . --remote origin --push
```

## Helper

```bash
chef publish-github --project . --owner <owner> --repo chef
```

## Notes

- Repository name stays `chef`.
- Owner can be personal account or organization.
- Release docs should point users to `docs/install.md`.
