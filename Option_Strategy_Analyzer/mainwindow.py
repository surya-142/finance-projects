import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QAbstractItemView
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtGui import QDoubleValidator
from option import Option
from spread import Spread


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create a central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.assumptions_label = QLabel("Note: All entered options must have the same underlying contract and expiration date.")
        self.spread_label = QLabel()

        # Create the plot
        self.figure = Figure()
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self.figure)

        # Create input fields for option details
        self.option_type_combo = QComboBox()
        self.option_type_combo.addItems(['Call', 'Put'])

        self.strike_edit = QLineEdit()
        self.strike_edit.setValidator(QDoubleValidator(0.0, float('inf'), 2))  # Restrict to non-negative floats

        self.buy_sell_combo = QComboBox()
        self.buy_sell_combo.addItems(['Buy', 'Sell'])

        self.premium_edit = QLineEdit()
        self.premium_edit.setValidator(QDoubleValidator(0.0, float('inf'), 2))  # Restrict to non-negative floats

        self.quantity_edit = QLineEdit()
        self.quantity_edit.setValidator(QDoubleValidator(1, float('inf'), 0))  # Restrict to positive integers

        # Create an "Add to Portfolio" button
        self.add_button = QPushButton("Add to Portfolio")
        self.add_button.clicked.connect(self.add_option)

        # Create a display table for showing added options
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(['Type', 'Strike', 'Buy/Sell', 'Premium', 'Quantity', 'Actions'])

        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)

        # Adjust the column widths
        self.table.setColumnWidth(0, 100)  # Type column width
        self.table.setColumnWidth(1, 70)  # Strike column width
        self.table.setColumnWidth(2, 90)  # Buy/Sell column width
        self.table.setColumnWidth(3, 70)  # Premium column width
        self.table.setColumnWidth(5, 100)  # Actions column width

        # Create layouts for the central widget
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Type:"))
        input_layout.addWidget(self.option_type_combo)
        input_layout.addWidget(QLabel("Strike:"))
        input_layout.addWidget(self.strike_edit)
        input_layout.addWidget(QLabel("Buy/Sell:"))
        input_layout.addWidget(self.buy_sell_combo)
        input_layout.addWidget(QLabel("Premium:"))
        input_layout.addWidget(self.premium_edit)
        input_layout.addWidget(QLabel("Quantity:"))
        input_layout.addWidget(self.quantity_edit)
        input_layout.addWidget(self.add_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.assumptions_label)
        main_layout.addWidget(self.table)
        main_layout.addWidget(self.canvas)
        main_layout.addLayout(input_layout)
        main_layout.addWidget(self.spread_label)
        self.centralWidget().setLayout(main_layout)
        self.options = []

        # Set up the initial stock price range
        self.stock_price_range = np.arange(30, 80, 1)

        # Set up the main window
        self.setWindowTitle('Options Strategy Analyzer')
        self.setGeometry(200, 200, 800, 600)

        # Update the plot initially
        self.update_plot()

    def update_spread_display(self):
        spread = Spread(self.options)
        spread_type = spread.analyze()
        spread.populate_attributes(spread_type, self.spread_label)

    def update_plot(self):
        self.ax.clear()

        if not self.options:
            self.ax.set_xlabel('Stock Price at Expiration')
            self.ax.set_ylabel('P&L')
            self.ax.set_title('Options Strategy Parity Graph')
            self.ax.grid()
            self.canvas.draw()
            return

        min_strike = min(option.strike for option in self.options)
        max_strike = max(option.strike for option in self.options)
        stock_price_range = np.arange(min_strike - 10, max_strike + 10, 1)

        total_payoff = np.zeros_like(stock_price_range, dtype=np.float64)

        for option in self.options:
            option_payoff = option.payoff(stock_price_range)
            total_payoff += option_payoff

        self.ax.plot(stock_price_range, total_payoff)
        self.ax.set_xlabel('Stock Price at Expiration')
        self.ax.set_ylabel('P&L')
        self.ax.set_title('Options Strategy Parity Graph')
        self.ax.grid()

        self.canvas.draw()
        self.update_spread_display()

    def add_option(self):
        # Retrieve the option details from the input fields
        option_type = self.option_type_combo.currentText()
        strike = float(self.strike_edit.text())
        is_buy = self.buy_sell_combo.currentText() == 'Buy'
        premium = float(self.premium_edit.text())
        quantity = int(self.quantity_edit.text())

        # Check if the option already exists in the options list
        existing_option = None
        for option in self.options:
            if (
                option.option_type == option_type
                and option.strike == strike
                and option.is_buy == is_buy
            ):
                existing_option = option
                break

        if existing_option:
            # Increment the quantity of the existing option
            existing_option.quantity += quantity
        else:
            # Create a new option object and add it to the options list
            option = Option(option_type, strike, is_buy, premium, quantity)
            self.options.append(option)

        # Clear the input fields
        self.strike_edit.clear()
        self.premium_edit.clear()
        self.quantity_edit.clear()

        # Update the plot and spread display
        self.update_plot()
        self.update_spread_display()

        # Update the table display
        self.update_table_display()


    def update_table_display(self):
        self.table.setRowCount(len(self.options))
    
        for i, option in enumerate(self.options):
            self.table.setItem(i, 0, QTableWidgetItem(option.option_type))
            self.table.setItem(i, 1, QTableWidgetItem(str(option.strike)))
            self.table.setItem(i, 2, QTableWidgetItem('Buy' if option.is_buy else 'Sell'))
            self.table.setItem(i, 3, QTableWidgetItem(str(option.premium)))
            self.table.setItem(i, 4, QTableWidgetItem(str(option.quantity)))

            # Add delete and edit buttons to the last column
            delete_button = QPushButton("Delete")
            edit_button = QPushButton("Edit")

            delete_button.clicked.connect(lambda _, row=i: self.delete_record(row))
            edit_button.clicked.connect(lambda _, row=i: self.edit_record(row))

            # Create a container widget for the buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.addWidget(delete_button)
            actions_layout.addWidget(edit_button)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setAlignment(Qt.AlignCenter)

            # Set the cell widget for the "Actions" column
            self.table.setCellWidget(i, 5, actions_widget)
            self.table.setColumnWidth(5, 130)  # Adjust the width of the "Actions" column

    def delete_record(self, row):
        self.options.pop(row)
        self.update_table_display()
        self.update_plot()

    def edit_record(self, row):
        if row < len(self.options):
            option = self.options[row]

            self.option_type_combo.setCurrentText(option.option_type)
            self.strike_edit.setText(str(option.strike))
            self.buy_sell_combo.setCurrentText('Buy' if option.is_buy else 'Sell')
            self.premium_edit.setText(str(option.premium))
            self.quantity_edit.setText(str(option.quantity))

            # Remove the existing record from the table
            self.table.removeRow(row)
            self.options.pop(row)

            # Update the plot with the remaining options
            self.update_plot()


    def update_table_display(self):
        self.table.setRowCount(len(self.options))

        for i, option in enumerate(self.options):
            self.table.setItem(i, 0, QTableWidgetItem(option.option_type))
            self.table.setItem(i, 1, QTableWidgetItem(str(option.strike)))
            self.table.setItem(i, 2, QTableWidgetItem('Buy' if option.is_buy else 'Sell'))
            self.table.setItem(i, 3, QTableWidgetItem(str(option.premium)))
            self.table.setItem(i, 4, QTableWidgetItem(str(option.quantity)))

            # Add delete and edit buttons to the last column
            delete_button = QPushButton("Delete")
            edit_button = QPushButton("Edit")

            delete_button.clicked.connect(lambda _, row=i: self.delete_record(row))
            edit_button.clicked.connect(lambda _, row=i: self.edit_record(row))

            # Create a container widget for the buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.addWidget(delete_button)
            actions_layout.addWidget(edit_button)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setAlignment(Qt.AlignCenter)

            # Set the cell widget for the "Actions" column
            self.table.setCellWidget(i, 5, actions_widget)
            self.table.setColumnWidth(5, 130)  # Adjust the width of the "Actions" column


        

