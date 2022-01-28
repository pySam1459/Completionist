import pygame
import pickle, random, os
pygame.init()

fullscreen = False#True
windowinfo = pygame.display.Info()
gamewidth, gameheight = windowinfo.current_w, windowinfo.current_h

gamewidth, gameheight = 1920, 1080
if fullscreen: screen = pygame.display.set_mode((gamewidth, gameheight), pygame.FULLSCREEN)
else: screen = pygame.display.set_mode((gamewidth, gameheight))
clock = pygame.time.Clock()

AROUND = [[0, -1], [1, 0], [0, 1], [-1, 0]]
levels = ["Easy", "Medium", "Advanced", "Hard", "Expert"]


class Tile:
    def __init__(self, i, j, x, y, w, h, start, level, col):
        self.x, self.y, self.i, self.j = x, y, i, j
        self.w, self.h = w, h
        self.rect = [self.x, self.y, self.w, self.h]
        self.level, self.col = level, col
        self.col2 = [255 - self.col[0], 255 - self.col[1], 255 - self.col[2]]

        self.theStart = self.state = start
        self.start = self.end = 0
        self.rank = 1 if self.theStart else -10

        self.changed = False

    def active(self):
        self.click()
        if self.state:
            self.getAround()
        
        self.render()

    def click(self):
        mousepos, mousepress = getmouse()
        if pointInRect(mousepos, self.rect) and mousepress[0] and not self.changed:
            self.changed = True
            if self.state:
                self.level.resetLine(self.rank)
                self.level.current = [self.i, self.j]
                self.level.getAvailable()
                self.end = 0

            elif [self.i, self.j] in self.level.available and not self.theStart:
                self.state = True
                self.rank = self.level.array[self.level.current[1]][self.level.current[0]].rank + 1
                self.level.current = [self.i, self.j]
                self.level.getAvailable()

        if not mousepress[0]:
            self.changed = False

    def getAround(self):
        count = 1
        for ax, ay in AROUND:
            ni, nj = self.i + ax, self.j + ay
            if exist(ni, nj, self.level.array):
                tile = self.level.array[nj][ni]
                if tile is not None:
                    if tile.rank + 1 == self.rank:
                        self.start = count
                    elif tile.rank - 1 == self.rank:
                        self.end = count

            count += 1

    def render(self):
        screen.fill([200, 200, 200], [self.x + self.w/10, self.y + self.h/10, self.w*4/5, self.h*4/5])

        if self.state:
            line = []
            for val in [self.start, self.end]:
                rect = [self.x + self.w / 5, self.y + self.h / 5, self.w - self.w / 2.5, self.h - self.h / 2.5]
                if val == 1:
                    rect[1], rect[3] = self.y-2, self.h - self.h / 5 + 2
                    line.append([self.x + self.w/2, self.y-2])
                elif val == 2:
                    rect[2] = self.w - self.w / 5 + 2
                    line.append([self.x + self.w + 2, self.y + self.h/2])
                elif val == 3:
                    rect[3] = self.h - self.h / 5 + 2
                    line.append([self.x + self.w/2, self.y + self.h + 2])
                elif val == 4:
                    rect[0], rect[2] = self.x-2, self.w - self.w / 5 + 2
                    line.append([self.x-2, self.y + self.h/2])

                screen.fill(self.col, rect)
            for l in line:
                pygame.draw.line(screen, self.col2, [self.x + self.w/2, self.y + self.h/2], l, 3)


