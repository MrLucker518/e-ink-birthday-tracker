import math
from datetime import datetime, timedelta

class Birthday:
    def __init__(self, birth_date):
        self.birth_date = datetime.strptime(birth_date, "%Y-%m-%d")

    def _get_next_birthday(self):
        now = datetime.now()
        next_birthday = self.birth_date.replace(year=now.year)
        if next_birthday < now:
            next_birthday = next_birthday.replace(year=now.year + 1)
        return next_birthday

    def get_progress(self):
        next_birthday = self._get_next_birthday()
        total_birthday_secs = next_birthday.timestamp() - self.birth_date.timestamp()
        return min(self.get_birthday_secs() / total_birthday_secs, 1)

    def get_age_str(self):
        return f'{self.get_total_years()}r {self.get_total_months()}m'

    def get_days_till_next_str(self):
        return f'Zbývá: {self.get_birthday_day()}d'

    def get_birthday_day(self):
        next_birthday = self._get_next_birthday()
        return (next_birthday - datetime.now()).days

    def get_birthday_secs(self):
        return time.time() - self.birth_date.timestamp()

    def get_total_years(self):
        now = datetime.now()
        return now.year - self.birth_date.year - ((now.month, now.day) < (self.birth_date.month, self.birth_date.day))

    def get_total_months(self):
        now = datetime.now()
        years_diff = now.year - self.birth_date.year
        months_diff = now.month - self.birth_date.month
        total_months = years_diff * 12 + months_diff
        if now.day < self.birth_date.day:
            total_months -= 1
        return total_months