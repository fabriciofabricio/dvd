"""
Implementação da classe Game para o jogo DVD Bounce Simulation.
"""
import random
import pygame
import os
import sys
from constants import (
    WIDTH, HEIGHT, MARGIN, AREA_SIZE, AREA_X, AREA_Y, SQUARE_SIZE,
    MIN_SPEED, MAX_SPEED, POWERUP_INTERVAL, SPIKE_DURATION,
    BLACK, WHITE, DARK_GRAY, LIGHT_GRAY, VIBRANT_COLORS, INFO_FONT
)
from square import Square
from powerup import PowerUp
from menu import show_menu

nome1 = "Luisao"
nome2 = "Matheus Nneuman"

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
        self.header_height = 80  # Altura do cabeçalho de informações
        
        # Ajustar a área do jogo para acomodar o cabeçalho
        self.adjust_game_area()
        
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
        
        # Estado de fim de jogo
        self.game_over = False
        self.winner = None
        
        # Carregar fontes
        self.title_font = pygame.font.SysFont("Arial", 20, bold=True)
        self.info_font = pygame.font.SysFont("Arial", 16)
        
        # Verificar se a pasta de imagens existe
        if not os.path.exists('images'):
            try:
                os.makedirs('images')
                print("Pasta 'images' criada com sucesso. Por favor, coloque suas imagens nela e reinicie o jogo.")
            except Exception as e:
                print(f"Erro ao criar pasta 'images': {e}")
        
        # Configurações personalizadas para os quadrados
        self.verify_images()
        
        # Define as configurações dos quadrados
        self.square_configs = [
            {
                "name": nome1, 
                "image_path": os.path.join("images", "square1.png"),
                "color_index": 0
            },
            {
                "name": nome2, 
                "image_path": os.path.join("images", "square2.png"),
                "color_index": 1
            }
        ]
    
    def adjust_game_area(self):
        """Ajusta a área do jogo para acomodar o cabeçalho de informações."""
        self.area_y += self.header_height
        self.area_size = min(self.width - 2 * self.margin, self.height - 2 * self.margin - self.header_height)
        self.area_x = (self.width - self.area_size) // 2
    
    def verify_images(self):
        """Verifica se as imagens esperadas existem e exibe uma mensagem de ajuda se não."""
        expected_images = ["square1.png", "square2.png"]
        images_path = "images"
        
        if not os.path.exists(images_path):
            print("\nERRO: Pasta 'images' não encontrada!")
            return False
        
        # Verificar cada imagem esperada
        missing_images = []
        for img in expected_images:
            path = os.path.join(images_path, img)
            if not os.path.exists(path):
                missing_images.append(img)
        
        if missing_images:
            print("\nAVISO: As seguintes imagens estão faltando:")
            for img in missing_images:
                print(f"  - {img}")
            
            print("\nPara usar imagens personalizadas, você precisa:")
            print("1. Coloque suas imagens na pasta 'images'")
            print("2. Renomeie-as para 'square1.png' e 'square2.png'")
            print("3. Reinicie o jogo\n")
        else:
            print("\nTodas as imagens foram encontradas com sucesso!")
        
        return len(missing_images) == 0
    
    def update_area_dimensions(self):
        """Atualiza as dimensões da área de jogo com base na margem atual."""
        self.area_size = min(self.width - 2 * self.margin, self.height - 2 * self.margin - self.header_height)
        self.area_x = (self.width - self.area_size) // 2
        self.area_y = self.header_height + self.margin
        
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
        
        # Resetar estado de fim de jogo
        self.game_over = False
        self.winner = None
    
    def create_square(self, color_index=None, name=None, image_path=None):
        """
        Cria um novo quadrado com posição aleatória.
        
        Args:
            color_index (int, optional): Índice da cor
            name (str, optional): Nome personalizado do quadrado
            image_path (str, optional): Caminho para a imagem
        """
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
            
            # Garantir que name seja uma string válida
            if name is not None:
                square_name = str(name)
            else:
                square_name = f"Jogador {color_index+1}"
                
            new_square = Square(x, y, self.square_size, color, name=square_name, color_index=color_index)
            
            # Configurar a área para o novo quadrado
            new_square.set_area(self.area_x, self.area_y, self.area_size)
            new_square.set_speed_limits(self.min_speed, self.max_speed)
            
            # Configurar a imagem se fornecida
            if image_path and os.path.exists(image_path):
                success = new_square.set_image(image_path)
                if success:
                    print(f"Imagem aplicada ao quadrado: {square_name}")
            
            # Verificar sobreposição com quadrados existentes
            overlap = False
            for sq in self.squares:
                if sq.is_alive and new_square.check_collision(sq):
                    overlap = True
                    break
            
            attempts += 1
        
        return new_square
    
    def create_squares(self):
        """Cria os quadrados iniciais com configurações personalizadas."""
        self.squares = []
        
        # Usar as configurações personalizadas para cada quadrado
        for i, config in enumerate(self.square_configs):
            color_index = config.get("color_index", i)
            name = config.get("name")
            image_path = config.get("image_path")
            
            new_square = self.create_square(
                color_index=color_index,
                name=name,
                image_path=image_path
            )
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
                        
                        # Resetar estado de fim de jogo
                        self.game_over = False
                        self.winner = None
                
                elif event.key == pygame.K_r and self.game_over:
                    # Reiniciar o jogo
                    self.game_over = False
                    self.winner = None
                    self.create_squares()
    
    def update(self):
        """Atualiza o estado do jogo."""
        # Se o jogo acabou, só atualizar partículas para animação
        if self.game_over:
            for square in self.squares:
                if not square.is_alive:
                    square.update()
            return
            
        # Verificar se todos os quadrados vivos foram destruídos
        alive_squares = sum(1 for square in self.squares if square.is_alive)
        
        # Verificar condição de fim de jogo
        if alive_squares < 2:
            # Encontrar o último quadrado sobrevivente ou o que eliminou o outro
            for square in self.squares:
                if square.is_alive:
                    self.game_over = True
                    self.winner = square
                    break
                
                # Se nenhum quadrado está vivo, verificar quem eliminou quem
                if not square.is_alive and square.killed_by:
                    self.game_over = True
                    self.winner = square.killed_by
                    break
        
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
                    
                    # Verificar se o quadrado j foi eliminado pelo quadrado i
                    if not self.squares[j].is_alive and self.squares[j].killed_by == self.squares[i]:
                        self.game_over = True
                        self.winner = self.squares[i]
                    
                    # Verificar se o quadrado i foi eliminado pelo quadrado j
                    if not self.squares[i].is_alive and self.squares[i].killed_by == self.squares[j]:
                        self.game_over = True
                        self.winner = self.squares[j]
        
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
    
    def render_player_info(self):
        """Renderiza as informações dos jogadores no topo da tela."""
        # Superfície do cabeçalho
        header = pygame.Surface((self.width, self.header_height))
        
        # Gradiente de fundo para o cabeçalho
        for y in range(self.header_height):
            # Efeito de gradiente suave: mais escuro na parte inferior
            color_value = max(25, 40 - int(y / self.header_height * 25))
            pygame.draw.line(header, (color_value, color_value, color_value + 10), 
                             (0, y), (self.width, y))
        
        # Título do jogo
        title = self.title_font.render("BATALHA MORTAL ATE A MORTE", True, (220, 220, 220))
        header.blit(title, (self.width // 2 - title.get_width() // 2, 10))
        
        # Linha divisória decorativa
        pygame.draw.line(header, (100, 100, 100), (20, 35), (self.width - 20, 35), 1)
        
        # Informações para cada jogador
        player_width = (self.width - 40) // len(self.squares)
        
        for i, square in enumerate(self.squares):
            # Calcular posição para este jogador
            x_pos = 20 + i * player_width
            
            # Painel de jogador com borda
            panel_rect = pygame.Rect(x_pos, 42, player_width - 10, 30)
            pygame.draw.rect(header, (45, 45, 45), panel_rect)
            pygame.draw.rect(header, square.original_color, panel_rect, 1)
            
            # Ícone do jogador (miniatura quadrada)
            icon_size = 20
            icon_rect = pygame.Rect(x_pos + 5, 47, icon_size, icon_size)
            
            if square.use_image and square.image:
                # Usar a imagem redimensionada
                mini_img = pygame.transform.scale(square.image, (icon_size, icon_size))
                header.blit(mini_img, icon_rect)
            else:
                # Desenhar um quadrado com a cor do jogador
                pygame.draw.rect(header, square.original_color, icon_rect)
            
            # Nome do jogador
            name_text = self.info_font.render(str(square.name), True, (220, 220, 220))
            header.blit(name_text, (x_pos + icon_size + 10, 47))
            
            # Barra de vida
            life_width = player_width - 20 - icon_size - 10  # Espaço restante
            life_height = 6
            
            # Fundo da barra (cinza escuro)
            life_bg_rect = pygame.Rect(x_pos + icon_size + 10, 
                                     47 + name_text.get_height() + 2, 
                                     life_width, life_height)
            pygame.draw.rect(header, (60, 60, 60), life_bg_rect)
            
            # Barra de vida atual colorida
            if square.is_alive:
                life_ratio = square.lives / square.max_lives
                life_color = self.get_health_color(life_ratio)
                
                life_fill_rect = pygame.Rect(x_pos + icon_size + 10, 
                                          47 + name_text.get_height() + 2,
                                          int(life_width * life_ratio), life_height)
                pygame.draw.rect(header, life_color, life_fill_rect)
                
                # Texto de vida
                life_text = self.info_font.render(f"{square.lives}/{square.max_lives}", 
                                               True, (220, 220, 220))
                life_text_x = x_pos + icon_size + 10 + life_width/2 - life_text.get_width()/2
                header.blit(life_text, (life_text_x, 47 + name_text.get_height() + 8))
            else:
                # Texto "ELIMINADO" se o jogador estiver morto
                elim_text = self.info_font.render("ELIMINADO", True, (220, 50, 50))
                elim_x = x_pos + icon_size + 10 + life_width/2 - elim_text.get_width()/2
                header.blit(elim_text, (elim_x, 47 + name_text.get_height() + 3))
        
        # Desenhar o cabeçalho na tela
        self.window.blit(header, (0, 0))
    
    def get_health_color(self, ratio):
        """Retorna uma cor baseada na proporção de vida (verde->amarelo->vermelho)."""
        if ratio > 0.6:
            # Verde para vida alta
            return (50, 200, 50)
        elif ratio > 0.3:
            # Amarelo para vida média
            return (220, 220, 50)
        else:
            # Vermelho para vida baixa
            return (220, 50, 50)
    
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
        
        # Renderizar informações dos jogadores no topo
        self.render_player_info()
        
        # Exibir informações sobre o menu
        menu_info = INFO_FONT.render("Pressione ESC para o MENU", True, LIGHT_GRAY)
        self.window.blit(menu_info, (10, self.height - 25))
        
        # Exibir mensagem de fim de jogo se o jogo acabou
        if self.game_over and self.winner:
            # Criar uma sobreposição semitransparente
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))  # Preto com 70% de opacidade
            self.window.blit(overlay, (0, 0))
            
            # Criar texto de fim de jogo
            game_over_font = pygame.font.SysFont("Arial", 48, bold=True)
            game_over_text = game_over_font.render("FIM DE JOGO", True, WHITE)
            
            # Usar o nome personalizado do vencedor
            winner_font = pygame.font.SysFont("Arial", 36)
            winner_text = winner_font.render(f"{str(self.winner.name)} Venceu!", True, self.winner.original_color)
            
            # Criar instrução de reinício
            restart_font = pygame.font.SysFont("Arial", 24)
            restart_text = restart_font.render("Pressione ESC para menu ou R para reiniciar", True, LIGHT_GRAY)
            
            # Posicionar e exibir textos
            self.window.blit(game_over_text, 
                              (self.width//2 - game_over_text.get_width()//2, 
                               self.height//2 - 80))
            self.window.blit(winner_text, 
                              (self.width//2 - winner_text.get_width()//2, 
                               self.height//2 - 20))
            self.window.blit(restart_text, 
                              (self.width//2 - restart_text.get_width()//2, 
                               self.height//2 + 40))
        
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