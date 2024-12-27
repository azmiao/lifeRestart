import base64
import os
from io import BytesIO

from PIL import ImageFont, ImageDraw, Image

from yuiChyan.resources import font_path

FILE_PATH = os.path.dirname(__file__)


class ImgText:
    font = ImageFont.truetype(font_path, 14)

    def __init__(self, text):
        # 预设宽度 可以修改成你需要的图片宽度
        self.width = 600
        # 文本
        self.text = text
        # 段落 , 行数, 行高
        self.paragraph, self.note_height, self.line_height, self.draw_height = self.split_text()

    def get_paragraph(self, text):
        txt = Image.new('RGBA', (400, 800), (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt)
        # 所有文字的段落
        paragraph = ''
        # 宽度总和
        sum_width = 0
        # 几行
        line_count = 1
        # 行高
        line_height = 0
        for char in text:
            bbox = draw.textbbox((0, 0), char, ImgText.font)
            width = bbox[2] - bbox[0]
            height = bbox[3] - bbox[1]
            sum_width += width
            if sum_width > self.width:  # 超过预设宽度就修改段落 以及当前行数
                line_count += 1
                sum_width = 0
                paragraph += '\n'
            paragraph += char
            line_height = max(height, line_height)
        if not paragraph.endswith('\n'):
            paragraph += '\n'
        return paragraph, line_height, line_count

    def split_text(self):
        # 按规定宽度分组
        max_line_height, total_lines = 0, 0
        allText = []
        for text in self.text.split('\n'):
            paragraph, line_height, line_count = self.get_paragraph(text)
            max_line_height = max(line_height, max_line_height)
            total_lines += line_count
            allText.append((paragraph, line_count))
        line_height = max_line_height
        total_height = total_lines * line_height
        draw_height = total_lines * line_height
        return allText, total_height, line_height, draw_height

    def draw_text(self):
        """
        绘图以及文字
        :return:
        """
        im = Image.new("RGB", (600, self.draw_height), (255, 255, 255))
        draw = ImageDraw.Draw(im)
        # 左上角开始
        x, y = 0, 0
        for paragraph, line_count in self.paragraph:
            draw.text((x, y), paragraph, fill=(0, 0, 0), font=ImgText.font)
            y += self.line_height * line_count
        bio = BytesIO()
        im.save(bio, format='PNG')
        base64_str = 'base64://' + base64.b64encode(bio.getvalue()).decode()
        mes = f"[CQ:image,file={base64_str}]"
        return mes
