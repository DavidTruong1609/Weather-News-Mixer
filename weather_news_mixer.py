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

# File name and path variables
SQL_db_name = "news_log.db"
HTML_file_name = "news.html"
background_image_file_path = "data/img_files/background_image.gif"
weatherzone_file_path = "data/xml_files/2019-10-14-weatherzone.xml"
courier_mail_file_path = "data/xml_files/2019-10-14-courier-mail.xml"
ABC_file_path = "https://www.abc.net.au/news/weather"
SBS_file_path = "https://www.sbs.com.au/news/tag/subject/weather"

# Regex patterns
title_pattern = "<title>(.*)<\/title>"
weatherzone_description_pattern = "<description>(.*)<\/description>"
weatherzone_date_pattern = "<pubDate>(.*)</pubDate>"
courier_mail_description_pattern = "<description><!\[CDATA\[(.*)<\/description>"
courier_mail_date_pattern = "<lastBuildDate>(.*)</lastBuildDate>"
ABC_pattern = '"title":{"children":"(.*?)"},"mediaIndicator"' 
ABC_date_pattern = '"firstPublished":"(.*?)",' 
ABC_img_pattern = '"imgSrc":"(.*?)",'
ABC_description_pattern = '"synopsis":"(.*?)",'
SBS_pattern = '"title":"(.*?)",'
SBS_img_pattern = '"image":"(.*?)",'

# String variables
title = "Weather News Mixer"
news_sources = ["ABC News", "SBS News", "Weatherzone", "Courier Mail"]
ABC_page_name = " [" + news_sources[0] + " - "
SBS_page_name = " [" + news_sources[1] + "]"
weatherzone_page_name = " [" + news_sources[2] + " - "
courier_mail_page_name = " [" + news_sources[3] + " - "

# HTML strings
HTML_header = """
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Your Weather News Mix</title>
                        <style>
                            body {
                                background-color: #b5ffff;
                                font-family: Arial, sans-serif;
                                margin: 0;
                                padding: 0;
                            }
                            header {
                                text-align: center;
                                padding-top: 20px;
                                padding-bottom: 10px;
                            }
                            img {
                                display: block;
                                margin: 0 auto;
                                max-width: 100%;
                                height: auto;
                            }
                            h1 {
                                color: #007BFF;
                                margin: 0;
                            }
                            h2 {
                                text-align: center;
                                color: #333333;
                            }
                            p.description {
                                text-align: left;
                                margin-left: 15%;
                                margin-right: 15%;
                                line-height: 1.6;
                                color: #555555;
                            }
                            h3.sources {
                                padding-left: 20px;
                            }
                            h3.date {
                                text-align: center;
                                color: #666666;
                                padding-bottom: 20px;
                            }
                            p.sources {
                                text-align: left;
                                color: #777777;
                            }
                            hr.divider {
                                border: 2px solid #0096fa;
                                width: 95%;
                                margin-bottom: 20px;
                            }
                            hr.newsDivider {
                                border: 1px solid #0096fa;
                                width: 75%;
                                margin-top: 20px;
                                margin-bottom: 40px;
                            }
                            p.errorMessage {
                                text-align: center;
                                color: #ff0000;
                            }
                        </style>
                </head>
                <body>
                    <header>
                        <h1>Your Weather News Mix</h1>
                        <br>
                        <hr class="divider">
                    </header>
            """
HTML_footer = """
                <hr class = "divider">
                <h3 class = "sources">Sources</h3>
                <ul>
                    <li>
                        <p class = "sources">ABC Weather News: <a href = "https://www.abc.net.au/news/weather">https://www.abc.net.au/news/weather</a></p>
                    </li>
                    <li>
                        <p class = "sources">SBS Weather News: <a href = "https://www.sbs.com.au/news/tag/subject/weather">https://www.sbs.com.au/news/tag/subject/weather</a></p>
                    </li>
                    <li>
                        <p class = "sources">Weatherzone News: <a href = "https://rss.weatherzone.com.au/?u=12994-1285&news=1">https://rss.weatherzone.com.au/?u=12994-1285&news=1</a></p>
                    </li>
                    <li>
                        <p class = "sources">Courier Mail News: <a href = "https://www.couriermail.com.au/news/queensland/weather/rss">https://www.couriermail.com.au/news/queensland/weather/rss</a></p>
                    </li>
            """

