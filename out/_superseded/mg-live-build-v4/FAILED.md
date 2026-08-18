# FAILED — mg-live-build-v4

| field | value |
|---|---|
| pipeline | minigame (Assignment 6 #2) |
| agent | **mg-programmer** |
| stage | **programmer** |
| time | 2026-08-18 02:30:03 |

## Error

```
AGENT FAILURE [mg-programmer]: patch failed post-checks twice: the headless PLAY-PROBE drove your patched build in a real browser and it FAILED: P4_first_use_line_shown. Probe detail: {"title": {"phase": "title", "active": false}, "wasd": {"before": [15, 24], "after": [15, 21]}, "flame": {"before": 0.5, "afterClick": 0.5}, "idle": {"survived_ms": 8000, "ended": false}, "tip": "You kindle a flame. Nearby people feel its warmth and adopt your conviction.\nWASD move \u00b7 L-click flame \u00b7 R-click roar\u2192carves a road \u00b7 Q wait", "resolution": {"resolved": {"active": false, "won": false, "failed": false}, "moveBefore": [15, 21], "moveAfter": [18, 21]}, "errors": []}
```

See RUN-LOG.md for the trail; runs are independent — fix and re-run.
