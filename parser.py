import os
import json
import re
import glob
from typing import List, Dict, Any
from openai import OpenAI
import docx
from dotenv import load_dotenv

# Load environment variables (if running locally without streamlit)
load_dotenv()

# Try to get API key from env or streamlit secrets (if running in streamlit)
api_key = os.getenv("OPENAI_API_KEY")
try:
    import streamlit as st
    if not api_key and "OPENAI_API_KEY" in st.secrets:
        api_key = st.secrets["OPENAI_API_KEY"]
except ImportError:
    pass

client = OpenAI(api_key=api_key)

RAW_DATA_DIR = "data/raw"
PROCESSED_DATA_FILE = "data/processed/knowledge_base.json"

def read_docx(file_path: str) -> str:
    """Reads text from a .docx file."""
    doc = docx.Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return "\n".join(full_text)

def read_file(file_path: str) -> str:
    """Reads text from a file based on extension."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".docx":
        return read_docx(file_path)
    elif ext in [".md", ".txt"]:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        print(f"Unsupported file type: {ext}")
        return ""

def chunk_text(text: str, chunk_size: int = 2000) -> List[str]:
    """
    Splits text into chunks. 
    Simple implementation: splits by double newlines, then groups.
    Better implementation would use semantic chunking or header-based splitting.
    """
    # Split by headers (Markdown style) or paragraphs
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = ""
    
    for para in paragraphs:
        if len(current_chunk) + len(para) > chunk_size:
            chunks.append(current_chunk)
            current_chunk = para
        else:
            current_chunk += "\n\n" + para if current_chunk else para
            
    if current_chunk:
        chunks.append(current_chunk)
        
    return chunks

def extract_cases_from_chunk(chunk: str) -> List[Dict[str, Any]]:
    """
    Uses OpenAI to extract structured case info from a text chunk.
    """
    if not chunk.strip():
        return []

    prompt = f"""
    You are a legal expert assistant. Your task is to extract legal cases and legal principles from the following notes.
    
    For each case or distinct legal principle found, extract:
    - Name: Case name (e.g., "Donoghue v Stevenson") or Principle name.
    - Facts: Brief summary of material facts.
    - Ratio: The ratio decidendi or key legal principle established.
    - Commentary: Any academic commentary, quotes, or critical analysis mentioned.
    
    Return a JSON object with a key "items" containing a list of these objects.
    If no cases or principles are found, return {{ "items": [] }}.
    
    Input Text:
    {chunk}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful legal extraction assistant. Output valid JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        content = response.choices[0].message.content
        data = json.loads(content)
        return data.get("items", [])
    except Exception as e:
        print(f"Error extracting from chunk: {e}")
        return []

def parse_notes():
    """Main function to parse all notes in raw directory."""
    files = glob.glob(os.path.join(RAW_DATA_DIR, "*"))
    all_items = []
    
    print(f"Found {len(files)} files in {RAW_DATA_DIR}")
    
    for file_path in files:
        if os.path.basename(file_path).startswith("."):
            continue
            
        print(f"Processing {file_path}...")
        text = read_file(file_path)
        if not text:
            continue
            
        chunks = chunk_text(text)
        print(f"Split into {len(chunks)} chunks. Extracting info...")
        
        for i, chunk in enumerate(chunks):
            items = extract_cases_from_chunk(chunk)
            all_items.extend(items)
            print(f"  Chunk {i+1}/{len(chunks)}: Found {len(items)} items")
            
    # Remove duplicates (simple check by name)
    unique_items = {}
    for item in all_items:
        name = item.get("name", "").strip()
        if name and name not in unique_items:
            unique_items[name] = item
            
    final_list = list(unique_items.values())
    
    os.makedirs(os.path.dirname(PROCESSED_DATA_FILE), exist_ok=True)
    with open(PROCESSED_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(final_list, f, indent=2)
        
    print(f"Saved {len(final_list)} extracted items to {PROCESSED_DATA_FILE}")

if __name__ == "__main__":
    # Check for API key
    if not api_key:
        print("Error: OPENAI_API_KEY not found. Please set it in .env or .streamlit/secrets.toml")
    else:
        parse_notes()

