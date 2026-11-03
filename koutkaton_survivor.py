import math
from abc import ABC, abstractmethod
import os
import sys
import pygame as pg


# 画像を相対パスで読み込めるよう、実行場所をこのファイルのあるフォルダにする
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# ゲーム画面と各キャラクターの基本設定
WIDTH, HEIGHT = 1100, 650
PLAYER_SPEED = 5
ENEMY_SPEED = 1.5
EGG_SPEED = 8


def load_image(path: str, size: tuple[int, int]) -> pg.Surface:
    """画像を読み込み、ゲーム画面に合う大きさへ縮小する。"""
    image = pg.image.load(path).convert_alpha()
    return pg.transform.smoothscale(image, size)


def make_student() -> pg.Surface:
    """敵の生徒画像を読み込む。"""
    return load_image("fig/生徒.png", (52, 72))


class enemy(pg.sprite.Sprite,ABC):
    """敵を管理する抽象クラス。"""
    def __init__(self,x,y,hp,img):
        super().__init__()

        self.hp = hp
        self.image = img
        self.rect = self.image.get_rect(center=(x, y))

    def move(self, player_rect: pg.Rect) -> None:
        """主人公の位置に向かって移動する。"""
        direction = pg.Vector2(player_rect.center) - pg.Vector2(self.rect.center)
        if direction.length_squared():
            direction.scale_to_length(ENEMY_SPEED)
            self.rect.move_ip(round(direction.x), round(direction.y))

    def damage(self, amount: int) -> None:
        """敵のHPを減らす。"""
        self.hp -= amount
        if self.hp <= 0:
            self.kill()

    @abstractmethod
    def update(self, player_rect: pg.Rect) -> None:
        pass


class nomal_enemy(enemy):
    """敵の生徒を管理するクラス。"""
    def __init__(self, x: int, y: int, hp: int = 1):
        img = pg.image.load("fig/生徒.png").convert_alpha()
        imgs = [pg.transform.scale(img, (80, 72))]
        super().__init__(x, y, hp,img)
        self.imgs = imgs
        self.image = self.imgs[0]
        self.rect = self.image.get_rect(center=(x, y))

    def update(self, player_rect: pg.Rect) -> None:
        """敵の状態を更新する。"""
        self.move(player_rect)


class yanki_enemy(enemy):
    """敵のヤンキーを管理するクラス。"""
    def __init__(self, x: int, y: int, hp: int = 1):
        img = pg.image.load("fig/yanki-.png").convert_alpha()
        imgs = [pg.transform.scale(img, (80, 80))]
        super().__init__(x, y, hp,img)
        self.imgs = imgs
        self.image = self.imgs[0]
        self.rect = self.image.get_rect(center=(x, y))

    def update(self, player_rect: pg.Rect) -> None:
        """敵の状態を更新する。"""
        self.move(player_rect)


class kamathu_enemy(enemy):
    """敵の蒲田マスコットを管理するクラス。"""
    def __init__(self, x: int, y: int, hp: int = 1):
        img = pg.image.load("fig/kamathu2.png").convert_alpha()
        imgs = [pg.transform.scale(img, (80, 80))]
        super().__init__(x, y, hp,img)
        self.imgs = imgs
        self.image = self.imgs[0]
        self.rect = self.image.get_rect(center=(x, y))

    def update(self, player_rect: pg.Rect) -> None:
        """敵の状態を更新する。"""
        self.move(player_rect)

class pathi_enemy(enemy):
    """敵の工学院マスコットを管理するクラス。"""
    def __init__(self, x: int, y: int, hp: int = 1):
        img = pg.image.load("fig/pathi.png").convert_alpha()
        imgs = [pg.transform.scale(img, (80, 80))]
        super().__init__(x, y, hp,img)
        self.imgs = imgs
        self.image = self.imgs[0]
        self.rect = self.image.get_rect(center=(x, y))

    def update(self, player_rect: pg.Rect) -> None:
        """敵の状態を更新する。"""
        self.move(player_rect)


