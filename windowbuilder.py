import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
import pandas as pd
from dateutil.relativedelta import relativedelta
from database import Database
import tkcalendar as tkc
import datetime as dt


class BudgetApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # Initialize window with specifications
        self.title("Business CBA App")
        self.geometry("1600x1000")
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure('Treeview', background='#D3D3D3', foreground='black',
                             rowheight=25, fieldbackground='#D3D3D3')
        self.style.map('Treeview', background=[('selected', '#347083')])

        # Initialize referenced variables
        self.confirm = False
        self.freq = ['Daily', 'Weekly', 'Biweekly', 'Monthly', 'Quarterly', 'Annually', 'Individual']
        self.expend_widgets = {}
        self.income_widgets = {}
        self.report_widgets = {}
        self.expend_analysis_df = pd.DataFrame()
        self.income_analysis_df = pd.DataFrame()
        self.final_df = pd.DataFrame()
        self.fig = plt.Figure(figsize=(5, 5))
        self.ax = self.fig.add_subplot(111)

        # Connect to database
        self.db = Database()
        self.expend_widgets['Data'] = self.db.pull_all_from_table('Expenditure')
        self.income_widgets['Data'] = self.db.pull_all_from_table('Income')

        # Search functionality

        # Create tab control
        self.tabControl = ttk.Notebook(self)

        # Create cost tab
        self.expend_widgets['Tab'] = self.tab_creator(self.tabControl, 'Expenditure')
        columns = self.db.get_columns('Expenditure')
        cost_tree_names = ["ID", "Expenditure Name", "Amount", "Frequency", "Tag", "Start Date", "End Date"]
        self.expend_widgets['Tree'] = self.tree_creator(self.expend_widgets['Tab'], columns, cost_tree_names)
        self.refresh_treeview(self.expend_widgets['Tree'], 'Expenditure')
        self.expend_widgets['Tree'].bind('<ButtonRelease-1>', lambda e: self.select_record(self.expend_widgets))

        self.expend_widgets['Entry Frame'] = tk.LabelFrame(self.expend_widgets['Tab'], text='Expense Record')
        self.expend_widgets['Entry Frame'].pack(fill='x', expand=1, padx=20)
        self.expend_widgets['ID'] = self.entry_frame_creator(self.expend_widgets['Entry Frame'],
                                                             'ID', row=0, column=0)
        self.expend_widgets['Name'] = self.entry_frame_creator(self.expend_widgets['Entry Frame'],
                                                               'Expenditure Name', row=0, column=2)
        self.expend_widgets['Amount'] = self.entry_frame_creator(self.expend_widgets['Entry Frame'],
                                                                 'Amount', row=0, column=4)
        self.expend_widgets['Freq'] = self.dropdown_creator(self.expend_widgets['Entry Frame'], self.freq,
                                                            'Frequency', row=0, column=6)
        self.expend_widgets['Tag'] = self.entry_frame_creator(self.expend_widgets['Entry Frame'],
                                                              'Tag', row=0, column=8)
        self.expend_widgets['Start'] = self.calendar_creator(self.expend_widgets['Entry Frame'], 'Start Date', row=0,
                                                             column=10, buffer={'year': 0, 'month': 0, 'day': 0})
        self.expend_widgets['End'] = self.calendar_creator(self.expend_widgets['Entry Frame'], 'End Date', row=0,
                                                           column=12,
                                                           buffer={'year': 1, 'month': 0, 'day': 0})

        self.expend_widgets['Button Frame'] = tk.LabelFrame(self.expend_widgets['Tab'], text='Commands')
        self.expend_widgets['Button Frame'].pack(fill='x', expand=1, padx=20)
        self.button_creator(self.expend_widgets['Button Frame'], 'Update Record',
                            lambda: self.update_cost_record(self.expend_widgets, 'Expenditure'), 0, 0)
        self.button_creator(self.expend_widgets['Button Frame'], 'Add Record',
                            lambda: self.submit(self.expend_widgets, 'Expenditure'), 0, 2)
        self.button_creator(self.expend_widgets['Button Frame'], 'Remove All Records',
                            lambda: self.clear_records(self.expend_widgets, 'Expenditure'), 0, 4)
        self.button_creator(self.expend_widgets['Button Frame'], 'Remove Selected Record',
                            lambda: self.delete_selected(self.expend_widgets, 'Expenditure'), 0, 6)
        self.button_creator(self.expend_widgets['Button Frame'], 'Clear Entry',
                            lambda: self.clear_entries(self.expend_widgets), 0, 8)

        self.expend_widgets['Terminal'] = tk.LabelFrame(self.expend_widgets['Tab'], text='Terminal')
        self.expend_widgets['Terminal'].pack(fill='x', expand=1, padx=20, side=tk.BOTTOM)
        self.expend_widgets['Terminal Text'] = tk.Label(self.expend_widgets['Terminal'])
        self.terminal_text(self.expend_widgets, '')

        # Create income tab
        self.income_widgets['Tab'] = self.tab_creator(self.tabControl, 'Income')
        columns = self.db.get_columns('Income')
        benefit_tree_names = ["ID", "Income Name", "Amount", "Frequency", "Tag", "Start Date", "End Date"]
        self.income_widgets['Tree'] = self.tree_creator(self.income_widgets['Tab'], columns, benefit_tree_names)
        self.refresh_treeview(self.income_widgets['Tree'], 'Income')
        self.income_widgets['Tree'].bind('<ButtonRelease-1>', lambda e: self.select_record(self.income_widgets))

        self.income_widgets['Entry Frame'] = tk.LabelFrame(self.income_widgets['Tab'], text='Expense Record')
        self.income_widgets['Entry Frame'].pack(fill='x', expand=1, padx=20)
        self.income_widgets['ID'] = self.entry_frame_creator(self.income_widgets['Entry Frame'],
                                                             'ID', row=0, column=0)
        self.income_widgets['Name'] = self.entry_frame_creator(self.income_widgets['Entry Frame'],
                                                               'Income Name', row=0, column=2)
        self.income_widgets['Amount'] = self.entry_frame_creator(self.income_widgets['Entry Frame'],
                                                                 'Amount', row=0, column=4)
        self.income_widgets['Freq'] = self.dropdown_creator(self.income_widgets['Entry Frame'], self.freq,
                                                            'Frequency', row=0, column=6)
        self.income_widgets['Tag'] = self.entry_frame_creator(self.income_widgets['Entry Frame'],
                                                              'Tag', row=0, column=8)
        self.income_widgets['Start'] = self.calendar_creator(self.income_widgets['Entry Frame'], 'Start Date', row=0,
                                                             column=10, buffer={'year': 0, 'month': 0, 'day': 0})
        self.income_widgets['End'] = self.calendar_creator(self.income_widgets['Entry Frame'], 'End Date', row=0,
                                                           column=12, buffer={'year': 1, 'month': 0, 'day': 0})

        self.income_widgets['Button Frame'] = tk.LabelFrame(self.income_widgets['Tab'], text='Commands')
        self.income_widgets['Button Frame'].pack(fill='x', expand=1, padx=20)
        self.button_creator(self.income_widgets['Button Frame'], 'Update Record',
                            lambda: self.update_cost_record(self.income_widgets, 'Income'), 0, 0)
        self.button_creator(self.income_widgets['Button Frame'], 'Add Record',
                            lambda: self.submit(self.income_widgets, 'Income'), 0, 2)
        self.button_creator(self.income_widgets['Button Frame'], 'Remove All Records',
                            lambda: self.clear_records(self.income_widgets, 'Income'), 0, 4)
        self.button_creator(self.income_widgets['Button Frame'], 'Remove Selected Record',
                            lambda: self.delete_selected(self.income_widgets, 'Income'), 0, 6)
        self.button_creator(self.income_widgets['Button Frame'], 'Clear Entry',
                            lambda: self.clear_entries(self.income_widgets), 0, 8)

        self.income_widgets['Terminal'] = tk.LabelFrame(self.income_widgets['Tab'], text='Terminal')
        self.income_widgets['Terminal'].pack(fill='x', expand=1, padx=20, side=tk.BOTTOM)
        self.income_widgets['Terminal Text'] = tk.Label(self.income_widgets['Terminal'])
        self.terminal_text(self.income_widgets, '')

        # Balance Book Tab:
        self.report_widgets['Tab'] = self.tab_creator(self.tabControl, 'Balance Book')
        self.confirm = True
        self.get_data_points()
        columns = ['Date', 'Amount']
        report_tree_names = ["Date", "Amount"]
        self.report_widgets['Tree'] = self.tree_creator(self.report_widgets['Tab'], columns, report_tree_names)
        self.update_report()
        self.report_widgets['Tree'].pack(fill='both', padx=20, pady=20, expand=1)

        # Pack tabs
        self.tabControl.pack(expand=1, fill='both')

    def get_data_points(self):
        self.expend_widgets['Data'] = self.db.pull_all_from_table('Expenditure')
        self.income_widgets['Data'] = self.db.pull_all_from_table('Income')
        cost_list = []
        for data in self.expend_widgets['Data']:
            cost_list.append((dt.datetime.strptime(data[5], '%m/%d/%y'), dt.datetime.strptime(data[6], '%m/%d/%y'),
                              data[3], float(data[2])))
        self.expend_analysis_df = self.generate_amounts(cost_list)

        benefit_list = []
        for data in self.income_widgets['Data']:
            benefit_list.append((dt.datetime.strptime(data[5], '%m/%d/%y'), dt.datetime.strptime(data[6], '%m/%d/%y'),
                                 data[3], float(data[2])))
        self.income_analysis_df = self.generate_amounts(benefit_list)
        self.expend_analysis_df['Amount'] = self.expend_analysis_df['Amount'] * -1

        self.final_df = pd.concat([self.income_analysis_df, self.expend_analysis_df])
        self.final_df.sort_index(inplace=True)
        self.final_df['cumulative'] = self.final_df['Amount'].cumsum()

    def update_report(self):
        self.get_data_points()
        tree = self.report_widgets['Tree']

        for row in tree.get_children():
            self.report_widgets['Tree'].delete(row)
        dates = self.final_df.index
        values = self.final_df['cumulative']
        tree.tag_configure('odd row', background='white')
        tree.tag_configure('even row', background='lightblue')
        count = 0
        for i in range(len(dates)):
            if dates[i].year > dt.date.today().year:
                if dates[i].month > dt.date.today().month:
                    break
            if count % 2 == 0:
                tree.insert(parent='', index='end', iid=str(count), text='',
                            values=(f'{dates[i].year}/{dates[i].month}/{dates[i].day}', f'${values[i]}'),
                            tags=('even row',))
            else:
                tree.insert(parent='', index='end', iid=str(count), text='',
                            values=(f'{dates[i].year}/{dates[i].month}/{dates[i].day}', f'${values[i]}'),
                            tags=('odd row',))
            count += 1
        tree.pack(fill='both', expand=True, padx=20, pady=20)

    @staticmethod
    def generate_amounts(list_of_info):
        df = pd.DataFrame(columns=['Date', 'Amount'])
        for item in list_of_info:
            num_periods = 1
            start, end, freq, amount = item
            if freq == 'Daily':
                num_periods = (end - start).days + 1
                date_list = [start + relativedelta(days=i) for i in range(num_periods)]
            elif freq == 'Weekly':
                num_periods = (end - start).days // 7 + 1
                date_list = [start + relativedelta(weeks=i) for i in range(num_periods)]
            elif freq == 'Biweekly':
                num_periods = (end - start).days // 14 + 1
                date_list = [start + relativedelta(weeks=i) * 2 for i in range(num_periods)]
            elif freq == 'Monthly':
                num_periods = (end - start).days // 30 + 1
                date_list = [start + relativedelta(months=i) for i in range(num_periods)]
            elif freq == 'Quarterly':
                num_periods = (end - start).days // 91 + 1
                date_list = [start + relativedelta(months=i) * 3 for i in range(num_periods)]
            elif freq == 'Annually':
                num_periods = (end - start).days // 365 + 1
                date_list = [start + relativedelta(years=i) for i in range(num_periods)]
            else:
                date_list = [start]
            amount_list = [amount] * num_periods
            new_info = pd.DataFrame(zip(date_list, amount_list), columns=['Date', 'Amount'])
            df = pd.concat([df, new_info])
        df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
        df = df.sort_values(by=['Date'])
        df.set_index(['Date'], inplace=True)
        return df

    @staticmethod
    def terminal_text(widget_master, text):
        widget_master['Terminal Text'].config(text=text)
        widget_master['Terminal Text'].pack(fill='x', pady=10, padx=10, side=tk.LEFT)

    def clear_records(self, widget_master, table):
        widget_master['Confirm Window'] = tk.Toplevel(self)
        widget_master['Confirm Window'].geometry('240x90+800+600')
        widget_master['Confirm Window'].title('Confirmation')
        confirm_frame = tk.LabelFrame(widget_master['Confirm Window'], text=f'Delete All {table[:-1]} Records?')
        confirm_frame.pack(fill='both', anchor='center', padx=20)

        def confirm_clear():
            widget_master['Confirm Window'].destroy()
            for data in self.db.pull_all_from_table(table):
                self.db.delete(table, 'rowid', '=', data[0])
            self.refresh_treeview(widget_master['Tree'], table)

        yes = tk.Button(confirm_frame, text='Yes', command=confirm_clear)
        no = tk.Button(confirm_frame, text='No', command=widget_master['Confirm Window'].destroy)
        yes.pack(fill='both', expand=1, padx=10, pady=10, side='left')
        no.pack(fill='both', expand=1, padx=10, pady=10, side='right')

    def delete_selected(self, master_widget, table):
        cost_id = master_widget['ID'].get()
        self.db.delete(table, 'rowid', '=', cost_id)
        self.refresh_treeview(master_widget['Tree'], table)

    @staticmethod
    def select_record(widget_master):
        widget_master['ID'].delete(0, tk.END)
        widget_master['Name'].delete(0, tk.END)
        widget_master['Amount'].delete(0, tk.END)
        widget_master['Freq'].delete(0, tk.END)
        widget_master['Tag'].delete(0, tk.END)
        widget_master['Start'].delete(0, tk.END)
        widget_master['End'].delete(0, tk.END)

        selected = widget_master['Tree'].focus()
        values = widget_master['Tree'].item(selected, 'values')

        widget_master['ID'].insert(0, values[0])
        widget_master['Name'].insert(0, values[1])
        widget_master['Amount'].insert(0, values[2])
        widget_master['Freq'].insert(0, values[3])
        widget_master['Tag'].insert(0, values[4])
        widget_master['Start'].insert(0, values[5])
        widget_master['End'].insert(0, values[6])

    def clear_entries(self, widget_master):
        widget_master['ID'].delete(0, tk.END)
        widget_master['Name'].delete(0, tk.END)
        widget_master['Amount'].delete(0, tk.END)
        widget_master['Freq'].delete(0, tk.END)
        widget_master['Tag'].delete(0, tk.END)
        widget_master['Start'].delete(0, tk.END)
        widget_master['End'].delete(0, tk.END)
        self.terminal_text(widget_master, '')

    def submit(self, widget_master, table):
        new_name = widget_master['Name'].get()
        new_cost = widget_master['Amount'].get()
        new_freq = widget_master['Freq'].get()
        new_tag = widget_master['Tag'].get()
        new_start_date = widget_master['Start'].get()
        new_end_date = widget_master['End'].get()
        try:
            new_cost = float(new_cost)
        except TypeError:
            pass

        if dt.datetime.strptime(new_start_date, '%m/%d/%y') > dt.datetime.strptime(new_end_date, '%m/%d/%y'):
            self.terminal_text(widget_master, 'Start date is later than end date.')
            return
        elif new_freq not in self.freq:
            self.terminal_text(widget_master, 'Not a valid frequency.')
            return
        elif type(new_cost) is not int and type(new_cost) is not float:
            self.terminal_text(widget_master, 'Not a valid amount.')
            return

        # Execute the query
        if table == 'Expenditure':
            self.db.add_expenditure(new_name, new_cost, new_freq, new_tag, new_start_date, new_end_date)
        elif table == 'Income':
            self.db.add_income(new_name, new_cost, new_freq, new_tag, new_start_date, new_end_date)

        # Refresh the treeview to show the updated record
        self.refresh_treeview(widget_master['Tree'], table)

    def update_cost_record(self, widget_master, table):
        # Get the values entered by the user
        new_id = widget_master['ID'].get()
        new_name = widget_master['Name'].get()
        new_cost = widget_master['Amount'].get()
        new_freq = widget_master['Freq'].get()
        new_tag = widget_master['Tag'].get()
        new_start_date = widget_master['Start'].get()
        new_end_date = widget_master['End'].get()

        try:
            new_cost = float(new_cost)
        except TypeError:
            self.terminal_text(widget_master, 'Not a valid amount.')
            return
        if dt.datetime.strptime(new_start_date, '%m/%d/%y') > dt.datetime.strptime(new_end_date, '%m/%d/%y'):
            self.terminal_text(widget_master, 'Start date is later than end date.')
            return
        elif new_freq not in self.freq:
            self.terminal_text(widget_master, 'Not a valid frequency.')
            return

        self.terminal_text(widget_master, '')

        # Execute the query
        self.db.update_record(table, new_name, new_cost, new_freq, new_tag, new_start_date, new_end_date, new_id)

        # Refresh the treeview to show the updated record
        self.refresh_treeview(widget_master['Tree'], table)

    @staticmethod
    def tab_creator(tab_controller, tab_name):
        tab = ttk.Frame(tab_controller)
        tab_controller.add(tab, text=tab_name)
        return tab

    @staticmethod
    def tree_creator(tab, columns, column_names):
        tree = ttk.Treeview(tab, columns=columns, show='headings')
        for i, name in enumerate(column_names):
            tree.column(f'#{i + 1}', anchor=tk.CENTER)
            tree.heading(f'#{i + 1}', text=name)
        tree_scroll = ttk.Scrollbar(tree)
        tree_scroll.config(command=tree.yview)
        tree_scroll.pack(side='right', fill='y')
        tree.configure(yscrollcommand=tree_scroll.set)
        return tree

    @staticmethod
    def entry_frame_creator(frame, text, row, column):
        label = tk.Label(frame, text=text)
        label.grid(row=row, column=column, padx=10, pady=10)
        entry = tk.Entry(frame)
        entry.grid(row=row, column=column + 1, padx=10, pady=10)
        return entry

    @staticmethod
    def dropdown_creator(frame, options, text, row, column):
        label = tk.Label(frame, text=text)
        label.grid(row=row, column=column, padx=10, pady=10)
        dropdown = ttk.Combobox(master=frame, state='normal', values=options)
        dropdown.grid(row=row, column=column + 1, padx=10, pady=10)
        return dropdown

    @staticmethod
    def button_creator(frame, text, command, row, column):
        button = tk.Button(frame, text=text, command=command)
        button.grid(row=row, column=column, padx=10, pady=10)

    @staticmethod
    def calendar_creator(frame, text: str, row: int, column: int, buffer: dict):
        label = tk.Label(frame, text=text)
        label.grid(row=row, column=column, pady=10, padx=10)
        cal = tkc.DateEntry(frame, selectmode='day', year=dt.datetime.now().year + buffer['year'],
                            month=dt.datetime.now().month + buffer['month'], day=dt.datetime.now().day + buffer['day'])
        cal.grid(row=row, column=column + 1, pady=10, padx=10)
        return cal

    def refresh_treeview(self, tree: ttk.Treeview, table):
        for row in tree.get_children():
            tree.delete(row)
        data = self.db.pull_all_from_table(table)
        tree.tag_configure('odd row', background='white')
        tree.tag_configure('even row', background='lightblue')
        count = 0
        for record in data:
            if count % 2 == 0:
                tree.insert(parent='', index='end', iid=str(count), text='', values=record, tags=('even row',))
            else:
                tree.insert(parent='', index='end', iid=str(count), text='', values=record, tags=('odd row',))
            count += 1
        tree.pack(fill='both', expand=True, padx=20)
        if self.confirm:
            self.update_report()

    def loop(self):
        self.mainloop()
        self.db.close()


if __name__ == '__main__':
    app = BudgetApp()
    app.loop()
