---
name: sync-meetings
description: Fetch new Flint meeting transcriptions from Elephan API, create structured meeting files in docs/meetings/, and update the engagement tracker.
disable-model-invocation: true
---

# Sync Meetings from Elephan

Fetch all meeting transcriptions containing "Flint" from the Elephan API, create structured markdown files in `docs/meetings/`, and update the engagement tracker. Only new meetings (not already synced) are processed.

## Step 1: Resolve API Key

Read the `ELEPHAN_API_KEY` from the root `.env` file:

```bash
grep -E '^ELEPHAN_API_KEY=' .env | cut -d'=' -f2-
```

If the variable is not found, report this error and stop:

> **Error:** `ELEPHAN_API_KEY` not found in root `.env` file. Add it: `ELEPHAN_API_KEY=elk_prod_...`

Store the key value for use in subsequent API calls.

## Step 2: Fetch All Transcriptions (Paginated)

Call the Elephan API to retrieve all transcriptions. Use `curl` via Bash:

```bash
curl -s -H "Authorization: Bearer $API_KEY" \
  "https://api.elephan.dev/v1/transcribes?page=1&limit=100"
```

The response is JSON with shape:

```json
{
  "data": [ { ...transcription objects... } ],
  "pagination": { "page": 1, "limit": 100, "total": N, "totalPages": N, "hasNext": bool, "hasPrev": bool }
}
```

**Pagination loop:** If `pagination.hasNext` is `true`, fetch subsequent pages (`page=2`, `page=3`, etc.) until all transcriptions are collected. Combine all `data` arrays.

## Step 3: Filter for "Flint" Meetings

From the complete transcription list, keep ONLY those where the `title` field contains the string "Flint" (case-insensitive match).

Report the count: "Found X transcriptions with 'Flint' in title out of Y total."

## Step 4: Deduplicate Against Existing Files

Search existing meeting files for Elephan transcript IDs:

Use Grep to search `docs/meetings/*.md` for the pattern `info-transcript/?t=` and extract all Elephan IDs that are already synced.

For each filtered "Flint" transcription, check if its `id` already appears in any existing meeting file's Meeting Link. If it does, skip it.

Report: "Skipping N already-synced meeting(s)."

If no new meetings remain after deduplication, report "No new Flint meetings to sync" and stop.

## Step 5: Create Meeting Files

For each NEW transcription, create a file in `docs/meetings/` following the exact format of existing files.

### Filename Convention

Format: `YYYY-MM-DD-descriptive-slug.md`

- **Date:** Extract from `dateIncluded` (ISO 8601 format from API)
- **Slug:** Take the `title`, lowercase it, strip any "Meet -" or "Meet –" prefix, replace spaces and special characters with hyphens, collapse consecutive hyphens, trim trailing hyphens. Keep it concise but descriptive.

Example: Title "Meet – Flint Weekly Check-in" with date 2026-02-05 becomes `2026-02-05-flint-weekly-check-in.md`

### File Template

Use this EXACT template structure (matching existing files like `2025-12-30-flint-kick-off.md`):

```markdown
# [title from API as-is]

## Metadata

- **Date:** [DD, Mon YYYY - HH:MM]
- **Duration:** [formatted duration]
- **Type:** [inferred from title or context]
- **Meeting Link:** https://app.elephan.ai/info-transcript/?t=[transcription id]

## Participants

| Name        | Role | Company |
| ----------- | ---- | ------- |
| [Speaker 1] | -    | -       |
| [Speaker 2] | -    | -       |

## Transcript

[Speaker Name] [MM:SS]: [text]

[Speaker Name] [MM:SS]: [text]
```

### Date Formatting

Convert ISO date (e.g., `2025-12-30T10:04:00.000Z`) to the informal format used in existing files:

- `30, Dec 2025 - 10:04`
- `16th, Jan 2026 - 14:30`

Use ordinal suffixes (1st, 2nd, 3rd, 4th, etc.) for the day number.

### Duration Formatting

The API returns `duration` in seconds. Convert to human-readable:

- Under 60 min: `43min`
- 60+ min: `1h 32min`
- Exact hours: `1h`

### Speaker Attribution and Transcript Formatting

The API provides two transcript sources:

1. `transcript.text` - Full text as a flat string with line breaks between speaker turns (NO speaker names or timestamps)
2. `transcript.speakers` - Array of anonymous segments: `{ text, start, end, sentiment }` (NO speaker name/ID)

