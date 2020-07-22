from random import randint
import sqlite3

class Banking:
    def __init__(self, issue_specs):
        self.conn = sqlite3.connect('card.s3db')  # database created if not existing
        self.cur = self.conn.cursor()

        self.part1 = issue_specs  # unchanged card part as var from instance
        self.id = 1
        self.balance = 0

        self.prompts = {
            'main': '''
1. Create an account
2. Log into account
0. Exit
''',
            'logged': '''
1. Balance
2. Add income
3. Do transfer
4. Close account
5. Log out
0. Exit
'''
        }
        self.sql_queries = {
            'main':
                "CREATE TABLE IF NOT EXISTS card ("
                "id INTEGER,"
                "number TEXT,"
                "pin TEXT,"
                "balance INTEGER DEFAULT 0)"
        }

        self.state = 'main'

    def get_luhn(self, card):  # 15 digits in = 1 digit out (not True/False returner)
        for i in range(len(card)):
            if i % 2 == 0:
                card[i] *= 2
                if card[i] > 9:
                    card[i] -= 9
        return str(10 - sum(card) % 10)[-1:]

    def card_issue(self):
        self.part2 = "%09d" % randint(0, 99_9999_999)  # rest digits generator_9
        self.part3 = self.get_luhn([int(num) for num in str(f'{self.part1}{self.part2}')])
        self.card_num = int(f'{self.part1}{self.part2}{self.part3}')

    def pin_issue(self):
        self.pin = "%04d" % randint(0, 9999)
        return self.pin

    def pre_login(self):
        user_check_list = ['card number', 'PIN']
        self.user_entry_list = []
        print()
        for i in range(len(user_check_list)):
            print('Enter your ' + user_check_list[i] + ': ')
            self.user_entry_list.append(input())

        self.user_data_process()  # fetching a row with card [0], pin [1], balance [2] from db by card# entered

        if self.user_details and self.user_details[1] == \
                self.user_entry_list[1]:  # card found [TRUE] and pin [1] match
            self.balance = self.user_details[2]
            print('\nYou have successfully logged in!')
            return True
        else:
            print('Wrong card number or PIN!')
            return False

    def login(self):
        self.state = 'logged'

        while 555 < 666:
            logged_in_action = self.UI_inp()

            if logged_in_action == '1':
                print(f'\nBalance: {self.user_details[2]}')
            if logged_in_action == '2':
                income = input('Enter income: ')
                self.cur.execute(f'UPDATE card SET balance = '
                                 f'{self.user_details[2]} + {income} WHERE number=?', self.card_user)
                self.user_data_process()  # update
                print(f'Income was added! Balance: {self.user_details[2]}')
            if logged_in_action == '3':
                transfer_check_list = ['card number', 'how much money you want to transfer']
                card_transfer_luhn_OK = True
                self.transfer_list = []
                print()

                print('Enter ' + transfer_check_list[0] + ': ')
                self.transfer_list.append(input())

                card_transfer_luhn = self.get_luhn([int(num) for num in self.transfer_list[0][:15]])
                if not card_transfer_luhn == self.transfer_list[0][-1]:
                    print('Probably you made mistake in the card number. Please try again!')
                    card_transfer_luhn_OK = False

                self.transfer_data_process()

                if card_transfer_luhn_OK:
                    if not self.transfer_details_found:
                        print('Such a card does not exist.')
                    elif self.user_details[0] == self.transfer_list[0]:
                        print('You can\'t transfer money to the same account!')
                    else:
                        print('Enter ' + transfer_check_list[1] + ': ')

                        self.transfer_list.append(int(input()))
                        self.transfer_list.append(self.transfer_list[1])  # bringing list as [0],[1],[2]
                        self.transfer_list[1] = None                      # bringing list as [0],[1],[2]

                        if self.user_details[2] < self.transfer_list[2]:
                            print('Not enough money!')
                        else:
                            print('Success!')
                            self.cur.execute(f'UPDATE card SET balance = '
                                             f'{self.user_details[2]} - {self.transfer_list[2]} WHERE number=?',
                                             self.card_user)
                            self.cur.execute(f'UPDATE card SET balance = '
                                             f'{self.transfer_details_found[2]} + {self.transfer_list[2]} WHERE number=?',
                                             self.card_transfer)
                            self.conn.commit()
            if logged_in_action == '4':
                self.cur.execute('DELETE FROM card WHERE number=?', self.card_user)
                self.conn.commit()
                print('The account has been closed!')
                break
            if logged_in_action == '5':
                print('\nYou have successfully logged out!')
                break
            elif logged_in_action == '0':
                print('\nBye!')
                self.conn.close()
                exit()

        self.state = 'main'

    def user_data_process(self):      # fetching a row with card [0], pin [1], balance [2] form db by card# entered
        self.card_user = (self.user_entry_list[0],)
        self.cur.execute('SELECT number, pin, balance FROM card WHERE number=?', self.card_user)
        self.user_details = self.cur.fetchone()
        self.conn.commit()

    def transfer_data_process(self):  # fetching a row with card [0], pin [1], balance [2] form db by card# entered
        self.card_transfer = (self.transfer_list[0],)
        self.cur.execute('SELECT number, pin, balance FROM card WHERE number=?', self.card_transfer)
        self.transfer_details_found = self.cur.fetchone()
        self.conn.commit()

    def UI_inp(self):
        return input(self.prompts[self.state])

    def SQL_que(self):
        return self.sql_queries[self.state]
        self.conn.commit()

    def update_db(self):
        self.cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='card';")
        check_table = self.cur.fetchall()

        if check_table:
            self.cur.execute('SELECT id FROM card;')
            id_last = [id[0] for id in self.cur.fetchall()]  # returning list from database
            if id_last:
                self.id = int(id_last[-1]) + 1

        self.account = (self.id, self.card_num, self.pin, self.balance)
        self.cur.execute('INSERT INTO card VALUES (?,?,?,?);', self.account)
        self.conn.commit()

    def run(self):
        while 555 < 666:
            self.cur.execute(self.SQL_que())  #this main SQL request put out by [main] state run

            main_driver = self.UI_inp()

            if main_driver == '1':
                self.card_issue()
                self.pin_issue()
                print(f'\nYour card has been created'
                      f'\nYour card number:'
                      f'\n{self.card_num}'
                      f'\nYour card PIN:'
                      f'\n{self.pin}')

                self.update_db()

            elif main_driver == '2':
                if self.pre_login():
                    self.login()
            elif main_driver == '0':
                print('\nBye!')
                self.conn.close()
                break

BWS_bank = Banking(4000_00)
BWS_bank.run()