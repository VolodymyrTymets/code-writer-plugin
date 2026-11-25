---
description: Paths the agent must never write to, and paths that need confirmation first. Read by the guard-protected-paths hook.
---

# Protected paths

Universal starter list. **`/setup` must append this repo's real paths** — the categories below tell you what
to look for; the specific names differ per ecosystem and per repo.

Every glob here is `**/`-prefixed unless the file it names can only exist at the repository root. A monorepo
is the normal case, not the exception: build output, lockfiles and generated code live under `apps/*`,
`packages/*` and `services/*`, and a rule written as `dist/**` protects nothing there. `**/` spans whole path
segments, so `**/dist/**` still covers a root-level `dist/` and does not touch `src/mydist/`.

A line starting with `!` is an **exception**: it wins wherever it sits in the list. `**/.env.*` would
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
**/dist/**
**/build/**
**/out/**
**/target/**
**/coverage/**
**/tmp/**
**/.cache/**
**/*.generated.*
**/*.gen.*
**/generated/**
**/__generated__/**
**/*.lock
**/*-lock.json
**/*-lock.yaml
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

<!-- /setup appends this repo's dependency dirs, generated paths, platform build folders and
     no-touch legacy areas here, discovered from the repo itself. Keep each line a glob. -->
