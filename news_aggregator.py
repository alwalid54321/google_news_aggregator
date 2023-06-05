import re
import webbrowser
from tkinter import *
import requests
from bs4 import BeautifulSoup
import openai
from GoogleNews import GoogleNews

openai.api_key = 'your openai api'

class Solution:
    def __init__(self):
        self.dx = [-1, 1, 0, 0]
        self.dy = [0, 0, -1, 1]

    def isValid(self, i, j, r, c):
        return i < r and j < c and i >= 0 and j >= 0

    def changeIslandType(self, i, j, r, c, grid):
        if i >= r or j >= c or i < 0 or j < 0 or grid[i][j] == 0 or grid[i][j] == 2:
            return
        grid[i][j] = 2
        for x in range(4):
            nr = i + self.dx[x]
            nc = j + self.dy[x]
            self.changeIslandType(nr, nc, r, c, grid)

    def shortestBridge(self, grid):
        r = len(grid)
        c = len(grid[0])
        q = []
        change = 0
        check = False

        # Change the islands
        for i in range(r):
            for j in range(c):
                if grid[i][j]:
                    self.changeIslandType(i, j, r, c, grid)
                    check = True
                    break
            if check:
                break

        # Get the new islands in the queue
        for i in range(r):
            for j in range(c):
                if grid[i][j] == 2:
                    q.append((i, j))

        while q:
            change += 1
            sz = len(q)
            while sz > 0:
                node = q.pop(0)
                sz -= 1
                # 4 directions
                for x in range(4):
                    nr = node[0] + self.dx[x]
                    nc = node[1] + self.dy[x]
                    if self.isValid(nr, nc, r, c):
                        if grid[nr][nc] == 0:
                            grid[nr][nc] = 2
                            q.append((nr, nc))
                        if grid[nr][nc] == 1:
                            return change - 1
        return 0


def search_and_display():
    # Get the search input from the input box
    search_query = input_box.get()

    # Create a GoogleNews object and search for news articles
    googlenews = GoogleNews()
    googlenews.search(search_query)

    # Retrieve the search results and summarize each article
    try:
        result = googlenews.result()
    except AttributeError:
        print("No results found")
        return
    summaries = []
    for article in result:
        summary = summarize_article(article['desc'], article['link'])
        summaries.append(summary)

    # Update the text area with the search results and summaries
    text_area.delete('1.0', END)
    text_area.insert(END, f"Search results for '{search_query}':\n\n")
    for i, article in enumerate(result):
        text_area.insert(END, f"Article {i+1}\n")
        text_area.insert(END, f"Title: {article['title']}\n", 'title')
        text_area.insert(END, f"Summary: {summaries[i]}\n", 'content')
        text_area.insert(END, article['link'], ('content', 'hyperlink'))
        text_area.insert(END, "\n\n")
    text_area.tag_configure('hyperlink', foreground='blue', underline=True)
    text_area.tag_bind('hyperlink', '<Button-1>', open_link)


def summarize_article(article, url):
    response = requests.get(url)
    text = ""

    try:
        soup = BeautifulSoup(response.content, "html.parser")
        text = soup.get_text()
        text = text[:1000]
    except:
        pass

    if not text:
        try:
            text = response.json()
            text = str(text)[:1000]
        except:
            pass

    if not text:
        try:
            text = response.content
            text = str(text)[:1000]
        except:
            pass

    model_engine = "text-davinci-003"
    prompt_text = prompt_input.get("1.0", "end-1c")
    prompt = f"{prompt_text}\n{article}\n\nHere is some additional scraped data for context. Ignore anything spurious such as HTML tags or social share/subscribe calls to action that doesn’t relate to {article}:\n{text}"

    response = openai.Completion.create(engine=model_engine, prompt=prompt, temperature=0.2, max_tokens=1500, n=1, stop=None)
    summary = response.choices[0].text

    return re.sub('\s+', ' ', summary).strip()


def open_link(event):
    text_widget = event.widget
    index = text_widget.index(f"@{event.x},{event.y}")
    tag_names = text_widget.tag_names(index)

    if 'hyperlink' in tag_names:
        line_start = text_widget.index(f"{index} linestart")
        line_end = text_widget.index(f"{index} lineend")
        line_text = text_widget.get(line_start, line_end)
        url_match = re.search("(?P<url>https?://[^\s]+)", line_text)
        if url_match:
            url = url_match.group("url")
            webbrowser.open_new(url)


# Create a GoogleNews object
googlenews = GoogleNews()

# Create the Tkinter application and set the title
root = Tk()
root.title("Google News Aggregator")
root.configure(background='#F5F5F5')

# Create the input box label
input_label = Label(root, text="Enter search query:")
input_label.pack(padx=10, pady=10)

# Create the input box
input_box = Entry(root, width=50)
input_box.pack(padx=10, pady=10)

# Create the prompt label
prompt_label = Label(root, text="Enter prompt data:")
prompt_label.pack(padx=10, pady=10)

# Create the prompt input box
prompt_input = Text(root, height=5, width=50)
prompt_input.pack(padx=10, pady=10)

# Create the search button
search_button = Button(root, text="Search", command=search_and_display)
search_button.pack(padx=10, pady=10)

# Create the text area
text_area = Text(root, height=30, width=200, bg='#FFFFFF', fg='black')
scrollbar = Scrollbar(root)
scrollbar.pack(side=RIGHT, fill=Y)
text_area.pack(side=LEFT, fill=Y)
scrollbar.config(command=text_area.yview)
text_area.config(yscrollcommand=scrollbar.set)
text_area.insert(END, "Google News Aggregator\n\n")
text_area.tag_configure('title', background='lightblue', font=('Arial', 14, 'bold'))
text_area.tag_configure('content', background='yellow', font=('Arial', 12))
text_area.tag_configure('hyperlink', foreground='blue', underline=True)
text_area.tag_bind('hyperlink', '<Button-1>', open_link)

# Set the tag configuration for hyperlink text
text_area.tag_configure('hyperlink', foreground='blue', underline=True)
# Bind the hyperlink tag to open the link in a web browser
text_area.tag_bind('hyperlink', '<Button-1>', open_link)

# Start the main loop
root.mainloop()
