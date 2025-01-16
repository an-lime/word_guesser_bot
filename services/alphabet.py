def get_alphabet() -> dict[str, str]:
    alpha = {f'char_{chr(character)}': f'{chr(character)}' for character in range(ord('А'), ord('Е') + 1)}
    alpha.update({'char Ё': 'Ё'})
    alpha.update({f'char_{chr(character)}': f'{chr(character)}' for character in range(ord('Ж'), ord('Я') + 1)})
    return alpha
