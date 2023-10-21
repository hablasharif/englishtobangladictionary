import requests
from bs4 import BeautifulSoup
import pandas as pd
import string
import html
import streamlit as st
import os

st.title('Moniword Web App')

# Input for the HTML file path
html_file_path = st.text_input("Enter the file path of your HTML file (e.g., C:/path/to/moniword.html):")

# Load existing data from the provided HTML file, if it exists
existing_df = pd.DataFrame()
existing_words = set()
if html_file_path:
    if os.path.isfile(html_file_path):
        try:
            with open(html_file_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f, 'html.parser')
            # Find the table element by searching for 'table' tags with class names or attributes specific to your HTML
            table = soup.find('table')
            if table:
                existing_df = pd.read_html(str(table))[0]
                existing_words = set(existing_df['Word'])
        except FileNotFoundError:
            st.warning("File not found. Please make sure you provide the correct file path.")
    else:
        st.info("The specified HTML file does not exist. A new HTML file will be created with the results.")

# Get input words from the user and process them
raw_words = st.text_area("Enter one or more words (separated by spaces):")
raw_words = raw_words.replace('\n', ' ')
words = raw_words.split()

ignore_words = set(["i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves", "he", "him", "his",
                     "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves", "what", "which",
                       "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
                         "having", "do", "does", "did", "doing", "will", "would", "should", "can", "could", "may", "might", "must", "ought", "shan", 
                         "shouldn", "won", "wouldn", "couldn", "mightn", "mustn", "aboard", "about", "above", "across", "after", "against", "along", 
                         "amid", "among", "around", "as", "at", "before", "behind", "below", "beneath", "beside", "between", "beyond", "but", "by", 
                         "concerning", "considering", "despite", "for", "from", "in", "inside", "into", "like", "near", 
                         "of", "off", "on", "onto", "out", "outside", "over", "past", "regarding", "round", "since", "through", "throughout", "till",
                           "to", "toward", "under","mine","the",
                     "underneath", "until", "unto", "up", "upon", "with", "within", "without", "shall", "when", "where", "whose", "why", "how", "god"])

words = [w for w in words if len(w) > 2 and w not in ignore_words]
words = list(set([w.lower() for w in words]))
translator = str.maketrans('', '', string.punctuation + string.digits + "।")
words = [w.translate(translator) for w in words]
words = [w for w in words if w not in existing_words]

bengali_meanings = []
for word in words:
    url = f"https://www.english-bangla.com/dictionary/{word}"
    response = requests.get(url)

    if response.status_code == 404:
        bengali_meanings.append(f"Sorry, '{word}' not found in the dictionary.")
    else:
        soup = BeautifulSoup(response.content, 'html.parser')
        span_tag = soup.find('span', class_='format1')

        if span_tag is None:
            bengali_meanings.append(f"Sorry, no Bengali meaning found for '{word}'.")
        else:
            bengali_meanings.append(span_tag.text.strip())

new_df = pd.DataFrame({'Word': words, 'Bengali Meaning': bengali_meanings})
df = pd.concat([existing_df, new_df], ignore_index=True)
df['#'] = df.reset_index().index + 1
styles = """
  <style>
    table {
      border-collapse: collapse;
      width: 100%;
    }
    th, td {
      padding: 8px;
      text-align: left;
      border-bottom: 1px solid #ddd;
    }
    th {
      background-color: #4CAF50;
      color: white;
    }
    tr:nth-child(even) {
      background-color: #f2f2f2;
    }
  </style>
"""
table_html = styles + df.to_html(index=False)

if html_file_path and len(words) > 0:
    try:
        with open(html_file_path, 'w', encoding='utf-8') as file:
            file.write(html.unescape(table_html))
        st.success(f"Updated HTML file: {html_file_path}")
    except FileNotFoundError:
        st.error(f"Error: Could not open the file for writing.")
        st.error(f"Please check if the directory and file path are correct.")
