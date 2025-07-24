from typing import List
import random
import uuid


class User:
    def __init__(self, id: str = None, save_object=False):
        self.id: str = id if id is not None else str(uuid.uuid4())
        self.firstName, self.lastName = self.generate_name()
        self.email: str = self.generate_mail()
        self.home = self.generate_home()
        self.company, self.work = self.generate_work()
        self.birthdate = None
        self.departement = None
        if save_object:
            import firebase
            firebase.save_object(self)

    def generate_name(self):
        first_names = [
            "Ahmed", "Mohamed", "Ali", "Hassan", "Mahmoud", "Youssef", "Omar", "Khaled",
            "Amine", "Kamel", "Fatma", "Aisha", "Zeineb", "Nour", "Sana", "Lina", "Hana",
            "Mariem", "Sami", "Mehdi", "Rami", "Nadia", "Sara", "Yasmin", "Hiba", "Mongi",
            "Fraj", "Kaisoun", "Tarek", "Imen", "Wassim", "Asma", "Bilel", "Souad",
            "Anis", "Rania", "Hamza", "Leila", "Firas", "Amal", "Zied", "Emna",
            "Karim", "Olfa", "Chaima", "Walid", "Ines", "Sofien"
        ]
        last_names = [
            "Ben Ali", "Trabelsi", "Jebali", "Mansouri", "Saidi", "Hammami",
            "Baccouche", "Chakroun", "Ghannouchi", "Zouari", "Tounsi", "Belhadj",
            "Karray", "Sfar", "Dridi", "Mejri", "Louati", "Saied",
            "Ayari", "Mathlouthi", "Marzouki", "Dhaouadi", "Belgacem",
            "Feriani", "Nafzaoui", "Mzali", "Sayyadi", "Stambouli",
            "Ayedi", "Ben Hassine", "Ben Romdhane", "Ben Yahia",
            "Bouazizi", "Arfaoui", "Bachiri"
        ]
        first = random.choice(first_names)
        last = random.choice(last_names)
        return first, last

    def generate_work(self):
        WORKPLACES = {
            "STIHL": [48.8315, 9.3095],
            "MERCEDES": [48.7833, 9.2250]
        }
        return random.choice(list(WORKPLACES.items()))

    def generate_home(self):
        lat_min, lat_max = 48.65, 48.95
        lon_min, lon_max = 8.95, 9.35
        return [random.uniform(lat_min, lat_max), random.uniform(lon_min, lon_max)]

    def generate_mail(self):
        return f"{self.firstName.lower()}.{self.lastName.lower()}@gmail.com"

    def print_infos(self):
        print(
            f"User {self.firstName} {self.lastName} with id: {self.id}")
        print(self.email, "\n")

    def to_dict(self):
        """Serialize the User object to a dictionary for Firestore."""
        return {
            'id': self.id,
            'firstName': self.firstName,
            'lastName': self.lastName,
            'email': self.email,
            'home': self.home,
            'work': self.work,
            'company': self.company,
            'birthdate': self.birthdate,
            'departement': self.departement
        }

    @staticmethod
    def from_dict(data):
        """Deserialize a dictionary from Firestore into a User object."""
        user = User(
            id=data.get('id')
        )
        user.firstName = data.get('firstName')
        user.lastName = data.get('lastName')
        user.email = data.get('email')
        user.birthdate = data.get('birthdate')
        user.departement = data.get('departement')
        user.home = data.get('home'),
        user.work = data.get('work'),
        user.company = data.get('company')
        return user
