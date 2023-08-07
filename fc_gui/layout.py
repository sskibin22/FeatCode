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
        self.main_win = True
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
        self.header_frame = Header(self, 1)
        self.table_frame = TFrame(self)

        # run GUI
        self.mainloop()

        # close FeatCode database connection
        self.fc.close_db_connection()

#TODO: implement timer functionality
class Header(ctk.CTkFrame):
    def __init__(self, parent : ctk.CTk, c_span : int):
        super().__init__(parent, 
                         fg_color=DEFAULT_FG_COLOR,
                         border_width=1,
                         border_color='white', 
                         corner_radius=0, 
                         height=HEADER_HEIGHT)
        self.parent = parent
        self.grid(row=0, 
                  column=0, 
                  columnspan=c_span,
                  sticky='nsew')
        
        self.create_rand_button()
        if not self.parent.main_win:
            self.create_stopwatch()
        
    def create_rand_button(self):
        func = None
        s = None
        if self.parent.main_win:
            func  = self.create_problem_window
        else:
            func = self.repop_problem_window
            s = 'left'
        rand_button = FCButton(self, 'Randomize', 68, func)
        rand_button.pack(side=s, pady=4, padx=4)
    
    def create_stopwatch(self):
        stopwatch = Stopwatch(self)
        stopwatch.pack(side='right', pady=4, padx=4)
    
    def create_problem_window(self):
         prob = self.parent.fc.get_random_problem()
         ProblemWindow(prob, self.parent.fc)
    
    def repop_problem_window(self):
        print('repopulating problem window')
        prob = self.parent.fc.get_random_problem()
        self.parent.problem_data = prob
        self.parent.repopulate_window()

class FCButton(ctk.CTkButton):
    def __init__(self, parent : ctk.CTkFrame, name : str, h : int, cmd):
        super().__init__(parent,
                         text=name,
                         text_color=TABLE_TEXT_COLOR,
                         font=FC_BUTTON_FONT,
                         height=h, 
                         fg_color=DEFAULT_BG_COLOR,
                         border_color='white',
                         hover_color=TABLE_SELECTED_COLOR,
                         border_width=1, 
                         command=cmd)
        

class Stopwatch(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=DEFAULT_BG_COLOR, border_color='white', border_width=1)
        self.update_time = ''
        self.running = False
        self.hours = 0
        self.minutes = 0
        self.seconds = 0

        self.columnconfigure(index=0, weight=1)
        self.columnconfigure(index=1, weight=1)
        self.columnconfigure(index=2, weight=1)
        self.rowconfigure(index=0, weight=4)
        self.rowconfigure(index=1, weight=1)

        self.display_label = ctk.CTkLabel(self, text='00:00:00', font=('Times', 30, 'bold'), bg_color=SWITCH_ENABLED_COLOR, height=30)
        self.display_label.grid(row=0, column=0, columnspan=3, sticky='nsew', padx=5, pady=(5, 0))

        self.play_button = ctk.CTkButton(self, text="Start", command=self.start, font=('Courier New', 11, 'bold'), fg_color=DEFAULT_FG_COLOR, width=45, height=20)
        self.play_button.grid(row=1, column=0, sticky='ns', padx=4, pady=4)

        self.pause_button = ctk.CTkButton(self, text="Pause", command=self.pause, font=('Courier New', 11, 'bold'), fg_color=DEFAULT_FG_COLOR, width=45, height=20)
        self.pause_button.grid(row=1, column=1, sticky='ns', pady=4)

        self.reset_button = ctk.CTkButton(self, text="Reset", command=self.reset, font=('Courier New', 11, 'bold'), fg_color=TABLE_SELECTED_COLOR, width=45, height=20)
        self.reset_button.grid(row=1, column=2, sticky='ns', padx=4, pady=4)

    def start(self):
        if not self.running:
            self.display_label.after(1000)
            self.update()
            self.running = True

    def pause(self):
        if self.running:
            self.display_label.after_cancel(self.update_time)
            self.running = False

    def reset(self):
        if self.running:
            self.display_label.after_cancel(self.update_time)
            self.running = False
        self.hours, self.minutes, self.seconds = 0, 0, 0
        self.display_label.configure(text='00:00:00')

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
        self.display_label.configure(text=hours_string + ':' + minutes_string + ':' + seconds_string)
        self.update_time = self.display_label.after(1000, self.update)
        
