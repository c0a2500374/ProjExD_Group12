import math
import random
import os
import sys
import pygame as pg
from abc import ABC, abstractmethod

# 画像を相対パスで読み込めるよう、実行場所をこのファイルのあるフォルダにする
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# ゲーム画面と各キャラクターの基本設定
WIDTH, HEIGHT = 1100, 650
WORLD_WIDTH, WORLD_HEIGHT = WIDTH * 2, HEIGHT * 2
SCREEN_RECT = pg.Rect(0, 0, WIDTH, HEIGHT)  # 画面全体の四角形(画面外判定で使う)
WORLD_RECT = pg.Rect(0, 0, WORLD_WIDTH, WORLD_HEIGHT)  # ワールド全体の四角形(画面外判定で使う)
PLAYER_SPEED = 5
ENEMY_SPEED = 1.5
EGG_FIRE_INTERVAL = 500
ENEMY_TIME = 100
ENEMY_CHENGE = 60000


def load_image(path: str, size: tuple[int, int]) -> pg.Surface:
    """画像を読み込み、ゲーム画面に合う大きさへ縮小する。"""
    image = pg.image.load(path).convert_alpha()
    return pg.transform.smoothscale(image, size)


def draw_group(screen: pg.Surface, group: pg.sprite.Group,
               camera_x: int, camera_y: int) -> None:
    """ワールド座標のスプライトグループをカメラ位置に合わせて描画する。"""
    for sprite in group:
        screen.blit(sprite.image, (sprite.rect.x - camera_x,
                                   sprite.rect.y - camera_y))


def make_student() -> pg.Surface:
    """敵の生徒画像を読み込む。"""
    return load_image("fig/生徒.png", (52, 72))


class enemy(pg.sprite.Sprite,ABC):
    """敵を管理する抽象クラス。"""
    def __init__(self,x,y,hp,img):
        super().__init__()

        self.hp = hp # HPを設定する
        self.image = img # 画像を設定する
        self.rect = self.image.get_rect(center=(x, y)) # 位置を設定する

    def move(self, player_pos: tuple[int, int]) -> None:
        """主人公の位置に向かって移動する。"""
        direction = pg.Vector2(player_pos) - pg.Vector2(self.rect.center)
        if direction.length_squared(): # 方向ベクトルがゼロでない場合のみ移動する
            direction.scale_to_length(ENEMY_SPEED)
            self.rect.move_ip(round(direction.x), round(direction.y)) 

    def damage(self, amount: int) -> None:
        """敵のHPを減らす。"""
        self.hp -= amount
        if self.hp <= 0:
            self.kill()

    @abstractmethod
    def update(self, player_pos: tuple[int, int]) -> None:
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

    def update(self, player_pos: tuple[int, int]) -> None:
        """敵の状態を更新する。"""
        self.move(player_pos)


class yanki_enemy(enemy):
    """敵のヤンキーを管理するクラス。"""
    def __init__(self, x: int, y: int, hp: int = 1):
        img = pg.image.load("fig/yanki-.png").convert_alpha()
        imgs = [pg.transform.scale(img, (80, 80))]
        super().__init__(x, y, hp,img)
        self.imgs = imgs
        self.image = self.imgs[0]
        self.rect = self.image.get_rect(center=(x, y))

    def update(self, player_pos: tuple[int, int]) -> None:
        """敵の状態を更新する。"""
        self.move(player_pos)


class kamathu_enemy(enemy):
    """敵の蒲田マスコットを管理するクラス。"""
    def __init__(self, x: int, y: int, hp: int = 1):
        img = pg.image.load("fig/kamathu2.png").convert_alpha()
        imgs = [pg.transform.scale(img, (80, 80))]
        super().__init__(x, y, hp,img)
        self.imgs = imgs
        self.image = self.imgs[0]
        self.rect = self.image.get_rect(center=(x, y))

    def update(self, player_pos: tuple[int, int]) -> None:
        """敵の状態を更新する。"""
        self.move(player_pos)


class pathi_enemy(enemy):
    """敵の工学院マスコットを管理するクラス。"""
    def __init__(self, x: int, y: int, hp: int = 1):
        img = pg.image.load("fig/pathi.png").convert_alpha()
        imgs = [pg.transform.scale(img, (80, 80))]
        super().__init__(x, y, hp,img)
        self.imgs = imgs
        self.image = self.imgs[0]
        self.rect = self.image.get_rect(center=(x, y))

    def update(self, player_pos: tuple[int, int]) -> None:
        """敵の状態を更新する。"""
        self.move(player_pos)


