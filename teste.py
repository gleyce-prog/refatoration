# Testes Unitários para o Sistema de Gerenciamento de Biblioteca
# Utilizando pytest como framework de teste

import pytest
from datetime import datetime
from refactored_library_code import (
    Livro, Usuario, Emprestimo, RepositorioLivros, 
    RepositorioUsuarios, RepositorioEmprestimos, 
    ServicoEmprestimo, GerenciadorBiblioteca
)


class TestLivro:
    """Testes para a classe Livro."""
    
    def test_criar_livro_valido(self):
        """Testa criação de livro com dados válidos."""
        livro = Livro("Clean Code", "Robert Martin", "978-1234567890", 2008)
        assert livro.titulo == "Clean Code"
        assert livro.autor == "Robert Martin"
        assert livro.isbn == "978-1234567890"
        assert livro.ano_publicacao == 2008
        assert livro.disponivel is True
    
    def test_titulo_vazio_deve_gerar_erro(self):
        """Testa se título vazio gera erro."""
        with pytest.raises(ValueError, match="Título não pode estar vazio"):
            Livro("", "Autor", "978-1234567890", 2020)
    
    def test_autor_vazio_deve_gerar_erro(self):
        """Testa se autor vazio gera erro."""
        with pytest.raises(ValueError, match="Autor não pode estar vazio"):
            Livro("Título", "", "978-1234567890", 2020)
    
    def test_isbn_invalido_deve_gerar_erro(self):
        """Testa se ISBN inválido gera erro."""
        with pytest.raises(ValueError, match="ISBN inválido"):
            Livro("Título", "Autor", "123456789", 2020)
    
    def test_ano_invalido_deve_gerar_erro(self):
        """Testa se ano inválido gera erro."""
        with pytest.raises(ValueError, match="Ano de publicação inválido"):
            Livro("Título", "Autor", "978-1234567890", 999)


class TestUsuario:
    """Testes para a classe Usuario."""
    
    def test_criar_usuario_valido(self):
        """Testa criação de usuário com dados válidos."""
        usuario = Usuario(1, "João Silva", "joao@email.com", "11999887766")
        assert usuario.id == 1
        assert usuario.nome == "João Silva"
        assert usuario.email == "joao@email.com"
        assert usuario.telefone == "11999887766"
    
    def test_nome_vazio_deve_gerar_erro(self):
        """Testa se nome vazio gera erro."""
        with pytest.raises(ValueError, match="Nome não pode estar vazio"):
            Usuario(1, "", "email@test.com", "123456789")
    
    def test_email_invalido_deve_gerar_erro(self):
        """Testa se email inválido gera erro."""
        with pytest.raises(ValueError, match="Email inválido"):
            Usuario(1, "Nome", "email_invalido", "123456789")
    
    def test_telefone_vazio_deve_gerar_erro(self):
        """Testa se telefone vazio gera erro."""
        with pytest.raises(ValueError, match="Telefone não pode estar vazio"):
            Usuario(1, "Nome", "email@test.com", "")


class TestEmprestimo:
    """Testes para a classe Emprestimo."""
    
    def test_criar_emprestimo(self):
        """Testa criação de empréstimo."""
        data_emp = datetime.now()
        emprestimo = Emprestimo("978-1234567890", 1, data_emp)
        assert emprestimo.isbn == "978-1234567890"
        assert emprestimo.usuario_id == 1
        assert emprestimo.data_emprestimo == data_emp
        assert emprestimo.data_devolucao is None
        assert emprestimo.is_ativo is True
    
    def test_devolver_emprestimo(self):
        """Testa devolução de empréstimo."""
        emprestimo = Emprestimo("978-1234567890", 1, datetime.now())
        emprestimo.devolver()
        assert emprestimo.data_devolucao is not None
        assert emprestimo.is_ativo is False


