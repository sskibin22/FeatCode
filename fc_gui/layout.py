import sys
import os
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'fc_code')))
from featcode import *
from settings import *
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

# def stylename_elements_options(stylename):
#     '''Function to expose the options of every element associated to a widget
#        stylename.'''
#     try:
#         # Get widget elements
#         style = ttk.Style()
#         layout = str(style.layout(stylename))
#         print('Stylename = {}'.format(stylename))
#         print('Layout    = {}'.format(layout))
#         elements=[]
#         for n, x in enumerate(layout):
#             if x=='(':
#                 element=""
#                 for y in layout[n+2:]:
#                     if y != ',':
#                         element=element+str(y)
#                     else:
#                         elements.append(element[:-1])
#                         break
#         print('\nElement(s) = {}\n'.format(elements))

#         # Get options of widget elements
#         for element in elements:
#             print('{0:30} options: {1}'.format(
#                 element, style.element_options(element)))

#     except tk.TclError:
#         print('_tkinter.TclError: "{0}" in function'
#               'widget_elements_options({0}) is not a regonised stylename.'
#               .format(stylename))

# stylename_elements_options('my.Vertical.TScrollbar')

class FCGUI(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color=DEFAULT_BG_COLOR)
        # main window settings
        self.title(MAIN_TITLE)
        self.geometry(f'{DEFAULT_WIDTH}x{DEFAULT_HEIGHT}')
        self.minsize(MIN_WIDTH, MIN_HEIGHT)

        # Grid settings
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0)
        self.rowconfigure(1, weight=1)

        # Initialize FeatCode object
        self.fc = FeatCode()

        # open FeatCode database connection
        self.fc.open_db_connection()

        # Frames
        self.header = Header(self)
        self.table_frame = TFrame(self)

        # run GUI
        self.mainloop()

        # close FeatCode database connection
        self.fc.close_db_connection()


class Header(ctk.CTkFrame):
    def __init__(self, parent : ctk.CTk):
        super().__init__(parent, 
                         fg_color=DEFAULT_FG_COLOR,
                         border_width=1,
                         border_color='white', 
                         corner_radius=0, 
                         height=HEADER_HEIGHT)
        self.grid(row=0, 
                  column=0, 
                  sticky='nsew')
        
# TODO: Add randomizer button

class TFrame(ctk.CTkFrame):
    def __init__(self, parent : ctk.CTk):
        super().__init__(parent, fg_color=DEFAULT_BG_COLOR)
        self.parent = parent
        self.grid(row=1, 
                  column=0, 
                  sticky='nsew', 
                  padx=TFRAME_PAD_X, 
                  pady=TFRAME_PAD_Y)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1)
        self.rowconfigure(0)
        self.rowconfigure(1, weight=1)

        self.create_table_header()
        self.create_table()
    
    def create_table_header(self):
        # Table header frame
        frame = ctk.CTkFrame(self, 
                             fg_color=DEFAULT_FG_COLOR, 
                             border_color='white', 
                             border_width=1)
        frame.grid(row=0, 
                   column=0,
                   columnspan=2,
                   sticky='nsew', 
                   pady = 4)
        # Table header URL input entry
        entry = ctk.CTkEntry(frame, 
                             height=T_ENTRY_HEIGHT, 
                             width=T_ENTRY_WIDTH, 
                             fg_color=DEFAULT_BG_COLOR, 
                             border_width=0)
        entry.pack(side = 'left', padx=T_ENTRY_PAD_X, pady=T_ENTRY_PAD_Y)
        # Table header add problem button
        add_button = ctk.CTkButton(frame,
                                   text='Add Problem',
                                   text_color=TABLE_TEXT_COLOR,
                                   font=TABLE_FONT,
                                   height=T_ENTRY_HEIGHT, 
                                   fg_color=DEFAULT_BG_COLOR,
                                   border_color='white',
                                   hover_color=TABLE_SELECTED_COLOR,
                                   border_width=1, 
                                   command=lambda:print('add button pressed'))
        add_button.pack(side='left', pady=T_ENTRY_PAD_Y)
        # Table header remove problem button
        remove_button = ctk.CTkButton(frame,
                                      text='Remove Problem',
                                      text_color=TABLE_TEXT_COLOR,
                                      font=TABLE_FONT,
                                      height=T_ENTRY_HEIGHT, 
                                      fg_color=DEFAULT_BG_COLOR,
                                      border_color='white',
                                      hover_color=TABLE_SELECTED_COLOR,
                                      border_width=1, 
                                      command=lambda:print('remove button pressed'))
        remove_button.pack(side='right', padx=T_ENTRY_PAD_X, pady=T_ENTRY_PAD_Y)

    def create_table(self):
        style = ttk.Style(self)
        # Configure style of TreeView
        style.theme_use('clam')
        style.configure('Treeview', 
                        background=DEFAULT_FG_COLOR, 
                        foreground=TABLE_TEXT_COLOR, 
                        fieldbackground=DEFAULT_FG_COLOR,
                        font = TABLE_FONT)
        style.configure('Treeview.Heading', 
                        background=DEFAULT_BG_COLOR, 
                        font = TABLE_FONT_BOLD)
        style.map('Treeview', 
                  background=[('selected', TABLE_SELECTED_COLOR)], 
                  foreground=[('selected', TABLE_TEXT_COLOR)])

        # Table settings
        table = ttk.Treeview(self, 
                             columns=COL_NAMES, 
                             show='headings', 
                             padding = TV_INNER_PAD)
        table.heading('problem', text='Problem', anchor='w')
        table.heading('seen', text='Seen', anchor='w')
        table.column('problem', minwidth=MIN_WIDTH)
        table.column('seen', stretch=tk.NO, minwidth=100, width=100)
        table.grid(row=1, column=0, sticky='nsew')

        # Scrollbar configuration
        scrollbar = ctk.CTkScrollbar(self,
                                orientation="vertical",
                                command=table.yview,
                                button_color=DEFAULT_FG_COLOR)
        scrollbar.grid(row=1, column=1, sticky='nsew')
        table.configure(yscrollcommand = scrollbar.set)

        

        # Table Tags for striped items design
        table.tag_configure('oddrow', background=DEFAULT_BG_COLOR)
        table.tag_configure('evenrow', background=DEFAULT_FG_COLOR)
        # Populate table
        for i, row in enumerate(self.parent.fc.get_table()):
            t = ('oddrow',)
            if i % 2 == 0:
                t = ('evenrow',)
            table.insert(parent = '', index=tk.END, values = (row[1], row[4]), tags=t)