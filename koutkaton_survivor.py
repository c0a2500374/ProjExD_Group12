import math
import os
import sys
import pygame as pg


# 画像を相対パスで読み込めるよう、実行場所をこのファイルのあるフォルダにする
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# ゲーム画面と各キャラクターの基本設定
WIDTH, HEIGHT = 1100, 650
WORLD_WIDTH, WORLD_HEIGHT = WIDTH * 2, HEIGHT * 2
SCREEN_RECT = pg.Rect(0, 0, WIDTH, HEIGHT)  # 画面全体の四角形(画面外判定で使う)
EGG_FIRE_INTERVAL = 500

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
        self.max_hp = 10
        self.hp = 10
        self.coin = 0
        self.speed_level = 0
        self.hp_upgrade_level = 0
    def reset(self):
        """
        ステータスを初期値に戻す
        """
        self.max_hp = 10
        self.hp = 10
        self.coin = 0
        self.speed_level = 0
        self.hp_upgrade_level = 0


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


def game_over_screen(screen: pg.Surface, background: pg.Surface) -> bool:
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
                Status.reset()
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

def main() -> None:
    """ゲーム画面を作成し、イベント処理と描画を繰り返す。"""
    pg.display.set_caption("こうかとんサバイバー")
    screen = pg.display.set_mode((WIDTH, HEIGHT))

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
    player = Player(player_image, (WIDTH // 2, HEIGHT // 2))
    enemies = pg.sprite.Group(Enemy(student_image, (WIDTH - 150, HEIGHT // 2)))
    eggs = pg.sprite.Group()
    beams = pg.sprite.Group()
    bombs = pg.sprite.Group()
    explosions = pg.sprite.Group()
    horses = pg.sprite.Group()

    last_egg_fire = -EGG_FIRE_INTERVAL
    player_rect = player_image.get_rect(center=(WORLD_WIDTH // 2, WORLD_HEIGHT // 2))
    enemy_rect = student_image.get_rect(center=(WORLD_WIDTH - 150, WORLD_HEIGHT // 2))
    enemy_alive = True
    facing = (1.0, 0.0)
    world_rect = pg.Rect(0, 0, WORLD_WIDTH, WORLD_HEIGHT)

    # 発射中の卵をSurface、位置、速度の組として管理する
    eggs: list[tuple[pg.Surface, pg.Rect, tuple[float, float]]] = []
    clock = pg.time.Clock()

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

        # 当たった卵と敵を消す
        pg.sprite.groupcollide(eggs, enemies, True, True)
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
        # こうかとんが背景の外へ出ないように位置を制限する
        player_rect.clamp_ip(world_rect)

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

        # 全てのスプライトを動かす
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
            if world_rect.colliderect(egg_rect):
                updated_eggs.append((egg, egg_rect, velocity))
        eggs = updated_eggs

        # こうかとんを中心に背景を動かし、背景の端でカメラを止める
        camera_x = min(max(player_rect.centerx - WIDTH // 2, 0), WORLD_WIDTH - WIDTH)
        camera_y = min(max(player_rect.centery - HEIGHT // 2, 0), WORLD_HEIGHT - HEIGHT)

        # 背景、敵、こうかとん、卵の順番で画面に描画する
        screen.blit(background, (-camera_x, -camera_y))
        if enemy_alive:
            screen.blit(student_image, (enemy_rect.x - camera_x, enemy_rect.y - camera_y))
        screen.blit(player_image, (player_rect.x - camera_x, player_rect.y - camera_y))
        for egg, egg_rect, _ in eggs:
            screen.blit(egg, (egg_rect.x - camera_x, egg_rect.y - camera_y))
        pg.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()