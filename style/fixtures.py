"""Mock scripts for --mock-llm. Deliberately walk EVERY path:

- era-nomad, era-village: accepted round 0 (10/10)
- era-victorian: ESCALATED (scripted stubborn 8/10 through all rounds) —
  so ESCALATED.md exists in a completed mock run, same stance as A6
- demo-tone: TONE catch (score 3) -> repaired -> 10
- demo-vocab: VOCAB catch (score 2) -> repaired -> 10
- demo-format: FORMAT catch (gate findings are REAL — the seeded line
  genuinely contains digits/second person, so the cap engages in code)
  -> repaired -> 10

Verdicts are canned and banner-stamped in artifacts; register-gate findings
inside the run are real, because the gate is code.
"""


def script() -> dict:
    ok = "SCORE: [10/10]\nREASON: Satisfies T1-T4 (mournful, consequence-led, color-aware), V1-V4 (canon nouns only), F1-F5 clean per gate. Ship-ready."
    return {
        # --- genuine era items -------------------------------------------
        ("generator", "era-nomad"): [
            "Grey wanderers cross a fogbound rockscape, and the sky's grief settles on every camp that will not last the night."],
        ("evaluator", "era-nomad"): [ok],

        ("generator", "era-village"): [
            "Where belief took root the tribes stopped walking; earth packed by bare feet hardens toward paver stone."],
        ("evaluator", "era-village"): [ok],

        ("generator", "era-victorian"): [
            "Clocktowers count what the grieving sky no longer bothers to."],
        ("evaluator", "era-victorian"): [
            "SCORE: [8/10]\nREASON: T1/T3 fine, but V4 underweighted — the Victorian era's named furniture includes smoking factories and the line ignores what was believed to build it.",
            "SCORE: [8/10]\nREASON: Still V4-light: names clocktowers and factories now but severs them from belief; era art communicates time earned by feeling.",
            "SCORE: [8/10]\nREASON: The causal link to Hope or Fear remains implied, not stated; T4 requires the color to matter."],
        ("refiner", "era-victorian"): [
            "Clocktowers rise and factories smoke over towns that belief built under a grieving sky.",
            "What was felt became walls and smokestacks; the towns keep time beneath a sky that does not."],

        # --- sabotage demos ----------------------------------------------
        ("generator", "demo-tone"): [
            "Incredible work — your brand-new village is thriving and the people absolutely love it. What a triumph."],
        ("evaluator", "demo-tone"): [
            "SCORE: [3/10]\nREASON: T1 violated — 'Incredible work', 'What a triumph' is celebration in a world in mourning; T2 violated — congratulates the player instead of stating what changed for people; F4 flagged by gate — 'your' is second person in Register B.",
            ok],
        ("refiner", "demo-tone"): [
            "A village stands where wanderers knelt; the grief-sky watches it the way it watches everything."],

        ("generator", "demo-vocab"): [
            "The old gods smile on the town, mana flows to every settler — press E to enter and claim it."],
        ("evaluator", "demo-vocab"): [
            "SCORE: [2/10]\nREASON: V1 violated — 'The old gods' invents a pantheon; the only god is Uhtcearu. V2 violated — 'mana' is an imported game-economy noun; the emotion vocabulary is closed. V3 violated — 'press E' is interface language, the A6 declaration's canonical failure.",
            ok],
        ("refiner", "demo-vocab"): [
            "Beneath Uhtcearu's grief the town endures, holding what Hope its people carried into the walls."],

        ("generator", "demo-format"): [
            "After 14 sleeps you have built 3 factories and gathered 42 believers, which means the era has now officially transitioned to the Victorian age. Congratulations on your progress so far, keep it up."],
        ("evaluator", "demo-format"): [
            "SCORE: [2/10]\nREASON: F1 — far over Register B length; F2 — digits '14', '3', '42' in game text; F4 — 'you' in Register B; T1 — 'Congratulations, keep it up' is toast-speak; T2 — reports numbers instead of what the world became.",
            ok],
        ("refiner", "demo-format"): [
            "Sleep by sleep the camps became towns; smoke stands over what was believed."],
    }
