import pygame
import neat
import time
import os
import random

pygame.font.init()


winWidth = 500
winHeight = 800

print(os.getcwd())

birdImgs = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))), pygame.transform.scale2x(
    pygame.image.load(os.path.join("imgs", "bird2.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]
pipeImg = pygame.transform.scale2x(
    pygame.image.load(os.path.join("imgs", "pipe.png")))
baseImg = pygame.transform.scale2x(
    pygame.image.load(os.path.join("imgs", "base.png")))
bgImg = pygame.transform.scale2x(
    pygame.image.load(os.path.join("imgs", "bg.png")))

font = pygame.font.SysFont("comicsans", 50)


class Bird:
    IMGS = birdImgs
    maxRotation = 25
    rotVel = 20
    animationTime = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tickCount = 0
        self.vel = 0
        self.height = self.y
        self.imgCount = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.vel = -10.5  # negative to go up
        self.tickCount = 0
        self.height = self.y

    def move(self):
        self.tickCount += 1
        # calculate displacement, how many pixels we move up or down
        displacement = self.vel*self.tickCount + 1.5*self.tickCount**2

        if displacement >= 16:
            displacement = 16

        if displacement < 0:
            displacement -= 2

        self.y = self.y + displacement

        if displacement < 0 or self.y < self.height + 50:
            if self.tilt < self.maxRotation:
                self.tilt = self.maxRotation
        else:
            if self.tilt > -90:
                self.tilt -= self.rotVel

    def draw(self, win):
        self.imgCount += 1

        if self.imgCount < self.animationTime:
            self.img = self.IMGS[0]
        elif self.imgCount < self.animationTime*2:
            self.img = self.IMGS[1]
        elif self.imgCount < self.animationTime*3:
            self.img = self.IMGS[2]
        elif self.imgCount < self.animationTime*4:
            self.img = self.IMGS[1]
        elif self.imgCount == self.animationTime*4 + 1:
            self.img = self.IMGS[0]
            self.imgCount = 0

        if self.tilt <= -80:   # when we are nose diving, we don't want to flap wings
            self.img = self.IMGS[1]
            self.imgCount = self.animationTime*2

        rotatedImage = pygame.transform.rotate(self.img, self.tilt)
        newRect = rotatedImage.get_rect(
            center=self.img.get_rect(topleft=(self.x, self.y)).center)
        win.blit(rotatedImage, newRect.topleft)

    def getMask(self):
        return pygame.mask.from_surface(self.img)


class Pipe:
    GAP = 200
    VEL = 5

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.top = 0
        self.bottom = 0
        self.pipeTop = pygame.transform.flip(pipeImg, False, True)
        self.pipeBottom = pipeImg

        self.passed = False
        self.setHeights()

    def setHeights(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.pipeTop.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        win.blit(self.pipeTop, (self.x, self.top))
        win.blit(self.pipeBottom, (self.x, self.bottom))

    def collide(self, bird):
        birdMask = bird.getMask()
        topMask = pygame.mask.from_surface(self.pipeTop)
        bottomMask = pygame.mask.from_surface(self.pipeBottom)

        # must be integers --> pygame masks documentation
        topOffset = (self.x - bird.x, self.top - round(bird.y))
        bottomOffset = (self.x - bird.x, self.bottom - round(bird.y))

        # returns None if no overlap
        bPoint = birdMask.overlap(bottomMask, bottomOffset)
        tPoint = birdMask.overlap(topMask, topOffset)

        if tPoint or bPoint:
            return True

        return False


class Base:
    VEL = 5  # same as pipe
    WIDTH = baseImg.get_width()
    IMG = baseImg

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


def drawWindow(win, birds, pipes, base, score):
    win.blit(bgImg, (0, 0)),

    for pipe in pipes:
        pipe.draw(win)
    
    for bird in birds:
        bird.draw(win)

    base.draw(win)
    score = font.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(score, (winWidth - 10 - score.get_width(), 10))

    pygame.display.update()


def gameOver(win):
    failMsg = font.render("You failed!", 1, (0, 0, 0))
    win.blit(failMsg, (winWidth/2 - failMsg.get_width()/2, 200))


def main(genomes, config):
    nets = []
    ge = []
    birds = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        g.fitness = 0
        ge.append(g)

    base = Base(730)
    pipes = [Pipe(700)]
    win = pygame.display.set_mode((winWidth, winHeight))
    clock = pygame.time.Clock()
    run = True
    score = 0

    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_q:
                    run = False
                    pygame.quit()
                    quit()

        pipeIndex = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].pipeTop.get_width():
                pipeIndex = 1
        else:
            run = False
            break

        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1

            output = nets[x].activate(
                (bird.y, abs(bird.y - pipes[pipeIndex].height), abs(bird.y - pipes[pipeIndex].bottom)))

            if output[0] > 0.5:
                bird.jump()

        base.move()

        pipeList = []
        addPipe = False
        for pipe in pipes:
            for x, bird in enumerate(birds):

                if pipe.collide(bird):
                    ge[x].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    addPipe = True
            if pipe.x + pipe.pipeTop.get_width() < 0:
                pipeList.append(pipe)

            pipe.move()

        if addPipe:
            score += 1
            for g in ge:
                g.fitness += 5

            pipes.append(Pipe(700))

        for pipe in pipeList:
            pipes.remove(pipe)

        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        drawWindow(win, birds, pipes, base, score)



def run(config_file):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation, config_file)

    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main, 50)


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)
