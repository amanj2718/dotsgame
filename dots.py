import pygame, sys
from pygame.locals import *

"""
TODO: Fix the game log.
"""

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
states = {'p1fd':0, 'p1sd':1, 'p2fd':2, 'p2sd':3}
curr_state = states['p1fd']
game_log = ["Player 1 --\n"]

class Dot(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load("dot.png")
		# self.image = pygame.Surface((5, 5))
		# self.image.fill(RED)
		self.rect = self.image.get_rect()
		self.rect.topleft = (x - self.rect.width/2, y - self.rect.height/2)
		self.x = x
		self.y = y
		self.pos = (self.x, self.y)

	def is_adjacent(self, other):
		if (abs(self.x - other.x) == side or abs(self.y - other.y) == side) and not (abs(self.x - other.x) == side and abs(self.y - other.y) == side):
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
		if self.occupied == 1 or self.occupied == 2:
			return False
		if (turn_stack[0].pos == self.rect.topleft and turn_stack[1].pos == self.rect.topright) or \
			(turn_stack[1].pos == self.rect.topleft and turn_stack[0].pos == self.rect.topright):
				self.top_edge = True
				self.check_occupied()
				return self.occupied
		if (turn_stack[0].pos == self.rect.topright and turn_stack[1].pos == self.rect.bottomright) or \
			(turn_stack[1].pos == self.rect.topright and turn_stack[0].pos == self.rect.bottomright):
			self.right_edge = True
			self.check_occupied()
			return self.occupied
		if (turn_stack[0].pos == self.rect.bottomleft and turn_stack[1].pos == self.rect.bottomright) or \
			(turn_stack[1].pos == self.rect.bottomleft and turn_stack[0].pos == self.rect.bottomright):
			self.bottom_edge = True
			self.check_occupied()
			return self.occupied
		if (turn_stack[0].pos == self.rect.topleft and turn_stack[1].pos == self.rect.bottomleft) or \
			(turn_stack[1].pos == self.rect.topleft and turn_stack[0].pos == self.rect.bottomleft):
			self.left_edge = True
			self.check_occupied()
			return self.occupied
		return False

	def check_occupied(self):
		if self.right_edge == True and self.left_edge == True and self.top_edge == True and self.bottom_edge == True:
			if curr_state == states['p1sd'] and self.occupied == False:
				self.occupied = 1
			if curr_state == states['p2sd'] and self.occupied == False:
				self.occupied = 2
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
			adjusted_rect = Rect(self.rect.topleft[0] + 3, self.rect.topleft[1] + 3, self.rect.width - 3, self.rect.height - 3)
			pygame.Surface.blit(screen, surf, adjusted_rect)
		elif self.occupied == 2:
			surf = pygame.Surface((self.rect.width, self.rect.height))
			surf.fill(BLUE)
			adjusted_rect = Rect(self.rect.topleft[0] + 3, self.rect.topleft[1] + 3, self.rect.width - 3, self.rect.height - 3)
			pygame.Surface.blit(screen, surf, adjusted_rect)

rects = []
for i in range(side, board.width, side):
	for j in range(side, board.height, side):
		rects.append(Square(i, j, side, side))
unoccupied_rects = rects

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

# game loop
while True:
	for event in pygame.event.get():
		if (event.type == KEYDOWN and event.key == K_ESCAPE) or event.type == pygame.QUIT:
			sys.exit()
		# handle mouse clicks
		if event.type == MOUSEBUTTONDOWN and event.button == 1:
			snapped = is_clickable(event.pos[0], event.pos[1])
			if snapped is not (-50, -50):
				# handle state
				if curr_state == states['p1fd']:
					d = Dot(snapped[0], snapped[1])
					dots.add(d)
					turn_stack.append(d)
					curr_state = states['p1sd']
					logstr = "Player 1 first dot -- ({0},{1})\n".format(snapped[0], snapped[1])
					game_log.append(logstr)

				elif curr_state == states['p2fd']:
					d = Dot(snapped[0], snapped[1])
					dots.add(d)
					turn_stack.append(d)
					curr_state = states['p2sd']
					logstr = "Player 2 first dot -- ({0}, {1})\n".format(snapped[0], snapped[1])
					game_log.append(logstr)

				elif curr_state == states['p1sd']:
					d = Dot(snapped[0], snapped[1])
					if d.pos != turn_stack[0].pos:
						dots.add(d)
						turn_stack.append(d)
						# draw a line if they are adjacent
						if turn_stack[0].is_adjacent(turn_stack[1]):
							logstr = "Player 1 second dot -- ({0}, {1})\n".format(snapped[0], snapped[1])
							game_log.append(logstr)

							result_list = map(lambda r: r.update(turn_stack), rects)
							if any(result_list):
								player1_points += result_list.count(1)
								curr_state = states['p1fd']
								# for r in rects:
								# 	result = r.update(turn_stack)
								# 	if result == 1:
								# 		curr_state = states['p1fd']
								# 		player1_points += 1
							else:
								curr_state = states['p2fd']
						# if dots are not adjacent
						else:
							clear_turn_stack()
							curr_state = states['p1fd']
						turn_stack = []

				elif curr_state == states['p2sd']:
					d = Dot(snapped[0], snapped[1])
					if d.pos != turn_stack[0].pos:
						dots.add(d)
						turn_stack.append(d)
						if turn_stack[0].is_adjacent(turn_stack[1]):
							logstr = "Player 2 second dot -- ({0}, {1})\n".format(snapped[0], snapped[1])
							game_log.append(logstr)

							print "".join(game_log)
							game_log = []

							result_list = map(lambda r: r.update(turn_stack), rects)
							if any(result_list):
								player2_points += result_list.count(2)
								curr_state = states['p2fd']
									# result = r.update(turn_stack)
									# if result == 2:
									# 	curr_state = states['p2fd']
									# 	player2_points += 1
							else:
								curr_state = states['p1fd']
						else:
							clear_turn_stack()
							curr_state = states['p2fd']
						turn_stack = []
	# background
	window.fill(WHITE)
	top_border = [[side*i, side] for i in range(1, board.width/side + 1)]
	bottom_border = [[side*i, board.height] for i in range(1, board.width/side + 1)]
	for top, bottom in zip(top_border, bottom_border):
		pygame.draw.line(window, BLACK, top, bottom, 2)
		pygame.draw.line(window, BLACK, list(reversed(top)), list(reversed(bottom)), 2)

	for rect in rects:
		rect.draw(window)
	dots.draw(window)
	if curr_state == states['p1fd'] or curr_state == states['p1sd']:
		status = font.render("Player 1\'s turn", 0, RED)
		pygame.Surface.blit(window, status, Rect(200, 25, status.get_width(), status.get_height()))
	elif curr_state == states['p2fd'] or curr_state == states['p2sd']:
		status = font.render("Player 2\'s turn", 0, RED)
		pygame.Surface.blit(window, status, Rect(200, 25, status.get_width(), status.get_height()))
	p1_text = font.render(str(player1_points), 0, GREEN)
	pygame.Surface.blit(window, p1_text, Rect(30, 30, p1_text.get_width(), p1_text.get_height()))
	p2_text = font.render(str(player2_points), 0, BLUE)
	pygame.Surface.blit(window, p2_text, Rect(530, 30, p2_text.get_width(), p2_text.get_height()))
	pygame.display.flip()