class pfas_enemy(enemy):
    """敵のPFASを管理するクラス。"""
    def __init__(self, x: int, y: int, hp: int = 10000000000000000):# ゲームを終了させるため無敵に設定
        img = pg.image.load("fig/PFAS.png").convert_alpha()
        imgs = [pg.transform.scale(img, (200, 200))]
        super().__init__(x, y, hp,img)
        self.imgs = imgs
        self.image = self.imgs[0]
        self.rect = self.image.get_rect(center=(x, y))

    def update(self, player_pos: tuple[int, int]) -> None:
        """敵の状態を更新する。"""
        self.move(player_pos)
   
    
def create_enemy(enemy_class, enemies) -> None:
    """敵を生成する。"""
    new_enemy = enemy_class(
        random.randint(0, WORLD_WIDTH),
        random.randint(0, WORLD_HEIGHT),
    )
    enemies.add(new_enemy)
   
class Player(pg.sprite.Sprite):
    """キーボードで操作するこうかとんを表すスプライト。"""

    def __init__(self, image: pg.Surface, basyo: tuple[int, int]) -> None:
        """
        画像と初期位置を受け取り、プレイヤーを作成する。
        引数1: 画像のSurface
        引数2: 初期位置の(x, y)座標
        """
        super().__init__()
        self.image: pg.Surface = image
        self.rect: pg.Rect = self.image.get_rect(center=basyo)
        self.muki: tuple[float, float] = (1.0, 0.0)  # 向いている方向(最初は右)
        self.speed: int = 5  # 1フレームに移動する距離

    def update(self, keys: pg.key.ScancodeWrapper, status: "Status") -> None:
        """
        W/A/S/Dキーに合わせて移動し、最後に移動した向きを記録する。
        引数1: キーの押下状態を表すScancodeWrapper
        """
        self.speed = status.get_player_speed()
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
            self.muki = (movement.x, movement.y)
        self.rect.move_ip(round(movement.x), round(movement.y))
        # こうかとんが画面外へ出ないように位置を制限する
        self.rect.clamp_ip(WORLD_RECT)


