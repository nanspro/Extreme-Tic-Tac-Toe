from time import time
import random

class Team41:

	def __init__(self):
		self.MAX = 1000000000
		self.default_depth = 2
		self.player_map = {}
		# self.maxTime = 0
		self.timeLimit = 14
		# [
		# 	freemove,
		# 	blocks_cc_won, blocks_cc_lost, blocks_edge_won, blocks_edge_lost,
		# 	bl_won, bl_lost,
		# 	bdiag_won, bdiag_lost,
		#
		# 	cells_cc_won, cells_cc_lost, cells_edge_won, cells_edge_lost,
		# 	cl_won, cl_lost,
		# 	cdiag_won, cdiag_lost,
		# 	# freedom/10.0,
		# 	# cfreedom/160.0,
		# ]
		self.feature_weights = [
			3000,
			9000, -9000, 6000, -6000,
			300, -300,
			345, -345,

			6, -6, 3, -3,
			3, -3,
			3.45, -3.45,
		]
		self.blwts = [0, 0, 30, 300, 1500]
		self.clwts = [0, 0, 30, 300, 1500]

	def move(self, board, old_move, flag):
		self.startTime = time()
		if flag == 'x':
			self.player_map[True] = 'x'
			self.player_map[False] = 'o'
		else:
			self.player_map[True] = 'o'
			self.player_map[False] = 'x'
		depth = self.default_depth
		ret = 0
		self.stopTime = False
		while time() - self.startTime < self.timeLimit:
			x = self.moveD(board, old_move, flag, depth)
			if not self.stopTime:
				ret = x
				depth += 1
		# print 'Depth ' + str(depth)
		self.stopTime = False
		return ret

	def moveD(self, board, old_move, flag, depth):

		moves = board.find_valid_move_cells(old_move)
		maxval = -self.MAX
		maxi = []
		for i in range(len(moves)):
			v = self.ab_minimax(board, moves[i], depth, -self.MAX, self.MAX, False)
			# print v
			if v > maxval:
				maxval = v
				# maxindex = i
				maxi = [i]
			elif v == maxval:
				maxi.append(i)

		# print maxi
		return moves[random.choice(maxi)]


	def ab_minimax(self, board, old_move, depth, alpha, beta, max_player):
		if time() - self.startTime > self.timeLimit or self.stopTime:
			self.stopTime = True
			return -1

		if depth == 0 or board.find_terminal_state() != ('CONTINUE', '-'):
			# sys.stdout.write(str(old_move) + ' ')
			return self.heuristic(board, old_move, not max_player)

		# print str(self.default_depth - depth) + '\t' + str(old_move)

		if max_player:
			v = -self.MAX
			moves = board.find_valid_move_cells(old_move)
			for new_move in moves:
				# temp_board = copy.copy(board)
				board.update(old_move, new_move, self.player_map[max_player])
				v = max(v, self.ab_minimax(board, new_move, depth - 1, alpha, beta, False))
				board.board_status[new_move[0]][new_move[1]] = '-'
				board.block_status[new_move[0]/4][new_move[1]/4] = '-'
				if self.stopTime:
					return -1
				alpha = max(alpha, v)
				if beta <= alpha:
					break
			return v

		else:
			v = self.MAX
			moves = board.find_valid_move_cells(old_move)
			for new_move in moves:
				# temp_board = copy.copy(board)
				board.update(old_move, new_move, self.player_map[max_player])
				v = min(v, self.ab_minimax(board, new_move, depth - 1, alpha, beta, True))
				board.board_status[new_move[0]][new_move[1]] = '-'
				board.block_status[new_move[0]/4][new_move[1]/4] = '-'
				if self.stopTime:
					return -1
				beta = min(beta, v)
				if beta <= alpha:
					break
			return v


	def heuristic(self, board, old_move, was_our_move):
		tstate = board.find_terminal_state()
		if tstate[1] == 'WON':
			if tstate[0] == self.player_map[True]:
				return self.MAX
			else:
				return -self.MAX

		features = self.extract_features(board, old_move, was_our_move)
		total = 0
		for i in range(len(self.feature_weights)):
			total += self.feature_weights[i] * features[i]

		return total


	def extract_features(self, board, old_move, was_our_move):

		blocks_cc_won = blocks_cc_lost = 0.0
		blocks_edge_won = blocks_edge_lost = 0.0
		cells_cc_won = cells_cc_lost = 0.0
		cells_edge_won = cells_edge_lost = 0.0
		bl_won = 0
		bl_lost = 0
		bdiag_won = bdiag_lost = 0
		freedom = 0
		freemove = 0 # -1 if opp gets freemove, 0 or 1 if we get freemove
		cl_won = cl_lost = 0
		cdiag_won = cdiag_lost = 0
		cfreedom = 0

		diag1_stat = 2
		diag1_count = 0
		diag2_stat = 2
		diag2_count = 0
		diag3_stat = 2
		diag3_count = 0
		diag4_stat = 2
		diag4_count = 0

		for i in range(4):
			row_stat = 2  # 1 - we are in adv in that row, 0 - drawn row, -1 - opp in adv
			col_stat = 2  # 2 - unitialized
			row_count = 0 # count of number of cells row_stat has in that row
			col_count = 0

			# Diag1
			if i==0:
				if board.block_status[i][1] == self.player_map[True]:
					if diag1_stat == 2 or diag1_stat == 1:
						diag1_stat = 1
						diag1_count += 1
					else:
						diag1_stat = 0
						diag1_count = 0
				elif board.block_status[i][1] == self.player_map[False]:
					if diag1_stat == 2 or diag1_stat == -1:
						diag1_stat = -1
						diag1_count += 1
					else:
						diag1_stat = 0
						diag1_count = 0
				elif board.block_status[i][1] == 'd':
					diag1_stat = 0

			# Diag2
				if board.block_status[i][2] == self.player_map[True]:
					if diag2_stat == 2 or diag2_stat == 1:
						diag2_stat = 1
						diag2_count += 1
					else:
						diag2_stat = 0
						diag2_count = 0
				elif board.block_status[i][2] == self.player_map[False]:
					if diag2_stat == 2 or diag2_stat == -1:
						diag2_stat = -1
						diag2_count += 1
					else:
						diag2_stat = 0
						diag2_count = 0
				elif board.block_status[i][2] == 'd':
					diag2_stat = 0

			if i==1:
				if board.block_status[i][2] == self.player_map[True]:
					if diag4_stat == 2 or diag4_stat == 1:
							diag4_stat = 1
							diag4_count += 1
					else:
							diag4_stat = 0
							diag4_count = 0
					if board.block_status[i][0] == self.player_map[True]:
						if diag1_stat == 2 or diag1_stat == 1:
							diag1_stat = 1
							diag1_count += 1
						else:
							diag1_stat = 0
							diag1_count = 0
				elif board.block_status[i][2] == self.player_map[False]:
					if diag4_stat == 2 or diag4_stat == -1:
							diag4_stat = -1
							diag4_count += 1
					else:
							diag4_stat = 0
							diag4_count = 0
					if board.block_status[i][0] == self.player_map[False]:
						if diag1_stat == 2 or diag1_stat == -1:
							diag1_stat = -1
							diag1_count += 1
						else:
							diag1_stat = 0
							diag1_count = 0
				else:
					diag1_stat = 0
					diag4_stat = 0

				if board.block_status[i][1] == self.player_map[True]:
					if diag3_stat == 2 or diag3_stat == 1:
							diag3_stat = 1
							diag3_count += 1
					else:
							diag3_stat = 0
							diag3_count = 0
					if board.block_status[i][3] == self.player_map[True]:
						if diag2_stat == 2 or diag2_stat == 1:
							diag2_stat = 1
							diag2_count += 1
						else:
							diag2_stat = 0
							diag2_count = 0
				elif board.block_status[i][1] == self.player_map[False]:
					if diag3_stat == 2 or diag3_stat == -1:
							diag3_stat = -1
							diag3_count += 1
					else:
							diag3_stat = 0
							diag3_count = 0
					if board.block_status[i][3] == self.player_map[False]:
						if diag2_stat == 2 or diag2_stat == -1:
							diag2_stat = -1
							diag2_count += 1
						else:
							diag2_stat = 0
							diag2_count = 0
				else:
					diag2_stat = 0
					diag3_stat = 0

			if i==2:
				if board.block_status[i][1] == self.player_map[True]:
					if diag1_stat == 2 or diag1_stat == 1:
							diag1_stat = 1
							diag1_count += 1
					else:
							diag1_stat = 0
							diag1_count = 0
					if board.block_status[i][3] == self.player_map[True]:
						if diag4_stat == 2 or diag4_stat == 1:
							diag4_stat = 1
							diag4_count += 1
					else:
							diag4_stat = 0
							diag4_count = 0
				elif board.block_status[i][1] == self.player_map[False]:
					if diag1_stat == 2 or diag1_stat == -1:
							diag1_stat = -1
							diag1_count += 1
					else:
							diag1_stat = 0
							diag1_count = 0
					if board.block_status[i][3] == self.player_map[False]:
						if diag4_stat == 2 or diag4_stat == -1:
							diag4_stat = -1
							diag4_count += 1
						else:
							diag4_stat = 0
							diag4_count = 0
				else:
					diag1_stat = 0
					diag4_stat = 0

				if board.block_status[i][2] == self.player_map[True]:
					if diag2_stat == 2 or diag2_stat == 1:
							diag2_stat = 1
							diag2_count += 1
					else:
							diag2_stat = 0
							diag2_count = 0
					if board.block_status[i][0] == self.player_map[True]:
						if diag3_stat == 2 or diag3_stat == 1:
							diag3_stat = 1
							diag3_count += 1
						else:
							diag3_stat = 0
							diag3_count = 0
				elif board.block_status[i][2] == self.player_map[False]:
					if diag2_stat == 2 or diag2_stat == -1:
							diag2_stat = -1
							diag2_count += 1
					else:
							diag2_stat = 0
							diag2_count = 0
					if board.block_status[i][0] == self.player_map[False]:
						if diag3_stat == 2 or diag3_stat == -1:
							diag3_stat = -1
							diag3_count += 1
						else:
							diag3_stat = 0
							diag3_count = 0
				else:
					diag2_stat = 0
					diag3_stat = 0

				if i==3:
					if board.block_status[i][1] == self.player_map[True]:
						if diag3_stat == 2 or diag3_stat == 1:
							diag3_stat = 1
							diag3_count += 1
						else:
							diag3_stat = 0
							diag3_count = 0
					elif board.block_status[i][1] == self.player_map[False]:
						if diag3_stat == 2 or diag3_stat == -1:
							diag3_stat = -1
							diag3_count += 1
						else:
							diag3_stat = 0
							diag3_count = 0
					elif board.block_status[i][1] == 'd':
						diag3_stat = 0

			# Diag2
					if board.block_status[i][2] == self.player_map[True]:
						if diag4_stat == 2 or diag4_stat == 1:
							diag4_stat = 1
							diag4_count += 1
						else:
							diag4_stat = 0
							diag4_count = 0
					elif board.block_status[i][2] == self.player_map[False]:
						if diag4_stat == 2 or diag4_stat == -1:
							diag4_stat = -1
							diag4_count += 1
						else:
							diag4_stat = 0
							diag4_count = 0
					elif board.block_status[i][2] == 'd':
						diag4_stat = 0					

			for j in range(4):
				# Row statistics
				if board.block_status[i][j] == self.player_map[True]:
					if row_stat == 2 or row_stat == 1:
						row_stat = 1
						row_count += 1
					else:
						row_stat = 0
						row_count = 0
				elif board.block_status[i][j] == self.player_map[False]:
					if row_stat == 2 or row_stat == -1:
						row_stat = -1
						row_count += 1
					else:
						row_stat = 0
						row_count = 0
				elif board.block_status[i][j] == 'd':
					row_stat = 0

				# Col statistics
				if board.block_status[j][i] == self.player_map[True]:
					if col_stat == 2 or col_stat == 1:
						col_stat = 1
						col_count += 1
					else:
						col_stat = 0
						col_count = 0
				elif board.block_status[j][i] == self.player_map[False]:
					if col_stat == 2 or col_stat == -1:
						col_stat = -1
						col_count += 1
					else:
						col_stat = 0
						col_count = 0
				elif board.block_status[j][i] == 'd':
					col_stat = 0

				# Block statistics
				if (i == 0 or i == 3) != (j == 0 or j == 3): # edge block
					if board.block_status[i][j] == self.player_map[True]:
						blocks_edge_won += 1
					elif board.block_status[i][j] == self.player_map[False]:
						blocks_edge_lost += 1
				else: # corner or one of the centre squares
					if board.block_status[i][j] == self.player_map[True]:
						blocks_cc_won += 1
					elif board.block_status[i][j] == self.player_map[False]:
						blocks_cc_lost += 1

				# Cell statistics for blocks which have not been won or drawn
				if board.block_status[i][j] == '-':
					cdiag1_stat = 2
					cdiag1_count = 0
					cdiag2_stat = 2
					cdiag2_count = 0
					cdiag3_stat = 2
					cdiag3_count = 0
					cdiag4_stat = 2
					cdiag4_count = 0
					for bi in range(4):
						crow_stat = 2  # 1 - we are in adv in that row, 0 - drawn row, -1 - opp in adv
						ccol_stat = 2  # 2 - unitialized
						crow_count = 0 # count of number of cells row_stat has in that row
						ccol_count = 0

						ci = 4*i + bi

						if bi==0:
							if board.board_status[4*i+bi][4*j+1] == self.player_map[True]:
								if cdiag1_stat == 2 or cdiag1_stat == 1:
									cdiag1_stat = 1
									cdiag1_count += 1
								else:
									cdiag1_stat = 0
									cdiag1_count = 0
							elif board.board_status[4*i+bi][4*j+1] == self.player_map[False]:
								if cdiag1_stat == 2 or cdiag1_stat == -1:
									cdiag1_stat = -1
									cdiag1_count += 1
								else:
									cdiag1_stat = 0
									cdiag1_count = 0
							elif board.board_status[4*i+bi][4*j+1] == 'd':
								cdiag1_stat = 0

						# Diag2
							if board.board_status[ci][4*j+2] == self.player_map[True]:
								if cdiag2_stat == 2 or cdiag2_stat == 1:
									cdiag2_stat = 1
									cdiag2_count += 1
								else:
									cdiag2_stat = 0
									cdiag2_count = 0
							elif board.board_status[ci][4*j+2] == self.player_map[False]:
								if cdiag2_stat == 2 or cdiag2_stat == -1:
									cdiag2_stat = -1
									cdiag2_count += 1
								else:
									cdiag2_stat = 0
									cdiag2_count = 0
							elif board.board_status[ci][4*j+2] == 'd':
								cdiag2_stat = 0

						if bi==1:
							if board.board_status[ci][4*j+2] == self.player_map[True]:
								if cdiag4_stat == 2 or cdiag4_stat == 1:
										cdiag4_stat = 1
										cdiag4_count += 1
								else:
										cdiag4_stat = 0
										cdiag4_count = 0
								if board.board_status[ci][4*j+0] == self.player_map[True]:
									if cdiag1_stat == 2 or cdiag1_stat == 1:
										cdiag1_stat = 1
										cdiag1_count += 1
									else:
										cdiag1_stat = 0
										cdiag1_count = 0
							elif board.board_status[ci][4*j+2] == self.player_map[False]:
								if cdiag4_stat == 2 or cdiag4_stat == -1:
										cdiag4_stat = -1
										cdiag4_count += 1
								else:
										cdiag4_stat = 0
										cdiag4_count = 0
								if board.board_status[ci][4*j+0] == self.player_map[False]:
									if cdiag1_stat == 2 or cdiag1_stat == -1:
										cdiag1_stat = -1
										cdiag1_count += 1
									else:
										cdiag1_stat = 0
										cdiag1_count = 0
							else:
								cdiag1_stat = 0
								cdiag4_stat = 0

							if board.board_status[ci][4*j+1] == self.player_map[True]:
								if cdiag3_stat == 2 or cdiag3_stat == 1:
										cdiag3_stat = 1
										cdiag3_count += 1
								else:
										cdiag3_stat = 0
										cdiag3_count = 0
								if board.board_status[ci][4*j+3] == self.player_map[True]:
									if cdiag2_stat == 2 or cdiag2_stat == 1:
										cdiag2_stat = 1
										cdiag2_count += 1
									else:
										cdiag2_stat = 0
										cdiag2_count = 0
							elif board.board_status[ci][4*j+1] == self.player_map[False]:
								if cdiag3_stat == 2 or cdiag3_stat == -1:
										cdiag3_stat = -1
										cdiag3_count += 1
								else:
										cdiag3_stat = 0
										cdiag3_count = 0
								if board.board_status[ci][4*j+3] == self.player_map[False]:
									if cdiag2_stat == 2 or cdiag2_stat == -1:
										cdiag2_stat = -1
										cdiag2_count += 1
									else:
										cdiag2_stat = 0
										cdiag2_count = 0
							else:
								cdiag2_stat = 0
								cdiag3_stat = 0

						if bi==2:
							if board.board_status[ci][4*j+1] == self.player_map[True]:
								if cdiag1_stat == 2 or cdiag1_stat == 1:
										cdiag1_stat = 1
										cdiag1_count += 1
								else:
										cdiag1_stat = 0
										cdiag1_count = 0
								if board.board_status[ci][4*j+3] == self.player_map[True]:
									if cdiag4_stat == 2 or cdiag4_stat == 1:
										cdiag4_stat = 1
										cdiag4_count += 1
								else:
										cdiag4_stat = 0
										cdiag4_count = 0
							elif board.board_status[ci][4*j+1] == self.player_map[False]:
								if cdiag1_stat == 2 or cdiag1_stat == -1:
										cdiag1_stat = -1
										cdiag1_count += 1
								else:
										cdiag1_stat = 0
										cdiag1_count = 0
								if board.board_status[ci][4*j+3] == self.player_map[False]:
									if cdiag4_stat == 2 or cdiag4_stat == -1:
										cdiag4_stat = -1
										cdiag4_count += 1
									else:
										cdiag4_stat = 0
										cdiag4_count = 0
							else:
								cdiag1_stat = 0
								cdiag4_stat = 0

							if board.board_status[ci][4*j+2] == self.player_map[True]:
								if cdiag2_stat == 2 or cdiag2_stat == 1:
										cdiag2_stat = 1
										cdiag2_count += 1
								else:
										cdiag2_stat = 0
										cdiag2_count = 0
								if board.board_status[ci][4*j+0] == self.player_map[True]:
									if cdiag3_stat == 2 or cdiag3_stat == 1:
										cdiag3_stat = 1
										cdiag3_count += 1
									else:
										cdiag3_stat = 0
										cdiag3_count = 0
							elif board.board_status[ci][4*j+2] == self.player_map[False]:
								if cdiag2_stat == 2 or cdiag2_stat == -1:
										cdiag2_stat = -1
										cdiag2_count += 1
								else:
										cdiag2_stat = 0
										cdiag2_count = 0
								if board.board_status[ci][4*j+0] == self.player_map[False]:
									if cdiag3_stat == 2 or cdiag3_stat == -1:
										cdiag3_stat = -1
										cdiag3_count += 1
									else:
										cdiag3_stat = 0
										cdiag3_count = 0
							else:
								cdiag2_stat = 0
								cdiag3_stat = 0

						if bi==3:
							if board.board_status[ci][4*j+1] == self.player_map[True]:
								if cdiag3_stat == 2 or cdiag3_stat == 1:
									cdiag3_stat = 1
									cdiag3_count += 1
								else:
									cdiag3_stat = 0
									cdiag3_count = 0
							elif board.board_status[4*i+bi][4*j+1] == self.player_map[False]:
								if cdiag3_stat == 2 or cdiag3_stat == -1:
									cdiag3_stat = -1
									cdiag3_count += 1
								else:
									cdiag3_stat = 0
									cdiag3_count = 0
							elif board.board_status[4*i+bi][4*j+1] == 'd':
								cdiag3_stat = 0

						# Diag2
							if board.board_status[ci][4*j+2] == self.player_map[True]:
								if cdiag4_stat == 2 or cdiag4_stat == 1:
									cdiag4_stat = 1
									cdiag4_count += 1
								else:
									cdiag4_stat = 0
									cdiag4_count = 0
							elif board.board_status[ci][4*j+2] == self.player_map[False]:
								if cdiag4_stat == 2 or cdiag4_stat == -1:
									cdiag4_stat = -1
									cdiag4_count += 1
								else:
									cdiag4_stat = 0
									cdiag4_count = 0
							elif board.board_status[ci][4*j+2] == 'd':
								cdiag4_stat = 0


							

						
						# if board.board_status[4*i+bi][4*j+bi] == self.player_map[True]:
						# 	if cdiag1_stat == 2 or cdiag1_stat == 1:
						# 		cdiag1_stat = 1
						# 		cdiag1_count += 1
						# 	else:
						# 		cdiag1_stat = 0
						# 		cdiag1_count = 0
						# elif board.board_status[4*i+bi][4*j+bi] == self.player_map[False]:
						# 	if cdiag1_stat == 2 or cdiag1_stat == -1:
						# 		cdiag1_stat = -1
						# 		cdiag1_count += 1
						# 	else:
						# 		cdiag1_stat = 0
						# 		cdiag1_count = 0

						# # Diag2
						# if board.board_status[4*i+bi][4*j+3-bi] == self.player_map[True]:
						# 	if cdiag2_stat == 2 or cdiag2_stat == 1:
						# 		cdiag2_stat = 1
						# 		cdiag2_count += 1
						# 	else:
						# 		cdiag2_stat = 0
						# 		cdiag2_count = 0
						# elif board.board_status[4*i+bi][4*j+3-bi] == self.player_map[False]:
						# 	if cdiag2_stat == 2 or cdiag2_stat == -1:
						# 		cdiag2_stat = -1
						# 		cdiag2_count += 1
						# 	else:
						# 		cdiag2_stat = 0
						# 		cdiag2_count = 0

						for bj in range(4):
							cj = 4*j + bj
							# Row statistics
							if board.board_status[4*i+bi][4*j+bj] == self.player_map[True]:
								if crow_stat == 2 or crow_stat == 1:
									crow_stat = 1
									crow_count += 1
								else:
									crow_stat = 0
									crow_count = 0
							elif board.board_status[4*i+bi][4*j+bj] == self.player_map[False]:
								if crow_stat == 2 or crow_stat == -1:
									crow_stat = -1
									crow_count += 1
								else:
									crow_stat = 0
									crow_count = 0

							# Col statistics
							if board.board_status[4*i+bj][4*j+bi] == self.player_map[True]:
								if ccol_stat == 2 or ccol_count == 1:
									ccol_stat = 1
									ccol_count += 1
								else:
									ccol_stat = 0
									ccol_count = 0
							elif board.board_status[4*i+bj][4*j+bi] == self.player_map[False]:
								if ccol_stat == 2 or ccol_stat == -1:
									ccol_stat = -1
									ccol_count += 1
								else:
									ccol_stat = 0
									ccol_count = 0

							if (bi == 0 or bi == 3) == (bj == 0 or bj == 3): # centre or corner squares
								if board.board_status[ci][cj] == self.player_map[True]:
									cells_edge_won += 1
								elif board.board_status[ci][cj] == self.player_map[False]:
									cells_edge_lost += 1
							else:
								if board.board_status[ci][cj] == self.player_map[True]:
									cells_cc_won += 1
								elif board.board_status[ci][cj] == self.player_map[False]:
									cells_cc_lost += 1

						if crow_stat == 1:
							cl_won += self.clwts[crow_count]
							cfreedom += 1
						elif crow_stat == -1:
							cl_lost += self.clwts[crow_count]
						elif crow_stat == 2:
							cfreedom += 1

						if ccol_stat == 1:
							cl_won += self.clwts[ccol_count]
							cfreedom += 1
						elif ccol_stat == -1:
							cl_lost += self.clwts[ccol_count]
						elif ccol_stat == 2:
							cfreedom += 1

					if cdiag1_stat == 1:
						cdiag_won += self.clwts[cdiag1_count]
						cfreedom += 1
					elif cdiag1_stat == -1:
						cdiag_lost += self.clwts[cdiag1_count]
					elif cdiag1_stat == 2:
						cfreedom += 1

					if cdiag2_stat == 1:
						cdiag_won += self.clwts[cdiag2_count]
						cfreedom += 1
					elif cdiag2_stat == -1:
						cdiag_lost += self.clwts[cdiag2_count]
					elif cdiag2_stat == 2:
						cfreedom += 1


			if row_stat == 1:
				bl_won += self.blwts[row_count]
				freedom += 1
			elif row_stat == -1:
				bl_lost += self.blwts[row_count]
			elif row_stat == 2:
				freedom += 1

			if col_stat == 1:
				bl_won += self.blwts[col_count]
				freedom += 1
			elif col_stat == -1:
				bl_lost += self.blwts[col_count]
			elif col_stat == 2:
				freedom += 1

		if diag1_stat == 1:
			bdiag_won += self.blwts[diag1_count]
			freedom += 1
		elif diag1_stat == -1:
			bdiag_lost += self.blwts[diag1_count]
		elif diag1_stat == 2:
			freedom += 1

		if diag2_stat == 1:
			bdiag_won += self.blwts[diag2_count]
			freedom += 1
		elif diag2_stat == -1:
			bdiag_lost += self.blwts[diag2_count]
		elif diag2_stat == 2:
			freedom += 1

		if diag3_stat == 1:
			bdiag_won += self.blwts[diag3_count]
			freedom += 1
		elif diag3_stat == -1:
			bdiag_lost += self.blwts[diag3_count]
		elif diag3_stat == 2:
			freedom += 1

		if diag4_stat == 1:
			bdiag_won += self.blwts[diag4_count]
			freedom += 1
		elif diag4_stat == -1:
			bdiag_lost += self.blwts[diag4_count]
		elif diag4_stat == 2:
			freedom += 1


		if board.block_status[old_move[0] % 4][old_move[1] % 4] != '-':
			freemove = -1 if was_our_move else 1


		return [
			freemove,
			blocks_cc_won, blocks_cc_lost, blocks_edge_won, blocks_edge_lost,
			bl_won, bl_lost,
			bdiag_won, bdiag_lost,

			cells_cc_won, cells_cc_lost, cells_edge_won, cells_edge_lost,
			cl_won, cl_lost,
			cdiag_won, cdiag_lost,
			# freedom/10.0,
			# cfreedom/160.0,
		]
