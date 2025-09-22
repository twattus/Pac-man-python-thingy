import pygame,sys
from pygame.locals import QUIT
import random
import math

screen_x=672 #3x magnification - squares are 24x24px
screen_y=864

speed_mult=3 #pixels per tick
tick=0

pygame.init()
screen=pygame.display.set_mode((screen_x,screen_y))
background=pygame.Rect(0,0,screen_x,screen_y)
board_background_image=pygame.image.load(open("pac_man_board_sprite.png")).convert()

pygame.display.set_caption('     Pac-Man')

def draw_text(text,font,col,x,y):
	img=font.render(text,True,col)
	screen.blit(img,(x,y))


debug_setting_draw_og_rect_walls_keep_false=False
energizer_power_up=False
energizer_tick=0
dead=False
pac_man_lives=3
points=0
level=1

pac_man_up=pygame.image.load(open("pac_man_rotations\Pac_Man_Up.png")).convert_alpha()
pac_man_left=pygame.image.load(open("pac_man_rotations\Pac_Man_Left.png")).convert_alpha()
pac_man_down=pygame.image.load(open("pac_man_rotations\Pac_Man_Down.png")).convert_alpha()
pac_man_right=pygame.image.load(open("pac_man_rotations\Pac_Man_Right.png")).convert_alpha()

pac_man=pygame.Rect(324,624,24,24) # the 'true' hitbox is only 1 tile in size - but the walls are drawn to be smaller so it all cancels out (see diagram below)

#
#
#       0  <-- hitbox (small)
#	
#		00 <--sprite (big)
#   	00
#
#
#		00 <--wall hitbox (big)
#		00
#		00
#
#
#		0 <--wall sprite (small)
#     	0
#		0
#
#		it all works out ig
#

pac_man_side_colliders=[pygame.Rect(pac_man.x,pac_man.y-speed_mult,pac_man.width,speed_mult),pygame.Rect(pac_man.x-speed_mult,pac_man.y,speed_mult,pac_man.height),
                        pygame.Rect(pac_man.x,pac_man.bottom,pac_man.width,speed_mult),pygame.Rect(pac_man.right,pac_man.y,speed_mult,pac_man.height)] #initial definition
#wasd config (up-left-down-right) ^

orthogonal_directions=[[0,-1],[-1,0],[0,1],[1,0]]
diagonal_directions=[[1,-1],[1,1],[-1,1],[-1,-1]]
#diagonal uses wd-ds-sa-aw config (only for neighbour() so order irrelevant)
total_directions=[[1,-1],[1,1],[-1,1],[-1,-1],[0,-1],[-1,0],[0,1],[1,0]]

pac_man_travelled_squares=[]
temp_ghost_colour=(0,0,0)
internal_game_over_timer=0

def orthogonal_neighbours(x,y):
	neighbour_count=0
	for e in range(0,len(orthogonal_directions)):
		try:
			if area_walls_init_text[y+orthogonal_directions[e][1]][x+orthogonal_directions[e][0]]:
				neighbour_count+=1
		except:
			try:
				if area_walls_init_text[(y+orthogonal_directions[e][1])][(x+orthogonal_directions[e][0])%len(orthogonal_directions)]:
					neighbour_count+=1
			except:
				continue
	return neighbour_count

def diagonal_neighbours(x,y):
	neighbour_count=0
	for e in range(0,len(diagonal_directions)):
		try:
			if area_walls_init_text[y+diagonal_directions[e][1]][x+diagonal_directions[e][0]]==1:
				neighbour_count+=1
		except:
			try:
				if area_walls_init_text[(y+diagonal_directions[e][1])][(x+diagonal_directions[e][0])%len(diagonal_directions)]==1:
					neighbour_count+=1
			except:
				continue

	return neighbour_count

def total_neighbours(x,y):
	return (orthogonal_neighbours(x,y)+diagonal_neighbours(x,y))

def dist(x_1,y_1,x_2,y_2):
	return math.sqrt((abs(x_2-x_1)**2)+(abs(y_2-y_1)**2))



ghosts_list=[[pygame.Rect(624,96,24,24),"blinky","chase",[-1,0]],[pygame.Rect(24,96,24,24),"pinky","chase",[1,0]],
			 [pygame.Rect(624,768,24,24),"inky","chase",[-1,0]],[pygame.Rect(24,768,24,24),"clyde","chase",[1,0]]]

