from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.deps import get_current_staff, get_current_user, get_optional_current_user
from app.db.session import get_db
from app.models.estoque import Estoque
from app.models.pedido import ItemPedido, Pedido, StatusPedido, CanalPedido
from app.models.pratos import Prato
from app.models.unidade import Unidade
from app.models.usuario import Usuario
from app.schemas.pedido import PedidoCreate, PedidoResponse
from app.schemas.pedido import PagamentoMockRequest, PagamentoResponse
from app.schemas.pedido import HistoricoStatusResponse
from app.models.pagamento import Pagamento, ResultadoPagamento
from typing import Optional
from fastapi import Query
from app.models.historico_status_pedido import HistoricoStatusPedido
from app.schemas.pedido import AtualizarStatusPedido
from app.models.pontos_fidelidade import PontosFidelidade


router = APIRouter(prefix="/pedidos", tags=["Pedidos"])


@router.post(
    "/",
    response_model=PedidoResponse,
    status_code=status.HTTP_201_CREATED,
)
def criar_pedido(
    dados: PedidoCreate,
    db: Session = Depends(get_db),
    usuario: Usuario | None = Depends(get_optional_current_user),
):
    unidade = db.query(Unidade).filter(
        Unidade.id == dados.unidade_id
    ).first()
    if unidade is None:
        raise HTTPException(status_code=404, detail="Unidade não encontrada")

    prato_ids = [item.prato_id for item in dados.itens]
    if len(prato_ids) != len(set(prato_ids)):
        raise HTTPException(
            status_code=422,
            detail="Informe cada prato uma única vez no pedido",
        )

    usuario_pedido_id = None
    if usuario is None:
        if dados.usuario_id is not None:
            raise HTTPException(
                status_code=401,
                detail="Faça login para associar um cliente ao pedido",
            )
    elif usuario.perfil == "CLIENTE":
        if dados.usuario_id not in (None, usuario.id):
            raise HTTPException(status_code=403, detail="Acesso negado")
        usuario_pedido_id = usuario.id
    elif usuario.perfil in ("ATENDENTE", "GERENTE"):
        usuario_pedido_id = dados.usuario_id
        if usuario_pedido_id is not None:
            cliente = db.query(Usuario).filter(
                Usuario.id == usuario_pedido_id,
                Usuario.ativo.is_(True),
                Usuario.perfil == "CLIENTE",
            ).first()
            if cliente is None:
                raise HTTPException(
                    status_code=404,
                    detail="Cliente não encontrado ou inativo",
                )
    else:
        raise HTTPException(status_code=403, detail="Perfil sem permissão")

    itens_pedido = []
    total = Decimal("0.00")

    for item in dados.itens:
        prato = db.query(Prato).filter(Prato.id == item.prato_id).first()
        if prato is None:
            raise HTTPException(status_code=404, detail="Prato não encontrado")
        if not prato.disponivel:
            raise HTTPException(status_code=409, detail="Prato indisponível")

        estoque = db.query(Estoque).filter(
            Estoque.id_unidade == dados.unidade_id,
            Estoque.id_prato == item.prato_id,
        ).first()
        if estoque is None or estoque.quantidade < item.quantidade:
            raise HTTPException(status_code=409, detail="Estoque insuficiente")

        preco = Decimal(str(prato.preco)).quantize(Decimal("0.01"))
        total += preco * item.quantidade
        itens_pedido.append(
            ItemPedido(
                prato_id=prato.id,
                quantidade=item.quantidade,
                preco_unitario=preco,
            )
        )

    pedido = Pedido(
        unidade_id=dados.unidade_id,
        usuario_id=usuario_pedido_id,
        canal_pedido=dados.canal_pedido,
        total=total,
        itens=itens_pedido,
        status=StatusPedido.AGUARDANDO_PAGAMENTO,
    )

    db.add(pedido)
    db.flush()
    db.add(
        HistoricoStatusPedido(
            pedido_id=pedido.id,
            status=pedido.status,
            alterado_por_id=usuario.id if usuario else None,
        )
    )
    db.commit()
    db.refresh(pedido)
    return pedido