class TestRepositorioLivros:
    """Testes para o RepositorioLivros."""
    
    def test_adicionar_livro(self):
        """Testa adição de livro ao repositório."""
        repo = RepositorioLivros()
        livro = Livro("Teste", "Autor", "978-1234567890", 2020)
        repo.adicionar(livro)
        
        livro_encontrado = repo.buscar_por_id("978-1234567890")
        assert livro_encontrado == livro
    
    def test_adicionar_livro_duplicado_deve_gerar_erro(self):
        """Testa se adicionar livro duplicado gera erro."""
        repo = RepositorioLivros()
        livro1 = Livro("Teste1", "Autor1", "978-1234567890", 2020)
        livro2 = Livro("Teste2", "Autor2", "978-1234567890", 2021)
        
        repo.adicionar(livro1)
        with pytest.raises(ValueError, match="já existe"):
            repo.adicionar(livro2)
    
    def test_buscar_por_termo(self):
        """Testa busca por termo."""
        repo = RepositorioLivros()
        livro1 = Livro("Python Avançado", "João", "978-1234567890", 2020)
        livro2 = Livro("Java Básico", "Maria", "978-0987654321", 2021)
        livro3 = Livro("Algoritmos", "Pedro Python", "978-1122334455", 2019)
        
        repo.adicionar(livro1)
        repo.adicionar(livro2)
        repo.adicionar(livro3)
        
        resultados = repo.buscar_por_termo("Python")
        assert len(resultados) == 2
        assert livro1 in resultados
        assert livro3 in resultados
    
    def test_listar_disponiveis(self):
        """Testa listagem de livros disponíveis."""
        repo = RepositorioLivros()
        livro1 = Livro("Disponível", "Autor", "978-1234567890", 2020)
        livro2 = Livro("Indisponível", "Autor", "978-0987654321", 2021)
        livro2.disponivel = False
        
        repo.adicionar(livro1)
        repo.adicionar(livro2)
        
        disponiveis = repo.listar_disponiveis()
        assert len(disponiveis) == 1
        assert livro1 in disponiveis
        assert livro2 not in disponiveis


class TestRepositorioUsuarios:
    """Testes para o RepositorioUsuarios."""
    
    def test_criar_usuario_com_id_automatico(self):
        """Testa criação de usuário com ID automático."""
        repo = RepositorioUsuarios()
        usuario = repo.criar_usuario("João", "joao@email.com", "123456789")
        
        assert usuario.id == 1
        assert repo.buscar_por_id(1) == usuario
    
    def test_multiplos_usuarios_ids_sequenciais(self):
        """Testa se múltiplos usuários recebem IDs sequenciais."""
        repo = RepositorioUsuarios()
        usuario1 = repo.criar_usuario("João", "joao@email.com", "123456789")
        usuario2 = repo.criar_usuario("Maria", "maria@email.com", "987654321")
        
        assert usuario1.id == 1
        assert usuario2.id == 2


class TestServicoEmprestimo:
    """Testes para o ServicoEmprestimo."""
    
    def setup_method(self):
        """Configura dados para cada teste."""
        self.repo_livros = RepositorioLivros()
        self.repo_usuarios = RepositorioUsuarios()
        self.repo_emprestimos = RepositorioEmprestimos()
        self.servico = ServicoEmprestimo(
            self.repo_livros, self.repo_usuarios, self.repo_emprestimos
        )
        
        # Dados de teste
        self.livro = Livro("Teste", "Autor", "978-1234567890", 2020)
        self.usuario = Usuario(1, "João", "joao@email.com", "123456789")
        
        self.repo_livros.adicionar(self.livro)
        self.repo_usuarios.adicionar(self.usuario)
    
    def test_emprestar_livro_com_sucesso(self):
        """Testa empréstimo bem-sucedido."""
        resultado = self.servico.emprestar_livro("978-1234567890", 1)
        
        assert resultado is True
        assert self.livro.disponivel is False
        
        emprestimos_ativos = self.repo_emprestimos.listar_ativos()
        assert len(emprestimos_ativos) == 1
        assert emprestimos_ativos[0].isbn == "978-1234567890"
        assert emprestimos_ativos[0].usuario_id == 1
    
    def test_emprestar_livro_inexistente_deve_gerar_erro(self):
        """Testa empréstimo de livro inexistente."""
        with pytest.raises(ValueError, match="Livro não encontrado"):
            self.servico.emprestar_livro("978-9999999999", 1)
    
    def test_emprestar_livro_indisponivel_deve_gerar_erro(self):
        """Testa empréstimo de livro indisponível."""
        self.livro.disponivel = False
        with pytest.raises(ValueError, match="Livro não está disponível"):
            self.servico.emprestar_livro("978-1234567890", 1)
    
    def test_emprestar_para_usuario_inexistente_deve_gerar_erro(self):
        """Testa empréstimo para usuário inexistente."""
        with pytest.raises(ValueError, match="Usuário não encontrado"):
            self.servico.emprestar_livro("978-1234567890", 999)
    
    def test_devolver_livro_com_sucesso(self):
        """Testa devolução bem-sucedida."""
        # Primeiro empresta
        self.servico.emprestar_livro("978-1234567890", 1)
        
        # Depois devolve
        resultado = self.servico.devolver_livro("978-1234567890", 1)
        
        assert resultado is True
        assert self.livro.disponivel is True
        
        emprestimos_ativos = self.repo_emprestimos.listar_ativos()
        assert len(emprestimos_ativos) == 0
    
    def test_devolver_emprestimo_inexistente_deve_gerar_erro(self):
        """Testa devolução de empréstimo inexistente."""
        with pytest.raises(ValueError, match="Empréstimo ativo não encontrado"):
            self.servico.devolver_livro("978-1234567890", 1)


