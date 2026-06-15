# Evaluation Spec — Pod Classifier

Complete this spec **before** writing any code for Milestone 3.

Use Plan or Ask mode to think through each blank field. When you're done,
your answers here become the blueprint for `compute_accuracy()` and
`compute_per_class_accuracy()` in `evaluate.py`.

---

## Background: What is evaluation?

After building a classifier, we need to know how well it works. Evaluation answers:
- **Overall:** What fraction of episodes did we classify correctly?
- **Per-class:** Are we better at some labels than others?

Both functions take the same inputs: a list of predicted labels and a list of
ground-truth labels, in the same order.

---

## compute_accuracy(predictions, ground_truth)

### What it does
Returns the fraction of predictions that exactly match the ground truth.

### Inputs

| Parameter | Type | Description |
|---|---|---|
| `predictions` | `list[str]` | Labels predicted by `classify_episode()`, one per episode. |
| `ground_truth` | `list[str]` | The correct labels, in the same order as `predictions`. |

### Output

| Return value | Type | Description |
|---|---|---|
| accuracy | `float` | A value between 0.0 and 1.0. |

---

### Spec fields — fill these in before writing code

**Formula:**

```
Accuracy is computed as:
Accuracy = (Number of correct predictions) / (Total number of predictions)

- A prediction is "correct" if it exactly matches the ground-truth label (e.g., both are "interview").
- We divide the number of correct predictions by the total number of items in the predictions/ground-truth list.
```

---

**Step-by-step logic:**

```
1. Check if the length of predictions or ground_truth is 0. If so, return 0.0 to avoid division by zero.
2. Initialize a counter for correct predictions to 0.
3. Loop through both lists in parallel using zip.
4. For each pair, check if the predicted label matches the ground-truth label. If yes, increment the counter.
5. Divide the counter by the total number of predictions and return the resulting float.
```

---

**Edge case — what if both lists are empty?**

```
The function should return 0.0 because there are no predictions to evaluate, and returning 0.0 avoids a ZeroDivisionError in Python.
```

---

**Worked example:**

```
predictions  = ["interview", "solo", "panel", "interview"]
ground_truth = ["interview", "solo", "solo",  "narrative"]

Comparison:
- Index 0: "interview" == "interview" (Correct)
- Index 1: "solo" == "solo" (Correct)
- Index 2: "panel" != "solo" (Incorrect)
- Index 3: "interview" != "narrative" (Incorrect)

Number of correct predictions = 2
Total predictions = 4
compute_accuracy() returns 2 / 4 = 0.5
```

---

## compute_per_class_accuracy(predictions, ground_truth)

### What it does
Returns accuracy broken down by each label. For each label in `VALID_LABELS`,
reports how many episodes with that ground-truth label were classified correctly.

### Inputs

| Parameter | Type | Description |
|---|---|---|
| `predictions` | `list[str]` | Labels predicted by `classify_episode()`. |
| `ground_truth` | `list[str]` | Correct labels, in the same order. |

### Output

A `dict` keyed by label. Each value is a dict with three keys:

```python
{
    "interview": {"correct": int, "total": int, "accuracy": float},
    "solo":      {"correct": int, "total": int, "accuracy": float},
    "panel":     {"correct": int, "total": int, "accuracy": float},
    "narrative": {"correct": int, "total": int, "accuracy": float},
}
```

---

### Spec fields — fill these in before writing code

**What does "correct" mean for a given class?**

```
An episode is correctly classified for a class (e.g., "interview") when its ground-truth label is "interview" and the predicted label is also "interview".
```

---

**What does "total" mean for a given class?**

```
"Total" means the number of episodes in the dataset whose ground_truth label is that specific class. It is NOT the number of times that class was predicted.
```

---

**Step-by-step logic:**

```
1. Initialize the result dictionary where each label in VALID_LABELS maps to {"correct": 0, "total": 0, "accuracy": 0.0}.
2. Loop over predictions and ground_truth in parallel using zip.
3. For each pair (pred, truth):
   - If truth is a valid label in the dictionary:
     - Increment the "total" count for the truth class.
     - If pred == truth, increment the "correct" count for that class.
4. After the loop, iterate through each class in the result dictionary:
   - If total > 0, calculate accuracy = correct / total.
   - Else, set accuracy = 0.0.
5. Return the result dictionary.
```

---

**Edge case — what if a class has no examples in ground_truth (total == 0)?**

```
The accuracy for that class should be set to 0.0. This prevents division by zero and correctly represents that there were no ground-truth cases of that class to evaluate.
```

---

**Worked example:**

```
predictions  = ["interview", "interview", "solo", "panel", "panel"]
ground_truth = ["interview", "solo",      "solo", "panel", "narrative"]

Matches by ground-truth classes:
- "interview": ground_truth has 1 instance (index 0, pred is "interview" - Correct). correct=1, total=1, accuracy=1.0.
- "solo": ground_truth has 2 instances (index 1: pred is "interview" - Incorrect; index 2: pred is "solo" - Correct). correct=1, total=2, accuracy=0.5.
- "panel": ground_truth has 1 instance (index 3: pred is "panel" - Correct). correct=1, total=1, accuracy=1.0.
- "narrative": ground_truth has 1 instance (index 4: pred is "panel" - Incorrect). correct=0, total=1, accuracy=0.0.

label       correct  total  accuracy
----------  -------  -----  --------
interview   1        1      1.0
solo        1        2      0.5
panel       1        1      1.0
narrative   0        1      0.0
```

---

## Reflection questions (discuss at the checkpoint)

1. Your overall accuracy might be decent even if one class has very low accuracy.
   Why is per-class accuracy a more informative metric than overall accuracy alone?

2. If `panel` episodes consistently get misclassified as `interview`, what does
   that tell you about your training labels or your prompt?

3. You labeled 20 training episodes and evaluated on 20 test episodes (5 per class).
   How might the evaluation results change if you had labeled 100 training episodes?
   What if you had 200 test episodes?
