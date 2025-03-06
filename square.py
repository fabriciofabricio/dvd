"""
Implementação da classe Square para o jogo DVD Bounce Simulation.
"""
import random
import math
import pygame
import os
from constants import WHITE, YELLOW, COLLISION_FLASH_DURATION


class Particle:
    """Classe para representar uma partícula da explosão."""
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 5)
        self.lifetime = random.randint(30, 60)  # Duração em frames
        
        # Velocidade aleatória em todas as direções
        speed = random.uniform(1, 5)
        angle = random.uniform(0, 2 * math.pi)
        self.vx = speed * math.cos(angle)
        self.vy = speed * math.sin(angle)
        
        # Fade out gradual
        self.fade_speed = random.uniform(0.01, 0.05)
        self.alpha = 1.0  # Transparência inicial
    
    def update(self):
        """Atualiza a partícula."""
        self.x += self.vx
        self.y += self.vy
        
        # Adicionar gravidade leve
        self.vy += 0.05
        
        # Reduzir vida
        self.lifetime -= 1
        
        # Reduzir transparência
        self.alpha = max(0, self.alpha - self.fade_speed)
        
        # Reduzir tamanho gradualmente
        if self.size > 0.5:
            self.size -= 0.1
    
    def draw(self, surface):
        """Desenha a partícula."""
        if self.lifetime <= 0 or self.alpha <= 0:
            return
        
        # Ajustar cor com base na transparência
        r, g, b = self.color
        color_with_alpha = (r, g, b, int(self.alpha * 255))
        
        # Criar superfície com suporte a transparência
        particle_surface = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
        pygame.draw.circle(particle_surface, color_with_alpha, (int(self.size), int(self.size)), int(self.size))
        
        # Desenhar na superfície principal
        surface.blit(particle_surface, (int(self.x - self.size), int(self.y - self.size)))
    
    def is_alive(self):
        """Verifica se a partícula ainda está viva."""
        return self.lifetime > 0 and self.alpha > 0


class WallParticle(Particle):
    """Classe para representar uma partícula de colisão com parede."""
    def __init__(self, x, y, color, angle_range):
        super().__init__(x, y, color)
        
        # Redefinir propriedades para partículas de colisão com parede
        self.size = random.uniform(1.5, 3.5)
        self.lifetime = random.randint(15, 25)  # Vida mais curta
        
        # Velocidade baseada no ângulo de colisão
        angle = math.radians(random.uniform(angle_range[0], angle_range[1]))
        speed = random.uniform(2, 5)
        self.vx = speed * math.cos(angle)
        self.vy = speed * math.sin(angle)
        
        # Fade mais rápido
        self.fade_speed = random.uniform(0.05, 0.1)


