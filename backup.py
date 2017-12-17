import sys
from PyQt4.QtCore import pyqtSlot
from PyQt4.QtGui import *

import requests
import os
from bs4 import BeautifulSoup

url = 'http://israblog.nana10.co.il/blogread.asp?blog={blognum}'
blog = url + '&year={year}&month={month}&pagenum={page}'

def download_all_images_for_page_and_return_new_content(content, blognum, html_path):
    soup = BeautifulSoup(content)
    images = soup.find_all('img')
    counter = 0
    if not os.path.exists(blognum + '/' + html_path):
        os.makedirs(blognum + '/' + html_path)
    for image in images:
        filename = image.get('src')
        try:
            downloaded_image = requests.get(filename)
        except Exception:
            continue
        save_path = blognum + '/' + html_path + '/' + str(counter) + '.jpg'
        link_path = html_path + '/' + str(counter) + '.jpg'
        with open(save_path, 'wb') as f:
            f.write(downloaded_image.content)
        counter += 1
        content = content.replace(bytes(filename, 'utf-8'), bytes(link_path, 'utf-8'))
    return content

def download_blog(blognum):
    site = requests.get(url.format(blognum=blognum))
    if b'noblog.htm' in site.content:
        return 'Blog not exists'
    else:
        if not os.path.exists(str(blognum)):
            os.makedirs(str(blognum))
        with open('{blognum}/main.html'.format(blognum=blognum), 'wb') as f:
            content = download_all_images_for_page_and_return_new_content(site.content, str(blognum), 'main')
            f.write(content)
        if b"var blogYear = '';" in site.content:
            return "Blog is empty"
    for year in range(2002, 2018):
        if bytes(str(year), 'utf-8') not in site.content:
            continue
        for month in range(1, 13):
            for page in range(1, 100):
                temp = blog.format(blognum=blognum, year=year, month=month, page=page)
                paging = requests.get(temp)
                if b'"postedit"' in paging.content:
                    with open('{blognum}/{year}_{month}_{page}.html'.format(blognum=blognum, year=year, month=month, page=page), 'wb') as f:
                        content = download_all_images_for_page_and_return_new_content(paging.content, str(blognum), '{year}_{month}_{page}'.format(year=year, month=month, page=page))
                        f.write(content)
                else:
                    break
    return 'Finished'

# create our window
app = QApplication(sys.argv)
w = QWidget()
w.setWindowTitle('Textbox example @pythonspot.com')

# Create textbox
textbox = QLineEdit(w)
textbox.move(20, 20)
textbox.resize(280, 40)

# Set window size.
w.resize(320, 150)

# Create a button in the window
button = QPushButton('Click me', w)
button.move(20, 80)


# Create the actions
@pyqtSlot()
def on_click():
    value = download_blog(textbox.text())
    textbox.setText(value)


# connect the signals to the slots
button.clicked.connect(on_click)

# Show the window and run the app
w.show()
app.exec_()


