# Author: Akdeniz Kutay Ocal
# Date: 29.01.2021
# Executable Creation Command:
# pyinstaller ./file_extractor.py --onefile --noconsole --add-binary "./driver/chromedriver.exe;./driver"

import tkinter as tk
from tkinter import filedialog, messagebox
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import os
import glob
import time
import shutil
import sys

username = ""
password = ""
directory_path = "Please select the desired folder location"
download_folder = "Please select the download folder location"
number_of_courses = ""
start_time = None
main_color = "#263D42"
second_color = "#263D35"


def file_extraction():
    global start_time
    chrome_options = Options()
    chrome_options.add_experimental_option('prefs', {
        "plugins.always_open_pdf_externally": True
    }
    )
    # driver = webdriver.Chrome(options=chrome_options)

    # for build
    def resource_path(relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.dirname(__file__)
        return os.path.join(base_path, relative_path)

    driver = webdriver.Chrome(resource_path(
        './driver/chromedriver.exe'), options=chrome_options)
    ###

    moodle_url = 'https://moodle.tedu.edu.tr/'
    driver.get(moodle_url)

    login_btn = driver.find_element_by_xpath(
        '//*[@id="frontpage-banner-content"]/a')
    login_btn.click()

    user_input = driver.find_element_by_xpath('//*[@id="username"]')
    user_input.send_keys(username)

    password_input = driver.find_element_by_xpath('//*[@id="password"]')
    password_input.send_keys(password)

    login_btn = driver.find_element_by_xpath('//*[@id="loginbtn"]')
    login_btn.click()

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    course_names = []
    course_links = list(soup.find_all("a", class_="dropdown-item", href=True))

    for i, element in enumerate(course_links):
        # For test purposes.
        # TODO Get all courses / Give option to choose course
        if i > number_of_courses - 1:
            break
        course_names.append(element['title'])

    directory = os.path.join(directory_path, 'Course Files')
    if not os.path.exists(directory):
        os.mkdir(directory)

    for i in range(number_of_courses):
        path = os.path.join(directory, str(course_names[i]))
        if not os.path.exists(path):
            os.mkdir(path)
            print(f"Directory {course_names[i]} created")

        driver.get(course_links[i]['href'])
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        resources = list(soup.find_all(
            "li", class_="activity resource modtype_resource"))
        for i, element in enumerate(resources):

            href = element.find_all("a")[0]['href']
            driver.get(href)

            time.sleep(2)

            files_path = os.path.join(download_folder, '*')
            files = sorted(
                glob.iglob(files_path), key=os.path.getmtime, reverse=True)
            while files[0].endswith(".crdownload") or files[0].endswith(".tmp"):
                time.sleep(2)
                files = sorted(
                    glob.iglob(files_path), key=os.path.getmtime, reverse=True)

            if start_time is None:
                start_time = os.path.getmtime(files[0])
            if os.path.getmtime(files[0]) < start_time:
                driver.back()
                continue
            try:
                shutil.move(files[0], path)
            except:
                continue
            print(f"File {files[0]} moved.")

    driver.close()
    finished = tk.Tk()
    messagebox.showinfo("Execution Finished", "Your folder is created.")
    finished.destroy()


def choose_folder_path():
    global directory_path
    directory_path = filedialog.askdirectory(
        initialdir="/", title="Select Desired Folder Location")
    for label in folder_label_frame.winfo_children():
        label.destroy()
    new_folder_label = tk.Label(
        folder_label_frame, text=directory_path, bg=second_color, fg="white")
    new_folder_label.pack()


def choose_download_path():
    global download_folder
    download_folder = filedialog.askdirectory(
        initialdir="/", title="Select Download Folder Location")
    for label in download_label_frame.winfo_children():
        label.destroy()
    new_download_label = tk.Label(
        download_label_frame, text=download_folder, bg=second_color, fg="white")
    new_download_label.pack()


def extract_all_files():
    if directory_path == "Please select the desired folder location":
        messagebox.showwarning("Folder path warning",
                               "Please select a folder location")
    if download_folder == "Please select the download folder location":
        messagebox.showwarning(
            "Download Folder path warning", "Please select a download folder location")

    else:
        global username, password, number_of_courses
        username = username_entry.get()
        password = password_entry.get()
        number_of_courses = int(course_entry.get())

        if username == "" or password == "" or number_of_courses == "":
            messagebox.showwarning(
                "Input warning", "Please enter valid information")
        else:
            root.destroy()
            # for element in main_frame.winfo_children():
            #     element.destroy()
            # # threading.Thread(target=file_extraction).start()
            # file_extraction()
            file_extraction()


if __name__ == '__main__':
    root = tk.Tk()
    root.title("Moodle File Extractor")
    canvas = tk.Canvas(root, height=500, width=400, bg=main_color)
    canvas.pack()

    main_frame = tk.Frame(root, bg=second_color)
    main_frame.place(relwidth=0.8, relheight=0.7, relx=0.1, rely=0.05)

    # Folder selection
    folder_frame = tk.Frame(main_frame, bg=second_color)
    folder_frame.place(relwidth=0.8, relheight=0.2, relx=0.1, rely=0.1)

    folder_button = tk.Button(folder_frame, text="Select Folder Location", padx=10, pady=5, fg="white", bg="#263D42",
                              command=choose_folder_path)
    folder_button.pack()

    folder_label_frame = tk.Frame(folder_frame, bg=second_color)
    folder_label_frame.place(relwidth=1, relheight=0.4, relx=0, rely=0.6)
    folder_label = tk.Label(
        folder_label_frame, text=directory_path, bg=second_color, fg="white")
    folder_label.pack()

    # Download folder selection
    download_frame = tk.Frame(main_frame, bg=second_color)
    download_frame.place(relwidth=0.8, relheight=0.2, relx=0.1, rely=0.4)

    download_button = tk.Button(download_frame, text="Select Download Folder", padx=10, pady=5, fg="white",
                                bg="#263D42",
                                command=choose_download_path)
    download_button.pack()

    download_label_frame = tk.Frame(download_frame, bg=second_color)
    download_label_frame.place(relwidth=1, relheight=0.4, relx=0, rely=0.6)
    download_label = tk.Label(
        download_label_frame, text=download_folder, bg=second_color, fg="white")
    download_label.pack()

    info_frame = tk.Frame(main_frame, bg=second_color)
    info_frame.place(relwidth=0.8, relheight=0.2, relx=0.1, rely=0.7)
    tk.Label(info_frame, text="Username",
             bg=second_color, fg="white").grid(row=0)
    tk.Label(info_frame, text="Password",
             bg=second_color, fg="white").grid(row=1)
    tk.Label(info_frame, text="Number of Courses  ",
             bg=second_color, fg="white").grid(row=2)
    username_entry = tk.Entry(info_frame)
    password_entry = tk.Entry(info_frame)
    course_entry = tk.Entry(info_frame)

    username_entry.grid(row=0, column=1)
    password_entry.grid(row=1, column=1)
    course_entry.grid(row=2, column=1)

    # Extract button area
    button_frame = tk.Frame(root, bg=main_color)
    button_frame.place(relwidth=0.8, relheight=0.15, relx=0.1, rely=0.80)

    extract_files = tk.Button(button_frame, text="Extract Files", padx=10, pady=5, fg="white", bg=main_color,
                              command=extract_all_files)
    extract_files.pack()
    footer = tk.Label(
        button_frame, text='Developed by Akdeniz Kutay Ocal', bg=second_color, fg="white")
    placeholder = tk.Label(button_frame, bg=main_color)
    placeholder.pack()
    footer.pack()

    root.mainloop()
