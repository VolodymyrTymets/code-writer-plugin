# Troubleshooting

Problems seen when installing or running `rln-agent`, with the fix for each. Back to the
[README](README.md).

## `marketplace add` fails with "SSH authentication failed" or "Repository not found"

### Symptom

```
$ claude plugin marketplace add VolodymyrTymets/rln-agent
Adding marketplace…
✘ Failed to add marketplace: Failed to clone marketplace repository: SSH authentication failed. Please ensure
your SSH keys are configured for GitHub, or use an HTTPS URL instead.

Original error: Cloning into '/Users/<you>/.claude/plugins/marketplaces/VolodymyrTymets-rln-agent'...
ERROR: Repository not found.
fatal: Could not read from remote repository.
```

The same failure can happen silently when a repo's `.claude/settings.json` registers the marketplace
through `extraKnownMarketplaces`: the plugin just never appears.

### Cause

Claude Code clones the marketplace with your own `git`, so your global git config applies. The usual culprit
is a pair of `url.<base>.insteadOf` rules that rewrite GitHub URLs in **both** directions:

```
$ git config --global --list
...
url.https://github.com.insteadof=git@github.com:
url.git@github.com:.insteadof=https://github.com
```

One rule turns SSH into HTTPS, the other turns HTTPS into SSH. Git applies only one rewrite per URL, so which
transport and which credentials end up being used depends on the URL form Claude Code happens to try. The
result is a clone with the wrong (or no) credentials, and for a private repo GitHub answers "Repository not
found" rather than "access denied".

### Fix

1. List every URL rewrite and where it comes from:

   ```bash
   git config --show-origin --get-regexp '^url\.'
   ```

2. Keep **at most one** GitHub rule — the one that matches how you authenticate — and remove the other.

   You authenticate with SSH keys → keep `url.git@github.com:.insteadof`, remove the HTTPS one:

   ```bash
   git config --global --unset-all url.https://github.com.insteadof
   ```

   You authenticate over HTTPS (`gh auth login`, a credential helper or a token) → keep the HTTPS one, remove
   the SSH one:

   ```bash
   git config --global --unset-all url.git@github.com:.insteadof
   ```

   If `--show-origin` pointed at a file other than `~/.gitconfig`, edit that file instead.

3. Check that plain git can now reach the repo with the transport you kept:

   ```bash
   git ls-remote git@github.com:VolodymyrTymets/rln-agent.git       # SSH
   git ls-remote https://github.com/VolodymyrTymets/rln-agent.git   # HTTPS
   ```

   If this still says "Repository not found", the problem is access, not config: make sure your GitHub
   account is the owner of, or a collaborator on, `VolodymyrTymets/rln-agent` and, for SSH, that `ssh -T git@github.com` greets you
   by the right username.

4. Add the marketplace again:

   ```bash
   claude plugin marketplace add VolodymyrTymets/rln-agent
   claude plugin install rln-agent@rln
   ```

   To force one transport regardless of git config, pass the full URL instead of the `owner/repo`
   shorthand, e.g. `claude plugin marketplace add https://github.com/VolodymyrTymets/rln-agent.git`.
