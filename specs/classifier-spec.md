# Classifier Spec — Pod Classifier

Complete this spec **before** writing any code for Milestone 2.

Use Plan or Ask mode to think through each blank field. When you're done,
your answers here become the blueprint for `build_few_shot_prompt()` and
`classify_episode()` in `classifier.py`.

---

## build_few_shot_prompt(labeled_examples, description)

### What it does
Constructs a prompt string for the LLM that includes the task instructions,
all labeled training examples, and the new episode description to classify.

### Inputs

| Parameter | Type | Description |
|---|---|---|
| `labeled_examples` | `list[dict]` | Each dict has `"title"`, `"description"`, `"label"` (and others). These are the examples you labeled in Milestone 1. |
| `description` | `str` | The episode description to classify. |

### Output

| Return value | Type | Description |
|---|---|---|
| prompt | `str` | A complete prompt string ready to send to the LLM. |

---

### Spec fields — fill these in before writing code

**Task instruction (what should the LLM know about the task?):**

```
You are classifying podcast episodes by their format. Classify the episode
into exactly one of these four labels:

- interview: a conversation between a host and one or more guests
- solo: a single host speaking from memory, experience, or opinion — no guests,
  no assembled external sources
- panel: multiple guests with roughly equal speaking time, often debating or
  discussing a topic together
- narrative: a story assembled from external sources — interviews, archival
  audio, reporting — with a clear narrative arc

Return only the label and your reasoning. Do not explain the taxonomy.
```

---

**How should labeled examples be formatted in the prompt?**

```
Each example should include the episode title, a brief excerpt or the full
description, and the correct label. Separate examples with a blank line or
a delimiter like "---". Include all fields that help the model see why the
label was applied — title and description are both useful; other fields
(like episode ID) are not needed.
```

---

**Example block sketch (write one concrete example):**

```
Title: {title}
Description: {description}
Label: {label}
```

---

**How should the new episode (to be classified) be presented?**

```
Present it in the same format as the labeled examples, but omit the Label
line and replace it with an instruction to classify. For example:

Title: {title}
Description: {description}
Label: ?

Then add a line like: "Classify the episode above. Return your answer in
the format below:" followed by the output format you chose.
```

---

**What output format should you request from the LLM?**

```
We request the following output format:
Label: <label>
Reasoning: <reasoning>

Tradeoffs:
- A single label on its own line is simple but lacks reasoning, making it harder to debug why the model made a choice.
- JSON is highly structured but LLMs sometimes add markdown wrappers or have syntax errors, requiring extra cleaning code.
- A prefix-based key-value format (Label: X / Reasoning: Y) is easy for the LLM to follow, works well even with markdown wrappers, and is extremely robust to parse using line-by-line prefix matching or simple regular expressions.
```

---

**Edge cases to handle in the prompt:**

```
- Empty labeled_examples: If the list is empty, we omit the reference examples section entirely and instruct the LLM to classify based only on its pre-existing knowledge of the definitions.
- Very short description: We still enclose the description in the standard template format (Title: ..., Description: ...). This ensures structural consistency so the LLM knows exactly which text to classify even if it is only a few words.
```

---

## classify_episode(description, labeled_examples)

### What it does
Classifies a single podcast episode description using the few-shot LLM classifier.
Returns a dict with a label and reasoning.

### Inputs

| Parameter | Type | Description |
|---|---|---|
| `description` | `str` | The episode description to classify. |
| `labeled_examples` | `list[dict]` | Labeled training examples from `load_labeled_examples()`. |

### Output

| Return value | Type | Description |
|---|---|---|
| result | `dict` | Must have keys `"label"` and `"reasoning"`. `"label"` must be one of `VALID_LABELS` or `"unknown"`. |

---

### Spec fields — fill these in before writing code

**Step 1 — Build the prompt:**

```
Call build_few_shot_prompt(labeled_examples, description) and store the
returned string in a variable (e.g., prompt). Pass through both arguments
exactly as received — no modification needed before calling.
```

---

**Step 2 — Send to the LLM:**

```
Call _client.chat.completions.create() with:
  - model: the model name from config (LLM_MODEL)
  - messages: a list with one dict — {"role": "user", "content": prompt}
    (system-design.md shows an optional system message too — either shape works)
  - max_tokens: a reasonable limit (e.g., 200–300) to keep responses concise

Extract the response text from:
  response.choices[0].message.content
```

---

**Step 3 — Parse the response:**

```
We will parse the response line-by-line or using regular expressions:
- For the label: search for the line starting with "Label:" (case-insensitive) and extract everything after the colon, strip whitespace, and convert to lowercase.
- For the reasoning: search for the line starting with "Reasoning:" (case-insensitive) and extract the rest of the text, including subsequent lines if any.
- Use regex matches like `r"(?i)label:\s*(\w+)"` and `r"(?i)reasoning:\s*(.*)"` (compiled with re.DOTALL) as a fallback to robustly capture the values.
```

---

**Step 4 — Validate the label:**

```
If the parsed label is not in VALID_LABELS, we set the label to "unknown" to prevent upstream issues.
```

---

**Step 5 — Handle errors gracefully:**

```
We wrap the API call and parsing logic in a try-except block. If a Groq API error, timeout, or unparseable response occurs, we catch the exception and return:
{
    "label": "unknown",
    "reasoning": "Error occurred during classification: " + str(e),
}
This allows the evaluation loop to continue classifying the remaining episodes.
```

---

### Return value structure

```python
{
    "label": str,      # one of VALID_LABELS, or "unknown" if invalid/error
    "reasoning": str,  # brief explanation from the LLM
}
```

---

## Notes on label quality

The classifier is only as good as your labels. If your training examples have
inconsistent or ambiguous labels, the LLM will learn the wrong pattern.

Before implementing the classifier, re-read `data/taxonomy.md` and double-check
any labels you're unsure about. Annotation quality is part of the lab.

---

## Implementation Notes

*Fill this in after implementing and testing both functions.*

**Test: what does the raw LLM response look like for one episode?**

```
Episode tested: Marine Biologist Dr. Amara Diallo on What Coral Bleaching Actually Looks Like
Raw response text:
Label: interview
Reasoning: This episode features a conversation between the host and Dr. Amara Diallo, where they discuss her experiences and expertise on coral reefs, making it a clear example of an interview format.
```

**How did you parse the label out of the response?**

```
We split the response text by lines, trimmed each line, and checked if the line (lower-cased) started with the prefixes "label:" or "reasoning:". If a line starts with "label:", we split by the first colon to extract the label, stripping whitespace and converting to lowercase. If a line starts with "reasoning:", we extract the reasoning. If a subsequent line is found that doesn't start with a known prefix, we append it to the reasoning to handle multi-line reasoning robustly.
```

**Did any episodes return `"unknown"`? If so, why?**

```
no
```

**One thing about the output format that surprised you:**

```
The LLM adheres extremely consistently to the requested "Label: <label>" format, without adding conversational wrappers like "Sure, here is the label:" or wrapping the key-value text in markdown codeblocks. This made line-by-line parsing extremely reliable.
```
