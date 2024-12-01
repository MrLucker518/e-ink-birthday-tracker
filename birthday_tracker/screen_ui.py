from PIL import Image, ImageDraw

from .icons import right_icon_path, left_icon_path, cake_icon_path
from .fonts import create_font
from .gray_scale import WHITE, DARK_GRAY, BLACK, LIGHT_GRAY


class ScreenUI:
    ICON_SIZE = 20
    ICON_CIRCLE_SIZE = 40
    ICON_X_MARGIN = 8
    PROGRESS_BAR_Y_CENTER = 105
    PROGRESS_BAR_HEIGHT = 10
    TEXT_MARGIN_TOP = 16
    TEXT_MARGIN_BOTTOM = 16

    def __init__(self, width, height, birthday):
        self.birthday = birthday
        self.width = width
        self.height = height
        self._img = Image.new('L', (self.width, self.height), 255)  # 255: clear the frame
        self._img_draw = ImageDraw.Draw(self._img)

    def _calculate_text_size(self, message, font):
        _, _, w, h = self._img_draw.textbbox((0, 0), message, font=font)
        return w, h

    def _draw_age(self):
        number_font = create_font(60)
        unit_font = create_font(40)
        
        age_parts = self.birthday.get_age_parts()
        total_width = 0
        max_height = 0
        
        for number, unit in age_parts:
            num_w, num_h = self._calculate_text_size(number, number_font)
            unit_w, unit_h = self._calculate_text_size(unit, unit_font)
            total_width += num_w + unit_w + 10
            max_height = max(max_height, num_h)
        
        if age_parts:
            total_width -= 10
        
        x = (self.width - total_width) / 2
        y = max(0, self.TEXT_MARGIN_TOP - max_height/4)
        
        for number, unit in age_parts:
            num_w, num_h = self._calculate_text_size(number, number_font)
            self._img_draw.text((x, y), number, font=number_font, fill=BLACK)
            
            x += num_w
            unit_w, unit_h = self._calculate_text_size(unit, unit_font)
            unit_y = y + (num_h - unit_h)
            self._img_draw.text((x, unit_y), unit, font=unit_font, fill=BLACK)
            
            x += unit_w + 10

    def _draw__remaining_days(self):
        font = create_font(30)
        days_till_next_str = self.birthday.get_days_till_next_str()
        w, h = self._calculate_text_size(days_till_next_str, font)
        pos = ((self.width-w)/2, (self.height-h-self.TEXT_MARGIN_BOTTOM))
        self._img_draw.text(pos, days_till_next_str, font=font, fill=BLACK)

    def _draw_right_icon(self):
        right = Image.open(right_icon_path)
        right.convert("1")
        circle_y1 = int(self.PROGRESS_BAR_Y_CENTER - self.ICON_CIRCLE_SIZE/2)
        circle_y2 = circle_y1 + self.ICON_CIRCLE_SIZE
        circle_x1 = self.width - self.ICON_CIRCLE_SIZE - self.ICON_X_MARGIN
        circle_x2 = self.width - self.ICON_X_MARGIN
        self._img_draw.ellipse((circle_x1, circle_y1, circle_x2, circle_y2), fill=DARK_GRAY)

        icon_x = int(circle_x1 + (self.ICON_CIRCLE_SIZE - right.width)/2)
        icon_y = int(circle_y1 + (self.ICON_CIRCLE_SIZE - right.height)/2)
        self._img.paste(right, (icon_x, icon_y), right)

    def _draw_left_icon(self):
        left = Image.open(left_icon_path)
        left.convert("1")
        circle_y1 = int(self.PROGRESS_BAR_Y_CENTER - self.ICON_CIRCLE_SIZE/2)
        circle_y2 = circle_y1 + self.ICON_CIRCLE_SIZE
        circle_x1 = self.ICON_X_MARGIN
        circle_x2 = circle_x1 + self.ICON_CIRCLE_SIZE
        self._img_draw.ellipse((circle_x1, circle_y1, circle_x2, circle_y2), fill=LIGHT_GRAY)

        icon_x = int(circle_x1 + (self.ICON_CIRCLE_SIZE - left.width)/2)
        icon_y = int(circle_y1 + (self.ICON_CIRCLE_SIZE - left.height)/2)
        self._img.paste(left, (icon_x, icon_y), left)

    def _draw_progress_bar_mid(self):
        self._draw_progress_done()
        self._draw_progress_remaining()
        self._draw_progress_circle()

    def _draw_progress_bar(self):
        self._draw_left_icon()
        self._draw_progress_bar_mid()
        self._draw_right_icon()

    def draw(self):
        if self.birthday.is_birthday_day():
            # Clear the frame first with white background
            self._img = Image.new('L', (self.width, self.height), 255)
            self._img_draw = ImageDraw.Draw(self._img)
            
            # Load and prepare cake image
            cake = Image.open(cake_icon_path)
            cake = cake.convert('L')  # Convert to grayscale
            cake = Image.eval(cake, lambda x: 255 - x)  # Invert colors
            
            # Calculate size to fill the display while maintaining aspect ratio
            margin = 20
            display_width = self.width - (2 * margin)
            display_height = self.height - (2 * margin)
            
            width_ratio = display_width / cake.width
            height_ratio = display_height / cake.height
            scale_ratio = min(width_ratio, height_ratio) * 1.5
            
            new_width = int(cake.width * scale_ratio)
            new_height = int(cake.height * scale_ratio)
            
            # Resize the cake
            cake = cake.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Calculate position to center the cake
            icon_x = (self.width - new_width) // 2
            icon_y = (self.height - new_height) // 2
            
            # Paste the cake icon
            self._img.paste(cake, (icon_x, icon_y))
            
            # Add the year text
            years = str(self.birthday.get_total_years())
            font = create_font(90)
            
            # Calculate text size
            w, h = self._calculate_text_size(years, font)
            
            # Calculate text position (center of the cake)
            text_x = (self.width - w) // 2
            text_y = icon_y + new_height * 0.7 - h // 2 - 4
            
            # Draw the text
            self._img_draw.text((text_x, text_y), years, font=font, fill=BLACK)
        else:
            self._draw_age()
            self._draw__remaining_days()
            self._draw_progress_bar()
        return self._img

    def _draw_progress_done(self):
        y1 = int(self.PROGRESS_BAR_Y_CENTER - self.PROGRESS_BAR_HEIGHT/2)
        y2 = y1 + self.PROGRESS_BAR_HEIGHT
        x1 = self.ICON_X_MARGIN + self.ICON_CIRCLE_SIZE
        x2 = self._get_progress_bar_mid_x_point()
        self._img_draw.rectangle((x1, y1, x2, y2), fill=LIGHT_GRAY)

    def _draw_progress_remaining(self):
        y1 = int(self.PROGRESS_BAR_Y_CENTER - self.PROGRESS_BAR_HEIGHT/2)
        y2 = y1 + self.PROGRESS_BAR_HEIGHT
        x1 = self._get_progress_bar_mid_x_point()
        x2 = self.width - self.ICON_X_MARGIN - self.ICON_CIRCLE_SIZE
        self._img_draw.rectangle((x1, y1, x2, y2), fill=DARK_GRAY)

    def _draw_progress_circle(self):
        mid_x = self._get_progress_bar_mid_x_point()
        mid_y = self.PROGRESS_BAR_Y_CENTER
        size = self.PROGRESS_BAR_HEIGHT
        pos = (mid_x-size/2, mid_y-size/2, mid_x+size/2, mid_y+size/2)
        self._img_draw.ellipse(pos, fill=LIGHT_GRAY)

    def _get_progress_bar_length(self):
        return self.width - 2*self.ICON_X_MARGIN - 2*self.ICON_CIRCLE_SIZE

    def _get_progress_bar_mid_x_point(self):
        offset = self.ICON_X_MARGIN + self.ICON_CIRCLE_SIZE
        return offset + self._get_progress_bar_length()*self.birthday.get_progress()