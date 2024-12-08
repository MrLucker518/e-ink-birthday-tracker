from datetime import datetime
from dateutil.relativedelta import relativedelta

class Birthday:
    def __init__(self, birth_date):
        self.birth_date = datetime.strptime(birth_date, "%Y-%m-%d")
        self.current_date = datetime.combine(datetime.now().date(), datetime.min.time())

    def _get_next_birthday(self):
        next_birthday = self.birth_date.replace(year=self.current_date.year)
        if next_birthday < self.current_date:
            next_birthday = next_birthday.replace(year=self.current_date.year + 1)
        return next_birthday
    
    def _get_last_birthday(self):
        last_birthday = self.birth_date.replace(year=self.current_date.year)
        if last_birthday > self.current_date:
            last_birthday = last_birthday.replace(year=self.current_date.year - 1)
        return last_birthday

    def get_progress(self):
        next_birthday = self._get_next_birthday()
        last_birthday = self._get_last_birthday()
        
        year_span = next_birthday.timestamp() - last_birthday.timestamp()
        elapsed = self.current_date.timestamp() - last_birthday.timestamp()
        
        return min(elapsed / year_span, 1)
    
    def get_age_parts(self):
        years = self.get_total_years()
        months = self.get_total_months() % 12
        days = self.get_total_days()

        parts = []
        if years > 0:
            if years == 1:
                year_word = "rok"
            elif 2 <= years <= 4:
                year_word = "roky"
            else:
                year_word = "let"
            parts.append((str(years), year_word))
        
        if months > 0:
            if parts:
                month_word = "m"
            elif months == 1:
                month_word = "měsíc"
            elif 2 <= months <= 4:
                month_word = "měsíce"
            else:
                month_word = "měsíců"
            parts.append((str(months), month_word))

        if days > 0:
            if parts:
                day_word = "d"
            elif days == 1:
                day_word = "den"
            elif 2 <= days <= 4:
                day_word = "dny"
            else:
                day_word = "dní"
            parts.append((str(days), day_word))
        
        return parts if parts else [('0', 'dní')]

    def get_days_till_next_str(self):
        return f'Zbývá: {self.get_birthday_day()}d'

    def get_birthday_day(self):
        next_birthday = self._get_next_birthday()
        return (next_birthday - self.current_date).days

    def get_total_years(self):

        return self.current_date.year - self.birth_date.year - ((self.current_date.month, self.current_date.day) < (self.birth_date.month, self.birth_date.day))

    def get_total_months(self):
        years_diff = self.current_date.year - self.birth_date.year
        months_diff = self.current_date.month - self.birth_date.month
        total_months = years_diff * 12 + months_diff
        if self.current_date.day < self.birth_date.day:
            total_months -= 1
        return total_months

    def get_total_days(self):
        months_difference = relativedelta(self.current_date, self.birth_date)
        remaining_days = (self.current_date - (self.birth_date + relativedelta(months=months_difference.months))).days
        return remaining_days
        
    def is_birthday_day(self):
        return (self.current_date.month, self.current_date.day) == (self.birth_date.month, self.birth_date.day)
