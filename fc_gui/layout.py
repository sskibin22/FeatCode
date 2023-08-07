#FeatCode GUI :: layout
#author: Scott Skibin

# Import libraries
from datetime import datetime as dt
import sys
import os
import webbrowser as wb
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'fc_code')))
from functools import partial
from PIL import Image
from featcode import *
from settings import *
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from tkinter import messagebox as mb
from tkhtmlview import HTMLLabel

#TODOs:
# center windows on creation

# Root FeatCode GUI object that inherits customtkinter's CTk object
# This is the will be instantiated in app.py to run the application 
class FCGUI(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color=DEFAULT_BG_COLOR)
        # Main window settings
        self.main_win = True
        self.title(MAIN_TITLE)
        self.geometry(f'{DEFAULT_WIDTH}x{DEFAULT_HEIGHT}')
        self.minsize(MIN_WIDTH, MIN_HEIGHT)

        # Grid layout settings
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0)
        self.rowconfigure(1, weight=1)

        # Initialize FeatCode object for backend API
        self.fc = FeatCode()

        # open FeatCode database connection
        self.fc.open_db_connection()

        # Main frames
        self.header_frame = Header(self, 1)
        self.table_frame = TFrame(self)

        # run FCGUI
        self.mainloop()

        # close FeatCode database connection
        self.fc.close_db_connection()

# This is the header object that will always be at the top of all windows
# The root window will only contain a 'randomize' button in the header
# The problem window will contain a 'randomize' button, a Stopwatch frame, and a 'save time' button
class Header(ctk.CTkFrame):
    def __init__(self, parent : ctk.CTk, c_span : int):
        super().__init__(parent, 
                         fg_color=DEFAULT_FG_COLOR,
                         border_width=1,
                         border_color='white', 
                         corner_radius=0, 
                         height=HEADER_HEIGHT)
        self.parent = parent
        self.stopwatch = None
        # Place Header in grid layout of parent widget
        self.grid(row=0, 
                  column=0, 
                  columnspan=c_span,
                  sticky='nsew')
        
        # Create widgets according to what window is the parent of this Header object
        self.create_rand_button()
        if not self.parent.main_win:
            self.create_save_time_button()
            self.stopwatch = self.create_stopwatch()

    # Create FCButton object for the 'randomize' button
    # The button placement and functionality depends on the parent window
    def create_rand_button(self):
        func = None
        s = None
        if self.parent.main_win:
            func  = self.create_problem_window
        else:
            func = self.repop_problem_window
            s = 'left'
        rand_button = FCButton(self, 'Randomize', 68, FC_BUTTON_WIDTH, func)
        rand_button.pack(side=s, pady=4, padx=4)

    # Create FCButton object for the 'save time' button and place it in parent layout
    def create_save_time_button(self):
        save_time_button = FCButton(self, 'Save\nTime', 68, FC_BUTTON_WIDTH, self.save_time)
        save_time_button.pack(side='right', pady=4, padx=4)
    
    # Create Stopwatch object, place it in parent layout and then return the object
    def create_stopwatch(self):
        stopwatch = Stopwatch(self)
        stopwatch.pack(side='right', pady=4)
        return stopwatch
    
    # Create a ProblemWindow object
    # ProblemWindow inherts the CTkToplevel class from customtkinter and will spawn a new window
    # This method is called whenever the 'randomize' button is pressed within the root window
    def create_problem_window(self):
         prob = self.parent.fc.get_random_problem()
         ProblemWindow(prob, self.parent.fc)
    
    # Repopulate the parent ProblemWindow with a newly selected random problem's data
    # This method is called whenever the 'randomize' button is pressed within the problem window
    def repop_problem_window(self):
        prob = self.parent.fc.get_random_problem()
        self.parent.problem_data = prob
        self.parent.repopulate_window()
    
    # Save the current time of the Stopwatch object to the problems database
    # This method is called whenever the 'save time' button is pressed within the problem window
    def save_time(self):
        if mb.askyesno(title='Save Time', message='Are you sure you want to overwrite your last saved time?'):
            time = self.stopwatch.curr_time
            self.parent.fc.save_time(time, self.parent.problem_data[0])

