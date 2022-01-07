import pygame
import arcade
import sys
from player import *
from blocks import *
from monsters import *

WIN_WIDTH = 800  # Ширина окна
WIN_HEIGHT = 640  # Высота
SCREEN_TITLE = 'RunningHero'
DISPLAY = (WIN_WIDTH, WIN_HEIGHT)
CENTER_OF_SCREEN = WIN_WIDTH / 2, WIN_HEIGHT / 2
FILE_DIR = os.path.dirname(__file__)
OPEN_FLAG = False


class Camera(object):
    def __init__(self, camera_func, width, height):
        self.camera_func = camera_func
        self.state = Rect(0, 0, width, height)

    def apply(self, target):
        return target.rect.move(self.state.topleft)

    def update(self, target):
        self.state = self.camera_func(self.state, target.rect)

    def reverse(self, pos):  # получение внутренних координат из глобальных
        return pos[0] - self.state.left, pos[1] - self.state.top


def camera_configure(camera, target_rect):
    l, t, _, _ = target_rect
    _, _, w, h = camera
    l, t = -l + WIN_WIDTH / 2, -t + WIN_HEIGHT / 2

    l = min(0, l)  # Не движемся дальше левой границы
    l = max(-(camera.width - WIN_WIDTH), l)  # Не движемся дальше правой границы
    t = max(-(camera.height - WIN_HEIGHT), t)  # Не движемся дальше нижней границы
    t = min(0, t)  # Не движемся дальше верхней границы

    return Rect(l, t, w, h)


def loadLevel(name):
    global playerX, playerY  # объявляем глобальные переменные, это координаты героя

    levelFile = open(f'%s/levels/{name}.txt' % FILE_DIR)
    line = " "

    while line[0] != "/":  # пока не нашли символ завершения файла
        line = levelFile.readline()  # считываем построчно
        if line[0] == "[":  # если нашли символ начала уровня
            while line[0] != "]":  # то, пока не нашли символ конца уровня
                line = levelFile.readline()  # считываем построчно уровень
                if line[0] != "]":  # и если нет символа конца уровня
                    endLine = line.find("|")  # то ищем символ конца строки
                    level.append(line[0: endLine])  # и добавляем в уровень строку от начала до символа "|"

        if line[0] != "":  # если строка не пустая
            commands = line.split()  # разбиваем ее на отдельные команды
            if len(commands) > 1:  # если количество команд > 1, то ищем эти команды
                if commands[0] == "player":  # если первая команда - player
                    playerX = int(commands[1])  # то записываем координаты героя
                    playerY = int(commands[2])
                if commands[0] == "portal":  # если первая команда portal, то создаем портал
                    tp = BlockTeleport(int(commands[1]), int(commands[2]), int(commands[3]), int(commands[4]))
                    entities.add(tp)
                    platforms.append(tp)
                    animatedEntities.add(tp)
                if commands[0] == "monster":  # если первая команда monster, то создаем монстра
                    mn = Monster(int(commands[1]), int(commands[2]), int(commands[3]), int(commands[4]),
                                 int(commands[5]), int(commands[6]))
                    entities.add(mn)
                    platforms.append(mn)
                    monsters.add(mn)


