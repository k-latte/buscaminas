import pygame
import random
import sys

# Inicializar Pygame
pygame.init()

# Constantes
WIDTH, HEIGHT = 600, 650  # Alto extra para mostrar información
GRID_SIZE = 20
CELL_SIZE = WIDTH // GRID_SIZE
MINE_COUNT = 20
WHITE = (255, 255, 255)
GRAY = (222, 222, 222)
DARK_GRAY = (145, 145, 145)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 128, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)

# Crear la ventana
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Buscaminas')


# Función para crear el tablero
def create_board():
    # Crear tablero vacío
    board = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

    # Colocar minas aleatoriamente
    mines_placed = 0
    while mines_placed < MINE_COUNT:
        x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
        if board[y][x] != -1:  # -1 representa una mina
            board[y][x] = -1
            mines_placed += 1

            # Incrementar los números alrededor de la mina
            for i in range(max(0, y - 1), min(GRID_SIZE, y + 2)):
                for j in range(max(0, x - 1), min(GRID_SIZE, x + 2)):
                    if board[i][j] != -1:
                        board[i][j] += 1

    return board


# Función para dibujar el tablero
def draw_board(board, revealed, flagged):
    screen.fill(WHITE)

    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)

            if revealed[y][x]:
                pygame.draw.rect(screen, GRAY, rect)
                if board[y][x] == -1:
                    # Dibujar mina
                    pygame.draw.circle(screen, BLACK, rect.center, CELL_SIZE // 3)
                elif board[y][x] > 0:
                    # Dibujar número
                    font = pygame.font.SysFont(None, 28)

                    # Elegir color según el número
                    colors = [BLUE, GREEN, RED, PURPLE, BLACK, ORANGE, BLACK, BLACK]
                    color = colors[min(board[y][x] - 1, len(colors) - 1)]

                    text = font.render(str(board[y][x]), True, color)
                    text_rect = text.get_rect(center=rect.center)
                    screen.blit(text, text_rect)
            else:
                pygame.draw.rect(screen, DARK_GRAY, rect)
                if flagged[y][x]:
                    # Dibujar bandera
                    points = [(x * CELL_SIZE + CELL_SIZE // 4, y * CELL_SIZE + CELL_SIZE // 4),
                              (x * CELL_SIZE + CELL_SIZE // 4, y * CELL_SIZE + CELL_SIZE * 3 // 4),
                              (x * CELL_SIZE + CELL_SIZE * 3 // 4, y * CELL_SIZE + CELL_SIZE // 2)]
                    pygame.draw.polygon(screen, RED, points)

            # Dibujar borde de la celda
            pygame.draw.rect(screen, BLACK, rect, 1)

    # Dibujar información del juego
    font = pygame.font.SysFont(None, 24)
    mines_left = MINE_COUNT - sum(sum(row) for row in flagged)
    info_text = f"Minas restantes: {mines_left}"
    text = font.render(info_text, True, BLACK)
    screen.blit(text, (10, HEIGHT - 40))


# Función para revelar celdas
def reveal_cell(board, revealed, flagged, x, y):
    if not (0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE) or revealed[y][x] or flagged[y][x]:
        return False

    revealed[y][x] = True

    # Si es una celda vacía, revelar celdas adyacentes
    if board[y][x] == 0:
        for i in range(max(0, y - 1), min(GRID_SIZE, y + 2)):
            for j in range(max(0, x - 1), min(GRID_SIZE, x + 2)):
                if not revealed[i][j]:
                    reveal_cell(board, revealed, flagged, j, i)

    return board[y][x] == -1  # Retorna True si es una mina


# Función para verificar victoria
def check_win(board, revealed, flagged):
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            # Si hay una celda que no es mina y no está revelada, aún no ha ganado
            if board[y][x] != -1 and not revealed[y][x]:
                return False
    return True


# Función principal del juego
def main():
    board = create_board()
    revealed = [[False for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    flagged = [[False for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    game_over = False
    win = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if not game_over and not win:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos[0] // CELL_SIZE, event.pos[1] // CELL_SIZE

                    # Verificar que el clic esté dentro del tablero
                    if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
                        if event.button == 1:  # Clic izquierdo
                            if not flagged[y][x]:
                                hit_mine = reveal_cell(board, revealed, flagged, x, y)
                                if hit_mine:
                                    game_over = True
                                    # Revelar todas las minas
                                    for i in range(GRID_SIZE):
                                        for j in range(GRID_SIZE):
                                            if board[i][j] == -1:
                                                revealed[i][j] = True

                        elif event.button == 3:  # Clic derecho
                            if not revealed[y][x]:
                                flagged[y][x] = not flagged[y][x]

            # Reiniciar juego con espacio
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                board = create_board()
                revealed = [[False for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
                flagged = [[False for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
                game_over = False
                win = False

        # Dibujar tablero
        draw_board(board, revealed, flagged)

        # Verificar victoria
        if not game_over and not win:
            win = check_win(board, revealed, flagged)

        # Mostrar mensaje según estado del juego
        font = pygame.font.SysFont(None, 36)
        if game_over:
            text = font.render("¡PERDISTE! Pulsa ESPACIO para reiniciar", True, RED)
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT - 20))
            screen.blit(text, text_rect)
        elif win:
            text = font.render("¡GANASTE! Pulsa ESPACIO para reiniciar", True, GREEN)
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT - 20))
            screen.blit(text, text_rect)

        pygame.display.flip()
        pygame.time.Clock().tick(30)


if __name__ == "__main__":
    main()