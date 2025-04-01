import os
import re
import argparse
from docx import Document
from transformers import pipeline


def save_docx(file_name, entries):
    
    doc = Document()
    
    for entry in entries:
        
        doc.add_paragraph(entry["speaker"], style="Heading 2")
        doc.add_paragraph(entry["time"], style="Heading 3")
        doc.add_paragraph(entry["speech"], style="Normal")

    doc.save(file_name)


def save_text(file_name, entries, metadata=False):

    with open(file_name, 'w') as file:
        for entry in entries:
            if metadata:
                file.write(entry["speaker"])
                file.write(" ")
                file.write(entry["time"])
                file.write(" ")
            file.write(entry["speech"])
            file.write("\n")


def filler_word_remover(input_text):
    pipe = pipeline(
        "text-generation",
        model="gpt2"
    )
    prompt = f'Remove the filler word from the following transcript:\n {input_text}\n'
    result = pipe(prompt, truncation=True, max_length=256)
    print(result[0].get('generated_text'))
    return result[0].get('generated_text')
   
    
def name_replacement(text, replace, replace_with):
    # print(replace)
    pattern = re.compile(r'\b' + re.escape(replace.split()[0]) + r'(?:\s+' + re.escape(" ".join(replace.split()[0][1:])) + r')?\b', re.IGNORECASE)
    return pattern.sub(replace_with, text)


def process_transcript(file_path):
    
    # Extract PID and Name from the path
    match = re.search(r'(P0\d+)', file_path)
    pid = match.group(1) if match else None
    match = re.search(r'-\s*(.*?).docx$', file_path)
    name = match.group(1) if match else None
        
    # Extract text
    doc = Document(transcript_path)
    
    # Step 1: Remove file's headings and footing
    paragraphs = doc.paragraphs[4:-1]

    transcript = []
    filler_words = []
    for para in paragraphs:
        para_text = para.text.strip()
        
        if not para_text:
            continue  # skip empty paragraphs
        
        # Step 2: Fix spacing issues
        para_text = re.sub(r'\s+', ' ', para_text)
        para_text = re.sub(r'\n\s+', '\n', para_text)
        para_text = re.sub(r'\s+\n', '\n', para_text)
        para_text = re.sub(r'\n+', '\n', para_text)
        
        # Step 3: Extract each line’s components (speaker label, timestamp, and spoken content).
        pattern = r"^(.+?)\s+(\d{1,2}:\d{2})\s+(.*)$"
        match = re.match(pattern, para_text)
        speaker = match.group(1)
        timestamp = match.group(2)
        speech = match.group(3)
        
        # TO-DO: Replace first names in the speeches
        # Step 4: Replaces people's names
        speaker = pid if speaker != "Hoorad Abootalebi" else "Interviewer"

        speech = name_replacement(speech, name, pid)
        
        # Step 5: Timestamp standardization (MM:SS)
        minute, second = timestamp.split(':')
        timestamp = f"{int(minute):02d}:{int(second):02d}"
        
        # TO-DO: Find a filler word remover
        # Step 6: Remove filler words (short snetences of interviewer)
        # if speaker == "Interviewer" and len(speech) < 20:
        #     filler_words.append(speech)
        #     continue
        # speech = filler_word_remover(speech)
        
        
        # Step 7: Remove redundant or duplicated content
        
        
        # Step 8: Fix puctuation
        
        
        # Creat and add a dictioanry to the list
        entry = {
            'speaker': speaker, 
            'time': timestamp, 
            'speech': speech
            }
        
        transcript.append(entry)
    return transcript
        
    
        
        
    # return clean_text
            
    # # Split the transcript into lines and normalize each one
    # lines = raw_text.splitlines()
    # normalized_lines = [normalize_line(line) for line in lines if line.strip()]
    
    # return "\n".join(normalized_lines)
    

def parse_arguments():

    parser = argparse.ArgumentParser(
        description="Process transcript files from a specified directory."
    )
    
    parser.add_argument('--input_dir', type=str, default='./Recordings', help="Directory containing the transcript files (default: ./Recordings)")
    
    
    return parser.parse_args()

# Example usage:
if __name__ == "__main__":
    args = parse_arguments()
    
    # Walk through each folder, subfolder, and file
    for root, dirs, files in os.walk(args.input_dir):
        # TO-DO: root = sorted(root)
        for file in files:
            if file.startswith("Interview_ Social and Cultural Observations on Practices in Cybersecurity Engagement (SCOPE)") and file.endswith(".docx"):
                print(f'Open Transcript: {file}')
                # Extract PID and Name from the path
                match = re.search(r'(P0\d+)', root)
                pid = match.group(1) if match else None
        
                # Create the full transcript path
                transcript_path = os.path.join(root, file)
                clean_transcrib = process_transcript(transcript_path)
                
                save_docx(f'{root}/Interview_Transcript_{pid}.docx', clean_transcrib)
                # save_text(f'{root}/{pid}.txt', clean_transcrib, False)

                # print(clean_transcrib)