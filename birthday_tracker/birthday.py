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
        rd = relativedelta(self.current_date, self.birth_date)
        
        years = rd.years
        months = rd.months
        days = rd.days
        weeks = days // 7
        days = days % 7

        def get_word_or_abbrev(num, words, abbrev, use_abbrev):
            if num <= 0:
                return None
            if use_abbrev:
                if abbrev == 'l/r':
                    return ('1' if num == 1 else str(num), 'r' if 1 <= num <= 4 else 'l')
                return (str(num), abbrev)
            if len(words) == 3:
                return (str(num), words[0] if num == 1 else words[1] if 2 <= num <= 4 else words[2])
            return None

        use_abbrev = False

        year_part = get_word_or_abbrev(years, ['rok', 'roky', 'let'], 'l/r', use_abbrev)
        month_part = get_word_or_abbrev(months, ['měsíc', 'měsíce', 'měsíců'], 'm', use_abbrev)
        week_part = get_word_or_abbrev(weeks, ['týden', 'týdny', 'týdnů'], 't', use_abbrev)
        day_part = get_word_or_abbrev(days, ['den', 'dny', 'dní'], 'd', use_abbrev)

        all_parts = [p for p in [year_part, month_part, week_part, day_part] if p]
        
        if len(all_parts) > 1:
            use_abbrev = True
            return [get_word_or_abbrev(num, words, abbrev, use_abbrev) 
                   for num, (words, abbrev) in [
                       (years, (['rok', 'roky', 'let'], 'l/r')),
                       (months, (['měsíc', 'měsíce', 'měsíců'], 'm')),
                       (weeks, (['týden', 'týdny', 'týdnů'], 't')),
                       (days, (['den', 'dny', 'dní'], 'd'))
                   ] if num > 0]

        return all_parts if all_parts else [('0', 'dní')]

    def get_days_till_next_str(self):
        return f'Zbývá: {self.get_birthday_day()}d'

    def get_birthday_day(self):
        next_birthday = self._get_next_birthday()
        return (next_birthday - self.current_date).days

    def get_total_years(self):
        return self.current_date.year - self.birth_date.year - ((self.current_date.month, self.current_date.day) < (self.birth_date.month, self.birth_date.day))
        
    def is_birthday_day(self):
        return (self.current_date.month, self.current_date.day) == (self.birth_date.month, self.birth_date.day)
