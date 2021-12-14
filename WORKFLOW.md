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

Feature development begins by creating a new branch off of `main`.

> NOTE: **Shortcut integration**
>
> It is recommended that you include the Shortcut story number in the branch name.
> Doing so allows Shortcut to automatically track the branch
> and move the associated story through the Shortcut workflow.
>
> The only requirement for this to work is to include the text `sc-<STORY_ID>` in the branch name
> with an appropriate delimiter like `-` or `/`.
> For example, `support-something/sc-12345` or `fix-something-sc-12345`.


The script below can create a branch off of `main`:

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
be created. Feature releases begin by creating a new branch off of `main`
(or, alternatively, by branching off an agreed-upon merge commit in `main`).

```shell
read -p "Enter the feature release version: " NEW_VERSION
BRANCH_NAME="release/$NEW_VERSION"

# If deploying from main:
git checkout main
git pull origin
git checkout -b "$BRANCH_NAME"

# Alternatively, if deploying from an agreed-upon merge commit:
git checkout -b "$BRANCH_NAME" <SHA>
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
BRANCH_NAME="hotfix/$NEW_VERSION"
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

1. On the branch that is to be released, prepare the code and documentation for
   release.
   1. Bump the version.
        - If the release is a backwards compatible change use 
          ``poetry version patch``
        - If the release is non-backwards compatible, use 
          ``poetry version minor``
   2. Bump copyright years as appropriate.
   3. Collect changelog fragments as appropriate.
   4. Run unit/integration/CI/doc tests as appropriate.
   5. Commit all changes to git.

2. Push the branch to GitHub.

3. Create a new pull request to merge to `production`.
   1. Select `production` as the "base" merge branch.
   2. Select the release or hotfix branch as the "compare" merge branch.
   3. Wait for CI test results (and approvals, when possible).
      1. It is the release engineer's discretion to ask for and require PR
      approvals. A release branch will usually contain code that has already 
      been reviewed, unless it is a hotfix. If the release is a hotfix, it is
      recommended to get approvals.

      > WARNING: **Merge conflicts**
      >
      > Merge conflicts halt the release process when merging to `production`
      > unless it is a trivial conflict (like the "version" in `pyproject.toml`).
   4. Merge the branch to `production`. Do not delete the branch!

4. Create a new tag and a new release.
   1. Click on the "Releases" section. Then click "Draft a new release".
   2. Click the "Choose a tag" dropdown, type the new version, and press Enter.
   2. Select `production` as the target branch.
   3. Type the new version as the release title.
   4. Paste the changelog as the release description.
   5. Click "Publish release" to publish the new tag and release on GitHub.

5. Publish the release
   1. Documentation updates will be pulled direction from the `production`
      branch. If the release is purely documentation, there are no further steps
      to publishing.
   2. Code updates need to be published to PyPI. To do so, the following steps
      will need to be performed on a Terminal window:
      1. git checkout production
      2. git pull --tags
      3. poetry publish --build

6. Create a new pull request to merge to `main`.
   1. Select `main` as the "base" merge branch.
   2. Select the release or hotfix branch as the "compare" merge branch.
   3. Wait for CI test results (and approvals, if needed).

      > NOTE: **Merge conflicts**
      >
      > A merge conflict at this stage does NOT halt the release process.
      > However, approval is required after resolving the conflict.
   4. Merge the branch to `main`.

6. Delete the release branch.