class Square:
    """Classe que representa um quadrado na simulação."""
    def __init__(self, x, y, size, color, name=None, color_index=0):
        """
        Inicializa um quadrado com posição, tamanho e cor específicos.
        
        Args:
            x (float): Posição inicial x
            y (float): Posição inicial y
            size (int): Tamanho do quadrado
            color (tuple): Cor RGB do quadrado
            name (str, optional): Nome personalizado do quadrado
            color_index (int, optional): Índice da cor (para nomes padrão)
        """
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.original_color = color
        
        # Garantir que name seja uma string válida
        if name is not None:
            self.name = str(name)
        else:
            # Usar valor padrão se name não for fornecido
            try:
                self.name = f"Jogador {int(color_index)+1}"
            except (ValueError, TypeError):
                self.name = "Jogador"
        
        # Imagem personalizada (opcional)
        self.image = None
        self.use_image = False  # Flag para controlar o uso da imagem
        
        # Sistema de vidas
        self.lives = 5
        self.max_lives = 5  # Máximo de vidas
        self.is_alive = True
        self.invincible_timer = 0  # Tempo de invencibilidade após perder uma vida
        
        # Atributos para os espinhos
        self.has_spikes = False
        self.spike_timer = 0
        
        # Atributos para o power-up de velocidade
        self.speed_boost = False
        self.speed_boost_timer = 0
        self.original_min_speed = 0
        self.original_max_speed = 0
        
        # Valores de área (serão configurados pelo Game)
        self.area_x = 0
        self.area_y = 0
        self.area_size = 0
        self.min_speed = 1.5
        self.max_speed = 4.5
        
        # Velocidade inicial aleatória
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1.5, 4.5)  # Valores padrão iniciais
        self.vx = speed * math.cos(angle)
        self.vy = speed * math.sin(angle)
        
        # Massa (para cálculos de colisão realistas)
        self.mass = size * size  # Proporcional à área
        
        # Partículas para explosão
        self.particles = []
        
        # Rastreamento de quem eliminou este quadrado
        self.killed_by = None
        
        # Novos atributos para efeito de colisão com parede
        self.wall_collision = False
        self.wall_collision_timer = 0
        self.wall_collision_side = None
        self.wall_collision_position = (0, 0)
        self.wall_particles = []
        
        # Efeito de compressão ao colidir
        self.compression = 1.0  # 1.0 = sem compressão
        self.compression_side = None  # qual direção comprimir ('x' ou 'y')
    
    def set_image(self, image_path):
        """
        Define uma imagem para o quadrado.
        
        Args:
            image_path (str): Caminho para o arquivo de imagem
        """
        if not os.path.exists(image_path):
            print(f"ERRO: Imagem não encontrada: {image_path}")
            self.use_image = False
            return False
            
        try:
            print(f"Carregando imagem: {image_path}")
            self.image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.size, self.size))
            self.use_image = True
            print(f"Imagem carregada com sucesso: {image_path}")
            return True
        except (pygame.error, FileNotFoundError, TypeError) as e:
            print(f"ERRO ao carregar imagem {image_path}: {e}")
            self.image = None
            self.use_image = False
            return False
    
    def set_area(self, area_x, area_y, area_size):
        """Define a área de jogo para colisões."""
        self.area_x = area_x
        self.area_y = area_y
        self.area_size = area_size
    
    def set_speed_limits(self, min_speed, max_speed):
        """Define os limites de velocidade."""
        # Guardando valores originais para uso com power-ups
        self.original_min_speed = min_speed
        self.original_max_speed = max_speed
        
        # Se não estiver com boost de velocidade ativo, atualizar os valores atuais
        if not hasattr(self, 'speed_boost') or not self.speed_boost:
            self.min_speed = min_speed
            self.max_speed = max_speed
        else:
            # Se estiver com boost ativo, mantém a proporção do boost
            # mas atualiza os limites base
            self.min_speed = min_speed * 1.6
            self.max_speed = max_speed * 1.6
    
    def take_damage(self, attacker=None):
        """
        Reduz uma vida do quadrado.
        
        Args:
            attacker: O quadrado que causou o dano (opcional)
        """
        if self.invincible_timer > 0:
            return  # Não tomar dano durante a invencibilidade

        self.lives -= 1
        
        # Ativar invencibilidade com efeito de piscar branco
        self.invincible_timer = 90  # 1.5 segundos de invencibilidade
        
        # Verificar se ainda está vivo
        if self.lives <= 0:
            self.explode()
            self.is_alive = False
            # Armazenar qual quadrado eliminou este
            self.killed_by = attacker
    
    def explode(self):
        """Cria a animação de explosão quando o quadrado perde todas as vidas."""
        # Criar partículas a partir do centro do quadrado
        center_x = self.x + self.size / 2
        center_y = self.y + self.size / 2
        
        # Gerar várias partículas com a cor do quadrado
        num_particles = 50
        for _ in range(num_particles):
            # Posição aleatória dentro do quadrado
            particle_x = random.uniform(self.x, self.x + self.size)
            particle_y = random.uniform(self.y, self.y + self.size)
            
            # Criar partícula com a cor do quadrado
            self.particles.append(Particle(particle_x, particle_y, self.original_color))
    
    def create_wall_particles(self, side, position):
        """
        Cria partículas na colisão com a parede.
        
        Args:
            side (str): Lado da colisão ('left', 'right', 'top', 'bottom')
            position (tuple): Posição (x, y) da colisão
        """
        num_particles = random.randint(6, 10)
        x, y = position
        
        # Definir ângulo de dispersão baseado no lado da colisão
        if side == 'left':
            angle_range = (-30, 30)  # Partículas para a direita
        elif side == 'right':
            angle_range = (150, 210)  # Partículas para a esquerda
        elif side == 'top':
            angle_range = (60, 120)  # Partículas para baixo
        else:  # bottom
            angle_range = (240, 300)  # Partículas para cima
        
        # Criar partículas coloridas
        for _ in range(num_particles):
            # Variação na posição para efeito mais natural
            particle_x = x + random.uniform(-5, 5)
            particle_y = y + random.uniform(-5, 5)
            
            # Cor baseada na cor original do quadrado, mas mais brilhante
            r, g, b = self.original_color
            particle_color = (min(255, r + 80), min(255, g + 80), min(255, b + 80))
            
            # Criar e adicionar a partícula
            self.wall_particles.append(WallParticle(particle_x, particle_y, particle_color, angle_range))
    
    def handle_wall_collision(self):
        """Verifica e trata colisões com as paredes da área restrita."""
        # Inicialmente, não há colisão
        collision_occurred = False
        
        # Verificar colisão com parede esquerda
        if self.x <= self.area_x:
            self.vx = abs(self.vx) * 1.05  # Rebater com um pequeno boost
            self.x = self.area_x
            collision_occurred = True
            self.wall_collision_side = 'left'
            self.wall_collision_position = (self.area_x, self.y + self.size / 2)
            self.compression = 0.7  # Comprimir para 70%
            self.compression_side = 'x'
        
        # Verificar colisão com parede direita
        elif self.x + self.size >= self.area_x + self.area_size:
            self.vx = -abs(self.vx) * 1.05  # Rebater com um pequeno boost
            self.x = self.area_x + self.area_size - self.size
            collision_occurred = True
            self.wall_collision_side = 'right'
            self.wall_collision_position = (self.area_x + self.area_size, self.y + self.size / 2)
            self.compression = 0.7  # Comprimir para 70%
            self.compression_side = 'x'
        
        # Verificar colisão com parede superior
        if self.y <= self.area_y:
            self.vy = abs(self.vy) * 1.05  # Rebater com um pequeno boost
            self.y = self.area_y
            collision_occurred = True
            self.wall_collision_side = 'top'
            self.wall_collision_position = (self.x + self.size / 2, self.area_y)
            self.compression = 0.7  # Comprimir para 70%
            self.compression_side = 'y'
        
        # Verificar colisão com parede inferior
        elif self.y + self.size >= self.area_y + self.area_size:
            self.vy = -abs(self.vy) * 1.05  # Rebater com um pequeno boost
            self.y = self.area_y + self.area_size - self.size
            collision_occurred = True
            self.wall_collision_side = 'bottom'
            self.wall_collision_position = (self.x + self.size / 2, self.area_y + self.area_size)
            self.compression = 0.7  # Comprimir para 70%
            self.compression_side = 'y'
        
        # Se ocorreu colisão, ativar os efeitos visuais
        if collision_occurred:
            self.wall_collision = True
            self.wall_collision_timer = COLLISION_FLASH_DURATION
            self.create_wall_particles(self.wall_collision_side, self.wall_collision_position)
            
            # Limitar a velocidade após a colisão para evitar que fique muito rápido
            speed = math.sqrt(self.vx**2 + self.vy**2)
            if speed > self.max_speed:
                ratio = self.max_speed / speed
                self.vx *= ratio
                self.vy *= ratio
    
    def activate_speed_boost(self, duration):
        """
        Ativa o efeito de aumento de velocidade por um período.
        
        Args:
            duration (int): Duração em frames para o boost de velocidade
        """
        self.speed_boost = True
        self.speed_boost_timer = duration
        
        # Guardar os limites de velocidade originais se não existirem
        if not hasattr(self, 'original_min_speed') or self.original_min_speed == 0:
            self.original_min_speed = self.min_speed / 1.6
        if not hasattr(self, 'original_max_speed') or self.original_max_speed == 0:
            self.original_max_speed = self.max_speed / 1.6
        
        # Aumentar os limites de velocidade em 60%
        self.min_speed = self.original_min_speed * 1.6
        self.max_speed = self.original_max_speed * 1.6
        
        # Dar um impulso imediato na velocidade atual
        current_speed = math.sqrt(self.vx**2 + self.vy**2)
        angle = math.atan2(self.vy, self.vx)
        target_speed = min(current_speed * 1.5, self.max_speed)
        
        self.vx = target_speed * math.cos(angle)
        self.vy = target_speed * math.sin(angle)
    
    def get_corners(self):
        """Retorna as coordenadas dos quatro cantos do quadrado."""
        return [
            (self.x, self.y),  # Superior esquerdo
            (self.x + self.size, self.y),  # Superior direito
            (self.x, self.y + self.size),  # Inferior esquerdo
            (self.x + self.size, self.y + self.size)  # Inferior direito
        ]
    
    def get_center(self):
        """Retorna o centro do quadrado."""
        return (self.x + self.size / 2, self.y + self.size / 2)
    
    def update(self):
        """Atualiza a posição e velocidade do quadrado"""
        # Atualizar partículas se o quadrado explodiu
        if not self.is_alive:
            for particle in self.particles:
                particle.update()
            # Remover partículas mortas
            self.particles = [p for p in self.particles if p.is_alive()]
            return
        
        # Reduzir timer de invencibilidade e aplicar efeito de piscar
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
            
            # Efeito piscante durante a invencibilidade
            if self.invincible_timer % 8 < 4:  # Alternar a cada 4 frames para um piscar mais rápido
                self.color = WHITE  # Branco
            else:
                self.color = self.original_color
                
            # Quando terminar a invencibilidade, garantir que a cor volta ao normal
            if self.invincible_timer == 0:
                self.color = self.original_color
        else:
            # Se não estiver invencível, garantir que a cor é a original
            self.color = self.original_color
        
        # Atualizar a posição
        self.x += self.vx
        self.y += self.vy
        
        # Verificar colisão com as paredes
        self.handle_wall_collision()
        
        # Atualizar timer de colisão com parede
        if self.wall_collision_timer > 0:
            self.wall_collision_timer -= 1
            if self.wall_collision_timer == 0:
                self.wall_collision = False
            
            # Restaurar gradualmente a forma original
            if self.compression < 1.0:
                # Restaurar mais rapidamente à medida que o tempo passa
                self.compression += (1.0 - self.compression) * 0.2
                if self.compression > 0.98:
                    self.compression = 1.0
        
        # Atualizar partículas de colisão com parede
        for particle in self.wall_particles:
            particle.update()
        # Remover partículas que acabaram
        self.wall_particles = [p for p in self.wall_particles if p.is_alive()]
        
        # Atualizar timer de espinhos
        if self.has_spikes and self.spike_timer > 0:
            self.spike_timer -= 1
            if self.spike_timer == 0:
                self.has_spikes = False
                
        # Atualizar timer de speed boost
        if self.speed_boost and self.speed_boost_timer > 0:
            self.speed_boost_timer -= 1
            
            # Atualizar a velocidade atual para refletir o boost
            current_speed = math.sqrt(self.vx**2 + self.vy**2)
            angle = math.atan2(self.vy, self.vx)
            
            # Aplicar um pequeno impulso adicional para manter o boost
            if current_speed < self.max_speed:
                new_speed = min(current_speed * 1.01, self.max_speed)
                self.vx = new_speed * math.cos(angle)
                self.vy = new_speed * math.sin(angle)
            
            # Quando o boost acabar, voltar às velocidades normais
            if self.speed_boost_timer == 0:
                self.speed_boost = False
                # Restaurar os limites originais de velocidade
                self.min_speed = self.original_min_speed
                self.max_speed = self.original_max_speed
                
                # Ajustar a velocidade atual se estiver acima do máximo original
                current_speed = math.sqrt(self.vx**2 + self.vy**2)
                if current_speed > self.max_speed:
                    ratio = self.max_speed / current_speed
                    self.vx *= ratio
                    self.vy *= ratio
        
        # Variar levemente a velocidade ao longo do tempo (extra)
        self.vx += random.uniform(-0.03, 0.03)
        self.vy += random.uniform(-0.03, 0.03)
        
        # Limitar a velocidade mínima e máxima
        speed = math.sqrt(self.vx**2 + self.vy**2)
        
        if speed < self.min_speed:
            self.vx = self.vx / speed * self.min_speed
            self.vy = self.vy / speed * self.min_speed
        elif speed > self.max_speed:
            self.vx = self.vx / speed * self.max_speed
            self.vy = self.vy / speed * self.max_speed
    
    def draw(self, surface):
        """Desenha o quadrado na superfície"""
        # Desenhar partículas se o quadrado explodiu
        if not self.is_alive:
            for particle in self.particles:
                particle.draw(surface)
            return
        
        # Desenhar partículas de colisão com parede
        for particle in self.wall_particles:
            particle.draw(surface)
        
        # Calcular dimensões com compressão para efeito de bounce
        width = self.size
        height = self.size
        
        # Aplicar compressão se estiver colidindo com uma parede
        if self.compression < 1.0:
            if self.compression_side == 'x':
                # Compressão horizontal
                width = int(self.size * self.compression)
                height = int(self.size * (2 - self.compression))  # Expandir verticalmente
            else:  # compression_side == 'y'
                # Compressão vertical
                height = int(self.size * self.compression)
                width = int(self.size * (2 - self.compression))  # Expandir horizontalmente
        
        # Ajustar posição para manter o quadrado centralizado
        x_offset = (self.size - width) / 2
        y_offset = (self.size - height) / 2
        adjusted_x = self.x + x_offset
        adjusted_y = self.y + y_offset
        
        # Preparar a cor do quadrado (se tiver speed boost, adicionar efeito azulado)
        current_color = self.color
        if self.speed_boost and pygame.time.get_ticks() % 10 < 5:  # Piscar rápido
            # Adicionar um tom azulado
            r, g, b = self.color
            current_color = (max(0, r-30), max(0, g-30), min(255, b+80))
        
        # Desenhar o quadrado base (com imagem ou cor sólida)
        if self.use_image and self.image:
            # Se estiver com compressão, redimensionar a imagem
            if self.compression < 1.0:
                scaled_image = pygame.transform.scale(self.image, (width, height))
            else:
                scaled_image = self.image
                
            # Se estiver invencível e piscando, mostrar efeito
            if self.invincible_timer > 0 and self.invincible_timer % 8 < 4:
                # Criar uma superfície branca semitransparente
                white_overlay = pygame.Surface((width, height), pygame.SRCALPHA)
                white_overlay.fill((255, 255, 255, 150))  # Branco semi-transparente
                
                # Desenhar primeiro a imagem e depois o overlay
                surface.blit(scaled_image, (int(adjusted_x), int(adjusted_y)))
                surface.blit(white_overlay, (int(adjusted_x), int(adjusted_y)))
            else:
                # Desenhar apenas a imagem
                surface.blit(scaled_image, (int(adjusted_x), int(adjusted_y)))
                
                # Se tiver speed boost, desenhar um brilho azul ao redor
                if self.speed_boost:
                    # Superfície para o brilho
                    glow_surface = pygame.Surface((width+20, height+20), pygame.SRCALPHA)
                    pygame.draw.rect(glow_surface, (50, 150, 255, 50), (10, 10, width, height), 5)
                    surface.blit(glow_surface, (int(adjusted_x-10), int(adjusted_y-10)))
        else:
            # Usar cor sólida se não tiver imagem ou se use_image for False
            pygame.draw.rect(surface, current_color, (adjusted_x, adjusted_y, width, height))
            
            # Se tiver speed boost, desenhar um brilho azul ao redor
            if self.speed_boost:
                # Efeito de rastro azul de velocidade
                trail_length = 10
                trail_alpha = 30
                for i in range(1, trail_length+1):
                    trail_x = adjusted_x - self.vx * i * 0.2
                    trail_y = adjusted_y - self.vy * i * 0.2
                    trail_surface = pygame.Surface((width, height), pygame.SRCALPHA)
                    trail_color = (50, 150, 255, trail_alpha - i * 2)
                    pygame.draw.rect(trail_surface, trail_color, (0, 0, width, height))
                    surface.blit(trail_surface, (int(trail_x), int(trail_y)))
        
        # Desenhar efeito de flash na borda se houve colisão recente
        if self.wall_collision and self.wall_collision_timer > 0:
            # Intensidade do flash baseada no timer
            flash_alpha = int(min(200, 255 * (self.wall_collision_timer / COLLISION_FLASH_DURATION)))
            flash_color = (255, 255, 255, flash_alpha)
            flash_width = 3  # Espessura da linha do flash
            
            # Criar superfície com suporte a transparência
            flash_surface = pygame.Surface((self.area_size, self.area_size), pygame.SRCALPHA)
            
            # Desenhar o flash de acordo com o lado da colisão
            if self.wall_collision_side == 'left':
                # Flash na parede esquerda
                pygame.draw.line(flash_surface, flash_color, 
                                 (0, max(0, self.y - self.area_y - 20)), 
                                 (0, min(self.area_size, self.y + self.size - self.area_y + 20)), 
                                 flash_width)
            elif self.wall_collision_side == 'right':
                # Flash na parede direita
                pygame.draw.line(flash_surface, flash_color, 
                                 (self.area_size - 1, max(0, self.y - self.area_y - 20)), 
                                 (self.area_size - 1, min(self.area_size, self.y + self.size - self.area_y + 20)), 
                                 flash_width)
            elif self.wall_collision_side == 'top':
                # Flash na parede superior
                pygame.draw.line(flash_surface, flash_color, 
                                 (max(0, self.x - self.area_x - 20), 0), 
                                 (min(self.area_size, self.x + self.size - self.area_x + 20), 0), 
                                 flash_width)
            elif self.wall_collision_side == 'bottom':
                # Flash na parede inferior
                pygame.draw.line(flash_surface, flash_color, 
                                 (max(0, self.x - self.area_x - 20), self.area_size - 1), 
                                 (min(self.area_size, self.x + self.size - self.area_x + 20), self.area_size - 1), 
                                 flash_width)
            
            # Desenhar a superfície de flash no jogo
            surface.blit(flash_surface, (self.area_x, self.area_y))
        
        # Desenhar espinhos se o quadrado tiver espinhos
        if self.has_spikes:
            # Definir parâmetros para os espinhos
            spike_length = self.size // 2.5
            base_color = YELLOW
            tip_color = (255, 150, 0)  # Laranja para a ponta
            
            # Adicionar pulsação aos espinhos
            pulse = (math.sin(pygame.time.get_ticks() / 200) + 1) * 0.2 + 0.8  # 0.8 a 1.2
            adjusted_length = int(spike_length * pulse)
            
            # Número de espinhos por lado
            num_spikes = 4
            
            # Espinhos superiores
            for i in range(num_spikes):
                x_pos = self.x + (i + 1) * self.size // (num_spikes + 1)
                # Criar pontos para um espinho mais elegante
                left_point = (x_pos - adjusted_length//3, self.y - adjusted_length//2)
                right_point = (x_pos + adjusted_length//3, self.y - adjusted_length//2)
                tip_point = (x_pos, self.y - adjusted_length)
                
                # Desenhar o corpo principal do espinho
                pygame.draw.polygon(surface, base_color, [
                    (x_pos, self.y),
                    left_point,
                    tip_point,
                    right_point
                ])
                
                # Desenhar uma linha brilhante no centro do espinho
                pygame.draw.line(surface, tip_color, (x_pos, self.y), tip_point, 2)
                
                # Desenhar um pequeno círculo brilhante na ponta
                pygame.draw.circle(surface, (255, 255, 200), tip_point, 2)
            
            # Espinhos inferiores
            for i in range(num_spikes):
                x_pos = self.x + (i + 1) * self.size // (num_spikes + 1)
                # Criar pontos para um espinho mais elegante
                left_point = (x_pos - adjusted_length//3, self.y + self.size + adjusted_length//2)
                right_point = (x_pos + adjusted_length//3, self.y + self.size + adjusted_length//2)
                tip_point = (x_pos, self.y + self.size + adjusted_length)
                
                # Desenhar o corpo principal do espinho
                pygame.draw.polygon(surface, base_color, [
                    (x_pos, self.y + self.size),
                    left_point,
                    tip_point,
                    right_point
                ])
                
                # Desenhar uma linha brilhante no centro do espinho
                pygame.draw.line(surface, tip_color, (x_pos, self.y + self.size), tip_point, 2)
                
                # Desenhar um pequeno círculo brilhante na ponta
                pygame.draw.circle(surface, (255, 255, 200), tip_point, 2)
            
            # Espinhos laterais esquerdos
            for i in range(num_spikes):
                y_pos = self.y + (i + 1) * self.size // (num_spikes + 1)
                # Criar pontos para um espinho mais elegante
                top_point = (self.x - adjusted_length//2, y_pos - adjusted_length//3)
                bottom_point = (self.x - adjusted_length//2, y_pos + adjusted_length//3)
                tip_point = (self.x - adjusted_length, y_pos)
                
                # Desenhar o corpo principal do espinho
                pygame.draw.polygon(surface, base_color, [
                    (self.x, y_pos),
                    top_point,
                    tip_point,
                    bottom_point
                ])
                
                # Desenhar uma linha brilhante no centro do espinho
                pygame.draw.line(surface, tip_color, (self.x, y_pos), tip_point, 2)
                
                # Desenhar um pequeno círculo brilhante na ponta
                pygame.draw.circle(surface, (255, 255, 200), tip_point, 2)
            
            # Espinhos laterais direitos
            for i in range(num_spikes):
                y_pos = self.y + (i + 1) * self.size // (num_spikes + 1)
                # Criar pontos para um espinho mais elegante
                top_point = (self.x + self.size + adjusted_length//2, y_pos - adjusted_length//3)
                bottom_point = (self.x + self.size + adjusted_length//2, y_pos + adjusted_length//3)
                tip_point = (self.x + self.size + adjusted_length, y_pos)
                
                # Desenhar o corpo principal do espinho
                pygame.draw.polygon(surface, base_color, [
                    (self.x + self.size, y_pos),
                    top_point,
                    tip_point,
                    bottom_point
                ])
                
                # Desenhar uma linha brilhante no centro do espinho
                pygame.draw.line(surface, tip_color, (self.x + self.size, y_pos), tip_point, 2)
                
                # Desenhar um pequeno círculo brilhante na ponta
                pygame.draw.circle(surface, (255, 255, 200), tip_point, 2)
    
    def check_collision(self, other):
        """
        Verifica se há colisão com outro quadrado
        
        Args:
            other (Square): O outro quadrado para verificar colisão
            
        Returns:
            bool: True se há colisão, False caso contrário
        """
        # Não verificar colisão se algum dos quadrados está "morto"
        if not self.is_alive or not other.is_alive:
            return False
            
        return (self.x < other.x + other.size and
                self.x + self.size > other.x and
                self.y < other.y + other.size and
                self.y + self.size > other.y)
    
    def distance_to_edge(self, other, nx, ny):
        """Calcula a distância do centro deste quadrado à borda do outro quadrado na direção especificada."""
        cx1, cy1 = self.get_center()
        
        # Verificar qual borda interceptamos
        if nx > 0:  # Direção positiva em x (direita)
            edge_x = other.x
        else:  # Direção negativa em x (esquerda)
            edge_x = other.x + other.size
            
        if ny > 0:  # Direção positiva em y (baixo)
            edge_y = other.y
        else:  # Direção negativa em y (cima)
            edge_y = other.y + other.size
        
        # Calcular distância
        dx = edge_x - cx1
        dy = edge_y - cy1
        
        return abs(dx * nx + dy * ny)
    
    def handle_collision_corner(self, other):
        """Verifica e manipula uma possível colisão de canto com outro quadrado."""
        # Obter cantos dos dois quadrados
        corners1 = self.get_corners()
        corners2 = other.get_corners()
        
        # Centro dos quadrados
        cx1, cy1 = self.get_center()
        cx2, cy2 = other.get_center()
        
        # Encontrar o par de cantos mais próximos
        min_dist = float('inf')
        nearest_corner1 = None
        nearest_corner2 = None
        
        for c1 in corners1:
            for c2 in corners2:
                dist = math.sqrt((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2)
                if dist < min_dist:
                    min_dist = dist
                    nearest_corner1 = c1
                    nearest_corner2 = c2
        
        # Se a distância entre os cantos mais próximos for muito pequena
        # e os quadrados estão realmente próximos uns dos outros
        threshold = self.size * 0.3  # Ajuste este valor conforme necessário
        
        if min_dist < threshold:
            # Vetor do canto 1 para o canto 2
            dx = nearest_corner2[0] - nearest_corner1[0]
            dy = nearest_corner2[1] - nearest_corner1[1]
            dist = max(0.1, math.sqrt(dx**2 + dy**2))  # Evitar divisão por zero
            
            # Normalizar o vetor
            nx = dx / dist
            ny = dy / dist
            
            # Calcular a velocidade relativa na direção normal
            vrx = other.vx - self.vx
            vry = other.vy - self.vy
            vr_dot_n = vrx * nx + vry * ny
            
            # Se os quadrados estão se aproximando
            if vr_dot_n < 0:
                # Calcular o impulso com base na conservação de momentum e energia
                m1 = self.mass
                m2 = other.mass
                e = 1.0  # Coeficiente de restituição (1 = colisão elástica)
                
                j = -(1 + e) * vr_dot_n / ((1/m1) + (1/m2))
                
                # Aplicar o impulso
                self.vx -= j * nx / m1
                self.vy -= j * ny / m1
                other.vx += j * nx / m2
                other.vy += j * ny / m2
                
                # Adicionar um pequeno componente aleatório para evitar comportamentos repetitivos
                angle = random.uniform(0, math.pi/4)  # Pequena variação aleatória
                self.vx += 0.2 * math.cos(angle)
                self.vy += 0.2 * math.sin(angle)
                other.vx += 0.2 * math.cos(angle + math.pi)
                other.vy += 0.2 * math.sin(angle + math.pi)
                
                # Corrigir a sobreposição (afastar os quadrados)
                overlap = threshold - dist
                if overlap > 0:
                    self.x -= nx * overlap / 2
                    self.y -= ny * overlap / 2
                    other.x += nx * overlap / 2
                    other.y += ny * overlap / 2
                
                return True  # Colisão tratada
        
        return False  # Não foi uma colisão de canto
    
    def handle_collision(self, other):
        """
        Manipula a colisão com outro quadrado usando física melhorada
        
        Args:
            other (Square): O outro quadrado envolvido na colisão
        """
        # Verificar dano por espinhos
        if self.has_spikes and other.is_alive:
            other.take_damage(self)
        
        if other.has_spikes and self.is_alive:
            self.take_damage(other)
        
        # Tentar lidar com colisão de canto primeiro
        if self.handle_collision_corner(other):
            # Se foi uma colisão de canto, não precisamos fazer mais nada
            # Remover espinhos na colisão
            if self.has_spikes:
                self.has_spikes = False
                self.spike_timer = 0
            
            if other.has_spikes:
                other.has_spikes = False
                other.spike_timer = 0
                
            return
        
        # Calcular os centros dos quadrados
        center_x1, center_y1 = self.get_center()
        center_x2, center_y2 = other.get_center()
        
        # Vetor de colisão (do quadrado 1 para o quadrado 2)
        dx = center_x2 - center_x1
        dy = center_y2 - center_y1
        distance = max(1, math.sqrt(dx**2 + dy**2))  # Evitar divisão por zero
        
        # Normalizar o vetor de colisão
        nx = dx / distance
        ny = dy / distance
        
        # Determinar o tipo de colisão com base na direção do vetor normal
        # e na posição relativa dos quadrados
        collision_type = "unknown"
        
        # Se o vetor normal é principalmente horizontal
        if abs(nx) > abs(ny):
            if nx > 0:  # Quadrado 1 está à esquerda do quadrado 2
                collision_type = "right-left"
            else:  # Quadrado 1 está à direita do quadrado 2
                collision_type = "left-right"
        else:  # Se o vetor normal é principalmente vertical
            if ny > 0:  # Quadrado 1 está acima do quadrado 2
                collision_type = "bottom-top"
            else:  # Quadrado 1 está abaixo do quadrado 2
                collision_type = "top-bottom"
        
        # Ajustar o vetor normal com base no tipo de colisão para colisões mais precisas
        if collision_type == "right-left" or collision_type == "left-right":
            ny = 0  # Colisão puramente horizontal
            nx = 1 if nx > 0 else -1
        elif collision_type == "bottom-top" or collision_type == "top-bottom":
            nx = 0  # Colisão puramente vertical
            ny = 1 if ny > 0 else -1
        
        # Renormalizar o vetor após modificá-lo
        norm = math.sqrt(nx**2 + ny**2)
        if norm > 0:
            nx /= norm
            ny /= norm
        
        # Verificar se os quadrados estão se movendo na mesma direção e são quase paralelos
        v1_mag = math.sqrt(self.vx**2 + self.vy**2)
        v2_mag = math.sqrt(other.vx**2 + other.vy**2)
        
        if v1_mag > 0 and v2_mag > 0:
            dot_product = (self.vx * other.vx + self.vy * other.vy) / (v1_mag * v2_mag)
            
            # Se o produto escalar for próximo de 1, os vetores estão apontando 
            # aproximadamente na mesma direção
            if dot_product > 0.7:  # Limiar arbitrário para "mesma direção"
                # Decidir aleatoriamente qual quadrado mudar de direção
                if random.random() < 0.5:
                    # Mudar a direção deste quadrado por um ângulo significativo
                    angle = random.uniform(math.pi/2, math.pi)
                    speed = math.sqrt(self.vx**2 + self.vy**2)
                    self.vx = speed * math.cos(angle)
                    self.vy = speed * math.sin(angle)
                else:
                    # Mudar a direção do outro quadrado
                    angle = random.uniform(math.pi/2, math.pi)
                    speed = math.sqrt(other.vx**2 + other.vy**2)
                    other.vx = speed * math.cos(angle)
                    other.vy = speed * math.sin(angle)
            else:
                # Usar física de colisão melhorada para outros casos
                
                # Calcular as velocidades relativas na direção normal
                v1n = self.vx * nx + self.vy * ny
                v2n = other.vx * nx + other.vy * ny
                
                # Calcular as velocidades tangenciais (perpendiculares à normal)
                v1tx = self.vx - v1n * nx
                v1ty = self.vy - v1n * ny
                v2tx = other.vx - v2n * nx
                v2ty = other.vy - v2n * ny
                
                # Calcular novas velocidades normais após colisão (colisão elástica)
                # Usando conservação de momento e energia
                m1 = self.mass
                m2 = other.mass
                
                # Fórmula para colisão elástica
                new_v1n = (v1n * (m1 - m2) + 2 * m2 * v2n) / (m1 + m2)
                new_v2n = (v2n * (m2 - m1) + 2 * m1 * v1n) / (m1 + m2)
                
                # Calcular as novas velocidades combinando componentes normais e tangenciais
                self.vx = new_v1n * nx + v1tx
                self.vy = new_v1n * ny + v1ty
                other.vx = new_v2n * nx + v2tx
                other.vy = new_v2n * ny + v2ty
                
                # Adicionar um pequeno componente aleatório para evitar comportamentos repetitivos
                self.vx += random.uniform(-0.1, 0.1)
                self.vy += random.uniform(-0.1, 0.1)
                other.vx += random.uniform(-0.1, 0.1)
                other.vy += random.uniform(-0.1, 0.1)
        else:
            # Caso um dos quadrados tenha velocidade zero, aplicar um impulso simples
            self.vx = -self.vx * 0.9 + random.uniform(-0.2, 0.2)
            self.vy = -self.vy * 0.9 + random.uniform(-0.2, 0.2)
            other.vx = -other.vx * 0.9 + random.uniform(-0.2, 0.2)
            other.vy = -other.vy * 0.9 + random.uniform(-0.2, 0.2)
        
        # Remover espinhos na colisão
        if self.has_spikes:
            self.has_spikes = False
            self.spike_timer = 0
        
        if other.has_spikes:
            other.has_spikes = False
            other.spike_timer = 0
        
        # Separar os quadrados para evitar sobreposição
        # Calcular a sobreposição com base no tipo de colisão
        if collision_type == "right-left":
            overlap = (self.x + self.size) - other.x
        elif collision_type == "left-right":
            overlap = (other.x + other.size) - self.x
        elif collision_type == "bottom-top":
            overlap = (self.y + self.size) - other.y
        elif collision_type == "top-bottom":
            overlap = (other.y + other.size) - self.y
        else:
            # Fallback para o cálculo tradicional
            overlap = (self.size + other.size) / 2 - distance
        
        if overlap > 0:
            self.x -= nx * overlap / 2
            self.y -= ny * overlap / 2
            other.x += nx * overlap / 2
            other.y += ny * overlap / 2