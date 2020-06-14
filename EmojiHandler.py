import re
from unidecode import unidecode


def add_emoji(lines):
    print(lines)
    """
    Function to add emoji to the lines.
    """
    for idx in range(len(lines)):  # for every line
        to_index = lines[idx].replace('-', ' ').split()
        for index in range(len(to_index)):  # remove diacritics and lower chars
            to_index[index] = unidecode(to_index[index].lower())
        for word in to_index:
            word = re.sub(r"\([^\(\)]*\)", '', word)  # for every word
            if word in emoji_dict:  # if it is in our emoji dictionary
                lines[idx] = lines[idx] + ' ' + emoji_dict[word]  # we add that emoji to the end of the line
    return lines  # return lines with emoji


emoji_dict = {
    "dimineata": '🌅',
    "brate": '🆘'
}
