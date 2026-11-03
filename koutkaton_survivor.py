import math
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


class Status:
    """
    こうかとんのHP・所持コインを管理するクラス
    """
    def __init__(self):
        self.max_hp = 1.0
        self.hp = 1.0
        self.coin = 1000000000  # テスト用初期コイン

        # 各項目の強化レベル
        self.speed_level = 0
        self.hp_upgrade_level = 0

        # 各項目の上限回数を設定
        self.max_hp_upgrade_level = 30

    def get_player_speed(self) -> float:
        """
        移動速度：初期値5.0 ＋ レベルにつき0.8上昇
        """
        return 5.0 + (self.speed_level * 0.8)


def draw_ui(screen: pg.Surface, font: pg.font.Font, stats: Status) -> None:
    """
    画面左上にHP,コインを描画する
    """
    # レベル・HP・コイン表示
    info_text = f"GPA: {stats.hp:1f}/{stats.max_hp:.1f}  COINS: {stats.coin}G"
    txt_surf = font.render(info_text, True, (255, 255, 255))
    screen.blit(txt_surf, (20, 15))


def open_shop(screen: pg.Surface, clock: pg.time.Clock, font: pg.font.Font, stats: Status) -> None:
    """
    ショップ画面（ポーズ中）の描画と入力処理
    """
    in_shop = True

    prices = {
        "speed": 30,
        "max_hp": 50,
    }

    while in_shop:
        cost_speed = int(prices["speed"] * (1.3 ** stats.speed_level))
        cost_hp = int(prices["max_hp"] * (1.3 ** stats.hp_upgrade_level))

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            
            if event.type == pg.KEYDOWN:
                if event.key in (pg.K_b, pg.K_ESCAPE):
                    in_shop = False

                # [1] 移動速度 UP
                elif event.key == pg.K_1 and stats.coin >= cost_speed:
                    stats.coin -= cost_speed
                    stats.speed_level += 1

                # [2] 最大HP UP
                elif event.key == pg.K_2 and stats.coin >= cost_hp and stats.hp_upgrade_level < stats.max_hp_upgrade_level:
                    stats.coin -= cost_hp
                    stats.hp_upgrade_level += 1
                    stats.max_hp += 0.1
                    stats.hp += 0.1

        # 背景の暗転
        overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        # UI描画
        title_surface = font.render("GAKUSYOKU : Bkey -> close", True, (255, 215, 0))
        screen.blit(title_surface, (WIDTH // 2 - title_surface.get_width() // 2, 70))

        info_surface = font.render(f"myCoin: {stats.coin} Coin  |  HP: {stats.hp:.1f}/{stats.max_hp:.1f}", True, (255, 255, 255))
        screen.blit(info_surface, (WIDTH // 2 - info_surface.get_width() // 2, 130))

        if stats.max_hp_upgrade_level <= stats.hp_upgrade_level:
            hp_cost_text = "MAX"
        else:
            hp_cost_text = f"{cost_hp} Coin"

        items = [
            f"[1] speedUP  (Lv.{stats.speed_level})  : {cost_speed} Coin",
            f"[2] maxhpUP  (Lv.{stats.hp_upgrade_level}/{stats.max_hp_upgrade_level})  : {hp_cost_text}",
        ]

        for i, text in enumerate(items):
            color = (255, 255, 255)
            if ((i == 0 and stats.coin < cost_speed) or
               (i == 1 and stats.coin < cost_hp)):
                color = (120, 120, 120)

            item_surface = font.render(text, True, color)
            screen.blit(item_surface, (WIDTH // 2 - 200, 220 + i * 55))

        pg.display.flip()
        clock.tick(60)


def main() -> None:
    pg.display.set_caption("こうかとんサバイバー")
    screen = pg.display.set_mode((WIDTH, HEIGHT))

    font = pg.font.SysFont("arial", 26)

    background = pg.transform.smoothscale(
        pg.image.load("fig/背景.png").convert(), (WIDTH, HEIGHT)
    )

    player_image = load_image("fig/こうかとん.png", (72, 72))
    student_image = make_student()
    player_rect = player_image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    enemy_rect = student_image.get_rect(center=(WIDTH - 150, HEIGHT // 2))
    enemy_alive = True
    facing = (1.0, 0.0)

    stats = Status()
    shoot_timer = 0

    eggs: list[tuple[pg.Surface, pg.Rect, tuple[float, float]]] = []
    clock = pg.time.Clock()

    while True:
        shoot_timer += 1

        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                eggs.append(create_egg(player_rect.center, facing))
            if event.type == pg.KEYDOWN and event.key == pg.K_b:
                open_shop(screen, clock, font, stats)

        # プレイヤー移動
        movement = pg.Vector2(0, 0)
        speed = stats.get_player_speed()  # status内のスピードを参照
        keys = pg.key.get_pressed()
        if keys[pg.K_w]:
            movement.y -= speed
        if keys[pg.K_s]:
            movement.y += speed
        if keys[pg.K_a]:
            movement.x -= speed
        if keys[pg.K_d]:
            movement.x += speed
        if movement.length_squared():
            movement.scale_to_length(speed)
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
                stats.coin += 20     # コイン獲得
                continue
            if screen.get_rect().colliderect(egg_rect):
                updated_eggs.append((egg, egg_rect, velocity))
        eggs = updated_eggs

        # 背景、敵、こうかとん、卵の順番で画面に描画する
        screen.blit(background, (0, 0))
        if enemy_alive:
            screen.blit(student_image, enemy_rect)
        screen.blit(player_image, player_rect)
        for egg, egg_rect, _ in eggs:
            screen.blit(egg, egg_rect)

        # UI描画
        draw_ui(screen, font, stats)

        pg.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()