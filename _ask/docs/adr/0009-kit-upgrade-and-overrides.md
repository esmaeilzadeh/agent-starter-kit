# Kit dogfood, upgrade-kit, and consumer overrides

The kit repo dogfoods its own `_ask/` + Cursor Binding. Consuming repos use overlay install plus `./ask upgrade` (`upgrade-kit.sh`) that refreshes **kit-owned** files from an explicit kit version/tag and never clobbers **consumer-owned** overrides: skill manifest, policies (or local), AGENTS local sections, `.cursor/rules/local/`, and `_ask/agents/*.local.md`. Community Skills track independently via manifest pins. Stock agents/templates/guide/spec/scripts/`ask` remain kit-owned so upgrades stay deliberate and mergeable.