#TODO: implement double click event for table       
class MyTreeview(ttk.Treeview):
    def __init__(self, parent : ctk.CTkFrame):
        super().__init__(parent, columns=COL_NAMES, show='headings', padding = TV_INNER_PAD)
        self.parent = parent
        self.tag_configure('oddrow', background=DEFAULT_BG_COLOR)
        self.tag_configure('evenrow', background=DEFAULT_FG_COLOR)
        self.row_idx = 0
        self.bind('<Double-Button-1>', self.create_problem_window)

    def heading(self, column, sort_by=None, **kwargs):
        if sort_by and not hasattr(kwargs, 'command'):
            func = getattr(self, f"_sort_by_{sort_by}", None)
            if func:
                kwargs['command'] = partial(func, column, False)
        return super().heading(column, **kwargs)

    def _sort(self, column, reverse, data_type, callback):
        l = [(self.set(k, column), k) for k in self.get_children('')]
        l.sort(key=lambda t: data_type(t[0]), reverse=reverse)

        # self.tag_configure('oddrow', background=DEFAULT_BG_COLOR)
        # self.tag_configure('evenrow', background=DEFAULT_FG_COLOR)

        for index, (_, k) in enumerate(l):
            t = ('oddrow',)
            if index % 2 == 0:
                t = ('evenrow',)
            self.item(k, tags=t)
            self.move(k, '', index)

        self.heading(column, command=partial(callback, column, not reverse))

    def _sort_by_num(self, column, reverse):
        self._sort(column, reverse, int, self._sort_by_num)

    def _sort_by_name(self, column, reverse):
        self._sort(column, reverse, str, self._sort_by_name)

    def create_problem_window(self, event):
         focused = self.focus()
         if focused:
            selected = self.item(focused)
            prob = self.parent.parent.fc.get_problem_by_title(selected['values'][0])
            ProblemWindow(prob, self.parent.parent.fc)

    # def _sort_by_date(self, column, reverse):
    #     def _str_to_datetime(string):
    #         return datetime.strptime(string, "%Y-%m-%d %H:%M:%S")
    #     self._sort(column, reverse, _str_to_datetime, self._sort_by_date)
        
