from aiogram.types import CallbackQuery


def get_alphabet(word: str) -> dict[str, str]:
    alpha = {f'char_{chr(character)}_{word}': f'{chr(character)}' for character in range(ord('А'), ord('Е') + 1)}
    alpha.update({f'char_Ё_{word}': 'Ё'})
    alpha.update({f'char_{chr(character)}_{word}': f'{chr(character)}' for character in range(ord('Ж'), ord('Я') + 1)})
    return alpha

def get_word_from_callback(callback: CallbackQuery):
    return callback.data.split('_')[-1]