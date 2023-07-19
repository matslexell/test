# Call this with 'npm run create-release'. If you're doing a major release, call
# it and add 'major' to the arguments. For example 'npm run create-release
# major'. If you want to override the protection rules, add 'override' to the
# arguments. For example 'npm run create-release override'. The order of the
# arguments doesn't matter.

import json
import subprocess
import sys
import webbrowser

override_protection = 'override' in sys.argv
is_major = 'major' in sys.argv


def run(command):
    return subprocess.check_output(command.split(' ')).decode().strip()


def protection_rules():
    run('git fetch')

    if run('git symbolic-ref --short HEAD') != 'staging':
        print('Current branch is not staging')
        sys.exit(1)

    if run('git rev-parse @{u}') != run('git rev-parse origin/staging'):
        print('Current branch is not up to date with origin')
        sys.exit(1)

    if run('git status --porcelain') != '':
        print('Current branch has uncommitted changes')
        sys.exit(1)

    if run('git log @{u}..') != '':
        print('Current branch has unpushed commits')
        sys.exit(1)

    if run('git ls-files --other --exclude-standard') != '':
        print('Current branch has untracked files')
        sys.exit(1)

    if run('git diff --name-only --diff-filter=U') != '':
        print('Current branch has unmerged files')
        sys.exit(1)


if not override_protection:
    protection_rules()

# Load version from package.json
with open('package.json') as f:
    data = json.load(f)
    current_version = data['version']

# Split the version into its components
major, minor, patch = current_version.split('-')[0].split('.')

# Store the latest release commit
last_release_commit = run(f'git rev-list -n 1 v{current_version}')

# Fetch total commits from current branch using git rev-list --count HEAD ^last_release_commit
total_commits = run(f'git rev-list --count HEAD ^{last_release_commit}')

# Fetch commits that contain 'feature' using git rev-list --grep='`Feature`' --count HEAD ^last_release_commit
feature_commits = run(
    f'git rev-list --grep=`Feature` --count HEAD ^{last_release_commit}')

# Compute new version
new_minor = int(minor) + int(feature_commits)
new_patch = int(patch) + int(total_commits) - \
    int(feature_commits) + 1  # +1 for the release commit

if is_major:
    new_minor = 0
    new_patch = 0
    major = int(major) + 1

new_version = f'{major}.{new_minor}.{new_patch}-beta'

print(f'Current version: {current_version}')
print(f'New version: {new_version}')

willProceed = input(
    'Would you like to proceed with creating the release? (y/n): ').strip().lower()

if willProceed != 'y' and willProceed != 'yes':
    sys.exit(1)

# Checkout to new branch
run(f'git branch -m release/v{new_version}')

# Update package.json
data['version'] = new_version
with open('package.json', 'w') as f:
    json.dump(data, f, indent=2)

# Run npx prettier --write package.json
run('npx prettier --write package.json')

# Run npm install
run('npm install')

# Commit changes
run('git add .')
subprocess.run(['git', 'commit', '-m', f'`Chore` release {new_version}']) # Doesn't work with run for some reason

# # create a tag called git tag v{version}
# run(f'git tag v{new_version}')

# # Push the tag to the repository
# run(f'git push origin v{new_version}')

# Push the branch to the repository
run(f'git push -u origin release/v{new_version}')

# Open the releases page on the GitHub repository
webbrowser.open('https://github.com/matslexell/test/releases/')

# # Open the page to create a new pull request for the new release branch
webbrowser.open(f'https://github.com/matslexell/test/pull/new/release/v{new_version}')
