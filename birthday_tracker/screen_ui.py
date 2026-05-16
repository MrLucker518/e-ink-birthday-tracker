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
    AGE_TOP_PADDING = 4
    AGE_BOTTOM_PADDING = 16

    def __init__(self, width, height, birthday):
        self.birthday = birthday
        self.width = width
        self.height = height
        self._img = Image.new('L', (self.width, self.height), 255)  # 255: clear the frame
        self._img_draw = ImageDraw.Draw(self._img)

    def _calculate_text_size(self, message, font):
        _, _, w, h = self._img_draw.textbbox((0, 0), message, font=font)
        return w, h

    def _measure_age_parts(self, age_parts, number_font, unit_font, spacing):
        segments = []
        total_width = 0
        num_ascent, num_descent = number_font.getmetrics()
        unit_ascent, unit_descent = unit_font.getmetrics()
        baseline = max(num_ascent, unit_ascent)
        line_height = baseline + max(num_descent, unit_descent)

        for idx, (number, unit) in enumerate(age_parts):
            num_w, _ = self._calculate_text_size(number, number_font)
            unit_w, _ = self._calculate_text_size(unit, unit_font)
            segment_w = num_w + unit_w
            total_width += segment_w
            if idx < len(age_parts) - 1:
                total_width += spacing
            segments.append((number, unit, num_w, unit_w))

        return {
            'segments': segments,
            'total_width': total_width,
            'line_height': line_height,
            'baseline': baseline,
        }

    def _find_single_line_age_layout(self, age_parts, max_width, max_height):
        for number_size in range(60, 17, -2):
            unit_size = max(14, int(number_size * 0.62))
            spacing = max(2, int(number_size * 0.12))
            number_font = create_font(number_size)
            unit_font = create_font(unit_size)
            metrics = self._measure_age_parts(age_parts, number_font, unit_font, spacing)

            if metrics['total_width'] <= max_width and metrics['line_height'] <= max_height:
                return {
                    'number_font': number_font,
                    'unit_font': unit_font,
                    'spacing': spacing,
                    'metrics': metrics,
                }

        return None

    def _draw_age_line(self, age_parts, y, layout):
        metrics = layout['metrics']
        x = (self.width - metrics['total_width']) / 2
        number_font = layout['number_font']
        unit_font = layout['unit_font']
        num_ascent, _ = number_font.getmetrics()
        unit_ascent, _ = unit_font.getmetrics()
        baseline_y = y + metrics['baseline']
        number_y = baseline_y - num_ascent
        unit_y = baseline_y - unit_ascent

        for idx, (number, unit, num_w, unit_w) in enumerate(metrics['segments']):
            self._img_draw.text((x, number_y), number, font=number_font, fill=BLACK)
            x += num_w
            self._img_draw.text((x, unit_y), unit, font=unit_font, fill=BLACK)
            x += unit_w
            if idx < len(metrics['segments']) - 1:
                x += layout['spacing']

    def _find_two_line_age_layout(self, line_1_parts, line_2_parts, max_width, max_height):
        for number_size in range(52, 17, -2):
            unit_size = max(14, int(number_size * 0.62))
            spacing = max(2, int(number_size * 0.12))
            line_gap = max(2, int(number_size * 0.15))
            number_font = create_font(number_size)
            unit_font = create_font(unit_size)

            metrics_1 = self._measure_age_parts(line_1_parts, number_font, unit_font, spacing)
            metrics_2 = self._measure_age_parts(line_2_parts, number_font, unit_font, spacing)
            total_height = metrics_1['line_height'] + line_gap + metrics_2['line_height']

            if (
                metrics_1['total_width'] <= max_width
                and metrics_2['total_width'] <= max_width
                and total_height <= max_height
            ):
                return {
                    'line_1': {
                        'number_font': number_font,
                        'unit_font': unit_font,
                        'spacing': spacing,
                        'metrics': metrics_1,
                    },
                    'line_2': {
                        'number_font': number_font,
                        'unit_font': unit_font,
                        'spacing': spacing,
                        'metrics': metrics_2,
                    },
                    'line_gap': line_gap,
                }

        return None

    def _draw_age(self):
        age_parts = self.birthday.get_age_parts()
        top_area_top = self.AGE_TOP_PADDING
        top_area_bottom = int(self.PROGRESS_BAR_Y_CENTER - self.PROGRESS_BAR_HEIGHT / 2) - self.AGE_BOTTOM_PADDING
        max_width = self.width - 2 * self.ICON_X_MARGIN
        max_height = max(12, top_area_bottom - top_area_top)

        single_line_layout = self._find_single_line_age_layout(age_parts, max_width, max_height)
        if single_line_layout:
            line_height = single_line_layout['metrics']['line_height']
            y = top_area_top + (max_height - line_height) / 2
            self._draw_age_line(age_parts, y, single_line_layout)
            return

        split_index = max(1, len(age_parts) // 2)
        line_1_parts = age_parts[:split_index]
        line_2_parts = age_parts[split_index:]

        two_line_layout = self._find_two_line_age_layout(line_1_parts, line_2_parts, max_width, max_height)
        if two_line_layout:
            line_1_height = two_line_layout['line_1']['metrics']['line_height']
            line_2_height = two_line_layout['line_2']['metrics']['line_height']
            total_height = line_1_height + two_line_layout['line_gap'] + line_2_height
            y1 = top_area_top + (max_height - total_height) / 2
            y2 = y1 + line_1_height + two_line_layout['line_gap']
            self._draw_age_line(line_1_parts, y1, two_line_layout['line_1'])
            self._draw_age_line(line_2_parts, y2, two_line_layout['line_2'])
            return

        compact_font = create_font(18)
        compact_text = ''.join([f'{number}{unit}' for number, unit in age_parts])
        compact_w, compact_h = self._calculate_text_size(compact_text, compact_font)
        x = (self.width - compact_w) / 2
        y = top_area_top + (max_height - compact_h) / 2
        self._img_draw.text((x, y), compact_text, font=compact_font, fill=BLACK)

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