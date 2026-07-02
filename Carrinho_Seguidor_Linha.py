import tkinter as tk
import math

class Ambiente:
    """Interface direta e simplificada para garantir execução em qualquer ambiente."""
    def __init__(self, root):
        self.root = root
        self.root.title("🏁 CARROS SIMULADOR")
        self.root.configure(bg="#1a1a24")
        
        self.rodando = True
        
        # -------------------------------------------------------------------------
        # PAINEL LATERAL DIRETO NO ROOT (Sem frames intermediários)
        # -------------------------------------------------------------------------
        self.painel = tk.Frame(root, bg="#2a2a3a", width=220, height=720, bd=2, relief=tk.RIDGE)
        self.painel.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        self.painel.pack_propagate(False)
        
        tk.Label(self.painel, text="🏎️ COMANDOS", font=("Arial", 14, "bold"), bg="#2a2a3a", fg="#ffffff").pack(pady=20)
        
        self.btn_pausa = tk.Button(
            self.painel, text="[⚠️ PARAR PARTIDA]", font=("Consolas", 10, "bold"),
            bg="#ffcc00", fg="#000000", width=18, height=2, command=self.alternar_pausa
        )
        self.btn_pausa.pack(pady=15)
        
        self.btn_reset = tk.Button(
            self.painel, text="[🏁 RESETAR PARTIDA]", font=("Consolas", 10, "bold"),
            bg="#00ff00", fg="#000000", width=18, height=2, command=self.reiniciar_simulacao
        )
        self.btn_reset.pack(pady=10)
        
        tk.Label(self.painel, text="🚀 VELOCIDADE:", font=("Consolas", 10, "bold"), bg="#2a2a3a", fg="#33ccff").pack(pady=(20, 5))
        
        self.slider_velocidade = tk.Scale(
            self.painel, from_=1, to=10, orient=tk.HORIZONTAL,
            bg="#2a2a3a", fg="#ffffff", highlightthickness=0, length=160
        )
        self.slider_velocidade.set(5)
        self.slider_velocidade.pack()
        
        self.lbl_status = tk.Label(
            self.painel, text="[RADIO]: Green Flag!\nCarro na pista.", font=("Consolas", 9, "bold"),
            bg="#111116", fg="#00ff00", width=20, height=4, bd=2, relief=tk.SUNKEN, anchor="nw", justify=tk.LEFT, padx=5, pady=5
        )
        self.lbl_status.pack(side=tk.BOTTOM, pady=20)

        # -------------------------------------------------------------------------
        # CANVAS DIRETO NO ROOT (Evita bugs de sobreposição)
        # -------------------------------------------------------------------------
        self.canvas = tk.Canvas(root, width=900, height=700, bg="#e0e0e0", bd=0, highlightthickness=0)
        self.canvas.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        # Inicializando os objetos de jogo
        self.pista = Pista(self.canvas)
        self.sensor = Sensor(self.canvas)
        
        self.x_ini, self.y_ini = self.pista.obter_ponto_inicial()
        self.carrinho = Carrinho(self.canvas, self.sensor, self.x_ini, self.y_ini, self.pista.pontos)
        
        # Força o desenho inicial dos elementos
        self.pista.desenhar()
        self.carrinho.desenhar()
        
        # Dispara o loop de animação
        self.atualizar_simulacao()

    def alternar_pausa(self):
        self.rodando = not self.rodando
        if self.rodando:
            self.btn_pausa.config(text="[⚠️ PIT STOP]", bg="#ffcc00")
            self.lbl_status.config(text="[RADIO]: Box fechado.\nRetornando à corrida!", fg="#00ff00")
        else:
            self.btn_pausa.config(text="[▶️ OUT OF BOXES]", bg="#00ff00")
            self.lbl_status.config(text="[RADIO]: No Pit Lane.\nTrocando pneus...", fg="#ffcc00")

    def reiniciar_simulacao(self):
        self.carrinho.reiniciar(self.x_ini, self.y_ini)
        self.lbl_status.config(text="[RADIO]: Grid resetado.\nCarro na largada!", fg="#33ccff")

    def atualizar_simulacao(self):
        if self.rodando:
            nova_velocidade = float(self.slider_velocidade.get())
            self.carrinho.mover(nova_velocidade)
            self.carrinho.desenhar()
            
        # FORÇA O WINDOWS/VS CODE A REDESENHAR A TELA ATIVAMENTE (Resolve o congelamento)
        self.root.update()
        self.root.after(15, self.atualizar_simulacao)


