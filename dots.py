import pygame, sys
from pygame.locals import *
from copy import deepcopy
from random import choice
from math import sqrt

pygame.init()

side = 50
dimensions = [550, 550]
board = Rect(side, side, 5*side, 5*side)

window = pygame.display.set_mode(dimensions)

BLACK = (0, 0, 0, 0)
WHITE = (255, 255, 255, 1)
RED = (255, 0, 0, 1)
GREEN = (0, 255, 0, 1)
BLUE = (0, 0, 255, 1)

player1_points = 0
player2_points = 0
turn_stack = []
MODE = 'MULTIPLAYER'
STATES = {'p1fd':0, 'p1sd':1, 'p2fd':2, 'p2sd':3}
curr_state = STATES['p1fd']
game_log = ["Player 1 --\n"]

class Dot(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load("dot.png")
		self.rect = self.image.get_rect()
		self.rect.topleft = (x - self.rect.width/2, y - self.rect.height/2)
		self.x = x
		self.y = y
		self.pos = (self.x, self.y)

	def is_adjacent(self, other):
		if (abs(self.x - other.x) == side or abs(self.y - other.y) == side) \
		and not (abs(self.x - other.x) == side and abs(self.y - other.y) == side):
			return True
		else:
			return False

class Square():
	def __init__(self, top, left, width, height):
		self.rect = Rect(top, left, width, height)
		self.left_edge = False
		self.right_edge = False
		self.top_edge = False
		self.bottom_edge = False
		self.occupied = False

	def update(self, stack):
		"""
		Takes turn stack, flip corresponding edge flag to true and check if all
		edges are occupied. Returns true if occupied.
		"""
		# the following two lines are a hack so that one can't overwrite squares
		if self.occupied == 1 or self.occupied == 2 or self.occupied == 3:
			return False
		if (stack[0].pos == self.rect.topleft and stack[1].pos == self.rect.topright) or \
		   (stack[1].pos == self.rect.topleft and stack[0].pos == self.rect.topright):
				self.top_edge = True
				self.check_occupied()
				return self.occupied
		if (stack[0].pos == self.rect.topright and stack[1].pos == self.rect.bottomright) or \
		   (stack[1].pos == self.rect.topright and stack[0].pos == self.rect.bottomright):
			self.right_edge = True
			self.check_occupied()
			return self.occupied
		if (stack[0].pos == self.rect.bottomleft and stack[1].pos == self.rect.bottomright) or \
		   (stack[1].pos == self.rect.bottomleft and stack[0].pos == self.rect.bottomright):
			self.bottom_edge = True
			self.check_occupied()
			return self.occupied
		if (stack[0].pos == self.rect.topleft and stack[1].pos == self.rect.bottomleft) or \
		   (stack[1].pos == self.rect.topleft and stack[0].pos == self.rect.bottomleft):
			self.left_edge = True
			self.check_occupied()
			return self.occupied
		return False

	def check_occupied(self):
		if self.right_edge == True and self.left_edge == True \
		and self.top_edge == True and self.bottom_edge == True:
			if curr_state == STATES['p1sd']:
				self.occupied = 1
			if curr_state == STATES['p2sd']:
				self.occupied = 2
			if MODE == 'AI_MODE' and curr_state == STATES['p2fd']:
				self.occupied = 3
		else:
			self.occupied = False

	def draw(self, screen):
		if self.left_edge is True:
			pygame.draw.line(screen, RED, self.rect.topleft, self.rect.bottomleft, 4)
		if self.right_edge is True:
			pygame.draw.line(screen, RED, self.rect.topright, self.rect.bottomright, 4)
		if self.top_edge is True:
			pygame.draw.line(screen, RED, self.rect.topleft, self.rect.topright, 4)
		if self.bottom_edge is True:
			pygame.draw.line(screen, RED, self.rect.bottomleft, self.rect.bottomright, 4)
		if self.occupied == 1:
			surf = pygame.Surface((self.rect.width, self.rect.height))
			surf.fill(GREEN)
			adjusted_rect = Rect(self.rect.topleft[0] + 3, self.rect.topleft[1] + 3,
								 self.rect.width - 3, self.rect.height - 3)
			pygame.Surface.blit(screen, surf, adjusted_rect)
		elif self.occupied == 2 or self.occupied == 3:
			surf = pygame.Surface((self.rect.width, self.rect.height))
			surf.fill(BLUE)
			adjusted_rect = Rect(self.rect.topleft[0] + 3, self.rect.topleft[1] + 3,
								 self.rect.width - 3, self.rect.height - 3)
			pygame.Surface.blit(screen, surf, adjusted_rect)

rects = []
for i in range(side, board.width, side):
	for j in range(side, board.height, side):
		rects.append(Square(i, j, side, side))

dots = pygame.sprite.Group()

# initialize font
font = pygame.font.Font(None, 24)

def is_clickable(x, y):
	snap_x, snap_y = -50, -50
	if x%side <= 10 and x%side >= 0:
		snap_x = x - x%side
	if y%side <= 10 and y%side >= 0:
		snap_y = y - y%side
	if x%side >= side - 10 and x%side < side:
		snap_x = (x/side + 1)*side
	if y%side >= side - 10 and y%side < side:
		snap_y = (y/side + 1)*side
	return snap_x, snap_y

def clear_turn_stack():
	initial = turn_stack[0]
	terminal = turn_stack[1]
	dots.remove(initial)
	dots.remove(terminal)

def render_ui():
	if curr_state == STATES['p1fd'] or curr_state == STATES['p1sd']:
		status = font.render("Player 1\'s turn", 0, RED)
		pygame.Surface.blit(window, status, Rect(200, 25, status.get_width(), status.get_height()))

	elif curr_state == STATES['p2fd'] or curr_state == STATES['p2sd']:
		status = font.render("Player 2\'s turn", 0, RED)
		pygame.Surface.blit(window, status, Rect(200, 25, status.get_width(), status.get_height()))
	
	p1_text = font.render(str(player1_points), 0, GREEN)
	pygame.Surface.blit(window, p1_text, Rect(30, 30, p1_text.get_width(), p1_text.get_height()))
	p2_text = font.render(str(player2_points), 0, BLUE)
	pygame.Surface.blit(window, p2_text, Rect(530, 30, p2_text.get_width(), p2_text.get_height()))

def draw_background():
	window.fill(WHITE)
	top_border = [[side*i, side] for i in range(1, board.width/side + 1)]
	bottom_border = [[side*i, board.height] for i in range(1, board.width/side + 1)]
	for top, bottom in zip(top_border, bottom_border):
		pygame.draw.line(window, BLACK, top, bottom, 2)
		pygame.draw.line(window, BLACK, list(reversed(top)), list(reversed(bottom)), 2)
"""
AI SYSTEM
"""
def get_filled_edges(rect):
	edges = [rect.left_edge, rect.top_edge, rect.right_edge, rect.bottom_edge]
	return edges.count(True)

def is_feasible(past_state, future_state):
	"""
	Return weight of decision based on a definite scale.
	Calculates all the squares that can be possibly occupied because of a chain-reaction.
	"""
	weight = 0
	for index, filled_edges in enumerate(past_state):
		# start checks only if there's a change
		future_edges = future_state[index]
		if future_edges != filled_edges:
			# dont help the player
			if filled_edges == 2 and future_edges == 3:
				weight -= 10
			# good if you occupied a square
			if filled_edges == 3 and future_edges == 4:
				weight += 10
			# safe moves
			if filled_edges == 1 and future_edges == 2:
				weight += 1
			if filled_edges == 0 and future_edges == 1:
				weight += 5
	if future_state.count(3) > past_state.count(3):
		weight -= 10
	return weight

def apply_move(move):
	"""
	Takes a move and returns a list of future_state of rects.
	"""
	rects_copy = deepcopy(rects)
	rect_index = move[0]
	rect_edge = move[1]
	offset = int(sqrt(len(rects)))
	if rect_edge == 'l':
		rects_copy[rect_index].left_edge = True
		if rect_index - offset >= 0:
			rects_copy[rect_index - offset].right_edge = True
	elif rect_edge == 'r':
		rects_copy[rect_index].right_edge = True
		if rect_index + offset <= 8:
			rects_copy[rect_index + offset].left_edge = True
	elif rect_edge == 't':
		rects_copy[rect_index].top_edge = True
		if rect_index%offset != 0:
			rects_copy[rect_index - 1].bottom_edge = True
	elif rect_edge == 'b':
		rects_copy[rect_index].bottom_edge = True
		if rect_index%offset != offset - 1:
			rects_copy[rect_index + 1].top_edge = True
	return map(get_filled_edges, rects_copy)

def one_filled_edge(index):
	rect = rects[index]
	base_str = ""
	if rect.left_edge == True:
		base_str = "rtb"
	elif rect.right_edge == True:
		base_str = "ltb"
	elif rect.top_edge == True:
		base_str = "lrb"
	elif rect.bottom_edge == True:
		base_str = "ltr"
	return [(index, i) for i in base_str]

def two_filled_edge(index):
	rect = rects[index]
	base_str = ""
	if rect.left_edge == False:
		base_str += 'l'
	if rect.right_edge == False:
		base_str += 'r'
	if rect.top_edge == False:
		base_str += 't'
	if rect.bottom_edge == False:
		base_str += 'b'
	return [(index, i) for i in base_str]

def three_filled_edge(index):
	rect = rects[index]
	if rect.left_edge == False:
		return [(index, 'l')]
	elif rect.right_edge == False:
		return [(index, 'r')]
	elif rect.top_edge == False:
		return [(index, 't')]
	elif rect.bottom_edge == False:
		return [(index, 'b')]

def ai_move():
	"""
	Returns a tuple (index_in_rects, edge_code).
	edge_codes: left_edge -- 'l', top_edge -- 't', 
				right_edge -- 'r', bottom_edge -- 'b'
	"""
	initial_state = map(get_filled_edges, rects)
	possible_moves = []
	for index, filled_edges in enumerate(initial_state):
		if filled_edges == 0:
			possible_moves.extend([(index, i) for i in 'ltrb'])
		elif filled_edges == 1:
			possible_moves.extend(one_filled_edge(index))
		elif filled_edges == 2:
			possible_moves.extend(two_filled_edge(index))
		elif filled_edges == 3:
			possible_moves.extend(three_filled_edge(index))
	print possible_moves
	possible_decisions = []
	for move in possible_moves:
		final_state = apply_move(move)
		possible_decisions.append(is_feasible(initial_state, final_state))
	print possible_decisions
	# randomizing when some decisions have the same weight
	max_weight = max(possible_decisions)
	# list of indices which have the same weight
	max_indices = []
	for index, weight in enumerate(possible_decisions):
		if weight == max_weight:
			max_indices.append(index)
	x = choice(max_indices)
	print x
	return possible_moves[x]
	# return possible_moves[possible_decisions.index(max(possible_decisions))]

def convert_to_stack(move):
	stack = []
	edge = move[1]
	r = rects[move[0]].rect
	if edge == 'l':
		d1 = Dot(r.left, r.top)
		d2 = Dot(r.left, r.bottom)
	elif edge == 'r':
		d1 = Dot(r.right, r.top)
		d2 = Dot(r.right, r.bottom)
	elif edge == 'b':
		d1 = Dot(r.right, r.bottom)
		d2 = Dot(r.left, r.bottom)
	elif edge == 't':
		d1 = Dot(r.right, r.top)
		d2 = Dot(r.left, r.top)
	dots.add(d1)
	dots.add(d2)
	stack.append(d1)
	stack.append(d2)
	return stack
"""
AI SYSTEM END
"""
def set_game_mode():
	global MODE
	ai_text = font.render("AI MODE", 0, RED)
	ai_rect = Rect(225, 150, ai_text.get_width(), ai_text.get_height())
	two_player = font.render("2 PLAYER", 0, RED)
	two_player_rect = Rect(225, 275, two_player.get_width(), two_player.get_height())
	done = False
	while not done:
		for event in pygame.event.get():
			if (event.type == KEYDOWN and event.key == K_ESCAPE) \
			or event.type == pygame.QUIT:
				sys.exit()
			if (event.type == MOUSEBUTTONDOWN and event.button == 1):
				if ai_rect.collidepoint((event.pos[0], event.pos[1])):
					MODE = 'AI_MODE'
					done = True
				elif two_player_rect.collidepoint((event.pos[0], event.pos[1])):
					MODE = 'MULTIPLAYER'
					done = True
		window.fill(BLACK)
		pygame.Surface.blit(window, ai_text, ai_rect)
		pygame.Surface.blit(window, two_player, two_player_rect)
		pygame.display.flip()

set_game_mode()
# game loop
while True:
	for event in pygame.event.get():
		if (event.type == KEYDOWN and event.key == K_ESCAPE) \
		or event.type == pygame.QUIT:
			sys.exit()
		# handle mouse clicks
		if event.type == MOUSEBUTTONDOWN and event.button == 1:
			snapped = is_clickable(event.pos[0], event.pos[1])
			if snapped is not (-50, -50):
				# gameplay logic
				if curr_state == STATES['p1fd']:
					d = Dot(snapped[0], snapped[1])
					dots.add(d)
					turn_stack.append(d)
					curr_state = STATES['p1sd']

				elif curr_state == STATES['p2fd'] and MODE == 'MULTIPLAYER':
					d = Dot(snapped[0], snapped[1])
					dots.add(d)
					turn_stack.append(d)
					curr_state = STATES['p2sd']

				elif curr_state == STATES['p1sd']:
					d = Dot(snapped[0], snapped[1])
					if d.pos != turn_stack[0].pos:
						dots.add(d)
						turn_stack.append(d)
						# draw a line if they are adjacent
						if turn_stack[0].is_adjacent(turn_stack[1]):
							result_list = map(lambda r: r.update(turn_stack), rects)
							if any(result_list):
								player1_points += result_list.count(1)
								curr_state = STATES['p1fd']
							else:
								curr_state = STATES['p2fd']
						# if dots are not adjacent
						else:
							clear_turn_stack()
							curr_state = STATES['p1fd']
						turn_stack = []

				elif curr_state == STATES['p2sd'] and MODE == 'MULTIPLAYER':
					d = Dot(snapped[0], snapped[1])
					if d.pos != turn_stack[0].pos:
						dots.add(d)
						turn_stack.append(d)
						if turn_stack[0].is_adjacent(turn_stack[1]):
							result_list = map(lambda r: r.update(turn_stack), rects)
							if any(result_list):
								player2_points += result_list.count(2)
								curr_state = STATES['p2fd']
							else:
								curr_state = STATES['p1fd']
						else:
							clear_turn_stack()
							curr_state = STATES['p2fd']
						turn_stack = []

	if MODE == 'AI_MODE' and curr_state == STATES['p2fd']:
		move = ai_move()
		result_list = map(lambda r: r.update(convert_to_stack(move)), rects)
		if any(result_list):
			player2_points += result_list.count(3)
			curr_state = STATES['p2fd']
		else:
			curr_state = STATES['p1fd']

	# background
	draw_background()

	for rect in rects:
		rect.draw(window)

	dots.draw(window)

	render_ui()

	pygame.display.flip()
	# game over condition
	lst = [rect.occupied for rect in rects]
	if all(lst):
		while True:
			for event in pygame.event.get():
				if (event.type == KEYDOWN and event.key == K_ESCAPE) \
				or event.type == pygame.QUIT:
					sys.exit()
			window.fill(WHITE, Rect(0, 0, 550, 43))
			if player1_points > player2_points:
				winner = "Player 1"
			elif player2_points > player1_points:
				winner = "Player 2"
			else:
				winner = "Both "
			over_text = font.render(winner+" won!", 0, RED)
			pygame.Surface.blit(window, over_text, Rect(200, 25, over_text.get_width(), over_text.get_height()))
			pygame.display.flip()