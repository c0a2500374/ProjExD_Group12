import math
import random
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


#アイテム機能の実装
#1GPAは体力（hp）回復、金のトイレはお金(coin)を増やす
class Items:
    """
    2種類のアイテムの出現
    """

    def __init__(self, kind, image_path, screen_size):
        self.kind = kind  
        self.min_interval = 4000  #アイテムが次に出現する時間
        self.max_interval = 15000  
        self.screen_width, self.screen_height = screen_size
        self.image = pg.image.load(image_path).convert_alpha()
        self.image = pg.transform.scale(self.image, (48, 48))
        self.rect = self.image.get_rect()
        self.active = False
        self.next_spawn = self._next_spawn_time()

    def _next_spawn_time(self):
        return pg.time.get_ticks() + random.randint(self.min_interval, self.max_interval)

    def update(self, player_rect, status):
        now = pg.time.get_ticks()

        if not self.active and now >= self.next_spawn:
            self.rect.x = random.randint(0, max(0, self.screen_width - self.rect.width))
            self.rect.y = random.randint(0, max(0, self.screen_height - self.rect.height))
            self.active = True

        if self.active and self.rect.colliderect(player_rect):
            self.active = False # 取得したら消える。
            self.next_spawn = self._next_spawn_time()
        
            if self.kind == "coin": # 金のトイレを取得したとき
                status.coin += 10
                #print(f"金のトイレ取得！ 現在のコイン：{status.coin}")
            elif self.kind == "hp": # 1GPAを取得したとき
                status.hp += 1
                #print(f"1GPA取得！ 現在のGPA：{status.hp}")  

    def draw(self, screen):
        if self.active:
            screen.blit(self.image, self.rect)



def main() -> None:
    pg.display.set_caption("こうかとんサバイバー")
    screen = pg.display.set_mode((WIDTH, HEIGHT))

    # 背景画像を画面全体に広げて表示する
    background = pg.transform.smoothscale(
        pg.image.load("fig/背景.png").convert(), (WIDTH, HEIGHT)
    )

    # キャラクター画像と初期位置を用意する
    player_image = load_image("fig/こうかとん.png", (72, 72))
    student_image = make_student()
    player_rect = player_image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    enemy_rect = student_image.get_rect(center=(WIDTH - 150, HEIGHT // 2))
    enemy_alive = True
    facing = (1.0, 0.0)

    # 発射中の卵をSurface、位置、速度の組として管理する
    eggs: list[tuple[pg.Surface, pg.Rect, tuple[float, float]]] = []
    clock = pg.time.Clock()

    items = [Items("hp", "fig/1GPA.png", (WIDTH, HEIGHT)),Items("coin", "fig/金のトイレ.png", (WIDTH, HEIGHT)),]
    
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

        for item in items:
            item.update(player_rect, status)

        # 背景、敵、こうかとん、卵の順番で画面に描画する
        screen.blit(background, (0, 0))
        if enemy_alive:
            screen.blit(student_image, enemy_rect)
        screen.blit(player_image, player_rect)
        for egg, egg_rect, _ in eggs:
            screen.blit(egg, egg_rect)

        for item in items:
            item.draw(screen)
        pg.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()