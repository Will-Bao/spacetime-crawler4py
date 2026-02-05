import sys

"""
This tokenize function parses the input by looping through n characters
from the input file. The operations it's performing on each characters,
such as checking for isalnum and isascii, adding characters to the
cache list, and adding words to the tokens list are all O(1).
Thus, it simplifies into O(n) (linear) runtime complexity.
"""
def tokenize(text: str) -> list[str]:
    tokens = []
    cache = ''

    for char in text:
        # Parses the file content by character
        if (char.isalnum() and char.isascii()):
            cache += char.lower()
        elif cache:
            tokens.append(cache)
            cache = ''

    if (cache):
        # Adds the last token
        tokens.append(cache)

    return tokens

"""
This computeWordFrequencies function counts the frequency of each token
by looping through the n tokens in the provided list. For each token in
the list, it either creates a new dictionary entry or increment an
existing entry to track duplicate tokens. It means the runtime complexity
for this function grows linearly with the input (O(n)).
"""
def compute_word_frequencies(tokens: list[str]) -> dict[str: int]:
    words = dict()
    for token in tokens:
        if token in words.keys():
            words[token] += 1
        else:
            words[token] = 1
    return words

"""
This print_tokens method utilizes the items() method to retrieve n values
from the provided dictionary, which is O(n) time complexity. It also uses
the sorted() method that has O(nlog(n)) time complexity to sort the dictionary
in descending order. Finally, printing all the tokens will have O(n) time
complexity for n items in the dictionary. Therefore, the time complexity of
this function adds to O(nlog(n)) (linearithmic time).
"""
def print_tokens(frequencies: dict[str: int]):
    token_values = frequencies.items()
    # Sort tokens in decending order by their frequency in the second index of the tuple
    sorted_tokens = sorted(token_values, key=lambda x: x[1], reverse=True)
    for word, amount in sorted_tokens:
        print(word, amount)

"""
The runtime complexity for main is O(n^3 log(n)) because it utilizes the
three previous functions, which combines their time complexity.
"""
def main():
    if (len(sys.argv) < 1):
        print("At least 1 file names required.")
        return

    print_tokens(compute_word_frequencies(tokenize(sys.argv[1])))


if __name__ == '__main__':
    main()