# A custom button object to keep button designs consistent throught application
# FCButton inherits from customtkinter's CTkButton class
class FCButton(ctk.CTkButton):
    def __init__(self, parent : ctk.CTkFrame, name : str, h : int, w : int, cmd):
        super().__init__(parent,
                         text=name,
                         text_color=TABLE_TEXT_COLOR,
                         font=FC_BUTTON_FONT,
                         height=h,
                         width=w, 
                         fg_color=DEFAULT_BG_COLOR,
                         border_color='white',
                         hover_color=TABLE_SELECTED_COLOR,
                         border_width=1, 
                         command=cmd)
        
# API/UI for a simple stopwatch with start, pause, and reset features
# The Stopwatch object inherits from the customtkinter CTkFrame 
class Stopwatch(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=DEFAULT_BG_COLOR, border_color='white', border_width=1)
        self.update_time = ''
        self.curr_time = '00:00:00'
        self.running = False
        self.hours = 0
        self.minutes = 0
        self.seconds = 0

        # Configure grid
        self.columnconfigure(index=0, weight=1)
        self.columnconfigure(index=1, weight=1)
        self.columnconfigure(index=2, weight=1)
        self.rowconfigure(index=0, weight=4)
        self.rowconfigure(index=1, weight=1)

        # Create time display label
        self.display_label = ctk.CTkLabel(self, text='00:00:00', font=('Times', 30, 'bold'), bg_color=SWITCH_ENABLED_COLOR, height=30)
        self.display_label.grid(row=0, column=0, columnspan=3, sticky='nsew', padx=5, pady=(5, 0))

        # Create start button 
        self.start_button = ctk.CTkButton(self, text="Start", command=self.start, font=('Courier New', 11, 'bold'), fg_color=DEFAULT_FG_COLOR, width=45, height=20)
        self.start_button.grid(row=1, column=0, sticky='ns', padx=4, pady=4)

        # Create pause button
        self.pause_button = ctk.CTkButton(self, text="Pause", command=self.pause, font=('Courier New', 11, 'bold'), fg_color=DEFAULT_FG_COLOR, width=45, height=20)
        self.pause_button.grid(row=1, column=1, sticky='ns', pady=4)

        # Create reset button
        self.reset_button = ctk.CTkButton(self, text="Reset", command=self.reset, font=('Courier New', 11, 'bold'), fg_color=TABLE_SELECTED_COLOR, width=45, height=20)
        self.reset_button.grid(row=1, column=2, sticky='ns', padx=4, pady=4)

    # Updates the time display label after 1000 ms (1s) if running is True
    def start(self):
        if not self.running:
            self.display_label.after(1000)
            self.update()
            self.running = True

    # Stop updating the time if running is True
    def pause(self):
        if self.running:
            self.display_label.after_cancel(self.update_time)
            self.running = False

    # Clear time back to '00:00:00' and stop updating
    def reset(self):
        if self.running:
            self.display_label.after_cancel(self.update_time)
            self.running = False
        self.hours, self.minutes, self.seconds = 0, 0, 0
        self.curr_time = '00:00:00'
        self.display_label.configure(text=self.curr_time)

    # Update the time by incrementing seconds, minutes, and hours variables accordingly
    # Then build the current time string in 'HH:MM:SS' format and update the time display label
    def update(self):
        self.seconds += 1
        if self.seconds == 60:
            self.minutes += 1
            self.seconds = 0
        if self.minutes == 60:
            self.hours += 1
            self.minutes = 0
        hours_string = f'{self.hours}' if self.hours > 9 else f'0{self.hours}'
        minutes_string = f'{self.minutes}' if self.minutes > 9 else f'0{self.minutes}'
        seconds_string = f'{self.seconds}' if self.seconds > 9 else f'0{self.seconds}'
        self.curr_time = hours_string + ':' + minutes_string + ':' + seconds_string
        self.display_label.configure(text=self.curr_time)
        self.update_time = self.display_label.after(1000, self.update)

