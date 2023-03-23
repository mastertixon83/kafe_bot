def declension(number: int, word: str):
    cases = [2, 0, 1, 1, 1, 2]
    titles = ['%s' % word, '%sа' % word, '%sов' % word]
    return titles[(number % 100 // 10 != 1) * cases[min(number % 10, 5)]]

number = 5
word = "человек"
print(f"{number} {declension(number, word)}")