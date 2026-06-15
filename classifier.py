import json
import os
from groq import Groq
from config import GROQ_API_KEY, LLM_MODEL, VALID_LABELS, DATA_PATH, TRAIN_FILE, LABELS_FILE

_client = Groq(api_key=GROQ_API_KEY)


def load_labeled_examples() -> list[dict]:
    """
    Load the training episodes and merge them with the student's labels.

    Returns a list of dicts, each with:
      - "id"          : episode ID
      - "title"       : episode title
      - "podcast"     : podcast name
      - "description" : episode description
      - "label"       : the label from my_labels.json (may be None if not yet annotated)

    Only returns episodes where the label is a valid, non-null string.
    Episodes with null labels are silently skipped.
    """
    train_path = os.path.join(DATA_PATH, TRAIN_FILE)
    labels_path = os.path.join(DATA_PATH, LABELS_FILE)

    with open(train_path, encoding="utf-8") as f:
        episodes = {ep["id"]: ep for ep in json.load(f)}

    with open(labels_path, encoding="utf-8") as f:
        labels = {entry["id"]: entry["label"] for entry in json.load(f)}

    labeled = []
    for ep_id, ep in episodes.items():
        label = labels.get(ep_id)
        if label in VALID_LABELS:
            labeled.append({**ep, "label": label})

    return labeled


def build_few_shot_prompt(labeled_examples: list[dict], description: str) -> str:
    """
    Build a few-shot classification prompt using the student's labeled training examples.
    """
    prompt = (
        "You are classifying podcast episodes by their format. Classify the episode "
        "into exactly one of these four labels:\n\n"
        "- interview: a conversation between a host and one or more guests\n"
        "- solo: a single host speaking from memory, experience, or opinion — no guests, no assembled external sources\n"
        "- panel: multiple guests with roughly equal speaking time, often debating or discussing a topic together\n"
        "- narrative: a story assembled from external sources — interviews, archival audio, reporting — with a clear narrative arc\n\n"
    )
    
    if labeled_examples:
        prompt += "Here are some labeled examples for reference:\n\n"
        for ex in labeled_examples:
            prompt += f"Title: {ex.get('title', 'Unknown')}\n"
            prompt += f"Description: {ex.get('description', '')}\n"
            prompt += f"Label: {ex.get('label', '')}\n"
            prompt += "---\n\n"
            
    prompt += (
        "Classify the podcast episode with the following description:\n\n"
        f"Description: {description}\n\n"
        "Return your answer in this exact format:\n"
        "Label: <one of: interview, solo, panel, narrative>\n"
        "Reasoning: <brief explanation of why this label applies>"
    )
    return prompt


def classify_episode(description: str, labeled_examples: list[dict]) -> dict:
    """
    Classify a single podcast episode description using the few-shot LLM classifier.
    """
    try:
        prompt = build_few_shot_prompt(labeled_examples, description)
        
        response = _client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.0,
        )
        content = response.choices[0].message.content
        
        label = "unknown"
        reasoning = ""
        
        for line in content.splitlines():
            line_stripped = line.strip()
            if not line_stripped:
                continue
            line_lower = line_stripped.lower()
            if line_lower.startswith("label:"):
                label = line_stripped.split(":", 1)[1].strip().lower()
            elif line_lower.startswith("reasoning:"):
                reasoning = line_stripped.split(":", 1)[1].strip()
            elif reasoning and not line_lower.startswith("label:"):
                reasoning += "\n" + line_stripped
                
        reasoning = reasoning.strip()
        if label not in VALID_LABELS:
            label = "unknown"
            
        return {
            "label": label,
            "reasoning": reasoning if reasoning else "No reasoning provided by LLM."
        }
    except Exception as e:
        return {
            "label": "unknown",
            "reasoning": f"An error occurred during classification: {str(e)}"
        }

