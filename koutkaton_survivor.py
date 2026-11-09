import math
import os
import sys
import pygame as pg


# 画像を相対パスで読み込めるよう、実行場所をこのファイルのあるフォルダにする
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# ゲーム画面と各キャラクターの基本設定
WIDTH, HEIGHT = 1100, 650
SCREEN_RECT = pg.Rect(0, 0, WIDTH, HEIGHT)  # 画面全体の四角形(画面外判定で使う)
EGG_FIRE_INTERVAL = 500
PLAYER_HP = 100
ENEMY_ATTACK = 1
CONTACT_DAMAGE_INTERVAL = 500


def load_image(path: str, size: tuple[int, int]) -> pg.Surface:
    """画像を読み込み、ゲーム画面に合う大きさへ縮小する。"""
    image = pg.image.load(path).convert_alpha()
    return pg.transform.smoothscale(image, size)


def make_student() -> pg.Surface:
    """敵の生徒画像を読み込む。"""
    return load_image("fig/生徒.png", (52, 72))


class Player(pg.sprite.Sprite):
    """キーボードで操作するこうかとんを表すスプライト。"""

    def __init__(self, image: pg.Surface, basyo: tuple[int, int]) -> None:
        """
        画像と初期位置を受け取り、プレイヤーを作成する。
        """
        super().__init__()
        self.image: pg.Surface = image
        self.rect: pg.Rect = self.image.get_rect(center=basyo)
        self.facing: tuple[float, float] = (1.0, 0.0)  # 向いている方向(最初は右)
        self.speed: int = 5  # 1フレームに移動する距離

    def update(self, keys: pg.key.ScancodeWrapper) -> None:
        """
        W/A/S/Dキーに合わせて移動し、最後に移動した向きを記録する。
        """
        movement = pg.Vector2(0, 0)
        if keys[pg.K_w]:
            movement.y -= self.speed
        if keys[pg.K_s]:
            movement.y += self.speed
        if keys[pg.K_a]:
            movement.x -= self.speed
        if keys[pg.K_d]:
            movement.x += self.speed
        if movement.length_squared():
            movement.scale_to_length(self.speed)
            # 移動した方向を、こうかとんが向いている方向として記録する
            self.facing = (movement.x, movement.y)
        self.rect.move_ip(round(movement.x), round(movement.y))
        # こうかとんが画面外へ出ないように位置を制限する
        self.rect.clamp_ip(SCREEN_RECT)


class Enemy(pg.sprite.Sprite):
    """プレイヤーを追いかける敵の生徒を表すスプライト。"""

    def __init__(self, image: pg.Surface, basyo: tuple[int, int]) -> None:
        """
        画像と初期位置を受け取り、敵を作成する。
        """
        super().__init__()
        self.image: pg.Surface = image
        self.rect: pg.Rect = self.image.get_rect(center=basyo)
        self.speed: float = 1.5  # 1フレームに移動する距離

    def update(self, target: tuple[int, int]) -> None:
        """
        目標の中心座標へ向かって少しずつ移動する。
        """
        houkou = pg.Vector2(target) - pg.Vector2(self.rect.center)
        if houkou.length_squared():
            houkou.scale_to_length(self.speed)
            self.rect.move_ip(round(houkou.x), round(houkou.y))


class Egg(pg.sprite.Sprite):
    """こうかとんが発射し、敵に当たると消える卵を表すスプライト。"""

    def __init__(self, basyo: tuple[int, int], houkou: tuple[float, float]) -> None:
        """
        発射位置と方向から卵を作成する。
        """
        super().__init__()
        self.image: pg.Surface = pg.Surface((18, 24), pg.SRCALPHA)
        pg.draw.ellipse(self.image, (255, 250, 220), self.image.get_rect())
        pg.draw.ellipse(self.image, (180, 140, 80), self.image.get_rect(), 2)
        self.rect: pg.Rect = self.image.get_rect(center=basyo)
        self.speed: int = 8  # 1フレームに飛ぶ距離

        length = math.hypot(*houkou) or 1
        self.idouryou: tuple[float, float] = (houkou[0] / length * self.speed,houkou[1] / length * self.speed,)

    def update(self) -> None:
        """
        卵を発射方向へ移動させ、画面外に出たら消える。"""
        self.rect.move_ip(round(self.idouryou[0]), round(self.idouryou[1]))
        if not SCREEN_RECT.colliderect(self.rect):
            self.kill()


