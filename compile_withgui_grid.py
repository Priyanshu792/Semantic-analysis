import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import string
from collections import Counter
import matplotlib.pyplot as plt
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import customtkinter
from nltk.corpus import stopwords
import speech_recognition as sr

def analyze_text(text):
    lower_case = text.lower()
    cleaned_text = lower_case.translate(str.maketrans('', '', string.punctuation))
    tokenized_words = cleaned_text.split()

    stop_words = set(stopwords.words('english'))

    final_words = []
    for word in tokenized_words:
        if word not in stop_words:
            final_words.append(word)

    emotion_list = []
    positive_keywords = []  # To store positive keywords
    negative_keywords = []  # To store negative keywords

    with open('emotions.txt', 'r') as file:
        for line in file:
            clear_line = line.replace("\n", '').replace(",", '').replace("'", '').strip()
            word, emotion = clear_line.split(':')
            if word in final_words:
                emotion_list.append(emotion)
                if emotion == 'happy':
                    positive_keywords.append(word)
                elif emotion == 'sad':
                    negative_keywords.append(word)

    global w
    w = Counter(emotion_list)

    print(positive_keywords)
    print(negative_keywords)

    # Display the keywords with colors
    if positive_keywords:
        positive_keywords_label.config(text="Positive Keywords: " + ', '.join(positive_keywords), foreground='green')
    else:
        positive_keywords_label.config(text="Positive Keywords: None", foreground='green')
    
    if negative_keywords:
        negative_keywords_label.config(text="Negative Keywords: " + ', '.join(negative_keywords), foreground='red')
    else:
        negative_keywords_label.config(text="Negative Keywords: None", foreground='red')

    result_label.config(text=f"Polarity_Score : {SentimentIntensityAnalyzer().polarity_scores(cleaned_text)}")
    sentiment_analyse(cleaned_text)

def show_graph():
    fig, ax1 = plt.subplots()
    ax1.bar(w.keys(), w.values())
    fig.autofmt_xdate()
    plt.show()

def sentiment_analyse(sentiment_text):
    score = SentimentIntensityAnalyzer().polarity_scores(sentiment_text)
    if score['neg'] > score['pos']:
        sentiment_label.config(text="Negative Sentiment")
    elif score['neu'] > 0.5:
        sentiment_label.config(text="Neutral Sentiment")
    elif score['neg'] < score['pos']:
        sentiment_label.config(text="Positive Sentiment")
    else:
        sentiment_label.config(text="Neutral Sentiment")

def listen_and_analyze():
    text_entry.delete('1.0', tk.END)
    r = sr.Recognizer()
    with sr.Microphone() as source:
        result_label.config(text="Listening...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
        result_label.config(text="Processing...")

    try:
        recognized_text = r.recognize_google(audio)
        text_entry.insert("end-1c", recognized_text)
        result_label.config(text="Audio Input Successfully Transcribed")
        analyze_text(recognized_text)
    except sr.UnknownValueError:
        result_label.config(text="Sorry, I could not understand the audio.")
    except sr.RequestError:
        result_label.config(text="Sorry, there was an error with the audio request.")

def open_file_dialog():
    file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav *.mp3 *.ogg")])
    if file_path:
        with open(file_path, 'rb') as file:
            audio_data = file.read()

        r = sr.Recognizer()
        with sr.AudioFile(file_path) as source:
            result_label.config(text="Processing...")
            audio = r.record(source)

        try:
            recognized_text = r.recognize_google(audio)
            text_entry.delete('1.0', tk.END)
            text_entry.insert("end-1c", recognized_text)
            result_label.config(text="Audio Input Successfully Transcribed")
            analyze_text(recognized_text)
        except sr.UnknownValueError:
            result_label.config(text="Sorry, I could not understand the audio.")
        except sr.RequestError:
            result_label.config(text="Sorry, there was an error with the audio request.")

gui = tk.Tk()
gui.title("Sentiment Analysis")

text_frame = ttk.Frame(gui)
text_frame.grid(row=0, column=0, sticky="nsew")
text_frame.grid_rowconfigure(1, weight=1)
text_frame.grid_columnconfigure(0, weight=1)

text_label = ttk.Label(text_frame, text="Enter text to analyze:")
text_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

text_entry = tk.Text(text_frame, wrap="word", width=40, height=10)
text_entry.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

text_scroll = ttk.Scrollbar(text_frame, command=text_entry.yview)
text_scroll.grid(row=1, column=1, sticky='nsew')
text_entry['yscrollcommand'] = text_scroll.set

voice_input_button = ttk.Button(text_frame, text="Voice Input", command=listen_and_analyze)
voice_input_button.grid(row=2, column=0, padx=10, pady=10, sticky="w")

file_input_button = ttk.Button(text_frame, text="Select Audio File", command=open_file_dialog)
file_input_button.grid(row=2, column=0, padx=10, pady=10, sticky="e")

analyze_button = ttk.Button(text_frame, text="Analyze", command=lambda: analyze_text(text_entry.get("1.0", "end-1c")))
analyze_button.grid(row=3, column=0, padx=10, pady=10, sticky="w")

result_frame = ttk.Frame(gui)
result_frame.grid(row=1, column=0, sticky="nsew")
result_frame.grid_rowconfigure(1, weight=1)
result_frame.grid_columnconfigure(0, weight=1)

result_label = ttk.Label(result_frame, text="")
result_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

sentiment_label = ttk.Label(result_frame, text="")
sentiment_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")

graph_button = ttk.Button(result_frame, text="Show Emotion Graph", command=show_graph)
graph_button.grid(row=2, column=0, padx=10, pady=10, sticky="w")

keywords_label = ttk.Label(gui, text="Keywords: ")  # Moved keywords_label out of result_frame
keywords_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")

# Create labels to display positive and negative keywords
positive_keywords_label = ttk.Label(gui, text="", font=("Helvetica", 12))
positive_keywords_label.grid(row=3, column=0, padx=10, pady=10, sticky="w")

negative_keywords_label = ttk.Label(gui, text="", font=("Helvetica", 12))
negative_keywords_label.grid(row=4, column=0, padx=10, pady=10, sticky="w")

gui.grid_rowconfigure(0, weight=1)
gui.columnconfigure(0, weight=1)
gui.geometry("500x600")
gui.mainloop()
