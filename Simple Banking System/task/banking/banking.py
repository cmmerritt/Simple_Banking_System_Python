import random
import sqlite3
import sys
import pprint

class BankSystem:

    def __init__(self):

        self.database = {}
        self.iin = "400000"
        self.balance = 0
        self.card_number = ""
        self.card_pin = ""

    conn = sqlite3.connect('card.s3db')
    cur = conn.cursor()


    def generate_account(self):
        card_number = []
        card_pin = []
        check_sum = ""
        for _ in range(9):
            card_number.append(str(random.randint(0, 9)))

        #check with Luhn algorithm
        #find number to check
        iin = [int(x) for x in self.iin]
        number_to_check = iin + [int(x) for x in card_number]
        #multiply odds positions by 2
        for i in range(0, len(number_to_check), 2):
            number_to_check[i] *= 2
        #substract 9 to numbers over 9
        for i in range(len(number_to_check)):
            if number_to_check[i] > 9:
                number_to_check[i] -= 9
        sum_number = sum(number_to_check)
        #find check_sum
        if sum_number % 10 == 0:
            check_sum = "0"
        else:
            check_sum = str(10 - (sum_number % 10))

        self.card_number = self.iin + "".join(card_number) + check_sum
        for _ in range(4):
            card_pin.append(str(random.randint(0, 9)))
        self.card_pin = "".join(card_pin)
        balance = self.balance
        self.database[self.card_number] = [self.card_pin, balance]

        return self.database

    def luhn_check(self):
        #find number to check
        iin = [int(x) for x in self.iin]
        number_to_check = iin + [int(x) for x in self.card_number]
        #multiply odds positions by 2
        for i in range(0, len(number_to_check), 2):
            number_to_check[i] *= 2
        #substract 9 to numbers over 9
        for i in range(len(number_to_check)):
            if number_to_check[i] > 9:
                number_to_check[i] -= 9
        sum_number = sum(number_to_check)
        return (sum_number % 10)

    def checksum(self, string):
        """
        Compute the Luhn checksum for the provided string of digits. Note this
        assumes the check digit is in place.
        """
        digits = list(map(int, string))
        odd_sum = sum(digits[-1::-2])
        even_sum = sum([sum(divmod(2 * d, 10)) for d in digits[-2::-2]])
        return (odd_sum + even_sum) % 10


    def verify(self, string):
        return (self.checksum(string) == 0)

    def generate_menu(self):
        self.create_database()
        while True:
            home_menu = input("1. Create an account\n2. Log into account\n0. Exit\n")
            if home_menu == "0":
                self.leave()
            if home_menu == "1":
                self.generate_account()
                self.retrieve_from_database()
                print(f"\nYour card has been created\n\ Your card number:\n{self.card_number}\nYour card PIN:\n{self.card_pin}\n")
            if home_menu == "2":
                self.login()

    def login(self):
        self.card_number = input("\nEnter your card number:\n")
        card_pin = input("Enter your PIN:\n")
        if self.card_number in self.database.keys() and card_pin in self.database[self.card_number]:
                print("\nYou have successfully logged in!\n")
                self.account_menu()
        else:
            print("\nWrong card number or PIN!\n")

    def account_menu(self):
        while True:
            submenu = input("1. Balance\n2. Add income \n3. Do transfer \n4. Close account \n5. Log out \n0. Exit\n")
            if submenu == "1":
                print(f"\nBalance: {self.balance}\n")
            elif submenu == "2":
                income = int(input("How much would you like to deposit? \n"))
                card_number = self.card_number
                conn = sqlite3.connect("card.s3db")
                cur = conn.cursor();
                cur.execute("UPDATE card SET balance = (balance + ?) WHERE number = (?)", (income, card_number,))
                conn.commit()
            elif submenu == "3":
                rec_acct = input("Which account number would you like to transfer to? \n")
                if rec_acct == self.card_number:
                    print("You can't transfer money to the same account! \n")
                    continue;
                conn = sqlite3.connect("card.s3db")
                cur = conn.cursor()
                cur.execute("SELECT number FROM card")
                res = cur.fetchall()
                if self.verify(rec_acct) is False:
                    print("Probably you made a mistake in the card number. Please try again! \n")
                    continue
                if (rec_acct,) not in res:
                    print("Such a card does not exist. \n")
                    continue
                tran_sum = int(input("How much would you like to transfer?\n"))
                #print(tran_sum + "\n")
                cur.execute("SELECT balance FROM card WHERE number = (?)", (self.card_number,))
                res = cur.fetchall()
                self.balance = res[0][0]
                if tran_sum > self.balance:
                    print("Not enough money! \n")
                else:
                    cur.execute("UPDATE card SET balance = (balance - ?) WHERE number = (?)", (tran_sum, self.card_number,))
                    cur.execute("UPDATE card SET balance = (balance + ?) WHERE number = (?)", (tran_sum, rec_acct,))
                    conn.commit()
            elif submenu == "4":
                self.delete_account()
                print(f"\nYour account is now closed.\n")
            elif submenu == "5":
                print("\nYou have successfully logged out!\n")
            elif submenu == "0":
                self.leave()

    def create_database(self):
        conn = sqlite3.connect("card.s3db")
        cur = conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS card (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    number TEXT,
                    pin TEXT,
                    balance INTEGER DEFAULT 0 );""")
        conn.commit()

    def add_to_database(self):
        conn = sqlite3.connect("card.s3db")
        cur = conn.cursor()
        cur.execute("INSERT INTO card VALUES (1, ?, ? ,?)",(self.card_number, self.card_pin, self.balance))
        conn.commit()

    def update_database(self):
        conn = sqlite3.connect("card.s3db")
        cur = conn.cursor()
        cur.execute("""INSERT INTO card (number, pin, balance)
                    VALUES (?, ?, ?)""",(self.card_number, self.card_pin, self.balance))
        conn.commit()

    def retrieve_from_database(self):
        conn = sqlite3.connect("card.s3db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM card")
        rows = cur.fetchall()
        if len(rows) == 0:
            self.add_to_database()
        else:
            self.update_database()

    def delete_account(self):
        conn = sqlite3.connect("card.s3db")
        cur = conn.cursor()
        cur.execute("""DELETE FROM card
         WHERE number = (?)""",(self.card_number,))
        conn.commit()

    def leave(self):
        self.conn.close()
        print("Bye!")
        sys.exit()


if __name__ == "__main__":
    card = BankSystem()
    card.generate_menu()
