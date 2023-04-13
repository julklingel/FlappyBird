import pygame
import neat
import time
import os
import random


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


def drawWindow(win, bird):
    win.blit(bgImg, (0, 0))
    bird.draw(win)
    pygame.display.update()


def main():
    bird = Bird(230, 350)
    win = pygame.display.set_mode((winWidth, winHeight))
    clock = pygame.time.Clock()
    run = True

    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_q:
                    run = False

                if event.key == pygame.K_SPACE:
                    bird.jump()

        bird.move()
        drawWindow(win, bird)

    pygame.quit()
    quit()


main()
