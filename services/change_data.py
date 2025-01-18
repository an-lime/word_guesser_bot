from aiogram.types import CallbackQuery


async def get_alphabet(word: str, del_letter: str = None) -> dict[str, str]:
    alpha = {f'char_{chr(character)}_{word}': f'{chr(character)}' for character in range(ord('А'), ord('Е') + 1)}
    alpha.update({f'char_Ё_{word}': 'Ё'})
    alpha.update({f'char_{chr(character)}_{word}': f'{chr(character)}' for character in range(ord('Ж'), ord('Я') + 1)})
    if del_letter is not None:
        del_letter = del_letter.replace('_', '')

        for key in list(alpha.keys()):
            if key.split('_')[1].lower() in del_letter:
                alpha[f'{key}*'] = alpha.pop(key)
                alpha = dict(sorted(alpha.items(), key=lambda x: x[1]))

                mykeys = list(alpha.keys())
                myitems = list(alpha.values())
                mykeys.insert(6, mykeys.pop(0))
                myitems.insert(6, myitems.pop(0))
                alpha = dict(zip(mykeys, myitems))

        for key in list(alpha.keys()):
            if key[-1] == '*':
                alpha[key] = '*'

    return alpha


def get_word_from_callback(callback: CallbackQuery):
    return callback.data.split('_')[-1]


def get_letter_from_callback(callback: CallbackQuery):
    return callback.data.split('_')[1]


def try_guess_letter(letter: str, word: str, word_completion: str) -> str:
    for i in range(len(word)):
        if word[i] == letter:
            word_completion = word_completion[:i] + letter + word_completion[i + 1:]
    return word_completion
