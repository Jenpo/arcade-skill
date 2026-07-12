# Arcade Skill Design

Arcade Skill is an agent-era waiting-room arcade. The visual language should
feel like a tiny cabinet beside a terminal: useful enough for developers,
playful enough to invite one run, and honest enough to avoid growth-hack gloss.

## Product Shape

- **Audience:** developers waiting on Codex, Claude Code, installs, tests, CI,
  lint, or diff generation.
- **Core feeling:** retro cabinet, terminal sidecar, short break, back to work.
- **Do not feel like:** a generic browser-game portal, a crypto casino, a mobile
  revive economy, or a SaaS landing page wearing game copy.

## Visual System

- Background: warm paper, not flat white.
- Primary surface: dark cabinet/screen panels.
- Accent colors: phosphor green, coin yellow, spike red, muted teal.
- Radius: 8px or less.
- Typography: system sans for pages, monospace for terminal/game signals.
- Imagery: actual game state, terminal/cabinet compositions, score meters.
- Layout: first viewport should reveal the product premise and at least one real
  arcade/game signal.

## UX Rules

- Language links and scenario links stay readable; do not crowd languages into
  body copy.
- Stripe support is allowed, but never framed as buying power.
- Ranked language must repeat: no paid health, no paid revive, no leaderboard
  advantage.
- Local skill sessions stay ad-free. AdSense belongs only to hosted web pages.

## Awesome Design MD Collaboration Angle

Proposed category: **Retro Web / Developer Tool / Agent UX**.

Pitch: Arcade Skill turns AI-agent waiting time into a tiny retro arcade cabinet.
The design combines terminal status, manifest hot-update architecture, and
Flash-era mini-game energy without becoming a generic games portal.

Contribution posture:

1. Use the upstream `Design MD Request` issue form. The repository currently
   says it cannot accept external `DESIGN.md` pull requests.
2. Submit `https://arcade.fxpeek.com/scenarios/` as the website.
3. Use `data@fxpeek.com` as the project delivery email and Priority `No`.
4. Link this design file and screenshots in Additional Details.
5. Disclose maker ownership and request a generated review, not an endorsement.

## Reference Audit

### Reference

- **Vercel:** quiet developer-tool hierarchy, compact technical labels, and
  restrained 4-8px radii.
- **Stripe:** one clear payment action, tabular treatment for money and status,
  and explicit transaction trust copy.
- **PlayStation:** real game state carries the visual story; chrome stays quiet,
  sections have one job, and game surfaces avoid decorative shadows.

### Keep

- The terminal plus arcade-cabinet composition. It explains the agent waiting
  room faster than generic product copy.
- The phosphor, coin, danger, and paper palette. It belongs to this product and
  should not be replaced by another brand's blue or indigo.
- The visible Stripe and fair-ranking rules. Trust is part of the interface.

### Fix

- **P1 / `/scenarios/`:** use compact 6px actions and plain navigation links;
  avoid making every link a pill.
- **P1 / cabinet preview:** show a recognisable pixel person, not a generic
  square, and use a flat screen color so the game state remains legible.
- **P2 / scenario cards:** remove decorative shadows and keep cards as simple
  indexed entries rather than floating marketing tiles.

### Avoid

- Vercel's monochrome identity, Stripe's mesh gradients, and PlayStation's blue
  brand system. They are references for hierarchy, not skins to copy.
- Oversized marketing headlines, decorative blobs, nested cards, and a payment
  CTA that competes with the play action.

### Verify

- Desktop: product premise, cabinet, play action, and one scenario row are
  visible without overlap at 1440x900.
- Mobile: navigation wraps cleanly, the cabinet appears before long copy, and
  no label or action overflows at 390x844.
- Keyboard: every link has a visible focus state.
- Trust: support remains Stripe-only, localhost remains ad-free, and no copy
  claims that global ranking or Stripe Pro is already live.

The ready-to-submit collaboration draft lives in
[`docs/awesome-design-md-proposal.md`](awesome-design-md-proposal.md).
