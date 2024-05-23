from tkinter import *
from re import findall
from urllib.request import urlopen
from sqlite3 import *

# Font variables
title_font = ("Verdana", 24, "bold")
spinbox_font = ("Helvetica", 20)
labelframe_font = ("Verdana", 12, "bold")
label_font = ("Helvetica", 12)
listbox_font = ("Times", 12, "bold")

# Colour variables
title_colour = "#00cdff"
label_colour = "#0096fa"
widget_colour = "#64c8fa"

# File paths
background_image_file_path = "data/img_files/background_image.gif"
weatherzone_file_path = "data/xml_files/2019-10-14-weatherzone.xml"
courier_mail_file_path = "data/xml_files/2019-10-14-courier-mail.xml"
ABC_file_path = "https://www.abc.net.au/news/weather"
SBS_file_path = "https://www.sbs.com.au/news/tag/subject/weather"

# Regex patterns
title_pattern = "<title>(.*)</title>"
weatherzone_date_pattern = "<pubDate>(.*)</pubDate>"
courier_mail_date_pattern = "<lastBuildDate>(.*)</lastBuildDate>"
ABC_pattern = '"title":{"children":"(.*?)"},"mediaIndicator"' 
ABC_date_pattern = '"firstPublished":"(.*?)",' 
SBS_pattern = '"title":"(.*?)",'

# String variables
title = "Weather News Mixer"
news_sources = ["ABC News", "SBS News", "Weatherzone", "Courier Mail"]
ABC_page_name = " [" + news_sources[0] + " - "
SBS_page_name = " [" + news_sources[1] + "]"
weatherzone_page_name = " [" + news_sources[2] + " - "
courier_mail_page_name = " [" + news_sources[3] + " - "

def regex_live_file(file_path, page_pattern):
    """
    Open live news URLs and regex them to filter out titles and publish dates.

    Args:
        file_path (str): The string URL path to read.
        page_pattern (str): The string pattern to regex search for news titles.

    Returns:
        tuple or list:
            - If `file_path` is `ABC_file_path`, returns a tuple:
                - list of str: List of string titles matching number of dates.
                - list of str: List of string dates found.
            - If `file_path` is `SBS_file_path`, returns a list:
                - list of str: List of string titles found excluding the first and last titles.
    
    Examples:
        >>> regex_live_file('http://example.com/abc_file', 'some_regex_pattern')
        (['Title1', 'Title2'], ['Date1', 'Date2'])

        >>> regex_live_file('http://example.com/sbs_file', 'some_regex_pattern')
        ['Title2', 'Title3']
    """
    # Open specified file and read contents
    with urlopen(file_path) as response:
        file_contents = response.read().decode("UTF-8")

    # Find titles in the file contents using the provided pattern
    titles = findall(page_pattern, file_contents)

    # Extract dates only if the file path is for ABC News
    if file_path == ABC_file_path:
        dates = findall(ABC_date_pattern, file_contents)

    # Return titles and dates if the file path is for ABC News
    if file_path == ABC_file_path:
        return titles[len(titles) - len(dates):], dates
    
    # Return titles excluding the first and last if the file path is for SBS News
    if file_path == SBS_file_path:
        return titles[1:-1]

def regex_archived_file(file_path, index, date_pattern):
    """
    Open archived news XML files and regex them to filter out titles and publish dates.

    Args:
        file_path (str): The string path of the file to read.
        index (int): The integer index to start regex search at to skip initial patterns.
        date_pattern (str): The string pattern to regex search for news publish date.

    Returns:
        tuple:
            - list of str: List of string titles found starting from the specified index.
            - list of str: List of string news publish dates found.
    
    Examples:
        >>> regex_archived_file('path/to/archive.txt', 2, r'\\d{4}-\\d{2}-\\d{2}')
        (['Title3', 'Title4'], ['2022-01-01', '2022-01-02'])
    """
    # Open specified file and read contents
    with open(file_path, encoding = 'UTF-8') as file:
        file_contents = file.read()

    # Find titles and dates using regex patterns
    titles = findall(title_pattern, file_contents)
    date = findall(date_pattern, file_contents)

    # Return titles starting from specified index and all dates found
    return titles[index:], date