class Pista:
    def __init__(self, canvas):
        self.canvas = canvas
        # Coordenadas do hexágono centralizado
        self.pontos = [
            450, 100,
            720, 220,
            720, 480,
            450, 600,
            180, 480,
            180, 220
        ]
        
    def obter_ponto_inicial(self):
        return self.pontos[0], self.pontos[1]

    def desenhar(self):
        # Zebra Larga (Borda vermelha externa)
        self.canvas.create_polygon(self.pontos, fill="", outline="#e10600", width=24, tags="zebra")
        # Pista de Asfalto (Preto clássico para o sensor ler perfeitamente)
        self.canvas.create_polygon(self.pontos, fill="", outline="#111111", width=12, tags="pista")
        # Linha central pontilhada
        self.canvas.create_polygon(self.pontos, fill="", outline="#ffffff", width=1, dash=(8, 8))


class EixoCarrinho:
    def __init__(self, x, y):
        self.comprimento = 24 
        self.x = x
        self.y = y
        self.angulo = 0
        
        self.x_esq, self.y_esq = 0, 0
        self.x_dir, self.y_dir = 0, 0
        self.x_pivo, self.y_pivo = x, y

    def atualizar_geometria(self, x, y, angulo):
        self.x = x
        self.y = y
        self.angulo = angulo
        
        metade = self.comprimento / 2
        self.x_esq = self.x - metade * math.sin(self.angulo)
        self.y_esq = self.y + metade * math.cos(self.angulo)
        
        self.x_dir = self.x + metade * math.sin(self.angulo)
        self.y_dir = self.y - metade * math.cos(self.angulo)
        
        self.x_pivo = self.x
        self.y_pivo = self.y


class Sensor:
    def __init__(self, canvas):
        self.canvas = canvas

    def esta_na_pista(self, x, y):
        # Lê uma pequena área ao redor do ponto central
        itens = self.canvas.find_overlapping(x - 1, y - 1, x + 1, y + 1)
        for item in itens:
            if "pista" in self.canvas.gettags(item):
                return True
        return False


class Carrinho:
    def __init__(self, canvas, sensor, x, y, pontos_pista):
        self.canvas = canvas
        self.sensor = sensor
        self.eixo = EixoCarrinho(x, y)
        
        self.destinos = [(pontos_pista[i], pontos_pista[i+1]) for i in range(0, len(pontos_pista), 2)]
        self.indice_destino = 1
        
        self.id_corpo = None
        self.id_pivo = None

    def reiniciar(self, x, y):
        self.indice_destino = 1
        self.eixo.atualizar_geometria(x, y, 0)

    def mover(self, velocidade):
        alvo_x, alvo_y = self.destinos[self.indice_destino]
        
        dx = alvo_x - self.eixo.x
        dy = alvo_y - self.eixo.y
        distancia = math.hypot(dx, dy)
        
        if distancia < velocidade:
            self.indice_destino = (self.indice_destino + 1) % len(self.destinos)
            alvo_x, alvo_y = self.destinos[self.indice_destino]
            dx = alvo_x - self.eixo.x
            dy = alvo_y - self.eixo.y
            distancia = math.hypot(dx, dy)

        angulo = math.atan2(dy, dx)
        
        novo_x = self.eixo.x + (dx / distancia) * velocidade
        novo_y = self.eixo.y + (dy / distancia) * velocidade
        
        self.eixo.atualizar_geometria(novo_x, novo_y, angulo)

    def desenhar(self):
        # Deleta os desenhos antigos antes de fazer os novos
        if self.id_corpo: self.canvas.delete(self.id_corpo)
        if self.id_pivo: self.canvas.delete(self.id_pivo)
        
        # Desenha o Chassi do Carro em Vermelho F1 super destacado
        self.id_corpo = self.canvas.create_line(
            self.eixo.x_esq, self.eixo.y_esq,
            self.eixo.x_dir, self.eixo.y_dir,
            fill="#ff0000", width=8
        )
        
        # O Capacete do Piloto: Fica verde brilhante se estiver cruzando a pista preta
        na_linha = self.sensor.esta_na_pista(self.eixo.x_pivo, self.eixo.y_pivo)
        cor_capacete = "#00ff00" if na_linha else "#ffffff"
        
        r = 4.5
        self.id_pivo = self.canvas.create_oval(
            self.eixo.x_pivo - r, self.eixo.y_pivo - r,
            self.eixo.x_pivo + r, self.eixo.y_pivo + r,
            fill=cor_capacete, outline="#000000", width=1
        )


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1150x720") # Proporção perfeita para garantir exibição completa
    root.resizable(False, False)
    app = Ambiente(root)
    root.mainloop()