class Enemy(pg.sprite.Sprite):
    """プレイヤーを追いかける敵の生徒を表すスプライト。"""

    def __init__(self, image: pg.Surface, basyo: tuple[int, int]) -> None:
        """
        画像と初期位置を受け取り、敵を作成する。
        引数1: 画像のSurface
        引数2: 初期位置の(x, y)座標
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
        引数1: 発射位置の(x, y)座標
        引数2: 発射方向の(x, y)ベクトル
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
        """卵を発射方向へ移動させ、画面外に出たら消える。"""
        self.rect.move_ip(round(self.idouryou[0]), round(self.idouryou[1]))
        if not WORLD_RECT.colliderect(self.rect):
            self.kill()


class Beam(pg.sprite.Sprite):
    """敵を貫通して進む片柳ビームを表すスプライト。"""

    def __init__(self,image: pg.Surface,basyo: tuple[int, int],houkou: tuple[float, float],) -> None:
        """
        画像、発射位置、方向からビームを作成する。
        引数1: 画像のSurface
        引数2: 発射位置の(x, y)座標
        引数3: 発射方向の(x, y)ベクトル
        """
        super().__init__()
        # 画像の向きを、こうかとんが向いている方向に合わせる
        angle = math.degrees(math.atan2(-houkou[1], houkou[0]))
        self.image = pg.transform.rotate(image, angle)
        self.rect = self.image.get_rect(center=basyo)
        self.speed: int = 12  # 1フレームに飛ぶ距離
        length = math.hypot(*houkou) or 1
        self.idouryou: tuple[float, float] = (houkou[0] / length * self.speed,houkou[1] / length * self.speed,)

    def update(self) -> None:
        """
        ビームを発射方向へ移動させ、画面外に出たら消える。
        """
        self.rect.move_ip(round(self.idouryou[0]), round(self.idouryou[1]))
        if not WORLD_RECT.colliderect(self.rect):
            self.kill()


class Bomb(pg.sprite.Sprite):
    """一定距離を進むと爆発するノートパソコン爆弾を表すスプライト。"""

    def __init__(self,image: pg.Surface,basyo: tuple[int, int],houkou: tuple[float, float],) -> None:
        """
        画像、発射位置、方向から爆弾を作成する。
        引数1: 画像のSurface
        引数2: 発射位置の(x, y)座標
        引数3: 発射方向の(x, y)ベクトル
        """
        super().__init__()
        angle = math.degrees(math.atan2(-houkou[1], houkou[0]))
        self.image = pg.transform.rotate(image, angle)
        self.rect = self.image.get_rect(center=basyo)
        self.speed: int = 7  # 1フレームに飛ぶ距離
        self.max_distance: int = 280  # この距離まで進むと爆発する
        length = math.hypot(*houkou) or 1
        self.idouryou: tuple[float, float] = (houkou[0] / length * self.speed,houkou[1] / length * self.speed,)
        self.susundakyori: float = 0.0  # 爆弾が進んだ距離を記録

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
        引数1: 爆発元のBombスプライト
        """
        super().__init__()
        img = pg.image.load("fig/effect.png").convert_alpha()
        img = pg.transform.smoothscale(img, (128, 128))
        img.set_colorkey((255, 255, 255))
        self.imgs = [img, pg.transform.flip(img, 1, 1)]  # 反転画像も用意
        self.image = self.imgs[0]
        self.rect = self.image.get_rect(center=bomb.rect.center)
        self.life: int = 30  # 爆発が表示される残りフレーム数

    def update(self) -> None:
        """
        爆発画像を切り替え、表示時間が終わったらスプライトを消す。
        """
        self.image = self.imgs[(self.life // 10) % 2]  # 10フレームごとに画像を切り替える
        self.life -= 1
        if self.life <= 0:
            self.kill()


class Horse(pg.sprite.Sprite):
    """こうかとんの周囲を回り、触れた敵を消す馬を表すスプライト。"""

    def __init__(self, image: pg.Surface, basyo: tuple[int, int]) -> None:
        """
        画像と初期位置を受け取り、馬を作成する。
        引数1: 画像のSurface
        引数2: 初期位置の(x, y)座標
        """
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=basyo)
        self.radius: int = 100  # こうかとんからの距離
        self.speed: float = 0.08  # 1フレームに進む角度(ラジアン)
        self.angle: float = 0.0  # 現在の角度(ラジアン)

    def update(self, center: tuple[int, int]) -> None:
        """
        こうかとんを中心とする円周上で馬を移動させる。
        """
        self.angle = (self.angle + self.speed) % (2 * math.pi)  # 角度を更新する、2πを超えたら0に戻す
        self.rect.center = (round(center[0] + math.cos(self.angle) * self.radius),round(center[1] + math.sin(self.angle) * self.radius))  # こうかとんを中心に円周上の座標を計算する

class Status:
    """
    こうかとんのHP・所持コインを管理するクラス
    """
    def __init__(self):
        self.max_hp = 1.0
        self.hp = 1.0
        self.coin = 0

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

    def damage(self, amount: float) -> None:
        """主人公のHPを減らす。"""
        self.hp = max(0.0, self.hp - amount)

    def reset(self):
        """
        ステータスを初期値に戻す
        """
        self.max_hp = 1.0
        self.hp = 1.0
        self.coin = 0
        self.speed_level = 0
        self.hp_upgrade_level = 0

def draw_ui(screen: pg.Surface, font: pg.font.Font, status: Status) -> None:
    """
    画面左上にHP,コインを描画する
    """
    # レベル・HP・コイン表示
    info_text = f"GPA: {status.hp:1f}/{status.max_hp:.1f}  COINS: {status.coin}G"
    txt_surf = font.render(info_text, True, (255, 255, 255))
    screen.blit(txt_surf, (20, 15))


def start_screen(screen: pg.Surface, background: pg.Surface) -> bool:
    """
    STARTボタンが押されたらTrueを返す。
    EXITボタンが押されたらFalseを返す。
    Trueが返るとゲームが始まり、Falseが返るとゲームを終了する。
    """
    font = pg.font.SysFont(None, 56, bold=True)

    # タイトルとボタンのテキストを描画
    title = font.render("KOUKATON SURVIVOR", True, (255, 255, 255))
    title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 45)).inflate(40, 20)
    # STARTボタンのテキストを描画
    start = font.render("START", True, (255, 255, 255))
    start_rect = start.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 55)).inflate(40, 20)
    # EXITボタンのテキストを描画
    exit = font.render("EXIT", True, (255, 255, 255))
    exit_rect = exit.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 135)).inflate(40, 20)

    while True:
        # ボタンを押したときの処理と終了操作を処理する
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return False
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and exit_rect.collidepoint(event.pos):
                return False
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and start_rect.collidepoint(event.pos):
                return True
        # 画面に背景とボタン用の四角（角が丸い）を描画する
        screen.blit(background, (0, 0))
        pg.draw.rect(screen, (45, 130, 70), title_rect, border_radius=10)
        pg.draw.rect(screen, (0, 170, 255), start_rect, border_radius=10)
        pg.draw.rect(screen, (170, 55, 55), exit_rect, border_radius=10)
        screen.blit(start, start.get_rect(center=start_rect.center))
        screen.blit(exit, exit.get_rect(center=exit_rect.center))
        screen.blit(title, title.get_rect(center=title_rect.center))
        pg.display.flip()
        pg.time.Clock().tick(60)

