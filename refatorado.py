# Código Refatorado - Sistema de Gerenciamento de Biblioteca
# Aplicando princípios de Clean Code e boas práticas de desenvolvimento

from datetime import datetime
from typing import List, Optional, Dict
from dataclasses import dataclass
from abc import ABC, abstractmethod
import re


@dataclass
class Livro:
    """Classe que representa um livro na biblioteca."""
    titulo: str
    autor: str
    isbn: str
    ano_publicacao: int
    disponivel: bool = True
    
    def __post_init__(self):
        """Valida os dados do livro após inicialização."""
        if not self.titulo.strip():
            raise ValueError("Título não pode estar vazio")
        if not self.autor.strip():
            raise ValueError("Autor não pode estar vazio")
        if not self._validar_isbn(self.isbn):
            raise ValueError("ISBN inválido")
        if self.ano_publicacao < 1000 or self.ano_publicacao > datetime.now().year:
            raise ValueError("Ano de publicação inválido")
    
    @staticmethod
    def _validar_isbn(isbn: str) -> bool:
        """Valida o formato do ISBN."""
        pattern = r'^978-\d{10}$'
        return bool(re.match(pattern, isbn))


@dataclass
class Usuario:
    """Classe que representa um usuário da biblioteca."""
    id: int
    nome: str
    email: str
    telefone: str
    
    def __post_init__(self):
        """Valida os dados do usuário após inicialização."""
        if not self.nome.strip():
            raise ValueError("Nome não pode estar vazio")
        if not self._validar_email(self.email):
            raise ValueError("Email inválido")
        if not self.telefone.strip():
            raise ValueError("Telefone não pode estar vazio")
    
    @staticmethod
    def _validar_email(email: str) -> bool:
        """Valida o formato do email."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))


@dataclass
class Emprestimo:
    """Classe que representa um empréstimo de livro."""
    isbn: str
    usuario_id: int
    data_emprestimo: datetime
    data_devolucao: Optional[datetime] = None
    
    @property
    def is_ativo(self) -> bool:
        """Verifica se o empréstimo está ativo."""
        return self.data_devolucao is None
    
    def devolver(self) -> None:
        """Marca o empréstimo como devolvido."""
        self.data_devolucao = datetime.now()


class IRepositorio(ABC):
    """Interface para repositórios de dados."""
    
    @abstractmethod
    def adicionar(self, item) -> None:
        pass
    
    @abstractmethod
    def buscar_por_id(self, id) -> Optional[object]:
        pass
    
    @abstractmethod
    def listar_todos(self) -> List[object]:
        pass


class RepositorioLivros(IRepositorio):
    """Repositório para gerenciar livros."""
    
    def __init__(self):
        self._livros: Dict[str, Livro] = {}
    
    def adicionar(self, livro: Livro) -> None:
        """Adiciona um livro ao repositório."""
        if livro.isbn in self._livros:
            raise ValueError(f"Livro com ISBN {livro.isbn} já existe")
        self._livros[livro.isbn] = livro
    
    def buscar_por_id(self, isbn: str) -> Optional[Livro]:
        """Busca livro por ISBN."""
        return self._livros.get(isbn)
    
    def buscar_por_termo(self, termo: str) -> List[Livro]:
        """Busca livros por título ou autor."""
        termo_lower = termo.lower()
        return [
            livro for livro in self._livros.values()
            if termo_lower in livro.titulo.lower() or termo_lower in livro.autor.lower()
        ]
    
    def listar_todos(self) -> List[Livro]:
        """Lista todos os livros."""
        return list(self._livros.values())
    
    def listar_disponiveis(self) -> List[Livro]:
        """Lista apenas livros disponíveis."""
        return [livro for livro in self._livros.values() if livro.disponivel]


class RepositorioUsuarios(IRepositorio):
    """Repositório para gerenciar usuários."""
    
    def __init__(self):
        self._usuarios: Dict[int, Usuario] = {}
        self._proximo_id = 1
    
    def adicionar(self, usuario: Usuario) -> None:
        """Adiciona um usuário ao repositório."""
        if usuario.id in self._usuarios:
            raise ValueError(f"Usuário com ID {usuario.id} já existe")
        self._usuarios[usuario.id] = usuario
        self._proximo_id = max(self._proximo_id, usuario.id + 1)
    
    def criar_usuario(self, nome: str, email: str, telefone: str) -> Usuario:
        """Cria um novo usuário com ID automático."""
        usuario = Usuario(self._proximo_id, nome, email, telefone)
        self.adicionar(usuario)
        return usuario
    
    def buscar_por_id(self, id: int) -> Optional[Usuario]:
        """Busca usuário por ID."""
        return self._usuarios.get(id)
    
    def listar_todos(self) -> List[Usuario]:
        """Lista todos os usuários."""
        return list(self._usuarios.values())


class RepositorioEmprestimos(IRepositorio):
    """Repositório para gerenciar empréstimos."""
    
    def __init__(self):
        self._emprestimos: List[Emprestimo] = []
    
    def adicionar(self, emprestimo: Emprestimo) -> None:
        """Adiciona um empréstimo ao repositório."""
        self._emprestimos.append(emprestimo)
    
    def buscar_por_id(self, id) -> Optional[Emprestimo]:
        """Não implementado para empréstimos."""
        pass
    
    def buscar_ativo_por_isbn_usuario(self, isbn: str, usuario_id: int) -> Optional[Emprestimo]:
        """Busca empréstimo ativo específico."""
        for emprestimo in self._emprestimos:
            if (emprestimo.isbn == isbn and 
                emprestimo.usuario_id == usuario_id and 
                emprestimo.is_ativo):
                return emprestimo
        return None
    
    def listar_todos(self) -> List[Emprestimo]:
        """Lista todos os empréstimos."""
        return self._emprestimos
    
    def listar_ativos(self) -> List[Emprestimo]:
        """Lista apenas empréstimos ativos."""
        return [emp for emp in self._emprestimos if emp.is_ativo]


class ServicoEmprestimo:
    """Serviço para gerenciar operações de empréstimo."""
    
    def __init__(self, repo_livros: RepositorioLivros, 
                 repo_usuarios: RepositorioUsuarios,
                 repo_emprestimos: RepositorioEmprestimos):
        self._repo_livros = repo_livros
        self._repo_usuarios = repo_usuarios
        self._repo_emprestimos = repo_emprestimos
    
    def emprestar_livro(self, isbn: str, usuario_id: int) -> bool:
        """Realiza empréstimo de um livro."""
        livro = self._repo_livros.buscar_por_id(isbn)
        if not livro:
            raise ValueError("Livro não encontrado")
        
        if not livro.disponivel:
            raise ValueError("Livro não está disponível")
        
        usuario = self._repo_usuarios.buscar_por_id(usuario_id)
        if not usuario:
            raise ValueError("Usuário não encontrado")
        
        # Realiza o empréstimo
        livro.disponivel = False
        emprestimo = Emprestimo(isbn, usuario_id, datetime.now())
        self._repo_emprestimos.adicionar(emprestimo)
        
        return True
    
    def devolver_livro(self, isbn: str, usuario_id: int) -> bool:
        """Realiza devolução de um livro."""
        emprestimo = self._repo_emprestimos.buscar_ativo_por_isbn_usuario(isbn, usuario_id)
        if not emprestimo:
            raise ValueError("Empréstimo ativo não encontrado")
        
        livro = self._repo_livros.buscar_por_id(isbn)
        if not livro:
            raise ValueError("Livro não encontrado")
        
        # Realiza a devolução
        emprestimo.devolver()
        livro.disponivel = True
        
        return True


class GerenciadorBiblioteca:
    """Classe principal para gerenciar a biblioteca."""
    
    def __init__(self):
        self._repo_livros = RepositorioLivros()
        self._repo_usuarios = RepositorioUsuarios()
        self._repo_emprestimos = RepositorioEmprestimos()
        self._servico_emprestimo = ServicoEmprestimo(
            self._repo_livros, self._repo_usuarios, self._repo_emprestimos
        )
    
    def adicionar_livro(self, titulo: str, autor: str, isbn: str, ano: int) -> None:
        """Adiciona um novo livro à biblioteca."""
        try:
            livro = Livro(titulo, autor, isbn, ano)
            self._repo_livros.adicionar(livro)
            print(f"✅ Livro '{titulo}' adicionado com sucesso!")
        except ValueError as e:
            print(f"❌ Erro ao adicionar livro: {e}")
    
    def adicionar_usuario(self, nome: str, email: str, telefone: str) -> None:
        """Adiciona um novo usuário à biblioteca."""
        try:
            usuario = self._repo_usuarios.criar_usuario(nome, email, telefone)
            print(f"✅ Usuário '{nome}' adicionado com ID {usuario.id}")
        except ValueError as e:
            print(f"❌ Erro ao adicionar usuário: {e}")
    
    def buscar_livros(self, termo: str) -> None:
        """Busca e exibe livros por termo."""
        livros = self._repo_livros.buscar_por_termo(termo)
        if livros:
            print(f"\n📚 Livros encontrados para '{termo}':")
            for livro in livros:
                status = "✅ Disponível" if livro.disponivel else "❌ Emprestado"
                print(f"  • {livro.titulo} - {livro.autor} ({livro.ano_publicacao}) - {status}")
        else:
            print(f"❌ Nenhum livro encontrado para '{termo}'")
    
    def emprestar_livro(self, isbn: str, usuario_id: int) -> None:
        """Empresta um livro para um usuário."""
        try:
            self._servico_emprestimo.emprestar_livro(isbn, usuario_id)
            livro = self._repo_livros.buscar_por_id(isbn)
            usuario = self._repo_usuarios.buscar_por_id(usuario_id)
            print(f"✅ Livro '{livro.titulo}' emprestado para {usuario.nome}")
        except ValueError as e:
            print(f"❌ Erro no empréstimo: {e}")
    
    def devolver_livro(self, isbn: str, usuario_id: int) -> None:
        """Devolve um livro emprestado."""
        try:
            self._servico_emprestimo.devolver_livro(isbn, usuario_id)
            livro = self._repo_livros.buscar_por_id(isbn)
            print(f"✅ Livro '{livro.titulo}' devolvido com sucesso!")
        except ValueError as e:
            print(f"❌ Erro na devolução: {e}")
    
    def listar_emprestimos_ativos(self) -> None:
        """Lista todos os empréstimos ativos."""
        emprestimos = self._repo_emprestimos.listar_ativos()
        if emprestimos:
            print("\n📋 Empréstimos Ativos:")
            for emp in emprestimos:
                livro = self._repo_livros.buscar_por_id(emp.isbn)
                usuario = self._repo_usuarios.buscar_por_id(emp.usuario_id)
                data_emp = emp.data_emprestimo.strftime("%d/%m/%Y")
                print(f"  • {livro.titulo} - {usuario.nome} (desde {data_emp})")
        else:
            print("✅ Nenhum empréstimo ativo")
    
    def listar_livros_disponiveis(self) -> None:
        """Lista todos os livros disponíveis."""
        livros = self._repo_livros.listar_disponiveis()
        if livros:
            print("\n📚 Livros Disponíveis:")
            for livro in livros:
                print(f"  • {livro.titulo} - {livro.autor} ({livro.ano_publicacao})")
        else:
            print("❌ Nenhum livro disponível")


def demonstrar_sistema():
    """Função para demonstrar o funcionamento do sistema refatorado."""
    print("=== SISTEMA DE GERENCIAMENTO DE BIBLIOTECA ===\n")
    
    # Criando instância do gerenciador
    biblioteca = GerenciadorBiblioteca()
    
    # Adicionando usuários
    print("1. Adicionando usuários:")
    biblioteca.adicionar_usuario("João Silva", "joao@email.com", "11999887766")
    biblioteca.adicionar_usuario("Maria Santos", "maria@email.com", "11888776655")
    biblioteca.adicionar_usuario("Pedro Costa", "pedro@email.com", "11777665544")
    
    print("\n" + "="*50)
    
    # Adicionando livros
    print("\n2. Adicionando livros:")
    biblioteca.adicionar_livro("Clean Code", "Robert Martin", "978-1234567890", 2008)
    biblioteca.adicionar_livro("Python Fluente", "Luciano Ramalho", "978-0987654321", 2015)
    biblioteca.adicionar_livro("Algoritmos", "Thomas Cormen", "978-1122334455", 2009)
    
    print("\n" + "="*50)
    
    # Listando livros disponíveis
    print("\n3. Livros disponíveis:")
    biblioteca.listar_livros_disponiveis()
    
    print("\n" + "="*50)
    
    # Realizando empréstimos
    print("\n4. Realizando empréstimos:")
    biblioteca.emprestar_livro("978-1234567890", 1)
    biblioteca.emprestar_livro("978-0987654321", 2)
    
    print("\n" + "="*50)
    
    # Listando empréstimos ativos
    print("\n5. Empréstimos ativos:")
    biblioteca.listar_emprestimos_ativos()
    
    print("\n" + "="*50)
    
    # Buscando livros
    print("\n6. Buscando livros:")
    biblioteca.buscar_livros("Python")
    biblioteca.buscar_livros("Clean")
    
    print("\n" + "="*50)
    
    # Devolvendo um livro
    print("\n7. Devolvendo livro:")
    biblioteca.devolver_livro("978-1234567890", 1)
    
    print("\n" + "="*50)
    
    # Estado final
    print("\n8. Estado final:")
    biblioteca.listar_livros_disponiveis()
    biblioteca.listar_emprestimos_ativos()


if __name__ == "__main__":
    demonstrar_sistema()