# Custom Treeview object with column sorting functionality
# FCTreeview inherits from tkinter's ttk.Treeview class and overrides it's heading method 
# to allow for sorting whenever a column heading pressed
class FCTreeview(ttk.Treeview):
    def __init__(self, parent : ctk.CTkFrame):
        super().__init__(parent, columns=COL_NAMES, show='headings', padding = TV_INNER_PAD)
        self.parent = parent
        self.tag_configure('oddrow', background=DEFAULT_BG_COLOR)
        self.tag_configure('evenrow', background=DEFAULT_FG_COLOR)
        self.row_idx = 0
        self.bind('<Double-Button-1>', self.create_problem_window)

    # Override heading method to include sort_by argument
    def heading(self, column, sort_by=None, **kwargs):
        if sort_by and not hasattr(kwargs, 'command'):
            func = getattr(self, f"_sort_by_{sort_by}", None)
            if func:
                kwargs['command'] = partial(func, column, False)
        return super().heading(column, **kwargs)

    # Sort FCTreeview items based on sorting method of heading that was clicked
    def _sort(self, column, reverse, data_type, callback):
        l = [(self.set(k, column), k) for k in self.get_children('')]
        l.sort(key=lambda t: data_type(t[0]), reverse=reverse)
        for index, (_, k) in enumerate(l):
            t = ('oddrow',)
            if index % 2 == 0:
                t = ('evenrow',)
            self.item(k, tags=t)
            self.move(k, '', index)

        self.heading(column, command=partial(callback, column, not reverse))

    # Sort numerically
    def _sort_by_num(self, column, reverse):
        self._sort(column, reverse, int, self._sort_by_num)

     # Sort alphabetically
    def _sort_by_name(self, column, reverse):
        self._sort(column, reverse, str, self._sort_by_name)

     # Sort by time
    def _sort_by_time(self, column, reverse):
        def _str_to_datetime(string):
            return dt.strptime(string, "%H:%M:%S")
        self._sort(column, reverse, _str_to_datetime, self._sort_by_time)

    # Create a new ProblemWindow object
    # This method is called whenever the 'double-click' event occurs on a focused item in the FCTreeview
    # Problem data corresponding to the focused item will populate the new problem window
    def create_problem_window(self, event):
         focused = self.focus()
         if focused:
            selected = self.item(focused)
            prob = self.parent.parent.fc.get_problem_by_title(selected['values'][0])
            ProblemWindow(prob, self.parent.parent.fc)    

