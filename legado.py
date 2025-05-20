# Código Original - Sistema de Gerenciamento de Biblioteca

import datetime


livros = []
usuarios = []
emprestimos = []

def adicionar_livro(titulo, autor, isbn, ano):
    livro = {
        'titulo': titulo,
        'autor': autor,
        'isbn': isbn,
        'ano': ano,
        'disponivel': True
    }
    livros.append(livro)
    print("Livro adicionado!")

def buscar_livro(termo):
    for livro in livros:
        if termo in livro['titulo'] or termo in livro['autor']:
            return livro
    return None

def emprestar_livro(isbn, usuario_id):
    livro_encontrado = None
    for livro in livros:
        if livro['isbn'] == isbn:
            livro_encontrado = livro
            break
    
    if livro_encontrado and livro_encontrado['disponivel']:
        usuario_encontrado = None
        for usuario in usuarios:
            if usuario['id'] == usuario_id:
                usuario_encontrado = usuario
                break
        
        if usuario_encontrado:
            livro_encontrado['disponivel'] = False
            emprestimo = {
                'isbn': isbn,
                'usuario_id': usuario_id,
                'data_emprestimo': datetime.datetime.now(),
                'data_devolucao': None
            }
            emprestimos.append(emprestimo)
            print(f"Livro {livro_encontrado['titulo']} emprestado para {usuario_encontrado['nome']}")
        else:
            print("Usuário não encontrado!")
    else:
        print("Livro não disponível!")

def devolver_livro(isbn, usuario_id):
    for emprestimo in emprestimos:
        if emprestimo['isbn'] == isbn and emprestimo['usuario_id'] == usuario_id and emprestimo['data_devolucao'] is None:
            emprestimo['data_devolucao'] = datetime.datetime.now()
            for livro in livros:
                if livro['isbn'] == isbn:
                    livro['disponivel'] = True
                    print(f"Livro {livro['titulo']} devolvido!")
                    return
    print("Empréstimo não encontrado!")

def listar_emprestimos():
    for emprestimo in emprestimos:
        if emprestimo['data_devolucao'] is None:
            print(f"ISBN: {emprestimo['isbn']}, Usuário: {emprestimo['usuario_id']}, Data: {emprestimo['data_emprestimo']}")

def adicionar_usuario(nome, email, telefone):

    id_usuario = len(usuarios) + 1
    usuario = {
        'id': id_usuario,
        'nome': nome,
        'email': email,
        'telefone': telefone
    }
    usuarios.append(usuario)
    print(f"Usuário {nome} adicionado com ID {id_usuario}")


def main():

    adicionar_usuario("João Silva", "joao@email.com", "123456789")
    adicionar_usuario("Maria Santos", "maria@email.com", "987654321")
    
    adicionar_livro("Python para Iniciantes", "João Autor", "978-1234567890", 2020)
    adicionar_livro("Algoritmos Avançados", "Maria Autora", "978-0987654321", 2021)
    
    emprestar_livro("978-1234567890", 1)
    listar_emprestimos()
    devolver_livro("978-1234567890", 1)

if __name__ == "__main__":
    main()