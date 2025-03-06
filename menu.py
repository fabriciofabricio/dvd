"""
Implementação do menu do jogo DVD Bounce Simulation.
"""
import pygame
from constants import (
    WIDTH, HEIGHT, MARGIN, MIN_SPEED, MAX_SPEED, SQUARE_SIZE,
    MENU_FONT, TITLE_FONT, BLACK, WHITE, YELLOW
)


def show_menu(window, current_config=None):
    """
    Exibe um menu para ajustar as configurações do jogo
    
    Args:
        window: Superfície principal do pygame
        current_config: Dicionário com as configurações atuais
        
    Returns:
        tuple: (continuar_jogo, configurações_atualizadas, resetar)
               continuar_jogo é um booleano que indica se o jogo deve continuar
               configurações_atualizadas é um dicionário com as novas configurações
               resetar é um booleano que indica se as configurações devem ser resetadas
    """
    # Configurações iniciais para o menu (usar valores atuais ou padrão)
    if current_config:
        margin = current_config.get('margin', MARGIN)
        square_size = current_config.get('square_size', SQUARE_SIZE)
        min_speed = current_config.get('min_speed', MIN_SPEED)
        max_speed = current_config.get('max_speed', MAX_SPEED)
    else:
        margin = MARGIN
        square_size = SQUARE_SIZE
        min_speed = MIN_SPEED
        max_speed = MAX_SPEED
    
    # Opções do menu
    options = [
        "Tamanho dos Quadrados: {}",
        "Margem da Área: {}",
        "Velocidade Mínima: {:.1f}",
        "Velocidade Máxima: {:.1f}",
        "Restaurar Configurações Padrão",
        "Voltar ao Jogo",
        "Sair"
    ]
    
    selected_option = 0
    menu_active = True
    reset_config = False
    
    while menu_active:
        # Preencher a tela com um fundo escuro semitransparente
        menu_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        menu_surface.fill((0, 0, 0, 200))  # RGBA: preto com 80% de opacidade
        
        # Título do menu
        title = TITLE_FONT.render("MENU DE CONFIGURAÇÕES", True, WHITE)
        title_rect = title.get_rect(center=(WIDTH // 2, 100))
        menu_surface.blit(title, title_rect)
        
        # Renderizar as opções do menu
        for i, option in enumerate(options):
            if i == 0:
                text = option.format(square_size)
            elif i == 1:
                text = option.format(margin)
            elif i == 2:
                text = option.format(min_speed)
            elif i == 3:
                text = option.format(max_speed)
            else:
                text = option
            
            color = YELLOW if i == selected_option else WHITE
            rendered_text = MENU_FONT.render(text, True, color)
            text_rect = rendered_text.get_rect(center=(WIDTH // 2, 180 + i * 50))
            menu_surface.blit(rendered_text, text_rect)
            
            # Adicionar setas para as opções ajustáveis
            if i < 4:  # Apenas opções ajustáveis
                left_arrow = MENU_FONT.render("<", True, color)
                right_arrow = MENU_FONT.render(">", True, color)
                menu_surface.blit(left_arrow, (WIDTH // 2 - 150, 180 + i * 50 - 12))
                menu_surface.blit(right_arrow, (WIDTH // 2 + 150, 180 + i * 50 - 12))
        
        # Desenhar instruções
        instructions = MENU_FONT.render("Use as setas para navegar e alterar valores", True, (200, 200, 200))
        menu_surface.blit(instructions, (WIDTH // 2 - instructions.get_width() // 2, HEIGHT - 100))
        
        # Sobrepor a superfície do menu à tela principal
        window.blit(menu_surface, (0, 0))
        pygame.display.flip()
        
        # Processar eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False, {}, False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    menu_active = False  # Fechar o menu
                
                elif event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(options)
                
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(options)
                
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if selected_option == 4:  # Restaurar padrões
                        margin = MARGIN
                        square_size = SQUARE_SIZE
                        min_speed = MIN_SPEED
                        max_speed = MAX_SPEED
                        reset_config = True
                    elif selected_option == 5:  # Voltar ao jogo
                        menu_active = False
                    elif selected_option == 6:  # Sair
                        return False, {}, False
                
                # Ajustar valores com as setas esquerda/direita
                elif event.key == pygame.K_LEFT:
                    if selected_option == 0:  # Tamanho dos quadrados
                        square_size = max(10, square_size - 5)
                    elif selected_option == 1:  # Margem da área
                        margin = max(10, margin - 10)
                    elif selected_option == 2:  # Velocidade mínima
                        min_speed = max(0.5, min_speed - 0.5)
                    elif selected_option == 3:  # Velocidade máxima
                        max_speed = max(min_speed + 0.5, max_speed - 0.5)
                
                elif event.key == pygame.K_RIGHT:
                    if selected_option == 0:  # Tamanho dos quadrados
                        square_size = min(100, square_size + 5)
                    elif selected_option == 1:  # Margem da área
                        margin = min(min(WIDTH, HEIGHT) // 2 - 50, margin + 10)
                    elif selected_option == 2:  # Velocidade mínima
                        min_speed = min(max_speed - 0.5, min_speed + 0.5)
                    elif selected_option == 3:  # Velocidade máxima
                        max_speed = min(10.0, max_speed + 0.5)
    
    # Retornar as configurações atualizadas
    return True, {
        'margin': margin,
        'square_size': square_size,
        'min_speed': min_speed,
        'max_speed': max_speed
    }, reset_config