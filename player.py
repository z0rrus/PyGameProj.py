from pygame import *
import pyganim
import os
import blocks
import monsters

MOVE_SPEED = 7
MOVE_EXTRA_SPEED = 2.5
WIDTH = 32
HEIGHT = 32
COLOR = "#888888"
JUMP_POWER = 10
JUMP_EXTRA_POWER = 1
GRAVITY = 0.35
ANIMATION_DELAY = 0.1
ANIMATION_SUPER_SPEED_DELAY = 0.05
ICON_DIR = os.path.dirname(__file__)

ANIMATION_RIGHT = [('%s/hero/r1.png' % ICON_DIR),
                   ('%s/hero/r2.png' % ICON_DIR),
                   ('%s/hero/r3.png' % ICON_DIR),
                   ('%s/hero/r4.png' % ICON_DIR),
                   ('%s/hero/r5.png' % ICON_DIR)]
ANIMATION_LEFT = [('%s/hero/l1.png' % ICON_DIR),
                  ('%s/hero/l2.png' % ICON_DIR),
                  ('%s/hero/l3.png' % ICON_DIR),
                  ('%s/hero/l4.png' % ICON_DIR),
                  ('%s/hero/l5.png' % ICON_DIR)]
ANIMATION_JUMP_LEFT = [('%s/hero/jl.png' % ICON_DIR, 0.1)]
ANIMATION_JUMP_RIGHT = [('%s/hero/jr.png' % ICON_DIR, 0.1)]
ANIMATION_JUMP = [('%s/hero/j.png' % ICON_DIR, 0.1)]
ANIMATION_STAY = [('%s/hero/0.png' % ICON_DIR, 0.1)]
ANIMATION_STAY_LEFT = [('%s/hero/0l.png' % ICON_DIR, 0.1)]
ANIMATION_DIE = [('%s/hero/die.png' % ICON_DIR, 0.1)]


class Player(sprite.Sprite):
    def __init__(self, x, y):
        sprite.Sprite.__init__(self)
        self.xvel = 0
        self.startX = x
        self.startY = y
        self.yvel = 0
        self.onGround = False
        self.image = Surface((WIDTH, HEIGHT))
        self.image.fill(Color(COLOR))
        self.rect = Rect(x, y, WIDTH, HEIGHT)
        self.image.set_colorkey(Color(COLOR))
        boltAnim = []
        boltAnimSuperSpeed = []
        for anim in ANIMATION_RIGHT:
            boltAnim.append((anim, ANIMATION_DELAY))
            boltAnimSuperSpeed.append((anim, ANIMATION_SUPER_SPEED_DELAY))
        self.boltAnimRight = pyganim.PygAnimation(boltAnim)
        self.boltAnimRight.play()
        self.boltAnimRightSuperSpeed = pyganim.PygAnimation(boltAnimSuperSpeed)
        self.boltAnimRightSuperSpeed.play()
        boltAnim = []
        boltAnimSuperSpeed = []
        for anim in ANIMATION_LEFT:
            boltAnim.append((anim, ANIMATION_DELAY))
            boltAnimSuperSpeed.append((anim, ANIMATION_SUPER_SPEED_DELAY))
        self.boltAnimLeft = pyganim.PygAnimation(boltAnim)
        self.boltAnimLeft.play()
        self.boltAnimLeftSuperSpeed = pyganim.PygAnimation(boltAnimSuperSpeed)
        self.boltAnimLeftSuperSpeed.play()

        self.boltAnimStay = pyganim.PygAnimation(ANIMATION_STAY)
        self.boltAnimStay.play()
        self.boltAnimStay.blit(self.image, (0, 0))  # По-умолчанию, стоим

        self.boltAnimStayLeft = pyganim.PygAnimation(ANIMATION_STAY_LEFT)
        self.boltAnimStayLeft.play()

        self.boltAnimJumpLeft = pyganim.PygAnimation(ANIMATION_JUMP_LEFT)
        self.boltAnimJumpLeft.play()

        self.boltAnimJumpRight = pyganim.PygAnimation(ANIMATION_JUMP_RIGHT)
        self.boltAnimJumpRight.play()

        self.boltAnimJump = pyganim.PygAnimation(ANIMATION_JUMP)
        self.boltAnimJump.play()

        self.boltAnimDie = pyganim.PygAnimation(ANIMATION_DIE)
        self.boltAnimDie.play()

        self.winner = False
        self.last_side = 'right'
        self.die_flag = False
        self.die_pic = False

    def update(self, left, right, up, running, platforms):
        if self.die_pic:
            self.die_pic = False
            self.die()
        if self.die_flag:
            self.image.fill(Color(COLOR))
            self.boltAnimDie.blit(self.image, (0, 0))
            self.die_pic = True
        else:
            if up:
                if self.onGround:
                    self.yvel = -JUMP_POWER
                    if running and (left or right):
                        self.yvel -= JUMP_EXTRA_POWER
                    self.image.fill(Color(COLOR))
                    self.boltAnimJump.blit(self.image, (0, 0))

            if left:
                self.last_side = 'left'
                self.xvel = -MOVE_SPEED
                self.image.fill(Color(COLOR))
                if running:
                    self.xvel -= MOVE_EXTRA_SPEED
                    if not up:
                        self.boltAnimLeftSuperSpeed.blit(self.image, (0, 0))
                else:
                    if not up:
                        self.boltAnimLeft.blit(self.image, (0, 0))
                if up:
                    self.boltAnimJumpLeft.blit(self.image, (0, 0))

            if right:
                self.last_side = 'right'
                self.xvel = MOVE_SPEED  # Право = x + n
                self.image.fill(Color(COLOR))
                if running:
                    self.xvel += MOVE_EXTRA_SPEED
                    if not up:
                        self.boltAnimRightSuperSpeed.blit(self.image, (0, 0))
                else:
                    if not up:
                        self.boltAnimRight.blit(self.image, (0, 0))
                if up:
                    self.boltAnimJumpRight.blit(self.image, (0, 0))

            if not (left or right):
                self.xvel = 0
                if not up:
                    self.image.fill(Color(COLOR))
                    if self.last_side == 'right':
                        self.boltAnimStay.blit(self.image, (0, 0))
                    else:
                        self.boltAnimStayLeft.blit(self.image, (0, 0))

            if not self.onGround:
                self.yvel += GRAVITY

            self.onGround = False;
            self.rect.y += self.yvel
            self.collide(0, self.yvel, platforms)

            self.rect.x += self.xvel
            self.collide(self.xvel, 0, platforms)

    def collide(self, xvel, yvel, platforms):
        for p in platforms:
            if sprite.collide_rect(self, p):
                if isinstance(p, blocks.BlockDie) or isinstance(p,
                                                                monsters.Monster):
                    self.die_flag = True
                elif isinstance(p, blocks.BlockTeleport):
                    self.teleporting(p.goX, p.goY)
                elif isinstance(p, blocks.Princess):
                    self.winner = True
                else:
                    if xvel > 0:
                        self.rect.right = p.rect.left

                    if xvel < 0:
                        self.rect.left = p.rect.right

                    if yvel > 0:
                        self.rect.bottom = p.rect.top
                        self.onGround = True
                        self.yvel = 0

                    if yvel < 0:
                        self.rect.top = p.rect.bottom
                        self.yvel = 0

    def teleporting(self, goX, goY):
        self.rect.x = goX
        self.rect.y = goY

    def die(self):
        time.wait(800)
        self.die_flag = False
        self.teleporting(self.startX, self.startY)
