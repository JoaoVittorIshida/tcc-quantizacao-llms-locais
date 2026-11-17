"""Zero-shot, direct-answer MMLU-Pro prompt for paired quantization comparisons."""


LETTERS = "ABCDEFGHIJ"


def doc_to_text(doc):
    options = "\n".join(
        f"{LETTERS[i]}. {option.strip()}" for i, option in enumerate(doc["options"])
    )
    return (
        "Choose the best answer. Reply with only its capital letter (A-J), "
        "without explanation.\n\n"
        f"Question: {doc['question'].strip()}\n"
        f"Options:\n{options}\nAnswer:"
    )
