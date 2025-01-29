# Notion Book Summarizer

This project automates the process of summarizing books marked as "Completed" in a Notion database. It uses OpenAI's GPT model to generate structured summaries and stores them in a separate Notion database.

## Features

- **Automatic Book Detection**: Fetches books marked as "Completed" in a Notion database.
- **AI-Powered Summaries**: Uses OpenAI's GPT model to generate detailed summaries.
- **Notion Integration**: Saves summaries as structured notes in a Notion database.
- **Batch Processing**: Runs periodically to check for new completed books.
- **Cloud-Ready**: Can be run continuously on a cloud server using `nohup`.

## Installation

### Prerequisites
- Python 3.8+
- A Notion API key
- An OpenAI API key
- `pip` installed

### Setup

1. Clone this repository:
   ```sh
   git clone https://github.com/sequery/NotionNoteTaker.git
   cd NotionNoteTaker
   ```

2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project directory and add your API keys:
   ```ini
   NotionAPI=your_notion_api_key
   OpenAIAPI=your_openai_api_key
   LibraryID=your_notion_library_database_id
   NotesID=your_notion_notes_database_id
   ```

## Usage

Run the script locally:
```sh
python script.py
```

### Running Continuously on a Cloud Server
For continuous execution on a cloud server, use `nohup`:
```sh
nohup python script.py > output.log 2>&1 &
```
- This allows the script to keep running in the background.
- The output will be logged to `output.log`.
- You can check the running process using:
  ```sh
  ps aux | grep script.py
  ```
- To stop the process, use:
  ```sh
  kill <process_id>
  ```

## Configuration

- Adjust the `time.sleep(3600 * 12)` value in `main()` if you want to change the frequency of book checks.
- Modify `generate_gpt_summary()` to tweak the summary format.

## Contributing

1. Fork the repository.
2. Create a new branch:
   ```sh
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```sh
   git commit -m "Add new feature"
   ```
4. Push to your branch:
   ```sh
   git push origin feature-name
   ```
5. Open a pull request.
<br />
Happy reading! 📚✨
