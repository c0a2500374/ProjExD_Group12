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
BEAM_SPEED = 12
BOMB_SPEED = 7
PLAYER_HP = 100
ENEMY_HP = 3
MY_ATTACK = 1
BEAM_ATTACK = 1
BOMB_ATTACK = 1
ENEMY_ATTACK = 1
EXP_REWARD = 1
COIN_REWARD = 1
CONTACT_DAMAGE_INTERVAL = 500


def load_image(path: str, size: tuple[int, int]) -> pg.Surface:
    """画像を読み込み、ゲーム画面に合う大きさへ縮小する。"""
    image = pg.image.load(path).convert_alpha()
    return pg.transform.smoothscale(image, size)


def make_student() -> pg.Surface:
    """敵の生徒画像を読み込む。"""
    return load_image("fig/生徒.png", (52, 72))


class Buki(pg.sprite.Sprite):
    """こうかとんが持つ武器のクラス。"""
    def __init__(self, image: pg.Surface, position: tuple[int, int]) -> None:
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=position)


def create_egg(
    position: tuple[int, int], direction: tuple[float, float]
) -> tuple[pg.Surface, pg.Rect, tuple[float, float]]:
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


class Beam(pg.sprite.Sprite):
    """片柳ビーム攻撃のクラス。"""
    def __init__(
        self,
        image: pg.Surface,
        position: tuple[int, int],
        direction: tuple[float, float],
    ) -> None:
        super().__init__()
        # 画像の向きを、こうかとんが向いている方向に合わせる
        angle = math.degrees(math.atan2(-direction[1], direction[0]))
        self.image = pg.transform.rotate(image, angle)
        self.rect = self.image.get_rect(center=position)
        length = math.hypot(*direction) or 1
        self.velocity = (
            direction[0] / length * BEAM_SPEED,
            direction[1] / length * BEAM_SPEED,
        )

    def update(self) -> None:
        """ビームを発射方向へ移動させる。"""
        self.rect.move_ip(round(self.velocity[0]), round(self.velocity[1]))

class bomb(pg.sprite.Sprite):
    """爆弾のクラス。"""
    def __init__(
        self,
        image: pg.Surface,
        position: tuple[int, int],
        direction: tuple[float, float],
    ) -> None:
        super().__init__()
        angle = math.degrees(math.atan2(-direction[1], direction[0]))
        self.image = pg.transform.rotate(image, angle)
        self.rect = self.image.get_rect(center=position)
        length = math.hypot(*direction) or 1
        self.velocity = (
            direction[0] / length * BOMB_SPEED,
            direction[1] / length * BOMB_SPEED,
        )

    def update(self) -> None:
        """爆弾を発射方向へ移動させる。"""
        self.rect.move_ip(round(self.velocity[0]), round(self.velocity[1]))
        self.rect = self.image.get_rect(center=position)
        length = math.hypot(*direction) or 1
        self.velocity = (direction[0] / length * BEAM_SPEED,direction[1] / length * BEAM_SPEED,)


class horse(pg.sprite.Sprite):
    """馬のクラス。"""
    def __init__(self, image: pg.Surface, position: tuple[int, int]) -> None:
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=position)

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
    beam_image = load_image("fig/beam_katayanagi.png", (180, 44))
    bomb_image = load_image("fig/notepc.png", (56, 56))
    uma_image = load_image("fig/uma.png", (72, 72))
    player_rect = player_image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    enemy_rect = student_image.get_rect(center=(WIDTH - 150, HEIGHT // 2))
    enemy_alive = True
    facing = (1.0, 0.0)
    myhp = PLAYER_HP
    enemy_hp = ENEMY_HP
    my_attack = MY_ATTACK
    enemy_attack = ENEMY_ATTACK
    exp = 0
    coin = 0
    last_contact_damage = -CONTACT_DAMAGE_INTERVAL

    # 発射中の卵をSurface、位置、速度の組として管理する
    eggs: list[tuple[pg.Surface, pg.Rect, tuple[float, float]]] = []
    beams: list[Beam] = []
    bombs: list[bomb] = []
    clock = pg.time.Clock()

    while True:
        # 終了操作とスペースキーによる卵の発射を処理する
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                eggs.append(create_egg(player_rect.center, facing))
            if event.type == pg.KEYDOWN and event.key == pg.K_b:
                beams.append(Beam(beam_image, player_rect.center, facing))
            if event.type == pg.KEYDOWN and event.key == pg.K_n:
                bombs.append(bomb(bomb_image, player_rect.center, facing))

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
            now = pg.time.get_ticks()
            if player_rect.colliderect(enemy_rect) and (
                now - last_contact_damage >= CONTACT_DAMAGE_INTERVAL
            ):
                myhp -= enemy_attack
                last_contact_damage = now

        # 卵を移動し、敵への命中または画面外への移動を確認する
        updated_eggs = []
        for egg, egg_rect, velocity in eggs:
            egg_rect.move_ip(round(velocity[0]), round(velocity[1]))
            if enemy_alive and egg_rect.colliderect(enemy_rect):
                enemy_hp -= my_attack
                if enemy_hp <= 0:
                    # 敵を倒したときに経験値とコインを獲得する
                    enemy_alive = False
                    exp += EXP_REWARD
                    coin += COIN_REWARD
                continue
            if screen.get_rect().colliderect(egg_rect):
                updated_eggs.append((egg, egg_rect, velocity))
        eggs = updated_eggs

        # ビームを移動し、敵に当たったら敵のHPを減らす
        updated_beams = []
        for beam in beams:
            beam.update()
            if enemy_alive and beam.rect.colliderect(enemy_rect):
                enemy_hp -= BEAM_ATTACK
                if enemy_hp <= 0:
                    enemy_alive = False
                    exp += EXP_REWARD
                    coin += COIN_REWARD
                continue
            if screen.get_rect().colliderect(beam.rect):
                updated_beams.append(beam)
        beams = updated_beams

        # 爆弾を移動し、敵に当たったら敵のHPを減らす
        updated_bombs = []
        for bomb_item in bombs:
            bomb_item.update()
            if enemy_alive and bomb_item.rect.colliderect(enemy_rect):
                enemy_hp -= BOMB_ATTACK
                if enemy_hp <= 0:
                    enemy_alive = False
                    exp += EXP_REWARD
                    coin += COIN_REWARD
                continue
            if screen.get_rect().colliderect(bomb_item.rect):
                updated_bombs.append(bomb_item)
        bombs = updated_bombs

        # 背景、敵、こうかとん、卵の順番で画面に描画する
        screen.blit(background, (0, 0))
        if enemy_alive:
            screen.blit(student_image, enemy_rect)
        screen.blit(player_image, player_rect)
        for egg, egg_rect, _ in eggs:
            screen.blit(egg, egg_rect)
        for beam in beams:
            screen.blit(beam.image, beam.rect)
        for bomb_item in bombs:
            screen.blit(bomb_item.image, bomb_item.rect)
        pg.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()