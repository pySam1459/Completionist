import pygame
import pickle, os
pygame.init()

fullscreen = False
windowinfo = pygame.display.Info()
gamewidth, gameheight = windowinfo.current_w, windowinfo.current_h
if fullscreen: screen = pygame.display.set_mode((gamewidth, gameheight), pygame.FULLSCREEN)
else: screen = pygame.display.set_mode((gamewidth, gameheight))
clock = pygame.time.Clock()

AROUND = [[0, -1], [1, 0], [0, 1], [-1, 0]]


class Tile:
    def __init__(self, rect, start=False):
        self.x, self.y, self.w, self.h = rect

        self.start = start

    def active(self):
        self.render()

    def render(self):
        col = [200, 200, 200]
        if self.start:
            col = [255, 225, 0]

        screen.fill(col, [self.x + self.w/10, self.y + self.h/10, self.w*4/5, self.h*4/5])

    def adjust(self, top, i, j, level):
        self.w, self.h = level.tileW, level.tileH
        self.x, self.y = top[0] + i*self.w, top[1] + j*self.h


class Level:
    tileW = tileH = 200

    def __init__(self):
        self.next, self.start, self.array = [], None, [[]]
        self.top = [gamewidth/2 - self.tileW/2, gameheight/2 - self.tileH/2]
        self.addTile([gamewidth/2 - self.tileW/2, gameheight/2 - self.tileH/2, self.tileW, self.tileH], [0, 0], True)

        self.prevpress = pygame.mouse.get_pressed()

    def active(self):
        self.nextControl()
        self.arrayControl()
        self.save()

    def nextControl(self):
        if self.start is not None:
            mousepos, mousepress = getmouse()
            for rect, index in self.next:
                screen.fill([225, 225, 225], rect)

                if pointInRect(mousepos, rect) and mousepress[0] and not self.prevpress[0]:
                    self.addTile(rect, index, False)

            self.prevpress = mousepress

    def adjustArray(self):
        height, length = gameheight+1, gamewidth+1
        while height >= gameheight or length >= gamewidth:
            height, length = (len(self.array) + 2) * self.tileH, (len(self.array[0]) + 2) * self.tileW
            if height >= gameheight or length >= gamewidth:
                self.tileH -= 1
                self.tileW -= 1

        self.top = [(gamewidth - length)/2, (gameheight - height)/2]
        for j, row in enumerate(self.array):
            for i, tile in enumerate(row):
                if tile is not None:
                    tile.adjust(self.top, i+1, j+1, self)

    def arrayControl(self):
        for row in self.array:
            for tile in row:
                if tile is not None:
                    tile.active()

    def addTile(self, rect, index, start):
        if start:
            self.start = Tile(rect, True)
            self.array[0].append(self.start)

        else:
            i, j = index
            if exist(i, j, self.array):
                self.array[j][i] = Tile(rect)

            else:
                if i < 0:
                    for k, row in enumerate(self.array):
                        row.insert(0, None if k != j else Tile(rect))
                    index = [0, j]

                elif j < 0:
                    self.array.insert(0, [None if k != i else Tile(rect) for k in range(len(self.array[0]))])
                    index = [i, 0]

                elif i >= len(self.array[0]):
                    for k, row in enumerate(self.array):
                        row.append(None if k != j else Tile(rect))
                    index = [len(self.array[0])-1, j]

                elif j >= len(self.array):
                    self.array.append([None if k != i else Tile(rect) for k in range(len(self.array[0]))])
                    index = [i, len(self.array) - 1]

        self.adjustArray()
        self.createNext(index)

    def createNext(self, index):
        self.next = []
        i, j = index
        tile = self.array[j][i]
        for ax, ay in AROUND:
            ni, nj = ax + i, ay + j
            add = True
            if exist(ni, nj, self.array):
                if self.array[nj][ni] is not None:
                    add = False

            if add:
                self.next.append([[tile.x + ax*self.tileW, tile.y + ay*self.tileH, self.tileW, self.tileH], [ni, nj]])

    def save(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_s]:
            cat = input("Category: ").title()
            if cat in os.listdir("levels"):
                array = []
                for row in self.array:
                    array.append([])
                    for tile in row:
                        if tile is None:
                            array[-1].append(0)
                        else:
                            array[-1].append(tile.start + 1)

                info = {"array": array, "w": self.tileW, "h": self.tileH}
                with open("levels/{}/{}.pkl".format(cat, len(os.listdir("levels/" + cat)) + 1), "wb") as file:
                    pickle.dump(info, file, pickle.HIGHEST_PROTOCOL) # levels/Beginner/1

            else:
                print("{} is not a category".format(cat))

        elif keys[pygame.K_r]:
            self.tileW = self.tileH = 200
            self.next, self.start, self.array = [], None, [[]]
            self.top = [gamewidth / 2 - self.tileW / 2, gameheight / 2 - self.tileH / 2]
            self.addTile([gamewidth / 2 - self.tileW / 2, gameheight / 2 - self.tileH / 2, self.tileW, self.tileH], [0, 0], True)


def exist(i, j, array):
    return 0 <= i < len(array[0]) and 0 <= j < len(array)


def pointInRect(point, rect):
    return rect[0] < point[0] < rect[0] + rect[2] and rect[1] < point[1] < rect[1] + rect[3]


def getmouse():
    return pygame.mouse.get_pos(), pygame.mouse.get_pressed()


def text(surface, col, pos, size, text, font, center):
    largetext = pygame.font.SysFont(font, size)
    if center:
        textsurf = largetext.render(text, True, col)
        textrect = textsurf.get_rect()
        textrect.center = pos
        surface.blit(textsurf, textrect)
    else:
        textsurf = largetext.render(text, True, col)
        surface.blit(textsurf, pos)


def main():
    level = Level()
    print("Categories ------- \n1| Beginner (Tutorial Levels)\n2| Easy\n3| Medium\n4| Advanced\n5| Hard\n6| Expert")
    while True:
        screen.fill([255, 255, 255])

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        level.active()

        pygame.display.update()


if __name__ == "__main__":
    main()