class pfas_enemy(enemy):
    """敵のPFASを管理するクラス。"""
    def __init__(self, x: int, y: int, hp: int = 10000000000000000):
        img = pg.image.load("fig/PFAS.png").convert_alpha()
        imgs = [pg.transform.scale(img, (200, 200))]
        super().__init__(x, y, hp,img)
        self.imgs = imgs
        self.image = self.imgs[0]
        self.rect = self.image.get_rect(center=(x, y))

    def update(self, player_rect: pg.Rect) -> None:
        """敵の状態を更新する。"""
        self.move(player_rect)
   
    


def create_egg(position: tuple[int, int], direction: tuple[float, float]) -> tuple[pg.Surface, pg.Rect, tuple[float, float]]:
    """こうかとんの向いている方向へ進む卵を生成する。"""
    # 卵の見た目をSurfaceに描画する
    egg = pg.Surface((18, 24), pg.SRCALPHA)
    pg.draw.ellipse(egg, (255, 250, 220), egg.get_rect())
    pg.draw.ellipse(egg, (180, 140, 80), egg.get_rect(), 2)

    # 向いている方向を正規化し、卵の速度を一定にする
    dx, dy = direction
    distance = math.hypot(dx, dy) or 1
    velocity = (dx / distance * EGG_SPEED, dy / distance * EGG_SPEED)
    rect = egg.get_rect(center=position)
    return egg, rect, velocity


def main() -> None:
    pg.display.set_caption("こうかとんサバイバー")
    screen = pg.display.set_mode((WIDTH, HEIGHT))

    # 背景画像を画面全体に広げて表示する
    background = pg.transform.smoothscale(
        pg.image.load("fig/背景.png").convert(), (WIDTH, HEIGHT)
    )

    # キャラクター画像と初期位置を用意する
    player_image = load_image("fig/こうかとん.png", (72, 72))
    enemys = pg.sprite.Group()
    enemys.add(pfas_enemy(WIDTH - 150, HEIGHT // 2))
    player_rect = player_image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    enemy = pfas_enemy(WIDTH - 150, HEIGHT // 2)
    enemy_rect = enemy.rect
    enemy_alive = True
    facing = (1.0, 0.0)

    # 発射中の卵をSurface、位置、速度の組として管理する
    eggs: list[tuple[pg.Surface, pg.Rect, tuple[float, float]]] = []
    clock = pg.time.Clock()

    while True:
        # 終了操作とスペースキーによる卵の発射を処理する
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                eggs.append(create_egg(player_rect.center, facing))

        # W/A/S/Dキーの入力から移動方向を作る
        movement = pg.Vector2(0, 0)
        keys = pg.key.get_pressed()
        if keys[pg.K_w]:
            movement.y -= PLAYER_SPEED
        if keys[pg.K_s]:
            movement.y += PLAYER_SPEED
        if keys[pg.K_a]:
            movement.x -= PLAYER_SPEED
        if keys[pg.K_d]:
            movement.x += PLAYER_SPEED
        if movement.length_squared():
            movement.scale_to_length(PLAYER_SPEED)
            # 移動した方向を、こうかとんが向いている方向として記録する
            facing = (movement.x, movement.y)
        player_rect.move_ip(round(movement.x), round(movement.y))
        # こうかとんが画面外へ出ないように位置を制限する
        player_rect.clamp_ip(screen.get_rect())

        # 生徒が生存している間だけ、こうかとんへ近づける
        if enemy_alive:
            direction = pg.Vector2(player_rect.center) - pg.Vector2(enemy_rect.center)
            if direction.length_squared():
                direction.scale_to_length(ENEMY_SPEED)
                enemy_rect.move_ip(round(direction.x), round(direction.y))

        # 卵を移動し、敵への命中または画面外への移動を確認する
        updated_eggs = []
        for egg, egg_rect, velocity in eggs:
            egg_rect.move_ip(round(velocity[0]), round(velocity[1]))
            if enemy_alive and egg_rect.colliderect(enemy_rect):
                # 命中した生徒を消し、命中した卵も削除する
                enemy_alive = False
                continue
            if screen.get_rect().colliderect(egg_rect):
                updated_eggs.append((egg, egg_rect, velocity))
        eggs = updated_eggs

        # 背景、敵、こうかとん、卵の順番で画面に描画する
        screen.blit(background, (0, 0))
        if enemy_alive:
            screen.blit(enemy.image, enemy_rect)
        screen.blit(player_image, player_rect)
        for egg, egg_rect, _ in eggs:
            screen.blit(egg, egg_rect)
        pg.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()