base_reference_ghosts_list=[[pygame.Rect(624,96,24,24),"blinky","chase",[-1,0]],[pygame.Rect(24,96,24,24),"pinky","chase",[1,0]],
			 				[pygame.Rect(624,768,24,24),"inky","chase",[-1,0]],[pygame.Rect(24,768,24,24),"clyde","chase",[1,0]]]
# ^ used for resetting ghosts after death or level change
# |



blinky_sprite=pygame.image.load(open("ghosts_folder\Blinky_ghost.png")).convert_alpha()
pinky_sprite=pygame.image.load(open("ghosts_folder\Pinky_ghost.png")).convert_alpha()
inky_sprite=pygame.image.load(open("ghosts_folder\Inky_ghost.png")).convert_alpha()
clyde_sprite=pygame.image.load(open("ghosts_folder\Clyde_ghost.png")).convert_alpha()
scared_sprite=pygame.image.load(open("ghosts_folder\Scared_ghost.png")).convert_alpha()


def opposite_vector(direction):
	return [direction[0]*-1,direction[1]*-1]


# #very inefficient, but it works
# ghosts_list_hitboxes=[[pygame.Rect(ghosts_list[0][0].x,ghosts_list[0][0].y-2,ghosts_list[0][0].width,2),pygame.Rect(ghosts_list[0][0].x-2,ghosts_list[0][0].y,2,ghosts_list[0][0].height),pygame.Rect(ghosts_list[0][0].x,ghosts_list[0][0].bottom,ghosts_list[0][0].width,2),pygame.Rect(ghosts_list[0][0].right,ghosts_list[0][0].y,2,ghosts_list[0][0].height)],
# 					  [pygame.Rect(ghosts_list[1][0].x,ghosts_list[1][0].y-2,ghosts_list[1][0].width,2),pygame.Rect(ghosts_list[1][0].x-2,ghosts_list[1][0].y,2,ghosts_list[1][0].height),pygame.Rect(ghosts_list[1][0].x,ghosts_list[1][0].bottom,ghosts_list[1][0].width,2),pygame.Rect(ghosts_list[1][0].right,ghosts_list[1][0].y,2,ghosts_list[1][0].height)],
# 					  [pygame.Rect(ghosts_list[2][0].x,ghosts_list[2][0].y-2,ghosts_list[2][0].width,2),pygame.Rect(ghosts_list[2][0].x-2,ghosts_list[2][0].y,2,ghosts_list[2][0].height),pygame.Rect(ghosts_list[2][0].x,ghosts_list[2][0].bottom,ghosts_list[2][0].width,2),pygame.Rect(ghosts_list[2][0].right,ghosts_list[2][0].y,2,ghosts_list[2][0].height)],
# 					  [pygame.Rect(ghosts_list[3][0].x,ghosts_list[3][0].y-2,ghosts_list[3][0].width,2),pygame.Rect(ghosts_list[3][0].x-2,ghosts_list[3][0].y,2,ghosts_list[3][0].height),pygame.Rect(ghosts_list[3][0].x,ghosts_list[3][0].bottom,ghosts_list[3][0].width,2),pygame.Rect(ghosts_list[3][0].right,ghosts_list[3][0].y,2,ghosts_list[3][0].height)]]


