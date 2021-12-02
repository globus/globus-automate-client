# Development workflows

This document prescribes how to branch and merge code in this project.

When provided, shell commands are designed to minimize human interaction.
In most cases the commands can be copied and pasted.

Some commands may not be available until the virtual environment is created and activated.

## Table of contents

* [Priority git branches](#priority-git-branches)
* [Everyday development](#everyday-development)
* [Preparing a feature release](#preparing-a-feature-release)
* [Preparing a hotfix release](#preparing-a-hotfix-release)
* [Merging release branches](#merging-release-branches)
* [Deploying to production](#deploying-to-production)

## Priority git branches

There are several git branches that have assigned significance.

### `main`

`main` tracks all repository changes. Every branch must eventually merge to 
`main`.

### `production`

`production` tracks code that is, or is about to be, deployed to PyPI or
ReadTheDocs. Each merge commit must be accompanied by a git tag representing
the released version.

## Everyday development

"Everyday" development refers to repository changes that are not intended for  
out-of-cycle release to the production environment. This may include 
non-critical bug fixes, documentation updates, CI/CD changes, dependency 
updates, or other tooling changes.

Feature development begins by creating a new branch off of `main`:

```shell
read -p "Enter the feature branch name: " BRANCH_NAME
# Everything below can run unmodified.
git checkout main
git pull
git checkout -b "$BRANCH_NAME"
```

Feature branches are merged back to `main`, and only to `main`.

## Preparing a feature release

When the code or documentation is ready for release, a new feature release will
be created. Feature releases begin by creating a new branch off of `main`:

```shell
read -p "Enter the feature release version: " NEW_VERSION
# Everything below can run unmodified.
BRANCH_NAME="release-$NEW_VERSION"
git checkout main
git pull origin
git checkout -b "$BRANCH_NAME"
```

Next, proceed to the [Merging release branches](#merging-release-branches) section.

## Preparing a hotfix release

If a bug is found in production and must be fixed immediately, this requires a
hotfix release. In general, dependency updates should not be in-scope for hotfix
releases.

Hotfix releases begin by creating a branch off of `production`:

```shell
read -p "Enter the hotfix release version: " NEW_VERSION
# Everything below can run unmodified.
BRANCH_NAME="hotfix-$NEW_VERSION"
git checkout production
git pull origin
git checkout -b "$BRANCH_NAME"
```

After creating the hotfix branch, fix that bug, create a changelog fragment and
commit the changes in the hotfix branch!

Next, proceed to the [Merging release branches](#merging-release-branches) section.

## Merging release branches

**NOTE**:
The steps in this document must be performed in a release or hotfix branch.
See the
[Preparing a feature release](#preparing-a-feature-release)
or
[Preparing a hotfix release](#preparing-a-hotfix-release)
section for steps to create a release or hotfix branch.

After creating a release or hotfix branch, you must follow these steps to merge
the branch to `production` and `main`:

1. Bump the version.
2. Bump copyright years as appropriate.
3. Collect changelog fragments as appropriate.
4. Commit all changes to git.
5. Submit a PR to merge the release branch into `production`.
   1. Wait for linting and unit/integration/CI/doc tests to pass.
   2. It is the release engineer's discretion to ask for and require PR
      approvals. A release branch will usually contain code that has already 
      been reviewed, unless it is a hotfix. If the release is a hotfix, it is
      recommended to get approvals.
6. Merge the release branch to `production`.
   1. After merging, tag the version in git.
   2. After tagging, create a new release with release notes.
7. Merge `production` into `main`.
8. Delete the remote and local release branch.

We should create a Github Action to automate steps 6.1, 6.2, 7, 8 and the production deployment.

## Deploying to production

Merges into `production` will trigger a documentation deployment to ReadTheDocs
and a Github Action will run to build and deploy the package to PyPI. Once the 
release is successfully merged into `production`, automated processes take over
and the public components will be released. It is the release engineer's
responsibility to ensure that the Github Action executes successfully and the 
changes are successfully deployed.
