# manual_bible_entry.py

import pandas as pd
import os

def get_input(prompt, last_value=None):
    """Helper to get user input, allowing defaults and a 'quit' command."""
    if last_value:
        prompt += f" [{last_value}]: "
    else:
        prompt += ": "

    value = input(prompt)
    if value.lower() == 'quit':
        return None
    if not value and last_value:
        return last_value
    return value

def main():
    """Main function to run the interactive data entry CLI."""

    file_path = 'data/raw/bible_pairs.csv'

    # Load existing data or create a new DataFrame
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
    else:
        df = pd.DataFrame(columns=['book', 'chapter', 'verse_num', 'sa_text', 'lesotho_text', 'notes'])

    last_book = None
    last_chapter = None

    print("--- Manual Bible Verse Entry ---")
    print("Type 'quit' at any prompt to exit.")

    while True:
        book = get_input("Book", last_book)
        if book is None: break

        while True:
            try:
                chapter_str = get_input("Chapter", last_chapter)
                if chapter_str is None: return
                chapter = int(chapter_str)
                break
            except ValueError:
                print("Invalid input. Please enter a number for the chapter.")

        while True:
            try:
                verse_num_str = get_input("Verse Number")
                if verse_num_str is None: return
                verse_num = int(verse_num_str)
                break
            except ValueError:
                print("Invalid input. Please enter a number for the verse.")

        sa_text = get_input("SA Text")
        if sa_text is None: break

        lesotho_text = get_input("Lesotho Text")
        if lesotho_text is None: break

        notes = get_input("Notes (optional)")
        if notes is None: break

        # Append new data and save
        new_entry = pd.DataFrame([{
            'book': book,
            'chapter': chapter,
            'verse_num': verse_num,
            'sa_text': sa_text,
            'lesotho_text': lesotho_text,
            'notes': notes
        }])
        df = pd.concat([df, new_entry], ignore_index=True)
        df.to_csv(file_path, index=False)

        print(f"--- Saved entry: {book} {chapter}:{verse_num} ---")

        # Remember last book and chapter for next entry
        last_book = book
        last_chapter = str(chapter)

    print("\nExiting data entry tool.")

if __name__ == '__main__':
    main()