# Table frame that will contain the layout and widgets for the table in the root window
# TFrame object inherits from customtkinter's CTkFrame class
class TFrame(ctk.CTkFrame):
    def __init__(self, parent : ctk.CTk):
        super().__init__(parent, fg_color=DEFAULT_BG_COLOR)
        self.parent = parent
        self.entry_str = tk.StringVar()
        # Place in grid layout of parent window
        self.grid(row=1, 
                  column=0, 
                  sticky='nsew', 
                  padx=TFRAME_PAD_X, 
                  pady=TFRAME_PAD_Y)
        
        # Configure grid layout
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1)
        self.rowconfigure(0)
        self.rowconfigure(1, weight=1)

        # Create table header and table displays
        self.create_table_header()
        self.table = self.create_table()
        self.fill_table()

    # Creates a table header frame that contains:
    #   - 'refresh' button 
    #   - 'URL' entry widget
    #   - 'add problem' button 
    #   - 'remove problem' button
    # All of these widgets interact directly with the FCTreeview class and the featcode backend API
    def create_table_header(self):
        # Table header frame
        frame = ctk.CTkFrame(self, 
                             fg_color=DEFAULT_FG_COLOR, 
                             border_color='white', 
                             border_width=1)
        # Place the header in the grid layout of it's parent
        frame.grid(row=0, 
                   column=0,
                   columnspan=2,
                   sticky='nsew', 
                   pady = 4)
        
        # Create refresh button and place in frame
        refresh_img = ctk.CTkImage(light_image=Image.open('fc_gui/assets/refresh_30.png'), size=(30, 30))

        refresh_button = ctk.CTkButton(frame, text='', image=refresh_img, command=self.refresh_table, width=30, fg_color=DEFAULT_FG_COLOR, hover_color=TABLE_SELECTED_COLOR)
        refresh_button.pack(side='left', pady=T_ENTRY_PAD_Y, padx=(8, 0))

        # Create URL input entry and place in frame
        entry = ctk.CTkEntry(frame, 
                             height=T_ENTRY_HEIGHT, 
                             width=T_ENTRY_WIDTH, 
                             fg_color=DEFAULT_BG_COLOR, 
                             border_width=0,
                             textvariable=self.entry_str)
        entry.pack(side = 'left', padx=T_ENTRY_PAD_X, pady=T_ENTRY_PAD_Y)

        # Create 'add problem' button and place in frame
        add_button = FCButton(frame, 'Add Problem', T_ENTRY_HEIGHT, FC_BUTTON_WIDTH, lambda:self.add_problem(self.entry_str))
        add_button.pack(side='left', pady=T_ENTRY_PAD_Y)

        # Create 'remove problem' button and place in frame
        remove_button = FCButton(frame, 'Remove Problem', T_ENTRY_HEIGHT, FC_BUTTON_WIDTH, self.remove_problem)
        remove_button.pack(side='right', padx=T_ENTRY_PAD_X, pady=T_ENTRY_PAD_Y)

    # Creates a table using the FCTreeview class and then returns it
    def create_table(self):
        # Configure style of FCTreeview
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('Treeview', 
                        background=DEFAULT_FG_COLOR, 
                        foreground=TABLE_TEXT_COLOR, 
                        fieldbackground=DEFAULT_FG_COLOR,
                        rowheight=TABLE_ROW_HEIGHT,
                        font = TABLE_FONT),
        style.configure('Treeview.Heading', 
                        background=DEFAULT_BG_COLOR, 
                        font = TABLE_FONT_BOLD,
                        rowheight=TABLE_ROW_HEIGHT)
        style.map('Treeview', 
                  background=[('selected', TABLE_SELECTED_COLOR)], 
                  foreground=[('selected', TABLE_TEXT_COLOR)])

        # Instantiate FCTreeview object as 'table'
        table = FCTreeview(self)

        # Initialize headings for every column
        table.heading('problem', text='Problem', anchor='w', sort_by='name')
        table.heading('time', text='Time', anchor='w', sort_by='time')
        table.heading('seen', text='Seen', anchor='w', sort_by='num')
        
        # Initialize columns
        table.column('problem', minwidth=MIN_WIDTH)
        table.column('time', stretch=tk.NO, minwidth=100, width=150)
        table.column('seen', stretch=tk.NO, minwidth=100, width=100)

        # Place table in parent frame
        table.grid(row=1, column=0, sticky='nsew')

        # Scrollbar configuration
        scrollbar = ctk.CTkScrollbar(self,
                                orientation="vertical",
                                command=table.yview,
                                button_color=DEFAULT_FG_COLOR)
        scrollbar.grid(row=1, column=1, sticky='nsew')
        table.configure(yscrollcommand = scrollbar.set)

        return table
    
    # This method is called whenever the 'add problem' button is pressed in the table header
    # The string variable associated with the 'URL' entry is grabbed and passed into the featcode.add_problem method (more on this in featcode.py)
    # If the URL passed is valid then a new problem is added to the problems database and the FCTreeview table
    def add_problem(self, url : str):
        errcode, title = self.parent.fc.add_problem(url.get())
        if errcode == 0:
            mb.showerror(title='Error', message='Problem already exists.')

        elif errcode == -1:
            mb.showerror(title='Error', message='Invalid URL.')
        else:
            t = ('oddrow',)
            if (self.table.row_idx + 1) % 2 == 0:
                t = ('evenrow',)
            self.table.insert(parent = '', index=tk.END, values = (title, '00:00:00', 0), tags=t)
            self.table.row_idx += 1
            mb.showinfo(title='Problem Added', message=f'Succesfully added [{title}] to table.')
            self.entry_str.set('')
    
    # This method is called whenever the 'remove problem' button is pressed in the table header
    # This method removes a selected item from the FCTreeview table and problems database
    def remove_problem(self):
        focused = self.table.focus()
        if focused:
            answer = mb.askyesno(title='Removal Prompt', message='Are you sure you want to remove the selected problem?')
            if answer:
                sel_idx = self.table.index(focused)
                selected = self.table.item(focused)
                errcode = self.parent.fc.remove_problem(selected['values'][0])
                if errcode == 0:
                    mb.showerror(title='Error', message='Problems table is empty.')
                if errcode == -1:
                    mb.showerror(title='Error', message='Selected problem does not exist in database.')
                else:
                    self.table.delete(focused)
                    self.table.row_idx -= 1
                    i = 1
                    if sel_idx % 2 == 0:
                        i = 0
                    for iid in self.table.get_children('')[sel_idx:]:
                        t = ('oddrow',)
                        if i % 2 == 0:
                            t = ('evenrow',)
                        self.table.item(iid, tags = t)
                        i += 1
                    mb.showinfo(title='Problem Removed', message=f"Succesfully removed [{selected['values'][0]}] from table.")
        else:
            mb.showerror(title='Error', message='No problem selected.')

    # This method deletes all items from the FCTreeview table
    def clear_table(self):
        for iid in self.table.get_children(''):
            self.table.delete(iid)
    
    # This method fills the FCTreeview with data from the problems database
    def fill_table(self):
        for i, row in enumerate(self.parent.fc.get_table()):
            t = ('oddrow',)
            if i % 2 == 0:
                t = ('evenrow',)
            
            time = row[6]
            if not time:
                time = '00:00:00'
            self.table.insert(parent = '', index=tk.END, values = (row[1], time, row[4]), tags=t)
            self.table.row_idx = i

    # This method is called whenever the 'refresh' button is pressed in the table header
    # Both clear_table() and fill_table() methods are called in order to 'refresh' the displayed table
    def refresh_table(self):
        self.clear_table()
        self.fill_table()