**Important:** The Elephan API does NOT provide speaker identification. Speaker segments are anonymous. The existing meeting files with named speakers (e.g., "Thiago Gomes [00:06]:") were manually enriched after import.

**Transcript formatting approach:**

1. Use `transcript.speakers` array to build the transcript with timestamps
2. Format each segment as: `Speaker [MM:SS]: [text]` where `start` is converted from milliseconds to `[MM:SS]`
3. The `start` field is in **milliseconds** -- divide by 1000 then convert to MM:SS with zero-padding
4. Leave speakers as "Speaker" (the user will manually attribute names later)

**Alternative if `transcript.text` is cleaner:** If `transcript.text` has clear paragraph breaks between turns, use it directly as the transcript body (simpler and preserves natural flow). Prefix each paragraph with its corresponding timestamp from the speakers array where possible.

**Participant table:** Leave empty with a placeholder row since speaker names are not available from the API:

```
| Name | Role | Company |
|------|------|---------|
| (attribute manually) | - | - |
```

### Type Field

Infer the meeting type from the title:

- Contains "kick-off" or "kickoff" -> "Kickoff"
- Contains "check-in" or "checkpoint" -> "Check-in"
- Contains "alignment" or "next steps" -> "Alignment"
- Contains "intro" or "introduction" -> "Introduction"
- Otherwise -> Use the `prompt` object's name if available, or "Meeting"

## Step 6: Bootstrap Engagement Tracker (If Missing)

Check if `docs/engagement-tracker.md` exists. If NOT, create it with this template:

```markdown
# Flint Engagement Tracker

## Current Status

- **Last Updated:** [today's date YYYY-MM-DD]
- **Last Meeting:** [none yet]
- **Engagement Phase:** Discovery

## Timeline

| Date | Meeting | Key Outcome |
| ---- | ------- | ----------- |

## Decision Log

## Open Items

## Next Steps

## Key Relationships

## Processed Meetings
```

## Step 7: Update Engagement Tracker

After creating all new meeting files, update the engagement tracker following these rules (from `/f/process-meetings`):

1. **Read** `docs/engagement-tracker.md`
2. **Identify unprocessed meetings:** List all `.md` files in `docs/meetings/`. Any file NOT listed in the "Processed Meetings" section is unprocessed.
3. **Process chronologically** (oldest first). For each unprocessed meeting:
   - Read the full transcript
   - Extract relevant information
   - Update the tracker sections:
     - **Current Status:** Update Last Updated (today), Last Meeting (most recent), Engagement Phase if there's a clear transition
     - **Timeline:** Add a row: `| YYYY-MM-DD | Meeting Title | One-line key outcome |`
     - **Decision Log:** Add any decisions made (reverse chronological, newest at top)
     - **Open Items:** Add new items, mark resolved ones. Format: `- [ ] [Item] -- [Owner] -- [Since: YYYY-MM-DD]`
     - **Next Steps:** Replace with current next steps from the latest meeting
     - **Key Relationships:** Add/update people. Format: `- **[Name]** -- [Role] -- [Stance: Champion / Neutral / etc.]`
     - **Processed Meetings:** Add `- [x] \`filename.md\``
4. **Write** the updated tracker

### Rules

- **No double processing** -- If a meeting file is already in "Processed Meetings", skip it
- **Chronological order** -- Process oldest to newest
- **Preserve existing content** -- Add to the tracker, don't overwrite previous entries
- **Be concise** -- Each entry should be scannable
- **Use exact filenames** -- In "Processed Meetings", list the filename exactly

## Step 8: Report

After completing all steps, output a summary:

```
Elephan Sync Complete:
- Fetched X transcriptions from Elephan API, Y with "Flint" in title
- Created Z new meeting file(s):
  - [filename1.md]
  - [filename2.md]
- Skipped N already-synced meeting(s)
- Engagement tracker updated with M new entries

Key updates:
- [Brief summary of what was added to the tracker]
```

If no new meetings: `No new Flint meetings to sync. All X Flint meetings are already in docs/meetings/.`

## Error Handling

- **API key missing:** Clear error directing to `.env` setup
- **API error (non-200):** Report HTTP status and response body, stop
- **Empty results:** "No transcriptions found in Elephan" and exit
- **No "Flint" matches:** "Found X transcriptions but none contain 'Flint' in title" and exit
- **Malformed transcript:** Skip with warning, continue processing others
- **File already exists with different content:** Do NOT overwrite. Report as already synced.