class Beam(pg.sprite.Sprite):
    """敵を貫通して進む片柳ビームを表すスプライト。"""

    def __init__(self,image: pg.Surface,basyo: tuple[int, int],houkou: tuple[float, float],) -> None:
        """
        画像、発射位置、方向からビームを作成する。
        """
        super().__init__()
        # 画像の向きを、こうかとんが向いている方向に合わせる
        angle = math.degrees(math.atan2(-houkou[1], houkou[0]))
        self.image: pg.Surface = pg.transform.rotate(image, angle)
        self.rect: pg.Rect = self.image.get_rect(center=basyo)
        self.speed: int = 12  # 1フレームに飛ぶ距離
        length = math.hypot(*houkou) or 1
        self.idouryou: tuple[float, float] = (houkou[0] / length * self.speed,houkou[1] / length * self.speed,)

    def update(self) -> None:
        """
        ビームを発射方向へ移動させ、画面外に出たら消える。"""
        self.rect.move_ip(round(self.idouryou[0]), round(self.idouryou[1]))
        if not SCREEN_RECT.colliderect(self.rect):
            self.kill()


class Bomb(pg.sprite.Sprite):
    """一定距離を進むと爆発するノートパソコン爆弾を表すスプライト。"""

    def __init__(self,image: pg.Surface,basyo: tuple[int, int],houkou: tuple[float, float],) -> None:
        """
        画像、発射位置、方向から爆弾を作成する。"""
        super().__init__()
        angle = math.degrees(math.atan2(-houkou[1], houkou[0]))
        self.image: pg.Surface = pg.transform.rotate(image, angle)
        self.rect: pg.Rect = self.image.get_rect(center=basyo)
        self.speed: int = 7  # 1フレームに飛ぶ距離
        self.max_distance: int = 280  # この距離まで進むと爆発する
        length = math.hypot(*houkou) or 1
        self.idouryou: tuple[float, float] = (houkou[0] / length * self.speed,houkou[1] / length * self.speed,)
        self.susundakyori: float = 0.0

    def update(self) -> None:
        """
        爆弾を発射方向へ移動させ、移動距離を更新する。
        """
        self.rect.move_ip(round(self.idouryou[0]), round(self.idouryou[1]))
        self.susundakyori += math.hypot(*self.idouryou)

    def reached_max_distance(self) -> bool:
        """
        爆弾が爆発する距離まで進んだかを返す。
        """
        return self.susundakyori >= self.max_distance