# The ProblemWindow class inherits from customtkinter's CTkToplevel class
# This is the 'problem window' that displays a selected problems description 
# and allows the user to practice within a textbox widget
class ProblemWindow(ctk.CTkToplevel):
    def __init__(self, problem, featcode):
        super().__init__(fg_color=DEFAULT_BG_COLOR, takefocus=True)
        self.main_win = False
        self.problem_data = problem
        self.fc = featcode

        # Problem window settings
        self.title(self.problem_data[1])
        self.geometry(f'{DEFAULT_PW_WIDTH}x{DEFAULT_PW_HEIGHT}')
        self.minsize(MIN_WIDTH, MIN_HEIGHT)

        # Grid settings
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0)
        self.rowconfigure(1, weight=1)

        # Frames
        self.header_frame = Header(self, 2)
        self.paned_frame = PanedFrame(self)

    # This method repopulates the current problem window with a new ranomly selected problem
    # It does so by instantiating a new PanedFrame class that fills it's contents with new problem data 
    # This new PanedFrame replaces the current paned_frame variable, leaving the old PanedFrame object for grabage collection
    def repopulate_window(self):
        self.title(self.problem_data[1])
        self.paned_frame = PanedFrame(self)

# The PanedFrame class inherits from tkinter's PanedWindow class
# The PanedWindow class allows the user to have control over how much space each frame in the window takes up horizontally
class PanedFrame(tk.PanedWindow):
    def __init__(self, parent : ctk.CTkToplevel):
        super().__init__(parent, bg = DEFAULT_BG_COLOR, orient='horizontal', bd=8, sashwidth=8)
        self.parent = parent
        self.grid(row=1, column=0, sticky='nsew')

        # Create a DescriptionFrame and add it to self
        self.desc_frame = DescriptionFrame(self)
        self.add(self.desc_frame, minsize=MIN_WIDTH, sticky='nsew')

        # Create an InputFrame and add it to self
        self.input_frame = InputFrame(self)
        self.add(self.input_frame, sticky='nsew')

