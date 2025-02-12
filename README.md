# YattaTachi-Book-Releases-Compiler

 A Python script that grabs the latest manga/light novel/book releases post from YattaTachi and Compiles them into CSV

## Requirements

- Python 3.12 or higher
- Pandas 2.2.3 or higher
- BeautifulSoup4 4.12.3 or higher

## Usage

Debian/Ubuntu:
Create a virtual environment and install the requirements above using the command below:

```bash
python3 -m venv venv
source venv/bin/activate
pip install pandas
pip install beautifulsoup4
```

Then, you can run the script using the command below:

```bash
python3 yatta_new_novels.py
```

It should create three files within the 'YattaTachi' directory, One contains the latest manga, light novel, and book releases, the other contains the NOOK Edition releases, and the third contains individual chapter releases
