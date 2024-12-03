import os
import pickle
from datetime import datetime

import pyphen

import globals


def save_to_json(routers, connections, output_folder="out"):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    stamp = datetime.now().strftime(globals.date_format)

    with open(os.path.join(output_folder, f"routers_{stamp}.dat"), "bw") as f:
        f.write(pickle.dumps(routers))

    with open(os.path.join(output_folder, f"connections_{stamp}.dat"), "bw") as f:
        f.write(pickle.dumps(connections))


def load_from_file():
    with open(get_newest_file_by_filename("out", "routers"), "rb") as fp:
        routers = pickle.load(fp)
    with open(get_newest_file_by_filename("out", "connections"), "rb") as fp:
        connections = pickle.load(fp)
    return routers, connections


def get_newest_file_by_filename(folder_path, prefix, date_format=globals.date_format):
    """
    Get the newest file in the folder with the specified prefix, based on the date in the filename.

    :param folder_path: Path to the folder to search
    :param prefix: Prefix of the file to match
    :param date_format: The datetime format of the date in the filename
    :return: The full path to the newest file, or None if no match is found
    """
    newest_file = None
    newest_date = None

    for file_name in os.listdir(folder_path):
        if file_name.startswith(prefix):
            try:
                date_str = file_name[len(prefix):].split('.')[0][1:]  # Remove prefix and file extension
                file_date = datetime.strptime(date_str, date_format)

                if newest_date is None or file_date > newest_date:
                    newest_date = file_date
                    newest_file = os.path.join(folder_path, file_name)
            except ValueError:
                # Skip files with invalid date formats
                continue

    return str(newest_file)


def hyphenate_and_wrap(text, width, lang='de'):
    dic = pyphen.Pyphen(lang=lang)

    def split_word(word):
        # Only split words longer than the width
        if len(word) > width:
            # Hyphenate the word using Pyphen
            hyphenated = dic.inserted(word, hyphen='-')
            parts = hyphenated.split('-')

            current_part = ""
            remaining_part = ""

            # Collect segments until the first part is within the width
            for part in parts:
                if len(current_part) + len(part) + 1 <= width:
                    current_part += part
                else:
                    remaining_part += part


            if remaining_part:
                return current_part + '-\n' + remaining_part
            else:
                return word
        else:
            return word

    # Process the text by splitting long words and preserving short ones
    split_text = ' '.join(split_word(word) for word in text.split())

    return split_text.split("\n")