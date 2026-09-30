# Fidelity test: /solutions/monitoring/ (first pass)

Method: read the live page at 1440px and compare it with what the kit generates (class trees and boxes).

| Check | Result |
|---|---|
| Feature-row wrapper classes | Match, exactly |
| Text half (h3, description) classes, flip order, padding | Match |
| Row size at 1440 | Live 1140 wide, text 551 / image 549 |
| Image box | **Gap found and fixed**: live box is `flex items-center justify-center min-h-[220px] md:min-h-[340px] lg:h-[400px]`; kit lacked the flex centring and min-heights. Added (scene rows use min-height, not the fixed 400, so tall scenes are not clipped) |
| Heading level | Live uses h3 in feature rows; our page uses h2 per the copy doc. Needs a decision |
| Case-study and FAQ sections | Markup was read but is **not yet saved** as templates, so they are not tested |
| Hero, CTA, footer | Not re-tested in this pass |
| Pixel diff at 390/768/1024/1440 | Not run: needs a machine that can load the live stylesheet |

Verdict: feature rows now match; page type stays "observed", not "verified", until case-study, FAQ, hero and CTA also pass.
