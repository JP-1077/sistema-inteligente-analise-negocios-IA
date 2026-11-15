"""
=======================================================================
                MÓDULO DE ENTIDADES BANCO DE DADOS
=======================================================================

Descrição:
Este módulo tem como premissa armazenar informações para criação das tabelas/entidades do banco de dados do sistema


Responsabilidades:
Disponibilizar toda a modelagem e estrutura das tabelas do banco de dados do sistema

"""

#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-*/
                                                            # 1. IMPORTAÇÕES DAS BIBLIOTECAS
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-*/
from typing import Any, Optional
from datetime import datetime
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    func,

)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.db import Base


#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-*/
                                                                    # 2. TABELAS
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-*/


#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
                 # 2.1 TABELA USUARIOS
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
class TabelaUsuarios(Base):

    __tablename__ = "tb_usuarios"
    __table_args__ = (
        CheckConstraint(
            "nivel_acesso IN ('admin', 'usuario')",
            name="ck_tb_usuarios_nivel_acesso",
        ),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    login: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)

    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    nivel_acesso: Mapped[str] = mapped_column(String(20), nullable=False, default="usuario")

    criado_em: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    bases_dados: Mapped[list["TabelaArmazenamentoBaseDados"]] = relationship(back_populates="usuario")

#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
                 # 2.2 TABELA INFOS ARQUIVOS
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
class TabelaArmazenamentoBaseDados(Base):

    __tablename__ = "tb_armazenamento_base_dados"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    usuario_id: Mapped[int] = mapped_column(ForeignKey("tb_usuarios.id"), nullable=False, index=True)

    nome_arquivo: Mapped[str] = mapped_column(String(255), nullable=False)

    formato: Mapped[str] = mapped_column(String(20), nullable=False)

    tamanho_bytes: Mapped[Optional[int]] = mapped_column(Integer)

    quantidade_linhas: Mapped[Optional[int]] = mapped_column(Integer)

    quantidade_colunas: Mapped[Optional[int]] = mapped_column(Integer)

    enviado_em: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    usuario: Mapped["TabelaUsuarios"] = relationship(back_populates="bases_dados")

#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
                 # 2.3 TABELA METRICAS BASES DADOS
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
class TabelaMetricasAnalises(Base):
    __tablename__ = "tb_metricas_analises"

    id_resultado: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    id_base: Mapped[int] = mapped_column(
        ForeignKey("tb_armazenamento_base_dados.id"),
        nullable=False,
        index=True,
    )

    nome_metrica: Mapped[str] = mapped_column(String(150), nullable=False)

    tipo_metrica: Mapped[str] = mapped_column(String(50), nullable=False)

    valor: Mapped[float] = mapped_column(Float, nullable=False)

    unidade: Mapped[Optional[str]] = mapped_column(String(50))

    dimensao: Mapped[Optional[str]] = mapped_column(String(150))

    periodo_inicio: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    periodo_fim: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    metodo_calculo: Mapped[Optional[str]] = mapped_column(Text)

    metadata_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON)

    data_calculo: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
                 # 2.4 TABELA API GEMINI
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
class TabelaRequisicoesApiGemini(Base):
    __tablename__ = "tb_requisicoes_api_gemini"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    modelo: Mapped[str] = mapped_column(String(100), nullable=False)

    status: Mapped[str] = mapped_column(String(30), nullable=False)

    solicitada_em: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    finalizada_em: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True))

    duracao_ms: Mapped[Optional[int]] = mapped_column(Integer)

    tokens_entrada: Mapped[Optional[int]] = mapped_column(Integer)

    tokens_saida: Mapped[Optional[int]] = mapped_column(Integer)

    resposta_texto: Mapped[Optional[str]] = mapped_column(Text)

    mensagem_erro: Mapped[Optional[str]] = mapped_column(Text)
