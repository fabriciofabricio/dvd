"""
Ponto de entrada principal para o jogo DVD Bounce Simulation.

Este jogo simula o efeito da tela do DVD, onde objetos se movem e rebatam nas
bordas da janela. O jogo inclui dois quadrados coloridos que se movem e colidem
entre si, com power-ups de espinhos que aparecem periodicamente.

Para executar o jogo:
    python main.py
"""
from game import Game


def main():
    """Função principal que inicia o jogo."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()