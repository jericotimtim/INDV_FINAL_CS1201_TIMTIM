import os
import random
from datetime import datetime
from utils.user_manager import UserManager
from utils.score import Score

class DiceGame:
    def __init__(self):
        self.user_manager = UserManager()
        self.scores = []
        self.current_user = None
        self.load_score()

    def load_score(self):
        if not os.path.exists("data"):
            os.makedirs("data")
        if not os.path.exists("data/rankings.txt"):
            with open("data/rankings.txt", "w"):
                pass
        with open("data/rankings.txt", "r") as file:
            for line in file:
                username, game_id, points, wins = line.strip().split(",")
                self.scores.append(Score(username, int(game_id), int(points), int(wins)))

    def save_score(self):
        with open("data/rankings.txt", "w") as file:
            sorted_scores = sorted(self.scores, key=lambda x: (x.points, x.wins), reverse=True)
            for score in sorted_scores[:10]:
                file.write(f"{score.username},{score.game_id},{score.points},{score.wins}\n")

    def play_game(self):
        if not self.current_user:
            print("Please sign in to play the game.")
            return

        print(f"Starting the game as {self.current_user.username}...")
        total_points = 0
        total_stages_won = 0

        while True:
            user_wins = 0
            cpu_wins = 0

            for _ in range(3):
                user_roll = random.randint(1, 6)
                cpu_roll = random.randint(1, 6)

                print(f"{self.current_user.username} rolled {user_roll}")
                print(f"CPU has rolled {cpu_roll}")

                if user_roll > cpu_roll:
                    print(f"You have won this round, {self.current_user.username}!")
                    user_wins += 1
                elif user_roll < cpu_roll:
                    print("CPU has won this round!")
                    cpu_wins += 1
                else:
                    print("It is a draw!")

            if user_wins > cpu_wins:
                total_points += user_wins
                total_stages_won += 1
                print(f"You won this stage, {self.current_user.username}!")
                print(f"Total Points: {total_points}")
            else:
                print(f"You have lost this stage, {self.current_user.username}..")
                print("Game Over.")
                print(f"You won {total_stages_won} stage(s) in total.")
                self.save_and_exit(total_points, total_stages_won)
                break

            choice = input("Would you like to go to the next stage? (1. Yes / 2. No): ")
            while choice not in ("1", "2"):
                print("Invalid option. Please select 1 for yes and 2 for no.")
                choice = input("Would you like to go to the next stage? (1. Yes / 2. No): ")

            if choice == "2":
                if total_stages_won == 0:
                    print("You did not win any stages. Better luck next time.")
                else:
                    print(f"You won {total_stages_won} stage(s) in total.")
                self.save_and_exit(total_points, total_stages_won)
                print("Exiting the game.")
                break

    def save_and_exit(self, total_points, total_stages_won):
        self.scores.append(Score(self.current_user.username, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), total_points, total_stages_won))
        self.save_score()

    def show_top_scores(self):
        if not self.scores:
            print("There have been no games played yet. Play games to see who gets the highest score.")
            return

        sorted_scores = sorted(self.scores, key=lambda x: (x.points, x.wins), reverse=True)
        print("Top Scores:")
        for i, score in enumerate(sorted_scores[:10], start=1):
            print(f"{i}. {score.username}: Points - {score.points}, Stages Won - {score.wins}")

    def logout(self):
        self.current_user = None
        print("You have successfully logged out.")
        self.menu()

    def menu(self):
        while True:
            print("\nWelcome to the Dice Roll Game!")
            print("1. Register")
            print("2. Log In")
            print("3. Exit")
            choice = input("Please enter your choice: ")
            if choice == "1":
                self.register()
            elif choice == "2":
                self.login()
                if self.current_user:
                    self.menu_logged_in()
                    break
            elif choice == "3":
                print("Exiting the game.")
                break
            else:
                print("Invalid option. Please attempt again.")

    def register(self):
        username = input("Enter Username (at least 4 characters) or leave blank to cancel: ")
        if not username:
            return

        while len(username) < 4:
            print("The username must be at least four characters long.")
            username = input("Enter Username (at least 4 characters) or leave blank to cancel: ")
            if not username:
                return

        password = input("Enter Password (at least 8 characters) or leave blank to cancel: ")
        if not password:
            return

        while len(password) < 8:
            print("The password must be at least eight characters long.")
            password = input("Enter Password (at least 8 characters) or leave blank to cancel: ")
            if not password:
                return

        if self.user_manager.validate_username(username):
            print("The username already exists. Please select a different one.")
            return

        self.user_manager.register(username, password)

    def login(self):
        username = input("Enter your Username (leave blank to cancel): ")
        if not username:
            return

        password = input("Enter your password (leave it blank to cancel): ")
        if not password:
            return

        user = self.user_manager.login(username, password)
        if user:
            self.current_user = user
            print(f"Logged in as {username}.")
        else:
            print("Incorrect Username or Password. Please try again.")

    def menu_logged_in(self):
        while True:
            print(f"\nWelcome {self.current_user.username}!")
            print("Menu:")
            print("1. Start Game")
            print("2. Display Top Scores")
            print("3. Log Out")
            choice = input("Enter Your Choice: ")
            if choice == "1":
                self.play_game()
            elif choice == "2":
                self.show_top_scores()
            elif choice == "3":
                self.logout()
                break
            else:
                print("Invalid choice. Kindly try again.")
