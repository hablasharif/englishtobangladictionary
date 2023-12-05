import streamlit as st
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

def get_bengali_meaning(word):
    url = f"https://www.english-bangla.com/dictionary/{word}"
    response = requests.get(url)

    if response.status_code == 404:
        return f"Sorry, '{word}' not found in the dictionary."
    else:
        soup = BeautifulSoup(response.content, 'html.parser')
        span_tags = soup.find_all('span', class_='format1')
        meanings = [span.text.strip() for span in span_tags]
        return f"Bengali meanings of '{word}': {', '.join(meanings)}"

def main():
    st.title("English to Bengali Dictionary")
    st.write("Enter the words (one per line) and click 'Get Meanings' to translate to Bengali. Enter 'q' to finish.")

    user_input = st.text_area("Enter words here:")

    if st.button("Get Meanings"):
        words = user_input.split()

        bengali_meanings = []

        with st.spinner("Translating..."):
            with tqdm(total=len(words), desc="Processing") as pbar:
                for word in words:
                    bengali_meanings.append(get_bengali_meaning(word))
                    pbar.update(1)

        for meaning in bengali_meanings:
            st.write(meaning)

if __name__ == "__main__":
    main()
