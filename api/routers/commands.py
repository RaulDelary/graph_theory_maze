from fastapi import APIRouter, Depends, HTTPException

from api.schemas.command import StartCommand, MoveCommand, ValidatePathCommand
from api.schemas.position import Position
from api.schemas.validate_path_response import ValidatePathResponse
from api.services.graph_service import GraphService
from api.services.session_service import SessionService

command_routes = APIRouter ()

@command_routes.post ("/iniciar")
async def start_maze (
  start_command: StartCommand,
  session_service: SessionService = Depends (SessionService),
  graph_service: GraphService = Depends (GraphService)
  ) -> Position:

  graph_service.verify_maze_exists (start_command.labirinto)
  session_service.create_session (start_command.id, start_command.labirinto)

  start_position = graph_service.get_start_position (start_command.labirinto)

  return start_position



@command_routes.get ("/labirintos")
async def list_mazes (graph_service: GraphService = Depends (GraphService)) -> list [str]:
  return graph_service.list_all_mazes ()



@command_routes.post ("/movimentar")
async def move (
  move_command: MoveCommand,
  session_service: SessionService = Depends (SessionService),
  graph_service: GraphService = Depends (GraphService)
) -> Position:

  graph_service.verify_maze_exists (move_command.labirinto)
  actual_position_number: int = session_service.get_actual_position_number_by_session_id (move_command.id, move_command.labirinto)

  if graph_service.is_legal_move (move_command.labirinto, actual_position_number, move_command.nova_posicao):
    session_service.update_session_actual_position (move_command.id, move_command.labirinto, move_command.nova_posicao)

  else:
    # TODO: Raise specific exception and tranfer the logic of response to the controler
    raise HTTPException (status_code = 403, detail = 'Movimento ilegal!')

  actual_position_number: int = session_service.get_actual_position_number_by_session_id (move_command.id, move_command.labirinto)
  position = graph_service.get_actual_position (actual_position_number, move_command.labirinto)

  return position



@command_routes.post ("/validar_caminho")
async def validate_path (
  validate_path_command: ValidatePathCommand,
  session_service: SessionService = Depends (SessionService),
  graph_service: GraphService = Depends (GraphService)
) -> ValidatePathResponse:

  graph_service.verify_maze_exists (validate_path_command.labirinto)
  session_service.verify_session_exists (validate_path_command.id + validate_path_command.labirinto)

  is_path_valid: bool = graph_service.validate_path (validate_path_command.labirinto, sorted (validate_path_command.todos_movimentos))
  moves_count: int = len (validate_path_command.todos_movimentos)

  return ValidatePathResponse (caminho_valido = is_path_valid, quantidade_movimentos = moves_count)