def preview_selections():
    """
    Previews selected news articles by extracting data from various sources and displaying it in a text widget.

    This method retrieves the number of articles to preview from user input, extracts the articles from different sources
    using specified regex patterns, and inserts the formatted article previews into a text widget. The text widget is updated
    to show the previews and then disabled to prevent further editing.

    Sources:
        - ABC News
        - SBS News
        - Weatherzone
        - Courier Mail

    Examples:
        >>> preview_selections()
        # Updates the text widget with the previews of selected news articles.
    """
    # Extract counts of articles from spinboxes
    ABC_count = int(ABC_news_spinbox.get())
    SBS_count = int(SBS_news_spinbox.get())
    weatherzone_count = int(weatherzone_news_spinbox.get())
    courier_mail_count = int(courier_mail_news_spinbox.get())

    # Enable text widget for editing and clear the text widget
    news_preview_text.config(state = NORMAL)
    news_preview_text.delete(1.0, END)

    # Insert article previews into the text widget based on count retreived from user input spinboxes
    if ABC_count > 0:
        for i in range(ABC_count):
            news_preview_text.insert(1.0, '"' + ABC_extract[0][i] + '"' + ABC_page_name + ABC_extract[1][i] + "]" + "\n")
    if SBS_count > 0:
        for i in range(SBS_count):
            news_preview_text.insert(1.0, '"' + SBS_extract[i] + '"' + SBS_page_name + "\n")
    if weatherzone_count > 0:
        for i in range(weatherzone_count):
            news_preview_text.insert(1.0, '"' + weatherzone_extract[0][i] + '"' + weatherzone_page_name + weatherzone_extract[1][0] + "]" + "\n")
    if courier_mail_count > 0:
        for i in range(courier_mail_count):
            news_preview_text.insert(1.0, '"' + courier_mail_extract[0][i] + '"' + courier_mail_page_name + courier_mail_extract[1][0] + "]" + "\n")

    # Disable text widget after editing
    news_preview_text.config(state = DISABLED)

def save_to_SQL():
    """
    Save selected news articles to an SQLite database.

    This method extracts the number of selected articles from the various news feeds based on user input from 
    spinboxes, connects to an SQLite database (creating it if it doesn't exist), creates a table for storing news 
    articles, clears any existing data in the table, and inserts the selected news articles into the table.

    Example:
        >>> save_to_SQL()
        # Saves the selected news articles to the 'news_log.db' SQLite database.
    """
    # Extract counts of articles from spinboxes
    ABC_count = int(ABC_news_spinbox.get())
    SBS_count = int(SBS_news_spinbox.get())
    weatherzone_count = int(weatherzone_news_spinbox.get())
    courier_mail_count = int(courier_mail_news_spinbox.get())
    
    # Connect to SQLite3 database (create if not exists)
    SQL_connect = connect("news_log.db")

    # Create a cursor object 
    SQL_cursor = SQL_connect.cursor()

    # Create a table
    SQL_cursor.execute('''CREATE TABLE IF NOT EXISTS selected_stories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        headline TEXT NOT NULL,
                        news_feed TEXT NOT NULL,
                        publication_date TEXT NOT NULL
                    )''')
    
    # Clear data in table
    SQL_cursor.execute('''DELETE FROM `selected_stories`''')

    # Insert selected news articles using queries into SQLite database
    if ABC_count > 0:
        for i in range(ABC_count):
            SQL_cursor.execute('''
                                INSERT INTO selected_stories (headline, news_feed, publication_date)
                                VALUES (?, ?, ?)
                            ''', (ABC_extract[0][i], news_sources[0], ABC_extract[1][i]))
    if SBS_count > 0:
        for i in range(SBS_count):
            SQL_cursor.execute('''
                                INSERT INTO selected_stories (headline, news_feed, publication_date)
                                VALUES (?, ?, ?)
                            ''', (SBS_extract[i], news_sources[1], "N/A"))
    if weatherzone_count > 0:
        for i in range(weatherzone_count):
            SQL_cursor.execute('''
                                INSERT INTO selected_stories (headline, news_feed, publication_date)
                                VALUES (?, ?, ?)
                            ''', (weatherzone_extract[0][i], news_sources[2], weatherzone_extract[1][0]))
    if courier_mail_count > 0:
        for i in range(courier_mail_count):
            SQL_cursor.execute('''
                                INSERT INTO selected_stories (headline, news_feed, publication_date)
                                VALUES (?, ?, ?)
                            ''', (courier_mail_extract[0][i], news_sources[3], courier_mail_extract[1][0]))

    # Commit changes
    SQL_connect.commit()

    # Close the connection
    SQL_connect.close()
   
# Extract titles and dates from various article sources
ABC_extract = regex_live_file(ABC_file_path, ABC_pattern)
SBS_extract = regex_live_file(SBS_file_path, SBS_pattern)
weatherzone_extract = regex_archived_file(weatherzone_file_path, 2, weatherzone_date_pattern)
courier_mail_extract = regex_archived_file(courier_mail_file_path, 1, courier_mail_date_pattern)