class TFrame(ctk.CTkFrame):
    def __init__(self, parent : ctk.CTk):
        super().__init__(parent, fg_color=DEFAULT_BG_COLOR)
        self.parent = parent
        self.entry_str = tk.StringVar()
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
        self.table = self.create_table()
        self.fill_table()

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
            self.table.insert(parent = '', index=tk.END, values = (title, 0), tags=t)
            self.table.row_idx += 1
            mb.showinfo(title='Problem Added', message=f'Succesfully added [{title}] to table.')
            self.entry_str.set('')
    
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
        
        # Table header refresh button
        refresh_img = ctk.CTkImage(light_image=Image.open('fc_gui/assets/refresh_30.png'), size=(30, 30))

        refresh_button = ctk.CTkButton(frame, text='', image=refresh_img, command=self.refresh_table, width=30, fg_color=DEFAULT_FG_COLOR, hover_color=TABLE_SELECTED_COLOR)
        refresh_button.pack(side='left', pady=T_ENTRY_PAD_Y, padx=(8, 0))

        # Table header URL input entry
        entry = ctk.CTkEntry(frame, 
                             height=T_ENTRY_HEIGHT, 
                             width=T_ENTRY_WIDTH, 
                             fg_color=DEFAULT_BG_COLOR, 
                             border_width=0,
                             textvariable=self.entry_str)
        entry.pack(side = 'left', padx=T_ENTRY_PAD_X, pady=T_ENTRY_PAD_Y)

        # Table header add problem button
        add_button = FCButton(frame, 'Add Problem', T_ENTRY_HEIGHT, lambda:self.add_problem(self.entry_str))
        # add_button = ctk.CTkButton(frame,
        #                            text='Add Problem',
        #                            text_color=TABLE_TEXT_COLOR,
        #                            font=TABLE_FONT,
        #                            height=T_ENTRY_HEIGHT, 
        #                            fg_color=DEFAULT_BG_COLOR,
        #                            border_color='white',
        #                            hover_color=TABLE_SELECTED_COLOR,
        #                            border_width=1, 
        #                            command=lambda:print('add button pressed'))
        add_button.pack(side='left', pady=T_ENTRY_PAD_Y)
        # Table header remove problem button
        remove_button = FCButton(frame, 'Remove Problem', T_ENTRY_HEIGHT, self.remove_problem)
        # remove_button = ctk.CTkButton(frame,
        #                               text='Remove Problem',
        #                               text_color=TABLE_TEXT_COLOR,
        #                               font=TABLE_FONT,
        #                               height=T_ENTRY_HEIGHT, 
        #                               fg_color=DEFAULT_BG_COLOR,
        #                               border_color='white',
        #                               hover_color=TABLE_SELECTED_COLOR,
        #                               border_width=1, 
        #                               command=lambda:print('remove button pressed'))
        remove_button.pack(side='right', padx=T_ENTRY_PAD_X, pady=T_ENTRY_PAD_Y)

    def create_table(self):
        style = ttk.Style(self)
        # Configure style of TreeView
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

        # Table settings
        table = MyTreeview(self)
        # table = MyTreeview(self, columns=COL_NAMES, show='headings', padding = TV_INNER_PAD)
        table.heading('problem', text='Problem', anchor='w', sort_by='name')
        table.heading('seen', text='Seen', anchor='w', sort_by='num')
        # table = ttk.Treeview(self, 
        #                      columns=COL_NAMES, 
        #                      show='headings', 
        #                      padding = TV_INNER_PAD,)
        # table.heading('problem', text='Problem', anchor='w')
        # table.heading('seen', text='Seen', anchor='w')
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

        # # Table Tags for striped items design
        # table.tag_configure('oddrow', background=DEFAULT_BG_COLOR)
        # table.tag_configure('evenrow', background=DEFAULT_FG_COLOR)
        # Populate table
        # self.fill_table(table)
        # for i, row in enumerate(self.parent.fc.get_table()):
        #     t = ('oddrow',)
        #     if i % 2 == 0:
        #         t = ('evenrow',)
        #     table.insert(parent = '', index=tk.END, values = (row[1], row[4]), tags=t)
        #     table.row_idx = i
        return table
    
    def clear_table(self):
        for iid in self.table.get_children(''):
            self.table.delete(iid)
    
    def fill_table(self):
        for i, row in enumerate(self.parent.fc.get_table()):
            t = ('oddrow',)
            if i % 2 == 0:
                t = ('evenrow',)
            self.table.insert(parent = '', index=tk.END, values = (row[1], row[4]), tags=t)
            self.table.row_idx = i

    def refresh_table(self):
        self.clear_table()
        self.fill_table()
    
class ProblemWindow(ctk.CTkToplevel):
    def __init__(self, problem, featcode):
        super().__init__(fg_color=DEFAULT_BG_COLOR, takefocus=True)
        self.main_win = False
        self.problem_data = problem
        self.fc = featcode
        self.title(self.problem_data[1])
        self.geometry(f'{DEFAULT_PW_WIDTH}x{DEFAULT_PW_HEIGHT}')
        self.minsize(MIN_WIDTH, MIN_HEIGHT)

        # Grid settings
        self.columnconfigure(0, weight=1)
        # self.columnconfigure(1, weight=8)
        self.rowconfigure(0)
        self.rowconfigure(1, weight=1)

        # Frames
        self.header_frame = Header(self, 2)
        self.paned_frame = PanedFrame(self)
        # self.desc_frame = DescriptionFrame(self)
        # self.input_frame = InputFrame(self)

    def repopulate_window(self):
        self.title(self.problem_data[1])
        # self.desc_frame = DescriptionFrame(self)
        self.paned_frame = PanedFrame(self)

