from notion_client import Client
from dotenv import load_dotenv
from openai import OpenAI

import os
import time

# Loading environment variables
load_dotenv()

# Notion API Key
NOTION_API_KEY = os.getenv("NotionAPI")

# Database IDs
LIBRARY_ID = os.getenv("LibraryID")
NOTES_ID = os.getenv("NotesID")

# OpenAI API Key
OPENAI_API_KEY = os.getenv("OpenAIAPI")

# Initialize Notion client and OpenAI client
notion = Client(auth=NOTION_API_KEY)
client = OpenAI(api_key=OPENAI_API_KEY)

def generate_gpt_summary(title):
    """Use OpenAI GPT to generate a summary of the book."""
    prompt = """ You are an expert summarizer designed to extract structured, comprehensive, and concise summaries of complex content. Break down the '{title}' into key points,
                ensuring clarity and detail without adding extra interpretation. Follow this example for the format:
                Title: Title of the Book
                Summary:
                    1. Key Point 1:
                        - Sub-point 1
                        - Sub-point 2
                    2. Key Point 2:
                        - Sub-point 1
                        - Sub-point 2
                        - Sub-point 3
                    And so on...
                    Do not stop until you summarize every key idea in the book.
                    """.format(title=title)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "You are a helpful book summarizer."},
                  {"role": "user", "content": prompt}]
    )

    print(response.choices[0].message.content)
    
    return response.choices[0].message.content


def split_text_into_blocks(text, max_length=2000):
    """Splits text into smaller Notion blocks, each ≤ max_length characters."""
    paragraphs = []
    while len(text) > max_length:
        split_index = text.rfind("\n", 0, max_length)  # Try to split at a newline
        if split_index == -1:  
            split_index = max_length  # If no newline, just split at max_length
        
        paragraphs.append(text[:split_index])
        text = text[split_index:].strip()  # Remove leading/trailing spaces
    
    paragraphs.append(text)  # Add the remaining text
    return paragraphs


def get_completed_books():
    # Query the Library database for completed books
    results = notion.databases.query(
        **{
            "database_id": LIBRARY_ID,
            "filter": {
                "property": "Status",
                "status": {
                    "equals": "Completed"
                }
            }
        }
    )
    return results["results"]

def create_book_note(book):
    """Create a new note for the book in the Book Notes database."""
    # Extract book properties
    title = book["properties"]["Name"]["title"][0]["text"]["content"]  # Adjust if the title property has a different name
    date_completed = (
        book["properties"]["Date"]["date"]["start"]
        if book["properties"]["Date"]["date"]
        else None
    )
    genre_relation = book["properties"]["Genres"]["relation"]  # Relation property
    cover = book.get("cover", None)
    cover_url = cover["external"]["url"] if cover and cover["type"] == "external" else None

    # Generate GPT Summary
    book_summary = generate_gpt_summary(title)

    # Split long summary into multiple Notion blocks
    summary_blocks = split_text_into_blocks(book_summary)

    # Create the note in the Notes database
    notion.pages.create(
        parent={"database_id": NOTES_ID},
        cover={  # Set the cover of the new page
            "type": "external",
            "external": {"url": cover_url or None}
        },
        title=[
            {"type": "text", "text": {"content": title}}
        ],
        properties={
            "Name": {  # Title property
                "title": [{"text": {"content": title}}]
            },
            "Books": {  # Relation to Library database
                "relation": [{"id": book["id"]}]
            },
            "Date Completed": {  # Date property
                "date": {"start": date_completed} if date_completed else None
            },
            "Genre": {  # Relation to Genre database
                "relation": genre_relation  # Pass the linked genres directly
            }
        },
        children=[
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [
                        {"type": "text", "text": {"content": f"Summary of {title}"}}
                    ]
                }
            }
        ] + [
            {  # Create separate paragraph blocks for each split summary part
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": part}}]
                }
            } for part in summary_blocks
        ]
    )

# Set to store processed book IDs to avoid duplicates
processed_books = set()

def main():
    while True:
        print("Checking for new completed books...")
        
        # Get the list of completed books from Notion
        completed_books = get_completed_books()
        
        # Iterate through the books and process only new ones
        for book in completed_books:
            book_id = book["id"]
            if book_id not in processed_books:
                # Create a note for the book
                create_book_note(book)
                print(f"Created note for: {book['properties']['Name']['title'][0]['text']['content']}")
                
                # Add the book ID to the processed set
                processed_books.add(book_id)
        
        # Wait for a specified amount of time before checking again
        time.sleep(3600 * 12)  # Check every 12 hours

if __name__ == "__main__":
    main()