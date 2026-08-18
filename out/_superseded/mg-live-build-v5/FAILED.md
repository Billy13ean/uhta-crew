# FAILED — mg-live-build-v5

| field | value |
|---|---|
| pipeline | minigame (Assignment 6 #2) |
| agent | **mg-programmer** |
| stage | **programmer** |
| time | 2026-08-18 02:35:40 |

## Error

```
AGENT FAILURE [mg-programmer]: patch failed post-checks twice: the headless PLAY-PROBE drove your patched build in a real browser and it FAILED: P5_click_feeds_flame, P6_survives_8s_idle, P4_first_use_line_shown, P7_control_returns_after_resolution. Probe detail: {"title": {"phase": "title", "active": false}, "activation": {"active": true, "phase": "play"}, "wasd": {"before": [15, 24], "after": [15, 21]}, "flame": {"before": 0, "afterClick": 0}, "idle": {"survived_ms": 0, "ended": true}, "tip": "You kindle a flame. Nearby people feel its warmth and adopt your conviction.\nWASD move \u00b7 L-click flame \u00b7 R-click roar\u2192carves a road \u00b7 Q wait", "resolution": {"resolved": {"active": true, "won": false, "failed": true}, "moveBefore": [15, 21], "moveAfter": [18, 21]}, "errors": []}
```

See RUN-LOG.md for the trail; runs are independent — fix and re-run.