def regex_live_file(file_path, page_pattern, image_pattern):
    """
    Open live news URLs and regex them to filter out titles, publish dates, descriptions and images.

    Args:
        file_path (str): The string URL path to read.
        page_pattern (str): The string pattern to regex search for news titles.
        image_pattern (str): The string pattern to regex search for images.

    Returns:
        tuple or list:
            - If `file_path` is `ABC_file_path`, returns a tuple:
                - list of str: List of string titles matching number of dates.
                - list of str: List of string dates found.
                - list of str: List of images matching number of dates.
                - list of str: List of descriptions matching number of dates.
            - If `file_path` is `SBS_file_path`, returns a list:
                - list of str: List of string titles found excluding the first and last titles.
                - list of str: List of images excluding the last one.
    
    Examples:
        >>> regex_live_file('http://example.com/abc_file', 'some_regex_pattern', 'some_image_pattern')
        (['Title1', 'Title2'], ['Date1', 'Date2'], ['Image1', 'Image2'], ['Description1', 'Description2'])

        >>> regex_live_file('http://example.com/sbs_file', 'some_regex_pattern', 'some_image_pattern')
        (['Title2', 'Title3'], ['Image1', 'Image2'])
    """
    # Open specified file and read contents
    with urlopen(file_path) as response:
        file_contents = response.read().decode("UTF-8")

    # Find titles and images in the file contents using the provided pattern
    titles = findall(page_pattern, file_contents)
    images = findall(image_pattern, file_contents)

    # Extract dates and descriptions only if the file path is for ABC News
    if file_path == ABC_file_path:
        dates = findall(ABC_date_pattern, file_contents)
        descriptions = findall(ABC_description_pattern, file_contents)
        
        # Move the 9th description to the start of the list to align with titles
        index_to_move = 8
        element = descriptions.pop(index_to_move)
        descriptions.insert(0, element)

        # Return titles, dates, images and descriptions for ABC News
        return titles[len(titles) - len(dates):], dates, images[len(images) - len(dates):], descriptions[len(descriptions) - len(dates):]
    
    # Return titles and images for SBS News
    if file_path == SBS_file_path:
        return titles[1:-1], images[:-1]

def regex_archived_file(file_path, title_index, description_index, date_pattern, description_pattern):
    """
    Open archived news XML files and regex them to filter out titles, publish dates and descriptions.

    Args:
        file_path (str): The string path of the file to read.
        title_index (int): The integer index to start regex search at to skip initial title patterns.
        description_index (int): The integer index to start regex search at to skip initial description patterns.
        date_pattern (str): The string pattern to regex search for news publish dates.
        description_pattern (str): The string pattern to regex search for news descriptions.

    Returns:
        tuple:
            - list of str: List of string titles found starting from the specified index.
            - list of str: List of string news publish dates found.
            - list of str: List of string descriptions found starting from the specified index.
    
    Examples:
        >>> regex_archived_file('path/to/archive.xml', 2, 1, r'\\d{4}-\\d{2}-\\d{2}', r'<description>.*?</description>')
        (['Title3', 'Title4'], ['2022-01-01', '2022-01-02'], ['Description2', 'Description3'])
    """
    # Open specified file and read contents
    with open(file_path, encoding = 'UTF-8') as file:
        file_contents = file.read()

    # Find titles, dates and descriptions using regex patterns
    titles = findall(title_pattern, file_contents)
    date = findall(date_pattern, file_contents)
    descriptions = findall(description_pattern, file_contents)

    # Return titles and descriptions starting from specified index as well as all dates found
    return titles[title_index:], date, descriptions[description_index:]

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
            news_preview_text.insert(1.0, '"' + SBS_extract[0][i] + '"' + SBS_page_name + "\n")
    if weatherzone_count > 0:
        for i in range(weatherzone_count):
            news_preview_text.insert(1.0, '"' + weatherzone_extract[0][i] + '"' + weatherzone_page_name + weatherzone_extract[1][0] + "]" + "\n")
    if courier_mail_count > 0:
        for i in range(courier_mail_count):
            news_preview_text.insert(1.0, '"' + courier_mail_extract[0][i] + '"' + courier_mail_page_name + courier_mail_extract[1][0] + "]" + "\n")

    # Disable text widget after editing
    news_preview_text.config(state = DISABLED)

