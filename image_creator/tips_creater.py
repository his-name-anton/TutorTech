from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import ImageFormatter
from pygments.styles import get_style_by_name

DEFAULT_BG_PATH = "img/bg/bg6.jpg"
LONG_BG_PATH = 'img/bg/bg_long.jpg'
DEFAULT_SAVE_PATH = 'result_new.png'
DEFAULT_CODE_STYLE = 'nord-darker'
DEFAULT_PROPORTIONS = (9, 10)

class BaseImg:

    def __init__(self, text,
                 save_path: str = None,
                 bg_path: str = None,
                 ):
        self.text: str = text
        self.save_path = DEFAULT_SAVE_PATH if not save_path else save_path
        self.bg_path = self.__select_bg() if not bg_path else bg_path


    def __select_bg(self):
        if self.text.count('\n') > 80:
            return LONG_BG_PATH
        else:
            return DEFAULT_BG_PATH

    def load_bg_img(self) -> Image:
        return Image.open(self.bg_path)

    def save_img(self, img: Image) -> None:
        img.save(self.save_path)


class CodeImg(BaseImg):

    def __init__(self, text,
                    language: str = 'python',
                    save_path: str = None,
                    bg_path: str = None,
                    code_style: str = None,
                    proportions: tuple = None,
                    font_size: int = 13
                    ):
        super().__init__(text, save_path, bg_path)
        self.language = language
        self.code_style = DEFAULT_CODE_STYLE if not code_style else code_style
        self.proportions = DEFAULT_PROPORTIONS if not proportions else proportions
        self.font_size = font_size


    def __get_lexer(self):
        try:
            lexer = get_lexer_by_name(self.language)
        except Exception:
            raise ModuleNotFoundError(f'{self.language} not found in pygments')
        return lexer

    def _create_only_code_img(self) -> Image:
        code_style = get_style_by_name(self.code_style)

        formatter = ImageFormatter(style=code_style,
                                   line_numbers=False,
                                   font_size=self.font_size)

        lexer = self.__get_lexer()

        highlighted_code = highlight(self.text, lexer, formatter)
        return Image.open(BytesIO(highlighted_code))


    def _create_window_code(self, code_img: Image) -> Image:
        code_img_w, code_img_h = code_img.size

        dir_size = {20: 'small',
                    40: 'medium',
                    10000: 'large'}

        size_dir = None
        for size_value, path in dir_size.items():
            if self.font_size <= size_value:
                size_dir = path
                break

        # размеры левой шапки
        ft = Image.open(f'img/sides/{size_dir}/first_top.png')
        ft_w, ft_h = ft.size
        new_main_height = code_img_h + ft_h

        # размеры правой шапки
        tt = Image.open(f'img/sides/{size_dir}/third_top.png')
        tt_w, tt_h = tt.size
        new_main_width = code_img_w

        # центральная шапка
        st = Image.open(f'img/sides/{size_dir}/second_top.png')
        st_w, st_h = st.size
        need_w_st = new_main_width - st_w - tt_w
        st = st.resize((need_w_st, st_h))

        # создаём новое изображение
        code_img_with_wrapper = Image.new('RGB', (new_main_width, new_main_height))

        # Вставляем шапку
        code_img_with_wrapper.paste(ft, (0, 0))
        code_img_with_wrapper.paste(st, (ft_w, 0))
        code_img_with_wrapper.paste(tt, (new_main_width - tt_w, 0))

        # Вставляем изображение с кодом
        code_img_with_wrapper.paste(code_img, (0, ft_h))

        return code_img_with_wrapper

    def _create_code_img(self) -> Image:
        img_code_init = self._create_only_code_img()
        img_code_wrapper = self._create_window_code(img_code_init)
        return img_code_wrapper


    def _check_prop(self, bg_size: tuple) -> bool:
        img: Image = self._create_only_code_img()
        img_w, img_h = img.size
        bg_w, bg_h = bg_size
        prop_first, prop_second = self.proportions
        prop_value = prop_first / prop_second
        if img_w < prop_value * bg_w and img_h < prop_value * bg_h:
            return False
        return True

    def create_picture_code(self, need_save:bool = False) -> Image:
        background_image = Image.open(self.bg_path)
        bg_w, bg_h = background_image.size

        while not self._check_prop(bg_size=(bg_w, bg_h)):
            self.font_size += 2

        foreground_image = self._create_code_img()

        background_width, background_height = background_image.size
        foreground_width, foreground_height = foreground_image.size

        x = (background_width - foreground_width) // 2
        y = (background_height - foreground_height) // 2


        result_img = background_image
        result_img.paste(foreground_image, (x, y))

        if need_save:
            self.save_img(result_img)

        return result_img

text = """
class BaseImg:

    def __init__(self, text,
                 save_path: str = None,
                 bg_path: str = None,
                 ):
        self.text = text
        self.save_path = DEFAULT_SAVE_PATH if not save_path else save_path
        self.bg_path = DEFAULT_BG_PATH if not bg_path else bg_path
    
"""

code_img = CodeImg(text, proportions=(8, 10)).create_picture_code(need_save=True)