ghosts_list_hitboxes=[[pygame.Rect(ghosts_list[0][0].x,ghosts_list[0][0].y-1,ghosts_list[0][0].width,1),pygame.Rect(ghosts_list[0][0].x-1,ghosts_list[0][0].y,1,ghosts_list[0][0].height),pygame.Rect(ghosts_list[0][0].x,ghosts_list[0][0].bottom,ghosts_list[0][0].width,1),pygame.Rect(ghosts_list[0][0].right,ghosts_list[0][0].y,1,ghosts_list[0][0].height)],
					[pygame.Rect(ghosts_list[1][0].x,ghosts_list[1][0].y-1,ghosts_list[1][0].width,1),pygame.Rect(ghosts_list[1][0].x-1,ghosts_list[1][0].y,1,ghosts_list[1][0].height),pygame.Rect(ghosts_list[1][0].x,ghosts_list[1][0].bottom,ghosts_list[1][0].width,1),pygame.Rect(ghosts_list[1][0].right,ghosts_list[1][0].y,1,ghosts_list[1][0].height)],
					[pygame.Rect(ghosts_list[2][0].x,ghosts_list[2][0].y-1,ghosts_list[2][0].width,1),pygame.Rect(ghosts_list[2][0].x-1,ghosts_list[2][0].y,1,ghosts_list[2][0].height),pygame.Rect(ghosts_list[2][0].x,ghosts_list[2][0].bottom,ghosts_list[2][0].width,1),pygame.Rect(ghosts_list[2][0].right,ghosts_list[2][0].y,1,ghosts_list[2][0].height)],
					[pygame.Rect(ghosts_list[3][0].x,ghosts_list[3][0].y-1,ghosts_list[3][0].width,1),pygame.Rect(ghosts_list[3][0].x-1,ghosts_list[3][0].y,1,ghosts_list[3][0].height),pygame.Rect(ghosts_list[3][0].x,ghosts_list[3][0].bottom,ghosts_list[3][0].width,1),pygame.Rect(ghosts_list[3][0].right,ghosts_list[3][0].y,1,ghosts_list[3][0].height)]]


base_reference_ghost_list_hitboxes=ghosts_list_hitboxes

def target_pos(ghost_name,state):
	target_position=[0,0]

	if state=="scatter":
		pass
	elif state=="chase":
		if ghost_name=="blinky": #red one - target is pac-man
			return [pac_man.x,pac_man.y] 
		
		elif ghost_name=="pinky": #pink one - target is 2 tiles in front of pac-man
			return [pac_man.x+(intended_direction[0]*24*2),pac_man.y+(intended_direction[1]*24*2)] 
		
		elif ghost_name=="inky": #blue one - target is inverse of blinky's position relative to pac-man
			return [ghosts_list[0][0].x+(2*(pac_man.x-ghosts_list[0][0].x)),ghosts_list[0][0].y+(2*(pac_man.y-ghosts_list[0][0].y))]

		elif ghost_name=="clyde": #orange one - target is pac-man when >8 tiles away, otherwise scatters
			if dist(ghosts_list[3][0].x,ghosts_list[3][0].y,pac_man.x,pac_man.y)>8*24:
				return [pac_man.x,pac_man.y]
			else:
				return [0,816]

	return target_position
	