# The DescriptionFrame class inheirts from customtkinter's CTkFrame class
# An HTMLLabel is placed within this DescriptionFrame which will display the selected problem's description
class DescriptionFrame(ctk.CTkFrame):
    def __init__(self, parent : ctk.CTk):
        super().__init__(parent, fg_color=DEFAULT_BG_COLOR)
        self.parent = parent
        
        # Configure grid layout
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1)
        self.rowconfigure(0)
        self.rowconfigure(1, weight=1)
        
        # Create description header
        self.create_description_header()

        # Create HTMLLabel to display problem description
        self.create_html_description()

    # Creates a frame that displays a 'LeetCode' button and a 'Seen' switch
    # The 'LeetCode' button gets the url associated with the current problem windows problem data as a string 
    # and then calls python's webbrowser function to open the url in the user's default browser
    # The seen switch updates the problem data's SEEN value as a 1 or a 0 depending on whether the switch is in the
    # 'on' position or 'off position
    def create_description_header(self):
        # Description header frame
        frame = ctk.CTkFrame(self, 
                             fg_color=DEFAULT_FG_COLOR, 
                             border_color='white', 
                             border_width=1)
        frame.grid(row=0, 
                   column=0,
                   columnspan=2,
                   sticky='nsew', 
                   pady = 4)
        
        # Create 'LeetCode' link button and place in description header frame
        link_button = FCButton(frame, 'LeetCode', T_ENTRY_HEIGHT, FC_BUTTON_WIDTH, lambda: wb.open(self.parent.parent.problem_data[2]))
        link_button.pack(side='left', pady=T_ENTRY_PAD_Y, padx=T_ENTRY_PAD_X)

        # Inline function that is called whenever the switch object is flipped by the user
        # This function calls featcode.mark_problem_as_unseen() and featcode.mark_problem_as_seen() based on what position the switch is set to
        # The current ProblemWindows problem data is then updated accordingly
        def switch_event():
            title = self.parent.parent.problem_data[1]
            if switch_var.get() == 0:
                self.parent.parent.fc.mark_problem_as_unseen(title)
            else:
                self.parent.parent.fc.mark_problem_as_seen(title)

            self.parent.parent.problem_data = self.parent.parent.fc.get_problem_by_title(title)

        # Create a switch widget and place in description header frame
        switch_var = tk.IntVar(value=self.parent.parent.problem_data[4])
        switch = ctk.CTkSwitch(frame, text="Seen", 
                               command=switch_event, 
                               variable=switch_var, 
                               onvalue=1, 
                               offvalue=0,
                               fg_color=SWITCH_ENABLED_COLOR,
                               button_color=DEFAULT_BG_COLOR,
                               progress_color=TABLE_SELECTED_COLOR)
        switch.pack(side='right', pady=T_ENTRY_PAD_Y, padx=T_ENTRY_PAD_X)

    # Instantiates an HTMLLabel object from the tkhtmlview library
    # This reads the current ProblemWindow's problem data PROMPT as a string of html tags and then translates it into a read-only text viewbox
    def create_html_description(self):
        html_label = HTMLLabel(self, html=self.parent.parent.problem_data[3], background='white', cursor='arrow', borderwidth=4, relief='groove') #.parent
        html_label.grid(row=1, column=0, sticky='nsew')

        # Create scrollbar
        scrollbar = ctk.CTkScrollbar(self,
                                orientation="vertical",
                                command=html_label.yview,
                                button_color=DEFAULT_FG_COLOR,
                                width=SCROLLBAR_WIDTH)
        scrollbar.grid(row=1, column=1, sticky='nsew')
        html_label.configure(yscrollcommand = scrollbar.set)