class TestGerenciadorBiblioteca:
    """Testes de integração para o GerenciadorBiblioteca."""
    
    def setup_method(self):
        """Configura gerenciador para cada teste."""
        self.gerenciador = GerenciadorBiblioteca()
    
    def test_fluxo_completo_emprestimo_devolucao(self, capsys):
        """Testa fluxo completo de empréstimo e devolução."""
        # Adiciona usuário e livro
        self.gerenciador.adicionar_usuario("João", "joao@email.com", "123456789")
        self.gerenciador.adicionar_livro("Clean Code", "Martin", "978-1234567890", 2008)
        
        # Empresta livro
        self.gerenciador.emprestar_livro("978-1234567890", 1)
        
        # Verifica output
        captured = capsys.readouterr()
        assert "✅ Usuário 'João' adicionado com ID 1" in captured.out
        assert "✅ Livro 'Clean Code' adicionado com sucesso!" in captured.out
        assert "✅ Livro 'Clean Code' emprestado para João" in captured.out
    
    def test_adicionar_livro_com_dados_invalidos(self, capsys):
        """Testa adição de livro com dados inválidos."""
        self.gerenciador.adicionar_livro("", "Autor", "978-1234567890", 2020)
        
        captured = capsys.readouterr()
        assert "❌ Erro ao adicionar livro: Título não pode estar vazio" in captured.out
    
    def test_buscar_livros_existentes(self, capsys):
        """Testa busca de livros existentes."""
        self.gerenciador.adicionar_livro("Python Avançado", "João", "978-1234567890", 2020)
        self.gerenciador.adicionar_livro("Java Básico", "Maria", "978-0987654321", 2021)
        
        self.gerenciador.buscar_livros("Python")
        
        captured = capsys.readouterr()
        assert "📚 Livros encontrados para 'Python':" in captured.out
        assert "Python Avançado - João (2020) - ✅ Disponível" in captured.out
    
    def test_buscar_livros_inexistentes(self, capsys):
        """Testa busca de livros inexistentes."""
        self.gerenciador.buscar_livros("Inexistente")
        
        captured = capsys.readouterr()
        assert "❌ Nenhum livro encontrado para 'Inexistente'" in captured.out


# Fixture para executar todos os testes
@pytest.fixture
def biblioteca_completa():
    """Fixture que retorna uma biblioteca com dados de teste."""
    gerenciador = GerenciadorBiblioteca()
    
    # Adiciona usuários
    gerenciador.adicionar_usuario("João Silva", "joao@email.com", "11999887766")
    gerenciador.adicionar_usuario("Maria Santos", "maria@email.com", "11888776655")
    
    # Adiciona livros
    gerenciador.adicionar_livro("Clean Code", "Robert Martin", "978-1234567890", 2008)
    gerenciador.adicionar_livro("Python Fluente", "Luciano Ramalho", "978-0987654321", 2015)
    
    return gerenciador


class TestIntegracao:
    """Testes de integração usando a fixture."""
    
    def test_cenario_biblioteca_completa(self, biblioteca_completa, capsys):
        """Testa cenário completo de uso da biblioteca."""
        # Empresta livros
        biblioteca_completa.emprestar_livro("978-1234567890", 1)
        biblioteca_completa.emprestar_livro("978-0987654321", 2)
        
        # Lista empréstimos ativos
        biblioteca_completa.listar_emprestimos_ativos()
        
        # Devolve um livro
        biblioteca_completa.devolver_livro("978-1234567890", 1)
        
        # Verifica estado final
        biblioteca_completa.listar_livros_disponiveis()
        
        captured = capsys.readouterr()
        
        # Verifica se as operações foram executadas corretamente
        assert "✅ Livro 'Clean Code' emprestado para João Silva" in captured.out
        assert "✅ Livro 'Python Fluente' emprestado para Maria Santos" in captured.out
        assert "📋 Empréstimos Ativos:" in captured.out
        assert "✅ Livro 'Clean Code' devolvido com sucesso!" in captured.out
        assert "📚 Livros Disponíveis:" in captured.out


# Função para executar todos os testes
def executar_testes():
    """Executa todos os testes e exibe relatório."""
    print("=== EXECUTANDO TESTES UNITÁRIOS ===\n")
 

if __name__ == "__main__":
    executar_testes()