# Variables for number of available titles for each news article source
ABC_num_titles = len(regex_live_file(ABC_file_path, ABC_pattern)[0])
SBS_num_titles = len(regex_live_file(SBS_file_path, SBS_pattern))
weatherzone_num_titles = 6
courier_mail_num_titles = 10

root = Tk() # Create instance of tkinter class

root.title(title) # Set window title

# Add background image to window
background_image = PhotoImage(file = background_image_file_path)
background_image_label = Label(root, image = background_image)
background_image_label.grid(row = 0, column = 0, rowspan = 3, columnspan = 3)

# Title label widget
title_label = Label(root, text = title, bg = title_colour, font = title_font)
title_label.grid(row = 0, column = 0, columnspan = 3)

## LabelFrame widget to hold all live news widgets
live_news_labelframe = LabelFrame(root, text = "Live Weather News", bg = label_colour, font = labelframe_font, labelanchor = "n")
live_news_labelframe.grid(row = 1, column = 0, padx = 10)

# Widgets for live news
ABC_news_label = Label(live_news_labelframe, text = "ABC News", bg = label_colour, font = label_font)
SBS_news_label = Label(live_news_labelframe, text = "SBS News", bg = label_colour, font = label_font)

ABC_news_spinbox = Spinbox(live_news_labelframe, from_ = 0, to = ABC_num_titles, width = 2, font = spinbox_font, bg = widget_colour)
SBS_news_spinbox = Spinbox(live_news_labelframe, from_ = 0, to = SBS_num_titles, width = 2, font = spinbox_font, bg = widget_colour)

# Grid live news widgets
ABC_news_label.grid(row = 0, column = 0, padx = 10)
SBS_news_label.grid(row = 1, column = 0, padx = 10)

ABC_news_spinbox.grid(row = 0, column = 2, padx = 10, pady = 15)
SBS_news_spinbox.grid(row = 1, column = 2, padx = 10, pady = 15)

# Frame widget to hold all button widgets
button_frame = Frame(root, bg = label_colour)
button_frame.grid(row = 1, column = 1, padx = 10)

# Button widgets
preview_button = Button(button_frame, text = "Preview Selections", bg = widget_colour, activebackground = label_colour, command = preview_selections)
export_button = Button(button_frame, text = "Export Selections", bg = widget_colour, activebackground = label_colour)
save_button = Button(button_frame, text = "Save Selections", bg = widget_colour, activebackground = label_colour, command = save_to_SQL)

# Pack all button widgets
preview_button.pack(padx = 15, pady = 10)
export_button.pack(padx = 15, pady = 10, fill = X)
save_button.pack(padx = 15, pady = 10, fill = X)

# LabelFrame widget to hold all old news widgets
old_news_labelframe = LabelFrame(root, text = "Old Weather News", bg = label_colour, font = labelframe_font, labelanchor = "n")
old_news_labelframe.grid(row = 1, column = 2)

# Widgets for old news
weatherzone_news_label = Label(old_news_labelframe, text = "Weatherzone News", bg = label_colour, font = label_font)
courier_mail_news_label = Label(old_news_labelframe, text = "Courier Mail News", bg = label_colour, font = label_font)

weatherzone_news_spinbox = Spinbox(old_news_labelframe, from_ = 0, to = weatherzone_num_titles, width = 2, font = spinbox_font, bg = widget_colour)
courier_mail_news_spinbox = Spinbox(old_news_labelframe, from_ = 0, to = courier_mail_num_titles, width = 2, font = spinbox_font, bg = widget_colour)

# Grid old news widgets
weatherzone_news_label.grid(row = 0, column = 0, padx = 10)
courier_mail_news_label.grid(row = 1, column = 0, padx = 10)

weatherzone_news_spinbox.grid(row = 0, column = 2, padx = 10, pady = 15)
courier_mail_news_spinbox.grid(row = 1, column = 2, padx = 10, pady = 15)

# Frame widget to hold all widgets involving news previewing
preview_frame = Frame(root)
preview_frame.grid(row = 2, column = 0, columnspan = 3)

# Widgets for news previewing
news_preview_text = Text(preview_frame, width = 80, height = 5, bg = label_colour, font = listbox_font, wrap = WORD, state = DISABLED, spacing1 = 5, spacing3 = 10)
news_preview_scrollbar = Scrollbar(preview_frame, orient = 'vertical')

# Link both news previewing text and scrollbar widgets
news_preview_text.config(yscrollcommand = news_preview_scrollbar.set)
news_preview_scrollbar.config(command = news_preview_text.yview)

# Pack all news previewing widgets
news_preview_text.pack(side = LEFT)
news_preview_scrollbar.pack(side = RIGHT, fill = Y)

# Display Tkinter GUI
root.mainloop()