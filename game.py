"""
Implementação da classe Game para o jogo DVD Bounce Simulation.
"""
import random
import pygame
from constants import (
    WIDTH, HEIGHT, MARGIN, AREA_SIZE, AREA_X, AREA_Y, SQUARE_SIZE,
    MIN_SPEED, MAX_SPEED, POWERUP_INTERVAL, SPIKE_DURATION,
    BLACK, WHITE, DARK_GRAY, LIGHT_GRAY, VIBRANT_COLORS, INFO_FONT
)
from square import Square
from powerup import PowerUp
from menu import show_menu


class Game:
    """Classe principal que gerencia o jogo."""
    def __init__(self):
        """Inicializa o jogo e suas configurações."""
        # Inicializar o pygame
        pygame.init()
        
        # Configurações do jogo
        self.width = WIDTH
        self.height = HEIGHT
        self.margin = MARGIN
        self.area_size = AREA_SIZE
        self.area_x = AREA_X
        self.area_y = AREA_Y
        self.square_size = SQUARE_SIZE
        self.min_speed = MIN_SPEED
        self.max_speed = MAX_SPEED
        
        # Configurar a janela
        self.window = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Simulação de Colisão - Estilo DVD")
        
        # Lista de entidades
        self.squares = []
        self.powerups = []
        
        # Temporizadores
        self.powerup_timer = 0
        self.powerup_interval = POWERUP_INTERVAL
        self.spike_duration = SPIKE_DURATION
        
        # Temporizador para respawn de quadrados
        self.respawn_timer = 0
        self.respawn_interval = 180  # 3 segundos a 60 FPS
        
        # Controle de FPS
        self.clock = pygame.time.Clock()
        self.running = False
    
    def update_area_dimensions(self):
        """Atualiza as dimensões da área de jogo com base na margem atual."""
        self.area_size = min(self.width, self.height) - 2 * self.margin
        self.area_x = (self.width - self.area_size) // 2
        self.area_y = (self.height - self.area_size) // 2
        
        # Atualizar as áreas de colisão para todos os quadrados existentes
        for square in self.squares:
            if square.is_alive:
                square.set_area(self.area_x, self.area_y, self.area_size)
                square.set_speed_limits(self.min_speed, self.max_speed)
    
    def reset_config(self):
        """Restaura as configurações para os valores padrão."""
        # Restaurar valores padrão das configurações
        from constants import MARGIN as DEFAULT_MARGIN
        from constants import SQUARE_SIZE as DEFAULT_SQUARE_SIZE
        from constants import MIN_SPEED as DEFAULT_MIN_SPEED
        from constants import MAX_SPEED as DEFAULT_MAX_SPEED
        
        self.margin = DEFAULT_MARGIN
        self.square_size = DEFAULT_SQUARE_SIZE
        self.min_speed = DEFAULT_MIN_SPEED
        self.max_speed = DEFAULT_MAX_SPEED
        
        # Atualizar dimensões da área
        self.update_area_dimensions()
        
        # Recriar quadrados com as configurações padrão
        self.create_squares()
    
    def create_square(self, color_index=None):
        """Cria um novo quadrado com posição aleatória."""
        # Determinar a cor do novo quadrado
        if color_index is None:
            color_index = random.randint(0, len(VIBRANT_COLORS) - 1)
            
        color = VIBRANT_COLORS[color_index % len(VIBRANT_COLORS)]
        
        # Tentar posicionar o quadrado sem sobreposição
        overlap = True
        attempts = 0
        new_square = None
        
        while overlap and attempts < 10:
            x = random.randint(self.area_x, self.area_x + self.area_size - self.square_size)
            y = random.randint(self.area_y, self.area_y + self.area_size - self.square_size)
            
            new_square = Square(x, y, self.square_size, color)
            
            # Configurar a área para o novo quadrado
            new_square.set_area(self.area_x, self.area_y, self.area_size)
            new_square.set_speed_limits(self.min_speed, self.max_speed)
            
            # Verificar sobreposição com quadrados existentes
            overlap = False
            for sq in self.squares:
                if sq.is_alive and new_square.check_collision(sq):
                    overlap = True
                    break
            
            attempts += 1
        
        return new_square
    
    def create_squares(self):
        """Cria os quadrados iniciais."""
        self.squares = []
        
        # Definir o número de quadrados (no mínimo 2)
        num_squares = 2
        
        # Criar os quadrados com posições aleatórias
        for i in range(num_squares):
            new_square = self.create_square(i)
            self.squares.append(new_square)
    
    def generate_powerup(self):
        """Gera um novo power-up em uma posição aleatória."""
        # Verificar se já existe um power-up ativo
        if len(self.powerups) == 0:
            x = random.randint(self.area_x + 10, self.area_x + self.area_size - 30)
            y = random.randint(self.area_y + 10, self.area_y + self.area_size - 30)
            self.powerups.append(PowerUp(x, y))
    
    def handle_events(self):
        """Processa os eventos do pygame."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Preparar configurações atuais para o menu
                    current_config = {
                        'margin': self.margin,
                        'square_size': self.square_size,
                        'min_speed': self.min_speed,
                        'max_speed': self.max_speed
                    }
                    
                    # Abrir o menu de configurações
                    continue_game, configs, reset_config = show_menu(self.window, current_config)
                    
                    if not continue_game:
                        self.running = False
                    elif reset_config:
                        # Restaurar configurações padrão
                        self.reset_config()
                    elif configs:
                        # Atualizar configurações
                        self.margin = configs['margin']
                        self.square_size = configs['square_size']
                        self.min_speed = configs['min_speed']
                        self.max_speed = configs['max_speed']
                        
                        # Atualizar dimensões da área
                        self.update_area_dimensions()
                        
                        # Recriar quadrados com as novas configurações
                        self.create_squares()
    
    def update(self):
        """Atualiza o estado do jogo."""
        # Verificar se todos os quadrados vivos foram destruídos
        alive_squares = sum(1 for square in self.squares if square.is_alive)
        
        # Respawn de quadrados se necessário
        if alive_squares < 2:
            self.respawn_timer += 1
            if self.respawn_timer >= self.respawn_interval:
                self.respawn_timer = 0
                
                # Verificar se todos os quadrados explodiram completamente 
                # (não têm mais partículas)
                all_exploded = True
                for square in self.squares:
                    if not square.is_alive and len(square.particles) > 0:
                        all_exploded = False
                        break
                
                # Se todos explodiram completamente, criar um novo quadrado
                if all_exploded:
                    # Remover quadrados "mortos" sem partículas
                    self.squares = [sq for sq in self.squares if sq.is_alive or len(sq.particles) > 0]
                    
                    # Criar um novo quadrado
                    new_square = self.create_square()
                    self.squares.append(new_square)
        else:
            self.respawn_timer = 0
        
        # Atualizar todos os quadrados
        for square in self.squares:
            square.update()
        
        # Verificar colisão entre todos os pares de quadrados vivos
        for i in range(len(self.squares)):
            if not self.squares[i].is_alive:
                continue
                
            for j in range(i + 1, len(self.squares)):
                if not self.squares[j].is_alive:
                    continue
                    
                if self.squares[i].check_collision(self.squares[j]):
                    self.squares[i].handle_collision(self.squares[j])
        
        # Atualizar temporizador de power-up
        self.powerup_timer += 1
        if self.powerup_timer >= self.powerup_interval:
            self.powerup_timer = 0
            self.generate_powerup()
        
        # Verificar colisão entre quadrados vivos e power-ups
        for square in self.squares:
            if not square.is_alive:
                continue
                
            for powerup in self.powerups:
                if powerup.active and powerup.check_collision(square):
                    # Ativar espinhos no quadrado
                    square.has_spikes = True
                    square.spike_timer = self.spike_duration
                    # Desativar o power-up
                    powerup.active = False
        
        # Remover power-ups inativos
        self.powerups = [p for p in self.powerups if p.active]
    
    def render(self):
        """Renderiza o jogo na tela."""
        # Preencher a tela com preto
        self.window.fill(BLACK)
        
        # Desenhar a área restrita com um contorno branco
        pygame.draw.rect(self.window, DARK_GRAY, (self.area_x, self.area_y, self.area_size, self.area_size))
        pygame.draw.rect(self.window, WHITE, (self.area_x, self.area_y, self.area_size, self.area_size), 2)
        
        # Desenhar power-ups
        for powerup in self.powerups:
            powerup.draw(self.window)
        
        # Desenhar todos os quadrados (vivos e explodindo)
        for square in self.squares:
            square.draw(self.window)
        
        # Exibir informações sobre o menu
        menu_info = INFO_FONT.render("Pressione ESC para o MENU", True, LIGHT_GRAY)
        self.window.blit(menu_info, (10, 10))
        
        # Atualizar a tela
        pygame.display.flip()
    
    def run(self):
        """Inicia o loop principal do jogo."""
        # Criar quadrados iniciais
        self.create_squares()
        
        # Iniciar o loop do jogo
        self.running = True
        while self.running:
            # Processar eventos
            self.handle_events()
            
            # Atualizar o estado do jogo
            self.update()
            
            # Renderizar
            self.render()
            
            # Limitar a taxa de quadros
            self.clock.tick(60)
        
        # Encerrar o pygame
        pygame.quit()