def export_to_HTML():
    """
    Export news articles to an HTML file based on counts from spinboxes.

    This function extracts the counts of articles from various spinboxes, constructs
    an HTML file with the news articles, and writes it to a specified file.

    Side Effects:
        Creates or overwrites an HTML file with the specified name, containing the
        news articles extracted from various sources.

    Examples:
        >>> export_to_HTML()
        # This will create an HTML file with the news articles as specified by the
        # counts from the spinboxes.
    """
    # Extract counts of articles from spinboxes
    ABC_count = int(ABC_news_spinbox.get())
    SBS_count = int(SBS_news_spinbox.get())
    weatherzone_count = int(weatherzone_news_spinbox.get())
    courier_mail_count = int(courier_mail_news_spinbox.get())

    with open(HTML_file_name, "w", encoding="UTF-8") as file:
        # Write the HTML header
        file.write(HTML_header)

        # Write ABC News articles if any
        if ABC_count > 0:
            for i in range(ABC_count):
                file.write(f"""
                        <h2>{ABC_extract[0][i]}</h2>
                        <img src = "{ABC_extract[2][i]}" style = "width: 250px;"></img>
                        <p class = "description">{ABC_extract[3][i]}</p>
                        <h3 class = "date">{ABC_page_name}{ABC_extract[1][i]}]</h3>
                        <hr class = "newsDivider">
                        """)
                
        # Write SBS News articles if any
        if SBS_count > 0:
            for i in range(SBS_count):
                file.write(f"""
                        <h2>{SBS_extract[0][i]}</h2>
                        <img src = "{SBS_extract[1][i]}" style = "width: 250px;"></img>
                        <p class = "errorMessage">No description available for this news website</p>
                        <h3 class = "date">{SBS_page_name}</h3>
                        <hr class = "newsDivider">
                        """)
                
        # Write Weatherzone news articles if any
        if weatherzone_count > 0:
            for i in range(weatherzone_count):
                file.write(f"""
                        <h2>{weatherzone_extract[0][i]}</h2>
                        <p class = "errorMessage">No image available for this news website</p>
                        <p class = "description">{weatherzone_extract[2][i]}</p>
                        <h3 class = "date">{weatherzone_page_name}{weatherzone_extract[1][0]}]</h3>
                        <hr class = "newsDivider">
                        """)
                
        # Write Courier Mail news articles if any
        if courier_mail_count > 0:
            for i in range(courier_mail_count):
                file.write(f"""
                        <h2>{courier_mail_extract[0][i]}</h2>
                        <p class = "errorMessage">No image available for this news website</p>
                        <p class = "description">{courier_mail_extract[2][i]}</p>
                        <h3 class = "date">{courier_mail_page_name}{courier_mail_extract[1][0]}]</h3>
                        <hr class = "newsDivider">
                        """)

        # Write the HTML footer
        file.write(HTML_footer)

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
    SQL_connect = connect(SQL_db_name)

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
                            ''', (SBS_extract[0][i], news_sources[1], "N/A"))
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
ABC_extract = regex_live_file(ABC_file_path, ABC_pattern, ABC_img_pattern)
SBS_extract = regex_live_file(SBS_file_path, SBS_pattern, SBS_img_pattern)
weatherzone_extract = regex_archived_file(weatherzone_file_path, 2, 1, weatherzone_date_pattern, weatherzone_description_pattern)
courier_mail_extract = regex_archived_file(courier_mail_file_path, 1, 0, courier_mail_date_pattern, courier_mail_description_pattern)

# Variables for number of available titles for each news article source
ABC_num_titles = len(regex_live_file(ABC_file_path, ABC_pattern, ABC_img_pattern)[0])
SBS_num_titles = len(regex_live_file(SBS_file_path, SBS_pattern, SBS_img_pattern)[0])
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
export_button = Button(button_frame, text = "Export Selections", bg = widget_colour, activebackground = label_colour, command = export_to_HTML)
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