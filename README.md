# Legal Voice Tutor

I built this tool because my law exams are closed-book and rely heavily on deep recall of cases and facts. I found that just reading my notes over and over wasn't sticking. I needed to actually *speak* the arguments to remember them. I made this for case ratios and facts predominantly.

I made this up to help me revise for my upcoming tort law exam. It basically takes messy notes (Word docs, etc.), parses them into a structured database of cases and principles, and then quizzes me on them. I tend to learn through audio and really benefit from people quizzing me so I thought I would try and build a tool for it. Mainly though this was built because I wanted to play around with the ElevenLabsAPI.

It's all voice-based. It asks me a question (using text-to-speech), I answer it out loud (transcribed via Whisper), and then it uses GPT-4 to grade my answer against my actual notes to tell me what I missed. 

Update 21/11: fixed the bugs in the parser

## How to use it

If you want to try this out with your own law notes, here's exactly what you need to do. (this probably win't work very well without case notes/for other subjects)

### 1. Get the code
Clone this repo or download the folder.

### 2. Install python
You need Python installed. Then just run this in your terminal to get the libraries (Streamlit, OpenAI, ElevenLabs, etc.):
```bash
pip install -r requirements.txt
```

### 3. Set up your API keys
This uses OpenAI for the intelligence/transcription and ElevenLabs for the voice. You'll need your own keys.

1. Look for the file at `.streamlit/secrets.toml.example`.
2. Rename it to just `secrets.toml` (remove the .example bit).
3. Open it and paste your keys in:
   ```toml
   OPENAI_API_KEY = "sk-..."
   ELEVENLABS_API_KEY = "..."
   ```
  

### 4. Add your notes
Make a file called "data" with sub-files labelled "processed" amd "raw" (leave "processed" empty) 
Dump your `.docx` or `.md` files into the `data/raw/` folder. The parser is pretty smart—it just looks for headers and chunks of text, so you don't need to format them perfectly.

### 5. Run it
Type this in your terminal:
```bash
streamlit run app.py
```
if that does not work use
```bash
streamlit run app.py --server.headless true
```
This will skip the "enter your email" prompt that Streamlit shows on the very first run

It'll open in your browser. It should indicate if it does not detect OpenAI or ElevenLabs keys. Click "Process Raw Notes" in the sidebar first to read your files (this will take a while if you upload a lot of notes), then just hit Start Quiz and start talking.

**N.B.** Make sure you have credit on your OpenAI Account for API usage as it will return with 0 cases processed if you do not have any credit and look like the parser has failed. 
Parsing will take ***A LOT*** of time I warn (but once you have done it once for the topic and have a file for processed notes you will not have to do it again).

## For Reviewers

To test this application with your own keys:
1.  Clone the repo.
2.  Add `OPENAI_API_KEY` and `ELEVENLABS_API_KEY` to `.streamlit/secrets.toml`.
3.  Upload any `.docx` or `.md` file containing legal cases to the sidebar (or drop in `data/raw` locally).