class Level:
    w = h = 200

    def __init__(self, cat, name):
        self.cat = self.name = None
        self.col, self.array, self.current = [], [], None
        self.available, self.win = [], False

        self.load(cat, name)
        self.backButton = Button([gamewidth-60, 10, 50, 50], "X", [50, 50, 50], [100, 100, 100])

    def load(self, cat, name):
        finish = False
        try:
            with open("levels/{}/{}.pkl".format(cat, name), "rb") as file:
                info = pickle.load(file)
            if cat != "Beginner":
                levelInfo[cat][int(name)-1] = True
                updateLevelInfo()
            self.name, self.cat = name, cat
            self.w, self.h = info["w"], info["h"]
            self.col = [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
            self.array, self.current = self.createArray(info["array"])
            self.available = []
            self.getAvailable()

            self.win = False

        except:
            if cat != "Beginner":
                index = levels.index(cat) + 1
                if index < len(levels):
                    levelInfo[levels[index]][0] = True
            finish = True

        return finish

    def createArray(self, array):
        width, height = len(array[0])*self.w, len(array)*self.h
        x, y = [(gamewidth - width)/2, (gameheight - height)/2]
        current = []
        for j, row in enumerate(array):
            for i, val in enumerate(row):
                if val == 0:
                    array[j][i] = None
                else:
                    array[j][i] = Tile(i, j, x + i*self.w, y + j*self.h, self.w, self.h, val == 2, self, self.col)
                    if val == 2:
                        current = [i, j]

        return array, current

    def getAvailable(self):
        self.available = []
        for ax, ay in AROUND:
            ni, nj = self.current[0] + ax, self.current[1] + ay
            if exist(ni, nj, self.array):
                if self.array[nj][ni] is not None:
                    if not self.array[nj][ni].state:
                        self.available.append([ni, nj])

    def active(self):
        self.arrayControl()
        finish = self.winControl()
        self.render()
        if self.backButton.active():
            finish = True
        return finish

    def arrayControl(self):
        self.win = True
        for row in self.array:
            for tile in row:

                if tile is not None:
                    tile.active()

                    if not tile.state:
                        self.win = False

    def winControl(self):
        finish = False
        if self.win and not pygame.mouse.get_pressed()[0]:
            finish = self.load(self.cat, str(int(self.name) + 1))
        return finish

    def resetLine(self, rank):
        for row in self.array:
            for tile in row:
                if tile is not None:
                    if tile.rank > rank:
                        tile.state, tile.rank = 0, -10
                        tile.end = 0

    def render(self):
        text(screen, [0, 0, 0], [5, 5], 25, "{} {}".format(self.cat.title(), self.name), "comicsansms", False)

    def renderTiles(self):
        for row in self.array:
            for tile in row:
                if tile is not None:
                    tile.render()


class Button:
    def __init__(self, rect, phrase, col, col2, col3=[200, 200, 200]):
        self.rect, self.text, self.col = rect, phrase, col
        self.col2, self.col3 = col2, col3

        self.size = int(self.rect[3]/2)
        self.adaptSize()
       
        self.clicked = False
        self.prevpress = pygame.mouse.get_pressed()

    def adaptSize(self):
        width = self.rect[2]+1000
        while width > self.rect[2]:
            test = pygame.font.SysFont("comicsansms", self.size)
            width, height = test.size(self.text)
            if width > self.rect[2]:
                self.size -= 1

    def active(self, allow=True):
        activate = False
        col, rect = self.col[:], self.rect[:]
        mousepos, mousepress = getmouse()
        size = self.size
        
        if pointInRect(mousepos, self.rect):
            rect = [rect[0] - rect[2]/10, rect[1] - rect[3]/10, rect[2]*6/5, rect[3]*6/5]
            size = int(self.size*6/5)
            if mousepress[0]:
                col = self.col2[:]
                self.clicked = True

            if not mousepress[0] and self.prevpress[0] and self.clicked:
                activate = True
                self.clicked = False

            elif not mousepress[0]:
                self.clicked = False

        else:
            self.clicked = False

        self.prevpress = mousepress
        if not allow:
            col = [225, 225, 225]
            activate = False

        screen.fill(col, rect)
        text(screen, self.col3, [rect[0] + rect[2] / 2, rect[1] + rect[3] / 2], size, self.text, "comicsansms", True)

        return activate


def exist(i, j, array):
    return 0 <= i < len(array[0]) and 0 <= j < len(array)


def pointInRect(point, rect):
    return rect[0] < point[0] < rect[0] + rect[2] and rect[1] < point[1] < rect[1] + rect[3]


def getmouse():
    return pygame.mouse.get_pos(), pygame.mouse.get_pressed()


def text(surface, col, pos, size, phrase, font, center):
    largetext = pygame.font.SysFont(font, size)
    if center:
        textsurf = largetext.render(phrase, True, col)
        textrect = textsurf.get_rect()
        textrect.center = pos
        surface.blit(textsurf, textrect)
    else:
        textsurf = largetext.render(phrase, True, col)
        surface.blit(textsurf, pos)


def updateLevelInfo():
    with open("levelInfo.pkl", "wb") as file:
        pickle.dump(levelInfo, file, pickle.HIGHEST_PROTOCOL)


with open("levelInfo.pkl", "rb") as file:
    levelInfo = pickle.load(file)


def menu():
    background = pygame.image.load("titleScreen.png")
    backButton = Button([15, 10, 100, 50], "<---", [50, 50, 50], [100, 100, 100])

    state = "front"
    playButton = Button([gamewidth/2-500, gameheight/3, 1000, 250], "Play", [0, 0, 225], [0, 0, 255])
    createButton = Button([gamewidth/2-500, gameheight/1.5, 1000, 250], "Create Level", [0, 0, 225], [0, 0, 255])

    # Categories
    cols = [[[60, 255, 0], [0, 205, 15]],
            [[0, 250, 255], [0, 150, 200]], [[0, 40, 255], [25, 0, 170]],
            [[190, 0, 255], [140, 0, 200]], [[255, 0, 0], [200, 0, 0]]]
    rectangles = [[200, 350, gamewidth/2-300, 150], [200, 550, gamewidth/2-300, 150],
                  [gamewidth/2+100, 350, gamewidth/2-300, 150], [gamewidth/2+100, 550, gamewidth/2-300, 150], [gamewidth/2 - (gamewidth/2-300)/2, 750, gamewidth/2-300, 150]]
    categories = [Button(rect, cat.title(), col[0], col[1], [127, 127, 127]) for cat, col, rect in zip(levels, cols, rectangles)]

    # Levels
    lengths = [[len(os.listdir("levels/"+cat)), cat] for cat in levels]
    levelButtons = []
    width = height = 200
    x, y = 150, 250
    for i in range(max(lengths)[0]):
        rect = [x, y, width, height]
        levelButtons.append(Button(rect, str(i+1), [0, 0, 225], [0, 0, 255]))
        if x+width*2+25 > gamewidth:
            y += height + 25
            x = 150
        else:
            x += width + 25

    cat, leng = None, 0
    while True:
        updateImage = True
        screen.blit(background, [0, 0])
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_x:
                    pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pass
                # print(event.pos)

        if state == "front":
            text(screen, [50, 50, 50], [gamewidth/2, gameheight/5], 150, "Completionist", "comicsansms", True)
            if playButton.active():
                if levelInfo["tutorial"]:
                    state = "tutorial"
                else:
                    state = "categories"

            if createButton.active():
                state = "create"

            if backButton.active():
                pygame.quit()
                quit()

        elif state == "tutorial":
            main("Beginner", "1")
            state, levelInfo["tutorial"] = "categories", False
            updateLevelInfo()

        elif state == "categories":
            text(screen, [50, 50, 50], [gamewidth/2, 150], 150, "Categories", "comicsansms", True)
            if backButton.active():
                state = "front"

            for button, info in zip(categories, lengths):
                if button.active():
                    leng, cat = info
                    state = "levels"

        elif state == "levels":
            text(screen, [50, 50, 50], [gamewidth / 2, 150], 150, "Levels", "comicsansms", True)
            if backButton.active():
                state = "categories"

            for i, button in enumerate(levelButtons):
                if button.active(levelInfo[cat][i]):
                    main(cat, str(i+1))
                    state, updateImage = "categories", False
                if i+1 >= leng:
                    break

        if updateImage:
            pygame.display.update()


def main(cat, name):
    level = Level(cat, name)
    while True:
        screen.fill([255, 255, 255])

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_x:
                    pygame.quit()
                    quit()

        if level.active():
            break

        pygame.display.update()


if __name__ == "__main__":
    menu()

