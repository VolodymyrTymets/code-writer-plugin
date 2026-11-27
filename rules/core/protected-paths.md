---
description: Paths the agent must never write to, and paths that need confirmation first. Read by the guard-protected-paths hook.
paths:
  - ".claude/rules/protected-paths*.md"
---

# Protected paths

Universal list: only what every repository has. Each stack installs its own `protected-paths.<stack>.md` beside
this file for dependency directories, lockfiles and build output, and the hook reads all of them. **`/setup` must add
this repo's real paths** — the categories below tell you what to look for; the specific names differ per ecosystem and
per repo.

Every glob here is `**/`-prefixed unless the file it names can only exist at the repository root. A monorepo
is the normal case, not the exception: build output, lockfiles and generated code live under `apps/*`,
`packages/*` and `services/*`, and a rule written as `dist/**` protects nothing there. `**/` spans whole path
segments, so `**/dist/**` still covers a root-level `dist/` and does not touch `src/mydist/`.

A line starting with `!` is an **exception**: it wins wherever it sits in the lists of its own file. `**/.env.*` would
otherwise cover `.env.example`, which holds no values and is the one file that records which variables a
service needs — a feature that adds a config variable has to update it. Add an exception whenever a pattern
here catches a file that carries no secret and is not generated. (The `!` entries in
`.claude/settings.json` look the same but are Claude Code's own gitignore negations, and those only carve
out of the rules written *above* them.)

Categories to hunt for during setup:

1. **Secrets and key material** — env files, certificates, private keys, signing material, service-account JSON.
2. **Dependency directories and lockfiles** — anything a dependency manager owns and regenerates.
3. **Build and cache output** — anything a build produces.
4. **Generated code** — API clients, ORM clients, protobuf or schema-generated output, i18n bundles, anything with a generator command.
5. **Platform build folders** — generated native or container build directories in a project that generates them from config.

## Never write (hook blocks, no in-session override)

```
**/.env
**/.env.*
!**/.env.example
!**/.env.sample
!**/.env.template
**/*.pem
**/*.key
**/*.p8
**/*.p12
**/*.jks
**/*.keystore
**/*.mobileprovision
**/id_rsa*
**/*credentials*.json
**/*service-account*.json
**/target/**
**/*.generated.*
**/*.gen.*
**/generated/**
**/__generated__/**
```

## Ask first (hook asks for confirmation)

```
.github/workflows/**
.gitlab-ci.yml
.claude/**
**/Dockerfile
**/docker-compose*.yml
**/Makefile
**/CLAUDE.md
```

## Project additions

<!-- /setup adds this repo's dependency dirs, generated paths, platform build folders and
     no-touch legacy areas here, discovered from the repo itself. Put each glob in a fenced block under a
     `### Never write` or `### Ask first` heading: that heading decides how the hook treats it. -->
