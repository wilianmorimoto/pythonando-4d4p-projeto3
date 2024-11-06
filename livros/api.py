from ninja import Router, Query
from .schemas import LivrosSchema, AvaliacaoSchema, FiltrosSortearSchema, LivrosViewSchema
from .models import Livros, Categorias
from typing import List

livros_router = Router()


@livros_router.post('/')
def create_livro(request, livro_schema: LivrosSchema):
  nome = livro_schema.dict()['nome']
  streaming = livro_schema.dict()['streaming']
  categorias = livro_schema.dict()['categorias']

  if streaming not in ['F', 'AK']:
    return 400, {'status': 'ERRO: Streaming deve ser F ou AK'}
  livro = Livros(nome=nome, streaming=streaming)
  livro.save()

  for categoria in categorias:
    categoria_temp = Categorias.objects.get(id=categoria)
    livro.categorias.add(categoria_temp)

  return {'status': 'ok'}


@livros_router.put('/{livro_id}')
def avaliar_livro(request, livro_id: int, avaliacao_schema: AvaliacaoSchema):
  comentarios = avaliacao_schema.dict()['comentarios']
  nota = avaliacao_schema.dict()['nota']

  try:
    livro = Livros.objects.get(id=livro_id)
    livro.comentarios = comentarios
    livro.nota = nota
    livro.save()

    return 200, {'status': 'Avaliação realizada com sucesso!'}
  except:
    return 500, {'status': 'Erro interno do servidor.'}


@livros_router.delete('/{livro_id}')
def deletar_livro(request, livro_id: int):
  livro = Livros.objects.get(id=livro_id)
  livro.delete()
  return 200, {'status': 'Livro excluído!'}


@livros_router.get('/sortear/', response={200: LivrosSchema, 404: dict})
def sortear_livro(request, filtros: Query[FiltrosSortearSchema]):
  nota_minima = filtros.dict()['nota_minima']
  categoria = filtros.dict()['categoria']
  reler = filtros.dict()['reler']

  livros = Livros.objects.all()
  if not reler:
    livros = livros.filter(nota=None)
  if nota_minima:
    livros = livros.filter(nota__gte=nota_minima)
  if categoria:
    livros = livros.filter(categorias__id=categoria)

  livro = livros.order_by('?').first()

  if livro:
    return 200, livro
  else:
    return 404, {'status': 'Nenhum livro encontrado.'}


@livros_router.get('/', response={200: List[LivrosViewSchema]})
def get_livro(request):
  livros = Livros.objects.all()
  return livros