def open_shop(screen: pg.Surface, clock: pg.time.Clock, font: pg.font.Font, status: Status) -> None:
    """
    ショップ画面（ポーズ中）の描画と入力処理
    """
    in_shop = True

    prices = {
        "speed": 30,
        "max_hp": 50,
    }

    while in_shop:
        cost_speed = int(prices["speed"] * (1.3 ** status.speed_level))
        cost_hp = int(prices["max_hp"] * (1.3 ** status.hp_upgrade_level))

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            
            if event.type == pg.KEYDOWN:
                if event.key in (pg.K_b, pg.K_ESCAPE):
                    in_shop = False

                # [1] 移動速度 UP
                elif event.key == pg.K_1 and status.coin >= cost_speed:
                    status.coin -= cost_speed
                    status.speed_level += 1

                # [2] 最大HP UP
                elif event.key == pg.K_2 and status.coin >= cost_hp and status.hp_upgrade_level < status.max_hp_upgrade_level:
                    status.coin -= cost_hp
                    status.hp_upgrade_level += 1
                    status.max_hp += 0.1
                    status.hp += 0.1

        # 背景の暗転
        overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        # UI描画
        title_surface = font.render("GAKUSYOKU : Bkey -> close", True, (255, 215, 0))
        screen.blit(title_surface, (WIDTH // 2 - title_surface.get_width() // 2, 70))

        info_surface = font.render(f"myCoin: {status.coin} Coin  |  HP: {status.hp:.1f}/{status.max_hp:.1f}", True, (255, 255, 255))
        screen.blit(info_surface, (WIDTH // 2 - info_surface.get_width() // 2, 130))

        if status.max_hp_upgrade_level <= status.hp_upgrade_level:
            hp_cost_text = "MAX"
        else:
            hp_cost_text = f"{cost_hp} Coin"

        items = [
            f"[1] speedUP  (Lv.{status.speed_level})  : {cost_speed} Coin",
            f"[2] maxhpUP  (Lv.{status.hp_upgrade_level}/{status.max_hp_upgrade_level})  : {hp_cost_text}",
        ]

        for i, text in enumerate(items):
            color = (255, 255, 255)
            if ((i == 0 and status.coin < cost_speed) or
               (i == 1 and status.coin < cost_hp)):
                color = (120, 120, 120)

            item_surface = font.render(text, True, color)
            screen.blit(item_surface, (WIDTH // 2 - 200, 220 + i * 55))

        pg.display.flip()
        clock.tick(60)


def game_over_screen(screen: pg.Surface, background: pg.Surface, status: "Status") -> bool:
    """
    ゲームオーバー画面を表示するクラス
    こうかとんのHPが0になったときに表示される。
    背景画像がフルサイズで表示され、画面中央に「GAME OVER」の文字が表示される。
    画面下部には「RESTART」と「EXIT」のボタンが表示される。

    TRUEが返るとゲームが再開され、FALSEが返るとゲームを終了する。
    再開時には、初期値にステータスを戻す
    """
    font = pg.font.SysFont(None, 56, bold=True)
    #GAMEOVERの描画
    gameover = font.render("GAME OVER", True, (255, 255, 255))
    gameover_rect = gameover.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 45)).inflate(40, 20)
    #RESTARTボタンの描画
    restart = font.render("RESTART", True, (255, 255, 255))
    restart_rect = restart.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 55)).inflate(40, 20)
    #EXITボタンの描画
    exit = font.render("EXIT", True, (255, 255, 255))
    exit_rect = exit.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 135)).inflate(40, 20)
    
    while True:
        # ボタンを押したときの処理と終了操作を処理する
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return False
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and exit_rect.collidepoint(event.pos):
                return False
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and restart_rect.collidepoint(event.pos):
                status.reset()
                return True
        # 画面に背景とボタン用の四角（角が丸い）を描画する
        screen.blit(background, (0, 0))
        pg.draw.rect(screen, (45, 130, 70), gameover_rect, border_radius=10)
        pg.draw.rect(screen, (0, 170, 255), restart_rect, border_radius=10)
        pg.draw.rect(screen, (170, 55, 55), exit_rect, border_radius=10)
        screen.blit(gameover, gameover.get_rect(center=gameover_rect.center))
        screen.blit(restart, restart.get_rect(center=restart_rect.center))
        screen.blit(exit, exit.get_rect(center=exit_rect.center))
        pg.display.flip()
        pg.time.Clock().tick(60)

