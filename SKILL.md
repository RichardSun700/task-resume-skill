---
name: task-resume
description: Automatic interrupted-task resume workflow with queueing and recovery. Use when a user asks to resume interrupted work after temporary context switches, protect priority tasks from drift, or enforce "finish current task then auto-resume previous interrupted task" behavior.
---

# Task Resume

Use this skill to ensure interrupted tasks are recovered automatically.

## Rules

- Treat user-explicit commands (`取消`, `暂停`, `改优先级`, `明天再做`) as overrides.
- Treat all other topic switches as potential interruptions.
- Before switching topics, persist interruption context to queue.
- After completing the active task, immediately resume the oldest queued interrupted task.
- If queue is empty, do nothing.

## Queue Storage

- Queue file: `memory/task-resume-queue.json`
- Use helper script: `scripts/task_resume_queue.py`

## Interruption Detection

Consider a task interrupted when all are true:
1. There is an active task with unfinished acceptance criteria.
2. A new user request is unrelated to finishing that active task.
3. User did not explicitly cancel/pause/defer the active task.

## On Interruption (enqueue)

Run:

```bash
python3 skills/task-resume/scripts/task_resume_queue.py add \
  --title "<active task title>" \
  --context "<what was done + exact next step>" \
  --acceptance "<acceptance criteria>" \
  --source "<session/channel>"
```

Then acknowledge briefly: queued + will auto-resume.

## On Active Task Completion (resume)

Run:

```bash
python3 skills/task-resume/scripts/task_resume_queue.py pop
```

- If one item is returned, resume it immediately and announce: `继续之前中断任务：<title>`.
- If empty, continue normal flow.

## Guardrails

- Never drop queued tasks silently.
- Always include `next_step` quality context when enqueueing.
- Deduplicate: if same task title and near-identical context exists in queue, update timestamp instead of appending.
- Keep queue max size 30; discard oldest overflow items after logging to `memory/YYYY-MM-DD.md`.

## Daily Hygiene

At least once daily:

```bash
python3 skills/task-resume/scripts/task_resume_queue.py list
```

If stale items (>7 days), ask user whether to cancel or schedule.