@router.post(
    "/{pedido_id}/pagamento",
    response_model=PagamentoResponse,
)
def simular_pagamento(
    pedido_id: int,
    dados: PagamentoMockRequest,
    db: Session = Depends(get_db),
    usuario_atendente: Usuario = Depends(get_current_staff),
):
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()

    if pedido is None:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    pagamento_existente = db.query(Pagamento).filter(
        Pagamento.pedido_id == pedido_id
    ).first()

    if pagamento_existente is not None:
        if pagamento_existente.resultado != dados.resultado:
            raise HTTPException(
                status_code=409,
                detail="Este pedido já possui um resultado de pagamento diferente",
            )
        pontos_creditados = db.query(PontosFidelidade.pontos).filter(
            PontosFidelidade.pedido_id == pedido_id
        ).scalar() or 0
        return {
            "id": pagamento_existente.id,
            "pedido_id": pagamento_existente.pedido_id,
            "resultado": pagamento_existente.resultado,
            "valor": pagamento_existente.valor,
            "pedido_status": pedido.status,
            "criado_em": pagamento_existente.criado_em,
            "pontos_creditados": pontos_creditados,
        }

    if pedido.status != StatusPedido.AGUARDANDO_PAGAMENTO:
        raise HTTPException(
            status_code=409,
            detail="O pedido não está aguardando pagamento",
        )

    pontos = 0
    if dados.resultado == ResultadoPagamento.APROVADO:
        for item in pedido.itens:
            estoque = db.query(Estoque).filter(
                Estoque.id_unidade == pedido.unidade_id,
                Estoque.id_prato == item.prato_id,
            ).first()

            if estoque is None or estoque.quantidade < item.quantidade:
                raise HTTPException(
                    status_code=409,
                    detail="Estoque insuficiente para concluir o pagamento",
                )

            estoque.quantidade -= item.quantidade

        pedido.status = StatusPedido.PAGO
        cliente = db.query(Usuario).filter(Usuario.id == pedido.usuario_id).first()
        if cliente is not None and cliente.consentimento_fidelidade:
            pontos = int(pedido.total)
            if pontos > 0:
                db.add(
                    PontosFidelidade(
                        usuario_id=cliente.id,
                        pedido_id=pedido.id,
                        pontos=pontos,
                    )
                )
    else:
        pedido.status = StatusPedido.PAGAMENTO_RECUSADO

    pontos_creditados = (
        pontos if dados.resultado == ResultadoPagamento.APROVADO else 0
    )

    pagamento = Pagamento(
        pedido_id=pedido.id,
        resultado=dados.resultado,
        valor=pedido.total,
    )
    db.add(pagamento)
    db.add(
        HistoricoStatusPedido(
            pedido_id=pedido.id,
            status=pedido.status,
            alterado_por_id=usuario_atendente.id,
        )
    )
    db.commit()
    db.refresh(pagamento)

    return {
        "id": pagamento.id,
        "pedido_id": pagamento.pedido_id,
        "resultado": pagamento.resultado,
        "valor": pagamento.valor,
        "pedido_status": pedido.status,
        "criado_em": pagamento.criado_em,
        "pontos_creditados": pontos_creditados,
    }

@router.patch("/{pedido_id}/status", response_model=PedidoResponse)
def atualizar_status_pedido(
    pedido_id: int,
    dados: AtualizarStatusPedido,
    db: Session = Depends(get_db),
    atendente: Usuario = Depends(get_current_staff),
):
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if pedido is None:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    transicoes_permitidas = {
        StatusPedido.AGUARDANDO_PAGAMENTO: {StatusPedido.CANCELADO},
        StatusPedido.PAGAMENTO_RECUSADO: {StatusPedido.CANCELADO},
        StatusPedido.PAGO: {StatusPedido.EM_PREPARO},
        StatusPedido.EM_PREPARO: {StatusPedido.PRONTO},
        StatusPedido.PRONTO: {StatusPedido.ENTREGUE},
    }

    if dados.status not in transicoes_permitidas.get(pedido.status, set()):
        raise HTTPException(
            status_code=409,
            detail=f"Não é permitido mudar de {pedido.status.value} para {dados.status.value}",
        )

    pedido.status = dados.status
    db.add(
        HistoricoStatusPedido(
            pedido_id=pedido.id,
            status=pedido.status,
            alterado_por_id=atendente.id,
        )
    )
    db.commit()
    db.refresh(pedido)
    return pedido

@router.get("/", response_model=list[PedidoResponse])
def listar_pedidos(
    canal_pedido: Optional[CanalPedido] = Query(default=None),
    status_pedido: Optional[StatusPedido] = Query(default=None),
    limite: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    consulta = db.query(Pedido)

    if usuario.perfil == "CLIENTE":
        consulta = consulta.filter(Pedido.usuario_id == usuario.id)
    elif usuario.perfil not in ("ATENDENTE", "GERENTE"):
        raise HTTPException(status_code=403, detail="Perfil sem permissão")

    if canal_pedido is not None:
        consulta = consulta.filter(Pedido.canal_pedido == canal_pedido)
    if status_pedido is not None:
        consulta = consulta.filter(Pedido.status == status_pedido)

    return (
        consulta.order_by(Pedido.criado_em.desc(), Pedido.id.desc())
        .limit(limite)
        .all()
    )


@router.get("/{pedido_id}", response_model=PedidoResponse)
def consultar_pedido(
    pedido_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if pedido is None:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    if usuario.perfil == "CLIENTE" and pedido.usuario_id != usuario.id:
        raise HTTPException(status_code=403, detail="Você não pode consultar este pedido")
    if usuario.perfil not in ("CLIENTE", "ATENDENTE", "GERENTE"):
        raise HTTPException(status_code=403, detail="Perfil sem permissão")

    return pedido


@router.get(
    "/{pedido_id}/historico",
    response_model=list[HistoricoStatusResponse],
)
def consultar_historico_pedido(
    pedido_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if pedido is None:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    if usuario.perfil == "CLIENTE" and pedido.usuario_id != usuario.id:
        raise HTTPException(status_code=403, detail="Você não pode consultar este pedido")
    if usuario.perfil not in ("CLIENTE", "ATENDENTE", "GERENTE"):
        raise HTTPException(status_code=403, detail="Perfil sem permissão")

    return (
        db.query(HistoricoStatusPedido)
        .filter(HistoricoStatusPedido.pedido_id == pedido_id)
        .order_by(HistoricoStatusPedido.id)
        .all()
    )