def main(lvl):
    global level, entities, animatedEntities, monsters, platforms, OPEN_FLAG

    level = []
    entities = pygame.sprite.Group()  # Все объекты
    animatedEntities = pygame.sprite.Group()  # все анимированные объекты, за исключением героя
    monsters = pygame.sprite.Group()  # Все передвигающиеся объекты
    platforms = []

    pygame.init()

    width, height = pygame.display.Info().current_w, pygame.display.Info().current_h
    w, h = 800, 640  # Размеры окна формы
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (width // 2 - w // 2, height // 2 - h // 2)

    screen = pygame.display.set_mode(DISPLAY)
    pygame.display.set_caption("RunningHero")
    loadLevel(lvl)
    bg = pygame.image.load('blocks/bg.png')
    left = right = False  # по умолчанию - стоим
    up = False
    running = False

    hero = Player(playerX, playerY)  # создаем героя по (x,y) координатам
    entities.add(hero)

    timer = pygame.time.Clock()
    x = y = 0
    for row in level:
        for col in row:
            if col == "-":
                pf = Platform(x, y)
                entities.add(pf)
                platforms.append(pf)
            if col == "*":
                bd = BlockDie(x, y)
                entities.add(bd)
                platforms.append(bd)
            if col == "P":
                pr = Princess(x, y)
                entities.add(pr)
                platforms.append(pr)
                animatedEntities.add(pr)

            x += PLATFORM_WIDTH  # блоки платформы ставятся на ширине блоков
        y += PLATFORM_HEIGHT
        x = 0  # на каждой новой строчке начинаем с нуля

    total_level_width = len(level[0]) * PLATFORM_WIDTH  # Высчитываем фактическую ширину уровня
    total_level_height = len(level) * PLATFORM_HEIGHT  # высоту

    camera = Camera(camera_configure, total_level_width, total_level_height)
    while not hero.winner:  # Основной цикл программы
        timer.tick(60)
        for e in pygame.event.get():
            if e.type == QUIT:
                pygame.quit()
                sys.exit()
            if e.type == KEYDOWN and e.key == K_UP:
                up = True
            if e.type == KEYDOWN and e.key == K_LEFT:
                left = True
            if e.type == KEYDOWN and e.key == K_RIGHT:
                right = True
            if e.type == KEYDOWN and e.key == K_LSHIFT:
                running = True

            if e.type == KEYUP and e.key == K_UP:
                up = False
            if e.type == KEYUP and e.key == K_RIGHT:
                right = False
            if e.type == KEYUP and e.key == K_LEFT:
                left = False
            if e.type == KEYUP and e.key == K_LSHIFT:
                running = False

        screen.blit(bg, (0, 0))

        animatedEntities.update()  # показываеaм анимацию
        monsters.update(platforms)  # передвигаем всех монстров
        camera.update(hero)  # центризируем камеру относительно персонажа
        hero.update(left, right, up, running, platforms)  # передвижение
        for e in entities:
            screen.blit(e.image, camera.apply(e))
        pygame.display.update()
        if OPEN_FLAG:
            arcade.close_window()
            OPEN_FLAG = False
    for e in entities:
        screen.blit(e.image, camera.apply(e))
    pygame.display.update()
    font = pygame.font.Font(None, 38)
    font_back = pygame.font.Font(None, 39)
    if lvl != 3:
        text_back = font_back.render(("Thank you, Hero! But our princess is in another level!"), 1,
                                     (0, 0, 0))
        screen.blit(text_back, (13, 103))
        text = font.render(("Thank you, Hero! But our princess is in another level!"), 1,
                           (255, 255, 255))
        screen.blit(text, (10, 100))
        pygame.display.update()
        time.wait(5000)
        pygame.display.update()
        # ждем 5 секунд и после - переходим на следующий уровень
    else:
        bg = pygame.image.load('blocks/win.png')
        screen.blit(bg, (0, 0))
        pygame.display.update()
        while 1:
            for e in pygame.event.get():  # Обрабатываем события
                if e.type == QUIT:
                    pygame.quit()
                    sys.exit()


class IntroductionView(arcade.View):
    def on_show(self):
        arcade.set_background_color(arcade.color.AMAZON)
        arcade.set_viewport(0, WIN_WIDTH - 1, 0, WIN_HEIGHT - 1)
        self.background = arcade.load_texture("blocks/hello.jpg")

    def on_draw(self):
        arcade.start_render()
        arcade.draw_texture_rectangle(WIN_WIDTH // 2, WIN_HEIGHT // 2, WIN_WIDTH, WIN_HEIGHT, self.background)

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        view = Rules()
        self.window.show_view(view)


class Rules(arcade.View):
    def on_show(self):
        arcade.set_background_color(arcade.color.AMAZON)
        arcade.set_viewport(0, WIN_WIDTH - 1, 0, WIN_HEIGHT - 1)
        self.background = arcade.load_texture("blocks/rules.jpg")

    def on_draw(self):
        arcade.start_render()
        arcade.draw_texture_rectangle(WIN_WIDTH // 2, WIN_HEIGHT // 2, WIN_WIDTH, WIN_HEIGHT, self.background)

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        global OPEN_FLAG
        OPEN_FLAG = True
        for lvl in range(1, 4):
            main(lvl)


def main0():
    window = arcade.Window(WIN_WIDTH, WIN_HEIGHT, SCREEN_TITLE, center_window=True)
    view = IntroductionView()
    window.show_view(view)
    arcade.run()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == "__main__":
    main0()
    sys.excepthook()