#0 is empty, 1 is wall, 2 is pellet, 3 is energizer
# - pellet uses grid hitboxes, so no extra list needed
# -"premature optimization" no it's easier AND faster 
#the highly re____ed formatting is for ease of editing
energizer_rects=[]
area_walls=[]
area_walls_init_text=[[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
					  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
					  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
					  [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
					  [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1], 
					  [1, 2, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 2, 1],
					  [1, 3, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 3, 1], 
					  [1, 2, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 2, 1],
					  [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1], 
					  [1, 2, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 2, 1],
					  [1, 2, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 2, 1], 
					  [1, 2, 2, 2, 2, 2, 2, 1, 1, 2, 2, 2, 2, 1, 1, 2, 2, 2, 2, 1, 1, 2, 2, 2, 2, 2, 2, 1],
					  [1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1], 
					  [1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1],
					  [1, 1, 1, 1, 1, 1, 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 2, 1, 1, 1, 1, 1, 1], 
					  [1, 1, 1, 1, 1, 1, 2, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 2, 1, 1, 1, 1, 1, 1],
					  [1, 1, 1, 1, 1, 1, 2, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 2, 1, 1, 1, 1, 1, 1], 
					  [0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0],
					  [1, 1, 1, 1, 1, 1, 2, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 2, 1, 1, 1, 1, 1, 1], 
					  [1, 1, 1, 1, 1, 1, 2, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 2, 1, 1, 1, 1, 1, 1],
					  [1, 1, 1, 1, 1, 1, 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 2, 1, 1, 1, 1, 1, 1], 
					  [1, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 1],
					  [1, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 1], 
					  [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
					  [1, 2, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 2, 1], 
					  [1, 2, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 2, 1],
					  [1, 3, 2, 2, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 2, 2, 3, 1], 
					  [1, 1, 1, 2, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 2, 1, 1, 1],
					  [1, 1, 1, 2, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 2, 1, 1, 1], 
					  [1, 2, 2, 2, 2, 2, 2, 1, 1, 2, 2, 2, 2, 1, 1, 2, 2, 2, 2, 1, 1, 2, 2, 2, 2, 2, 2, 1],
					  [1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1],
					  [1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1],
					  [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
					  [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
					  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
					  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],]

for y in range(0,len(area_walls_init_text)):
	for x in range(0,len(area_walls_init_text[y])):
		if area_walls_init_text[y][x]==1:
			area_walls.append(pygame.Rect(x*24,y*24,24,24))
		elif area_walls_init_text[y][x]==3:
			energizer_rects.append(pygame.Rect((x*24)+4,(y*24)+4,16,16))

area_walls.extend([pygame.Rect(-24,384,24,24),pygame.Rect(-24,432,24,24),pygame.Rect(-48,384,24,24),pygame.Rect(-48,432,24,24),
				   pygame.Rect(672,384,24,24),pygame.Rect(672,432,24,24),pygame.Rect(696,384,24,24),pygame.Rect(696,432,24,24)])# prevents ghosts from turning in the tunnels


def ghost_collision_values_and_valid_moves(ghost_id,mode):
	collisions=[0,0,0,0]
	ghost_collision_valid_directions=[[0,-1],[-1,0],[0,1],[1,0]]
	for e in range(0,len(ghosts_list_hitboxes[ghost_id])):
		for f in range(0,len(area_walls)):
			if pygame.Rect.colliderect(ghosts_list_hitboxes[ghost_id][e],area_walls[f]):
				collisions[e]=1
				ghost_collision_valid_directions[e]=[0,0]
	while [0,0] in ghost_collision_valid_directions:
		ghost_collision_valid_directions.remove([0,0])

	if mode==0:
		return sum(collisions)
	elif mode==1:
		return ghost_collision_valid_directions
	elif mode==2:
		return [sum(collisions),ghost_collision_valid_directions]


direction=[1,0]
intended_direction=direction #used for player input
valid_directions=[[0,-1],[-1,0],[0,1],[1,0]]
pac_man_blit_direction=[1,0]

previous_frame_ghost_hitboxes_value=[]
for e in range(0,4):
	previous_frame_ghost_hitboxes_value.append(ghost_collision_values_and_valid_moves(e,0))

# current_frame_ghost_hitboxes_value=[]
# for e in range(0,4):
# 	current_frame_ghost_hitboxes_value.append(ghost_collision_values_and_valid_moves(e,0))

def reset_to_base_game_state():
	global pac_man,ghosts_list,ghosts_list_hitboxes,dead,direction,intended_direction,pac_man_blit_direction,pac_man_side_colliders,pac_man_lives
	pac_man=0
	dead=False #resets ghost & player positions - however not pellets & energizers
	pac_man_lives-=1
	pac_man=pygame.Rect(324,624,24,24)
	direction=[1,0]
	intended_direction=[1,0]
	pac_man_blit_direction=[1,0]
	pac_man_side_colliders=[pygame.Rect(pac_man.x,pac_man.y-speed_mult,pac_man.width,speed_mult),pygame.Rect(pac_man.x-speed_mult,pac_man.y,speed_mult,pac_man.height),
					pygame.Rect(pac_man.x,pac_man.bottom,pac_man.width,speed_mult),pygame.Rect(pac_man.right,pac_man.y,speed_mult,pac_man.height)]
	ghosts_list=[[pygame.Rect(624,96,24,24),"blinky","chase",[-1,0]],[pygame.Rect(24,96,24,24),"pinky","chase",[1,0]],
			 				[pygame.Rect(624,768,24,24),"inky","chase",[-1,0]],[pygame.Rect(24,768,24,24),"clyde","chase",[1,0]]]
	ghosts_list_hitboxes=base_reference_ghost_list_hitboxes
	
def win_level():
	global pac_man_travelled_squares,level, energizer_rects, pac_man_lives
	pac_man_travelled_squares=[]
	energizer_rects=[pygame.Rect(28, 148, 16, 16), pygame.Rect(628, 148, 16, 16), pygame.Rect(28, 628, 16, 16), pygame.Rect(628, 628, 16, 16)]
	level+=1
	pac_man_lives+=1 #cancels out -1 life from reset_game_state
	reset_to_base_game_state()

def game_over():
	global pac_man_travelled_squares,level,pac_man_lives,points,internal_game_over_timer,energizer_rects
	reset_to_base_game_state()
	energizer_rects=[pygame.Rect(28, 148, 16, 16), pygame.Rect(628, 148, 16, 16), pygame.Rect(28, 628, 16, 16), pygame.Rect(628, 628, 16, 16)]
	pac_man_lives=3
	level=1
	points=0
	pac_man_travelled_squares=[]
	internal_game_over_timer=150


while True:
	clock=pygame.time.Clock()
	tick+=1
	board=pygame.key.get_pressed()

	if internal_game_over_timer==0:

		if pac_man_lives==0:
			game_over()

		if energizer_tick>0:
			energizer_tick-=1
			energizer=True
		else:
			energizer=False



		if (board[pygame.K_w] or board[pygame.K_UP]):
			intended_direction=[0,-1]
			pac_man_blit_direction=[0,-1]
			if [0,-1] in valid_directions:
				direction=[0,-1] #arrow keys now valid - however they are cringe
				# direction is (x,y)
				

		elif (board[pygame.K_a] or board[pygame.K_LEFT]):
			intended_direction=[-1,0]
			pac_man_blit_direction=[-1,0]
			if [-1,0] in valid_directions:
				direction=[-1,0]
				
				

		elif (board[pygame.K_s] or board[pygame.K_DOWN]): 
			intended_direction=[0,1]
			pac_man_blit_direction=[0,1]
			if [0,1] in valid_directions:
				direction=[0,1]
				
				

		elif (board[pygame.K_d] or board[pygame.K_RIGHT]): 
			intended_direction=[1,0]
			pac_man_blit_direction=[1,0]
			if [1,0] in valid_directions:
				direction=[1,0]
				

		valid_directions=[[0,-1],[-1,0],[0,1],[1,0]]
		for e in range(0,len(pac_man_side_colliders)):
			pac_man_collided_on_wall=False
			for f in range(0,len(area_walls)):
				if pygame.Rect.colliderect(pac_man_side_colliders[e],area_walls[f]):
					pac_man_collided_on_wall=True
					break

			
			if pac_man_collided_on_wall:
				if e==0:#there must be faster ways of doing this, too bad I dont give a f___
					direction[1]=max(direction[1],0)
					valid_directions.remove([0,-1])
				elif e==1:
					direction[0]=max(direction[0],0)
					valid_directions.remove([-1,0])
				elif e==2:
					direction[1]=min(direction[1],0)
					valid_directions.remove([0,1])
				elif e==3:
					direction[0]=min(direction[0],0)
					valid_directions.remove([1,0])
		

		if intended_direction in valid_directions:
			pac_man.x+=intended_direction[0]*speed_mult
			pac_man.y+=intended_direction[1]*speed_mult
			direction=intended_direction

			
		else:
			pac_man.x+=direction[0]*speed_mult
			pac_man.y+=direction[1]*speed_mult		

		for e in range(0,len(energizer_rects)):
			if pygame.Rect.colliderect(pac_man,energizer_rects[e]):
				energizer_rects[e]=0
				energizer=True
				energizer_tick=360
		while 0 in energizer_rects:
			energizer_rects.remove(0)

		if pac_man.x<-(48+speed_mult):
			pac_man.x=screen_x+speed_mult
		elif pac_man.x>screen_x+speed_mult:
			pac_man.x=-(48+speed_mult)

		if [pac_man.x//24,pac_man.y//24] not in pac_man_travelled_squares:
			pac_man_travelled_squares.append([pac_man.x//24,pac_man.y//24])
			points+=250
			

		# previous_frame_ghost_hitboxes_value=[]
		# for e in range(0,4):
		# 	previous_frame_ghost_hitboxes_value.append(ghost_collision_values_and_valid_moves(e,0))

		for e in range(0,len(ghosts_list)):
			if ghosts_list[e][0].x<-(48+2):
				ghosts_list[e][0].x=screen_x+2
			elif ghosts_list[e][0].x>screen_x+2:
				ghosts_list[e][0].x=-(48+2)

		pac_man_side_colliders=[pygame.Rect(pac_man.x,pac_man.y-speed_mult,pac_man.width,speed_mult),pygame.Rect(pac_man.x-speed_mult,pac_man.y,speed_mult,pac_man.height),
							pygame.Rect(pac_man.x,pac_man.bottom,pac_man.width,speed_mult),pygame.Rect(pac_man.right,pac_man.y,speed_mult,pac_man.height)] #idk may have to go though
		


		# for e in range(0,len(pac_man_side_colliders)): #DEBUG
		# 	pygame.draw.rect(screen,(255,0,0),pac_man_side_colliders[e])





		ghosts_list_hitboxes=[[pygame.Rect(ghosts_list[0][0].x,ghosts_list[0][0].y-1,ghosts_list[0][0].width,1),pygame.Rect(ghosts_list[0][0].x-1,ghosts_list[0][0].y,1,ghosts_list[0][0].height),pygame.Rect(ghosts_list[0][0].x,ghosts_list[0][0].bottom,ghosts_list[0][0].width,1),pygame.Rect(ghosts_list[0][0].right,ghosts_list[0][0].y,1,ghosts_list[0][0].height)],
							[pygame.Rect(ghosts_list[1][0].x,ghosts_list[1][0].y-1,ghosts_list[1][0].width,1),pygame.Rect(ghosts_list[1][0].x-1,ghosts_list[1][0].y,1,ghosts_list[1][0].height),pygame.Rect(ghosts_list[1][0].x,ghosts_list[1][0].bottom,ghosts_list[1][0].width,1),pygame.Rect(ghosts_list[1][0].right,ghosts_list[1][0].y,1,ghosts_list[1][0].height)],
							[pygame.Rect(ghosts_list[2][0].x,ghosts_list[2][0].y-1,ghosts_list[2][0].width,1),pygame.Rect(ghosts_list[2][0].x-1,ghosts_list[2][0].y,1,ghosts_list[2][0].height),pygame.Rect(ghosts_list[2][0].x,ghosts_list[2][0].bottom,ghosts_list[2][0].width,1),pygame.Rect(ghosts_list[2][0].right,ghosts_list[2][0].y,1,ghosts_list[2][0].height)],
							[pygame.Rect(ghosts_list[3][0].x,ghosts_list[3][0].y-1,ghosts_list[3][0].width,1),pygame.Rect(ghosts_list[3][0].x-1,ghosts_list[3][0].y,1,ghosts_list[3][0].height),pygame.Rect(ghosts_list[3][0].x,ghosts_list[3][0].bottom,ghosts_list[3][0].width,1),pygame.Rect(ghosts_list[3][0].right,ghosts_list[3][0].y,1,ghosts_list[3][0].height)]]

		current_frame_ghost_hitboxes_value=[]
		for e in range(0,4):
			current_frame_ghost_hitboxes_value.append(ghost_collision_values_and_valid_moves(e,0))



		#<DRAW ZONE>
		
		#pygame.draw.rect(screen,(0,0,0),background)
		screen.blit(board_background_image,(0,0))



		
		pellet_count_on_screen=0
		for y in range(0,len(area_walls_init_text)):
			for x in range(0,len(area_walls_init_text[y])):
				if area_walls_init_text[y][x]==2 and [x,y] not in pac_man_travelled_squares:
					pellet_count_on_screen+=1
					pygame.draw.rect(screen,(255,255,255),pygame.Rect((x*24)+8,(y*24)+8,8,8)) #pellet

				elif area_walls_init_text[y][x]==3 and [x,y] not in pac_man_travelled_squares: #energizer
					pygame.draw.rect(screen,(255,255,255),pygame.Rect((x*24)+4,(y*24)+4,16,16))
		
		if pellet_count_on_screen==0:
			win_level()


		#pygame.draw.rect(screen,(255,255,0),pac_man) #draw section (ghosts drawn at end of loop)

		if pac_man_blit_direction==[0,-1]:
			screen.blit(pac_man_up,(pac_man.x-12,pac_man.y-12))

		elif pac_man_blit_direction==[-1,0]:
			screen.blit(pac_man_left,(pac_man.x-12,pac_man.y-12))

		elif pac_man_blit_direction==[0,1]:
			screen.blit(pac_man_down,(pac_man.x-12,pac_man.y-12))

		elif pac_man_blit_direction==[1,0]:
			screen.blit(pac_man_right,(pac_man.x-12,pac_man.y-12))

		if debug_setting_draw_og_rect_walls_keep_false:
			for e in range(0,len(area_walls)):
				if total_neighbours(area_walls[e].x//24,area_walls[e].y//24)==8:
					pygame.draw.rect(screen,(0,0,127),area_walls[e]) #surrounded tiles are differentiated
				else:
					pygame.draw.rect(screen,(0,0,255),area_walls[e]) #placeholder-will blit full image later?
		


		#<DRAW ZONE\>


		for e in range(0,len(ghosts_list)):
			#pygame.draw.rect(screen,(255,0,0),pygame.Rect(target_pos(ghosts_list[e][1],ghosts_list[e][2])[0],target_pos(ghosts_list[e][1],ghosts_list[e][2])[1],16,16)) #temp thing

			if energizer:
				if pygame.Rect.colliderect(ghosts_list[e][0],pac_man):
					ghosts_list[e][0]=[[pygame.Rect(624,96,24,24),"blinky","chase",[-1,0]],[pygame.Rect(24,96,24,24),"pinky","chase",[1,0]],
								[pygame.Rect(624,768,24,24),"inky","chase",[-1,0]],[pygame.Rect(24,768,24,24),"clyde","chase",[1,0]]][e][0]
			else:
				if pygame.Rect.colliderect(ghosts_list[e][0],pac_man):
					dead=True
					reset_to_base_game_state()



			if True: #or previous_frame_ghost_hitboxes_value!=current_frame_ghost_hitboxes_value: #needs optimisation
				ghost_turn_options=ghost_collision_values_and_valid_moves(e,1)

				while opposite_vector(ghosts_list[e][3]) in ghost_turn_options:
					ghost_turn_options.remove(opposite_vector(ghosts_list[e][3]))

				target_distances_list=[]
				for f in range(0,len(ghost_turn_options)):
					target_distances_list.append(dist(ghosts_list[e][0].x+(ghost_turn_options[f][0])*2,ghosts_list[e][0].y+(ghost_turn_options[f][1]*2),
										target_pos(ghosts_list[e][1],ghosts_list[e][2])[0],target_pos(ghosts_list[e][1],ghosts_list[e][2])[1]))


				try:
					if energizer:
						ghosts_list[e][3]=random.choice(ghost_turn_options)
					else:
						ghosts_list[e][3]=ghost_turn_options[target_distances_list.index(min(target_distances_list))]
				except:
					ghosts_list[e][3]=opposite_vector(ghosts_list[e][3])

			if energizer:
				ghosts_list[e][0].x+=ghosts_list[e][3][0]*1 #100% slower than pac man when energized
				ghosts_list[e][0].y+=ghosts_list[e][3][1]*1
			else:
				ghosts_list[e][0].x+=ghosts_list[e][3][0]*2 #50% slower than pac man normally
				ghosts_list[e][0].y+=ghosts_list[e][3][1]*2



			if energizer:
				temp_ghost_id=scared_sprite
			elif e==0:
				#temp_ghost_colour=(255,0,0)
				temp_ghost_id=blinky_sprite
			elif e==1:
				#temp_ghost_colour=(255,184,255)
				temp_ghost_id=pinky_sprite
			elif e==2:
				#temp_ghost_colour=(0,255,255)
				temp_ghost_id=inky_sprite
			elif e==3:
				#temp_ghost_colour=(255,184,92)
				temp_ghost_id=clyde_sprite
			#pygame.draw.rect(screen,temp_ghost_colour,ghosts_list[e][0])
			screen.blit(temp_ghost_id,(ghosts_list[e][0].x-12,ghosts_list[e][0].y-12))

		draw_text(f"{1000000000+(points)-250}",pygame.font.SysFont("emulogic",24),(255,255,255),-24,0) 
		#billion is hidden by start pos to allow leading zeros for authenticity

		draw_text(f"level:{level}",pygame.font.SysFont("emulogic",24),(255,255,255),0,36)

		if pac_man_lives>2:
			screen.blit(pac_man_right,(96,screen_y-48))
		if pac_man_lives>1:
			screen.blit(pac_man_right,(48,screen_y-48))
		if pac_man_lives>0:
			screen.blit(pac_man_right,(0,screen_y-48))		

	else:
		internal_game_over_timer-=1
		draw_text("GAME",pygame.font.SysFont("emulogic",128),(255,255,255),64,250)

		draw_text("OVER",pygame.font.SysFont("emulogic",128),(255,255,255),64,384)

	


	clock.tick(60)
	for event in pygame.event.get():
		if event.type == QUIT:
			pygame.quit()
			sys.exit()
	pygame.display.update()