class PanedFrame(tk.PanedWindow):
    def __init__(self, parent : ctk.CTkToplevel):
        super().__init__(parent, bg = DEFAULT_BG_COLOR, orient='horizontal', bd=8, sashwidth=8)
        self.parent = parent
        self.grid(row=1, column=0, sticky='nsew')

        self.desc_frame = DescriptionFrame(self)
        self.add(self.desc_frame, minsize=MIN_WIDTH, sticky='nsew')

        self.input_frame = InputFrame(self)
        self.add(self.input_frame, sticky='nsew')

class DescriptionFrame(ctk.CTkFrame):
    def __init__(self, parent : ctk.CTk):
        super().__init__(parent, fg_color=DEFAULT_BG_COLOR)
        self.parent = parent
        # self.grid(row=1, 
        #           column=0, 
        #           sticky='nsew', 
        #           padx=TFRAME_PAD_X, 
        #           pady=TFRAME_PAD_Y)
        
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1)
        self.rowconfigure(0)
        self.rowconfigure(1, weight=1)
        
        self.create_description_header()
        self.create_html_description()

    def create_html_description(self):
        html_label = HTMLLabel(self, html=self.parent.parent.problem_data[3], background='white', cursor='arrow', borderwidth=4, relief='groove') #.parent
        html_label.grid(row=1, column=0, sticky='nsew')

        scrollbar = ctk.CTkScrollbar(self,
                                orientation="vertical",
                                command=html_label.yview,
                                button_color=DEFAULT_FG_COLOR,
                                width=SCROLLBAR_WIDTH)
        scrollbar.grid(row=1, column=1, sticky='nsew')
        html_label.configure(yscrollcommand = scrollbar.set)

    def create_description_header(self):
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
            
        link_button = FCButton(frame, 'LeetCode', T_ENTRY_HEIGHT, lambda: wb.open(self.parent.parent.problem_data[2]))
        link_button.pack(side='left', pady=T_ENTRY_PAD_Y, padx=T_ENTRY_PAD_X)

        def switch_event():
            title = self.parent.parent.problem_data[1]
            if switch_var.get() == 0:
                self.parent.parent.fc.mark_problem_as_unseen(title)
            else:
                self.parent.parent.fc.mark_problem_as_seen(title)

            self.parent.parent.problem_data = self.parent.parent.fc.get_problem_by_title(title)

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
        

class InputFrame(ctk.CTkFrame):
    def __init__(self, parent : ctk.CTk):
        super().__init__(parent, fg_color=DEFAULT_BG_COLOR)
        self.parent = parent
        self.tb_str = tk.StringVar()
        # self.grid(row=1, 
        #           column=1, 
        #           sticky='nsew', 
        #           padx=TFRAME_PAD_X, 
        #           pady=TFRAME_PAD_Y)
        
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1)
        self.rowconfigure(0)
        self.rowconfigure(1, weight=1)

        self.create_input_header()
        self.text_box = self.create_text_box()
        
    def create_text_box(self):
        text_box = ctk.CTkTextbox(self, fg_color=DEFAULT_BG_COLOR, border_color=DEFAULT_FG_COLOR, border_width=TB_BORDER_W, scrollbar_button_color=DEFAULT_FG_COLOR, wrap='none', font=('Courier New', 18))
        text_box.grid(row=1, column=0, sticky='nsew') #, padx=TFRAME_PAD_X, pady=TFRAME_PAD_Y
        font = tk.font.Font(font=text_box.cget('font'))
        tab = font.measure('    ')

        text_box.configure(tabs=tab)
        return text_box

    def create_input_header(self):
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
        
        #TODO: save button functionality
        save_button = FCButton(frame, 'Save', T_ENTRY_HEIGHT, self.save_input_text)
        save_button.pack(side='left', pady=T_ENTRY_PAD_Y, padx=T_ENTRY_PAD_X)

        clear_button = FCButton(frame, 'Clear', T_ENTRY_HEIGHT, self.clear_input_text)
        clear_button.pack(side='left', pady=T_ENTRY_PAD_Y)

        #TODO: load button

    def save_input_text(self):
        input = self.text_box.get("1.0",'end-1c')
        print(input)

    def clear_input_text(self):
        self.text_box.delete("1.0",'end-1c')
        



FCGUI()