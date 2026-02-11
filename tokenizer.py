import sys

STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am",
    "an", "and", "any", "are", "aren", "as", "at", "be", "because",
    "been", "before", "being", "below", "between", "both", "but", "by",
    "cannot", "could", "couldn", "did", "didn", "do",
    "does", "doesn", "doing", "don", "down", "during", "each",
    "few", "for", "from", "further", "had", "hadnt", "has", "hasn",
    "have", "haven", "having", "he", "her",
    "here", "hers", "herself", "him", "himself", "his",
    "how", "hows", "i", "d", "ll", "m", "ve", "if", "in", "t",
    "into", "is", "isn", "it", "s", "itself", "lets",
    "me", "more", "most", "mustn", "my", "myself", "no", "nor",
    "not", "of", "off", "on", "once", "only", "or", "other", "ought",
    "our", "ours", "ourselves", "out", "over", "own", "same", "shan",
    "she", "should", "shouldnt", "so", "some", "such", "than", "that", "the", "their",
    "them", "themselves", "then", "there", "these", "they", "this", "those",
    "through", "to", "too", "under", "until", "up", "very", "was",
    "wasn", "we", "were", "weren", "what", "when", "where",
    "which", "while", "who", "whom", "why", "with",
    "would", "wouldn", "you", "your", "yours", "yourself", "yourselves",
}

"""
This tokenize function parses the input by looping through n characters
from the input file. It also calculates the check sum value of the line's tokens, The operations its performing on each characters,
such as checking for isalnum and isascii, adding characters to the
cache list, and adding words to the tokens list are all O(1). 
Thus, it simplifies into O(n) (linear) runtime complexity.
"""
def tokenize(text: str) -> tuple[list[str], int]:
    tokens = []
    cache = ''

    check_sum = 0

    for char in text:
        # Parses the file content by character
        if (char.isalnum() and char.isascii()):
            cache += char.lower()
            check_sum += ord(char.lower())
        elif cache:
            tokens.append(cache)
            cache = ''

    if (cache):
        # Adds the last token
        tokens.append(cache)

    return (tokens, check_sum)

"""
This computeWordFrequencies function counts the frequency of each token
by looping through the n tokens in the provided list. For each token in
the list, it either creates a new dictionary entry or increment an
existing entry to track duplicate tokens. It means the runtime complexity
for this function grows linearly with the input (O(n)).
"""
def compute_word_frequencies(tokens: list[str], current_words: dict[str: int]) -> dict[str: int]:
    for token in tokens:
        if (token in STOP_WORDS
            or len(token) == 1
            or token.isdigit()):
            continue
        if token in current_words.keys():
            current_words[token] += 1
        else:
            current_words[token] = 1
    return current_words