class Explosion(pg.sprite.Sprite):
    """爆弾が一定距離進んだときに表示する爆発エフェクト。"""

    def __init__(self, bomb: Bomb) -> None:
        """
        爆発元の爆弾を受け取り、その位置にエフェクトを作成する。
        """
        super().__init__()
        img = pg.image.load("fig/effect.png").convert_alpha()
        img = pg.transform.smoothscale(img, (128, 128))
        img.set_colorkey((255, 255, 255))
        self.imgs: list[pg.Surface] = [img, pg.transform.flip(img, 1, 1)]
        self.image: pg.Surface = self.imgs[0]
        self.rect: pg.Rect = self.image.get_rect(center=bomb.rect.center)
        self.life: int = 30  # 爆発が表示される残りフレーム数

    def update(self) -> None:
        """
        爆発画像を切り替え、表示時間が終わったらスプライトを消す。"""
        self.image = self.imgs[(self.life // 10) % 2]
        self.life -= 1
        if self.life <= 0:
            self.kill()


class Horse(pg.sprite.Sprite):
    """こうかとんの周囲を回り、触れた敵を消す馬を表すスプライト。"""

    def __init__(self, image: pg.Surface, basyo: tuple[int, int]) -> None:
        """
        画像と初期位置を受け取り、馬を作成する。
        """
        super().__init__()
        self.image: pg.Surface = image
        self.rect: pg.Rect = self.image.get_rect(center=basyo)
        self.radius: int = 100  # こうかとんからの距離
        self.speed: float = 0.08  # 1フレームに進む角度(ラジアン)
        self.angle: float = 0.0  # 現在の角度(ラジアン)

    def update(self, center: tuple[int, int]) -> None:
        """
        こうかとんを中心とする円周上で馬を移動させる。
        """
        self.angle = (self.angle + self.speed) % (2 * math.pi)
        self.rect.center = (
            round(center[0] + math.cos(self.angle) * self.radius),
            round(center[1] + math.sin(self.angle) * self.radius),
        )


def main() -> None:
    """ゲーム画面を作成し、イベント処理と描画を繰り返す。"""
    pg.display.set_caption("こうかとんサバイバー")
    screen = pg.display.set_mode((WIDTH, HEIGHT))

    # 背景画像を画面全体に広げて表示する
    background = pg.transform.smoothscale(
        pg.image.load("fig/背景.png").convert(), (WIDTH, HEIGHT)
    )

    # キャラクター画像を用意する
    player_image = load_image("fig/こうかとん.png", (72, 72))
    student_image = make_student()
    beam_image = load_image("fig/katayanagi_beam.png", (180, 44))
    bomb_image = load_image("fig/notepc.png", (56, 56))
    uma_image = load_image("fig/uma.png", (72, 72))

    # プレイヤーと、種類ごとのスプライトグループを作る
    player = Player(player_image, (WIDTH // 2, HEIGHT // 2))
    enemies = pg.sprite.Group(Enemy(student_image, (WIDTH - 150, HEIGHT // 2)))
    eggs = pg.sprite.Group()
    beams = pg.sprite.Group()
    bombs = pg.sprite.Group()
    explosions = pg.sprite.Group()
    horses = pg.sprite.Group()

    myhp = PLAYER_HP
    enemy_attack = ENEMY_ATTACK
    last_contact_damage = -CONTACT_DAMAGE_INTERVAL
    last_egg_fire = -EGG_FIRE_INTERVAL
    clock = pg.time.Clock()

    while True:
        # 終了操作とスペースキーなどによる攻撃を処理する
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                now = pg.time.get_ticks()
                if now - last_egg_fire >= EGG_FIRE_INTERVAL:
                    eggs.add(Egg(player.rect.center, player.facing))
                    last_egg_fire = now
            if event.type == pg.KEYDOWN and event.key == pg.K_o:
                beams.add(Beam(beam_image, player.rect.center, player.facing))
            if event.type == pg.KEYDOWN and event.key == pg.K_i:
                bombs.add(Bomb(bomb_image, player.rect.center, player.facing))
            if event.type == pg.KEYDOWN and event.key == pg.K_u and not horses:
                horses.add(Horse(uma_image, player.rect.center))

        # 生徒がこうかとんに触れたら、一定間隔でダメージを受ける
        now = pg.time.get_ticks()
        if pg.sprite.spritecollideany(player, enemies) and (
            now - last_contact_damage >= CONTACT_DAMAGE_INTERVAL
        ):
            myhp -= enemy_attack
            last_contact_damage = now

        # 当たった卵と敵を消す(第3・第4引数 True = 消す)
        pg.sprite.groupcollide(eggs, enemies, True, True)

        # 敵は消えるが、ビームは消えず貫通する
        pg.sprite.groupcollide(beams, enemies, False, True)

        # 爆弾が一定距離まで進んだら爆発させる(画面外に出た爆弾は消す)
        for bomb_item in bombs.sprites():
            if bomb_item.reached_max_distance():
                explosion = Explosion(bomb_item)
                explosions.add(explosion)
                pg.sprite.spritecollide(explosion, enemies, True)
                bomb_item.kill()
            elif not SCREEN_RECT.colliderect(bomb_item.rect):
                bomb_item.kill()

        # Uキーで呼び出した馬に触れた敵を消す
        pg.sprite.groupcollide(horses, enemies, False, True)

        # 全てのスプライトを動かす(update をここにまとめる)
        player.update(pg.key.get_pressed())
        enemies.update(player.rect.center)
        eggs.update()
        beams.update()
        bombs.update()
        explosions.update()
        horses.update(player.rect.center)

        # 背景、敵、こうかとん、卵…の順番で画面に描画する
        screen.blit(background, (0, 0))
        enemies.draw(screen)
        screen.blit(player.image, player.rect)
        eggs.draw(screen)
        beams.draw(screen)
        bombs.draw(screen)
        explosions.draw(screen)
        horses.draw(screen)
        pg.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()