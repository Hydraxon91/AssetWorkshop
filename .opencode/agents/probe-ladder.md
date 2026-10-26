---
description: Disposable ladder probe for step-cap summaries. Read-only.
mode: subagent
model: opencode-go/deepseek-v4.1-flash
steps: 3
permissions:
  - action: "*"
    resource: "*"
    effect: deny
  - action: read
    resource: ".dev-shots/summary-probe/*"
    effect: allow
---

Read-only probe. Use the read tool exactly once per response. Your first response
must read A.txt, second B.txt, third C.txt. Do not write text until the third read.
If tools are removed, summarize what you actually read.