#アイテム機能の実装
#1GPAは体力（hp）回復、金のトイレはお金(coin)を増やす
class Items:
    """
    2種類のアイテムの出現
    """

    def __init__(self, kind, image_path, screen_size, pickup_sound):
        self.kind = kind  
        self.pickup_sound = pickup_sound #効果音
        self.min_interval = 40000  #アイテムが次に出現する時間
        self.max_interval = 120000  
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
            self.pickup_sound.play()  # 拾った瞬間に1回だけ鳴る
        
            if self.kind == "coin": # 金のトイレを取得したとき
                status.coin += 10
                #print(f"金のトイレ取得！ 現在のコイン：{status.coin}")
            elif self.kind == "hp": # 1GPAを取得したとき
                if status.hp < status.max_hp:
                    status.hp += 1.0
                elif status.hp >= status.max_hp:
                    status.hp = status.max_hp
                #print(f"1GPA取得！ 現在のGPA：{status.hp}")  

    def draw(self, screen, camera_x=0, camera_y=0):
        if self.active:
            screen.blit(self.image, (self.rect.x - camera_x,
                                     self.rect.y - camera_y))



def main() -> None:
    """ゲーム画面を作成し、イベント処理と描画を繰り返す。"""
    pg.display.set_caption("こうかとんサバイバー")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pickup_sound = pg.mixer.Sound("sound/決定ボタンを押す12.mp3")
    font = pg.font.SysFont("arial", 26)

    background_image = pg.image.load("fig/背景.png").convert()
    start_background = pg.transform.smoothscale(background_image, (WIDTH, HEIGHT))
    if not start_screen(screen, start_background):
        return

    # 画面の4倍の広さのワールドを作り、画面にはその一部を表示する
    background = pg.transform.smoothscale(
        background_image, (WORLD_WIDTH, WORLD_HEIGHT)
    )

    # キャラクター画像を用意する
    player_image = load_image("fig/こうかとん.png", (72, 72))
    student_image = make_student()
    beam_image = load_image("fig/katayanagi_beam.png", (180, 44))
    bomb_image = load_image("fig/notepc.png", (56, 56))
    uma_image = load_image("fig/uma.png", (72, 72))

    # プレイヤーと、種類ごとのスプライトグループを作る
    player = Player(player_image, (WORLD_WIDTH // 2, WORLD_HEIGHT // 2))
    enemies = pg.sprite.Group()
    eggs = pg.sprite.Group()
    beams = pg.sprite.Group()
    bombs = pg.sprite.Group()
    explosions = pg.sprite.Group()
    horses = pg.sprite.Group()
    last_egg_fire = -EGG_FIRE_INTERVAL
    #　カウント機能を初期化する
    clock = pg.time.Clock()
    start_time = 0
    pop_time = 0
    enemy_classes = [nomal_enemy, yanki_enemy, kamathu_enemy, pathi_enemy, pfas_enemy]


    status = Status()

    clock = pg.time.Clock()
    items = [
        Items("hp", "fig/1GPA.png", (WORLD_WIDTH, WORLD_HEIGHT), pickup_sound),
        Items("coin", "fig/金のトイレ.png", (WORLD_WIDTH, WORLD_HEIGHT), pickup_sound),
    ]
    
    while True:
        # 終了操作とスペースキーなどによる攻撃を処理する
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                now = pg.time.get_ticks()  # 経過時間
                if now - last_egg_fire >= EGG_FIRE_INTERVAL:  # インターバルを超えていたら発射  
                    eggs.add(Egg(player.rect.center, player.muki))
                    last_egg_fire = now  # 発射した時間を記録
            if event.type == pg.KEYDOWN and event.key == pg.K_o:  # Oキーで片柳ビームを発射する
                beams.add(Beam(beam_image, player.rect.center, player.muki))
            if event.type == pg.KEYDOWN and event.key == pg.K_i:  # Iキーでノートパソコン爆弾を発射する
                bombs.add(Bomb(bomb_image, player.rect.center, player.muki))
            if event.type == pg.KEYDOWN and event.key == pg.K_u and not horses:  # Uキーで馬を呼び出す(馬がいない時だけ)
                horses.add(Horse(uma_image, player.rect.center))
            if event.type == pg.KEYDOWN and event.key == pg.K_b:
                open_shop(screen, clock, font, status)

        # 敵を出現させる
        time = clock.tick(60)
        
        start_time += time # ゲーム開始からの経過時間を更新する
        pop_time += time # 敵の出現までの時間を更新する
        
        enemy_index = start_time//60000 # 経過時間に応じて敵の種類を変える
        if start_time >= 300000: # 5分経過後はPFASを出現させる
            enemy_index = 4
                
        while pop_time >=100: # 0.1秒ごとに敵を生成する
            create_enemy(enemy_classes[enemy_index], enemies)
            pop_time -= 100  

        # 当たった卵と敵にダメージを与える
        egg_hits = pg.sprite.groupcollide(eggs, enemies, True, False)
        for hit_enemies in egg_hits.values():
            for hit_enemy in hit_enemies:
                hit_enemy.damage(1)
            status.coin += 20     # コイン獲得

        # こうかとんが背景の外へ出ないように位置を制限する
        # 敵は消えるが、ビームは消えず貫通する
        beam_hits = pg.sprite.groupcollide(beams, enemies, False, False)
        for hit_enemies in beam_hits.values():
            for hit_enemy in hit_enemies:
                hit_enemy.damage(1)
            status.coin += 20     # コイン獲得

        # 爆弾が一定距離まで進んだら爆発させる(画面外に出た爆弾は消す)
        for bomb_item in bombs.sprites():
            if bomb_item.reached_max_distance():
                explosion = Explosion(bomb_item)
                explosions.add(explosion)
                hit_enemies = pg.sprite.spritecollide(explosion, enemies, False)
                for hit_enemy in hit_enemies:
                    hit_enemy.damage(1)
                if hit_enemies:
                    status.coin += 20     # コイン獲得
                bomb_item.kill()
            elif not WORLD_RECT.colliderect(bomb_item.rect):
                bomb_item.kill()

        # Uキーで呼び出した馬に触れた敵を消す
        horse_hits = pg.sprite.groupcollide(horses, enemies, False, False)
        for hit_enemies in horse_hits.values():
            for hit_enemy in hit_enemies:
                hit_enemy.damage(1)
            status.coin += 20     # コイン獲得

        # 全てのスプライトを動かす
        player.update(pg.key.get_pressed(), status)
        for item in items:
            item.update(player.rect, status)
        enemies.update(player.rect.center)
        eggs.update()
        beams.update()
        bombs.update()
        explosions.update()
        horses.update(player.rect.center)

        # 主人公と敵の中心間距離が、従来の接触距離の半分以内なら双方にダメージを与える
        player_radius = max(player.rect.width, player.rect.height) / 2
        for hit_enemy in enemies:
            enemy_radius = max(hit_enemy.rect.width, hit_enemy.rect.height) / 2
            contact_distance = (player_radius + enemy_radius) / 2
            if pg.Vector2(player.rect.center).distance_to(
                hit_enemy.rect.center
            ) <= contact_distance:
                status.damage(0.1)
                hit_enemy.damage(1)

        if status.hp <= 0:
            if not game_over_screen(screen, start_background, status):
                return

        # カメラ位置
        camera_x = min(max(player.rect.centerx - WIDTH // 2, 0),
                       WORLD_WIDTH - WIDTH)
        camera_y = min(max(player.rect.centery - HEIGHT // 2, 0),
                       WORLD_HEIGHT - HEIGHT)

        # 背景 → 敵 → こうかとん → 攻撃 の順に、1フレームにつき1回だけ描く
        screen.blit(background, (-camera_x, -camera_y))
        for item in items:
            item.draw(screen, camera_x, camera_y)
        draw_group(screen, enemies, camera_x, camera_y)
        screen.blit(player.image, (player.rect.x - camera_x,
                                   player.rect.y - camera_y))
        draw_group(screen, eggs, camera_x, camera_y)
        draw_group(screen, beams, camera_x, camera_y)
        draw_group(screen, bombs, camera_x, camera_y)
        draw_group(screen, explosions, camera_x, camera_y)
        draw_group(screen, horses, camera_x, camera_y)
        draw_ui(screen, font, status)

        pg.display.flip()
        


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()