# The InputFrame class inherits from customtkinter's CTkFrame class
# A CTkTextBox is placed within this frame which will act as a basic code editor from the user to work in
class InputFrame(ctk.CTkFrame):
    def __init__(self, parent : ctk.CTk):
        super().__init__(parent, fg_color=DEFAULT_BG_COLOR)
        self.parent = parent
        self.tb_str = tk.StringVar()
        
        # Configure grid layout
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1)
        self.rowconfigure(0)
        self.rowconfigure(1, weight=1)

        # Create the input header
        self.create_input_header()

        # Create the input text box
        self.text_box = self.create_text_box()

    # Creates the header frame that will contain the 'save' and 'clear' buttons for the input text box
    def create_input_header(self):
        # InputFrame header frame
        frame = ctk.CTkFrame(self, 
                             fg_color=DEFAULT_FG_COLOR, 
                             border_color='white', 
                             border_width=1)
        frame.grid(row=0, 
                   column=0,
                   columnspan=2,
                   sticky='nsew', 
                   pady = 4)
        
        # Create the 'save' button and place it in the input header frame
        save_button = FCButton(frame, 'Save', T_ENTRY_HEIGHT, FC_BUTTON_WIDTH, self.save_input_text)
        save_button.pack(side='left', pady=T_ENTRY_PAD_Y, padx=T_ENTRY_PAD_X)

        # Create the 'clear' button and place it in the input header frame
        clear_button = FCButton(frame, 'Clear', T_ENTRY_HEIGHT, FC_BUTTON_WIDTH, self.clear_input_text)
        clear_button.pack(side='left', pady=T_ENTRY_PAD_Y)

    # Instantiates a CTkTextbox object and then returns it
    def create_text_box(self):
        # Create the text box and place it in the parent frame
        text_box = ctk.CTkTextbox(self, fg_color=DEFAULT_BG_COLOR, border_color=DEFAULT_FG_COLOR, border_width=TB_BORDER_W, scrollbar_button_color=DEFAULT_FG_COLOR, wrap='none', font=('Courier New', 18))
        text_box.grid(row=1, column=0, sticky='nsew')

        # Configure the tab spacing to 4-spaces
        font = tk.font.Font(font=text_box.cget('font'))
        tab = font.measure('    ')
        text_box.configure(tabs=tab)

        # If the current ProblemWindow's problem data contains work saved from a previous session, fill the text box with it
        if self.parent.parent.problem_data[5]:
            text_box.insert("1.0", self.parent.parent.problem_data[5])

        return text_box

    # Saves the input text to the currently selected problem data in the problems database 
    # featcode.save_solution() is called where the text input of the user is passed as a string as well as the current problem's database id
    def save_input_text(self):
        if mb.askyesno(title='Save Work', message='Are you sure you want to overwrite your last save?'):
            input = self.text_box.get("1.0",'end-1c')
            self.parent.parent.fc.save_solution(input, self.parent.parent.problem_data[0])
        
    # This method clears the textbox
    def clear_input_text(self):
        if mb.askyesno(title='Clear Work', message='Are you sure you want to clear your work?'):
            self.text_box.delete("1.0",'end-1c')