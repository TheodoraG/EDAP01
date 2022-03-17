import gym
import random
import requests
import numpy as np
import argparse
import sys
import copy
import time
from gym_connect_four import ConnectFourEnv

env: ConnectFourEnv = gym.make("ConnectFour-v0")

#global variables
ROW_COUNT = 6
COLUMN_COUNT = 7

SERVER_PIECE = -1
AI_PIECE = 1

#SERVER_ADRESS = "http://localhost:8000/"
SERVER_ADRESS = "https://vilde.cs.lth.se/edap01-4inarow/"
API_KEY = 'nyckel'
STIL_ID = ["th6636ga-s"] # TODO: fill this list with your stil-id's

def call_server(move):
   res = requests.post(SERVER_ADRESS + "move",
                       data={
                           "stil_id": STIL_ID,
                           "move": move, # -1 signals the system to start a new game. any running game is counted as a loss
                           "api_key": API_KEY,
                       })
   # For safety some respose checking is done here
   if res.status_code != 200:
      print("Server gave a bad response, error code={}".format(res.status_code))
      exit()
   if not res.json()['status']:
      print("Server returned a bad status. Return message: ")
      print(res.json()['msg'])
      exit()
   return res

def check_stats():
   res = requests.post(SERVER_ADRESS + "stats",
                       data={
                           "stil_id": STIL_ID,
                           "api_key": API_KEY,
                       })

   stats = res.json()
   return stats

"""
You can make your code work against this simple random agent
before playing against the server.
It returns a move 0-6 or -1 if it could not make a move.
To check your code for better performance, change this code to
use your own algorithm for selecting actions too
"""
def opponents_move(env):
   env.change_player() # change to oppoent
   avmoves = env.available_moves()
   if not avmoves:
      env.change_player() # change back to student before returning
      return -1

   # TODO: Optional? change this to select actions with your policy too
   # that way you get way more interesting games, and you can see if starting
   # is enough to guarrantee a win
   action = random.choice(list(avmoves))

   state, reward, done, _ = env.step(action)
   if done:
      if reward == 1: # reward is always in current players view
         reward = -1
   env.change_player() # change back to student before returning
   return state, reward, done

"""
Alpha beta pruning algorithm
Returns the selected action and its utility value

References: https://github.com/aimacode/aima-python/blob/master/games.py
            https://github.com/KeithGalli/Connect4-Python/blob/master/connect4_with_ai.py
"""
def alpha_beta_cutoff(state, d, maxPlayer):
   
   def max_value(state,alpha,beta,d,maxPlayer):
      #cutoff test
      if d == 0 or winning_move(state, maxPlayer) or winning_move(state, not maxPlayer):
         return eval_fn(state)
      #max_value finds the action with the highest utility value + the utility value
      #the first element of uv is the action
      #the second element of uv is the utility value
      uv = [-1,-np.inf]
      #get all available actions
      for a in get_valid_locations(state):
         next_state = copy.deepcopy(state)
         #update the state of the game  (do the selected action)
         make_move(next_state, a, AI_PIECE)
         #call to min_value function
         uv_new = min_value(next_state, alpha, beta, d-1,
                              False)[1]
         #keep the action only if
         #the found utility is higher then the current utility
         if uv_new>uv[1]:
              uv = [a, uv_new]
         alpha = max(alpha,uv[1])
         if alpha>= beta:
            break
      return uv


   def min_value(state,alpha,beta,d,maxPlayer):
      #cutoff test
      if d == 0 or winning_move(state, maxPlayer) or winning_move(state, not maxPlayer):
         return eval_fn(state)
      #min_value finds the action with the lowest utility value + the utility value
      #the first element of uv is the action
      #the second element of uv is the utility value
      uv = [-1,np.inf]
      #get all available actions
      for a in get_valid_locations(state):
         next_state = copy.deepcopy(state)
         #update the state of the game  (do the selected action)
         make_move(next_state, a, SERVER_PIECE)
         #call to min_value function
         uv_new = max_value(next_state, alpha, beta, d-1,
                             True)[1]
         #keep the action only if
         #the found utility is lower then the current utility
         if uv_new<uv[1]:
              uv = [a, uv_new]
         beta = min(beta,uv[1])
         if alpha>= beta:
            break
      return uv

   #compute the alpha-beta pruning algorithm
   #the first value of best_score is the action (column)
   #the second value is the utility value
   best_score = [-1,-np.inf]
   beta = np.inf
   #get all available actions
   for a in get_valid_locations(state):
      next_state = copy.deepcopy(state)
      #make_move(next_state, a, maxPlayer)
      #uv_new  = min_value(next_state,best_score[1],beta,1,False)[1]
      #update the state of the game  (do the selected action)
      make_move(next_state, a, AI_PIECE)
      #get the lowest utility value of the new state
      uv_new  = min_value(next_state,best_score[1],beta,1,False)[1]
      #keep the action only if
      #the found utility is higher then the current utility
      if uv_new>best_score[1]:
         #update best_score
         best_score = [a, uv_new]
   #return the best action and utility value
   return best_score

  
def student_move(state):
   """
   TODO: Implement your min-max alpha-beta pruning algorithm here.
   Give it whatever input arguments you think are necessary
   (and change where it is called).
   The function should return a move from 0-6
   """
   state = copy.deepcopy(state)
   #return the action using Alpha-Beta cutoff algorithm
   return alpha_beta_cutoff(state,5,AI_PIECE)[0]


"""
Update the state of the game after you select an action
action = the column of the board/game
"""
def make_move(state, action, player):
   #from the bottom line to the upper one
   for row in list(reversed(range(state.shape[0]))):
      #see if the space is free
      if state[row, action] == 0:
         if player:
            #mark the place for the AI agent
            state[row, action] = AI_PIECE
            break
         else:
            #mark the place for the server
            state[row, action] = SERVER_PIECE
            break
   return state

"""
Check if the current action (column)
is valid
"""
def is_valid_location(state, action:int):
	return state[0][action] == 0


"""
Check all valid locations (columns)
"""
def get_valid_locations(state):
	valid_locations = []
	for col in range(state.shape[1]):
		if is_valid_location(state, col):
			valid_locations.append(col)
	return valid_locations


""" 
Evaluation function: 
compute the score of the state

References: https://github.com/KeithGalli/Connect4-Python/blob/master/connect4_with_ai.py
"""
def eval_fn(state):
   totalScore = 0 #score for the current combination of connected cells
   state = state

   #check rows (horizontally)
   for row in state:
      for index in range(state.shape[1]-3):
         currentComb = [row[index+i] for i in range(4)]
         #add the current set score to the total score of the game
         totalScore += score_in_a_row(currentComb)

   #check columns (vertically)
   for row in np.flip(np.transpose(state)):
      for index in range(state.shape[0]-3):
         currentComb = [row[index+i] for i in range(4)]
         totalScore += score_in_a_row(currentComb)

   #check diagonally
   #positive sloped diagonal
   for row in range(state.shape[0]-3):
      for index in range(state.shape[1]-3):
         currentComb = [state[row+i, index+i] for i in range(4)]
         totalScore += score_in_a_row(currentComb)

   #negative sloped diagonal
   for row in range(state.shape[0]-3):
      for index in range(state.shape[1]-3):
         currentComb = [state[row+3-i, index+i] for i in range(4)]
         totalScore += score_in_a_row(currentComb)

   #place the AI agent in the middle of the game 
   for row in range(state.shape[0]):
      if state[row, 3] == AI_PIECE:
         totalScore += 1
   #return -1 if invalid move, totalScore otherwise
   return [-1, totalScore]

"""
Heuristic function
Sets the score
Count the numbers of 4,3,2 in a row 
Row is actually a set of 4 cells
Assign a score for each

Reference: https://github.com/KeithGalli/Connect4-Python/blob/master/connect4_with_ai.py
"""
def score_in_a_row(row):   
   score = 0
   min_count = 0   #number of cells corresponding to the min player
   max_count = 0   #number of cells corresponding to the max player
   empty_count = 0  #empty cells


   #if it's a 1, then it corresponds to the max player
   max_count = row.count(AI_PIECE)
   #if it's a -1, then it corresponds to the max player
   min_count = row.count(SERVER_PIECE)
   #if it's a 0, then it's an empty location
   empty_count = row.count(0)

   #set a score for each move corresponding to the max player
   if max_count == 4:
      score += 5000001  
   elif max_count == 3 and empty_count == 1:
      score += 5000
   elif max_count == 2 and empty_count == 2:
      score += 500

   #set a score for each move corresponding to the min player
   #penalize for good moves of the min player
   elif min_count == 4:
      score -= 5000000
   elif min_count == 3 and empty_count == 1:
      score -= 5001
   elif min_count == 2 and empty_count == 2:
      score -= 501

   return score


"""
Check if the player wins 
Return true if it wins

Reference: https://github.com/KeithGalli/Connect4-Python/blob/master/connect4_with_ai.py
"""
def winning_move(state, player):
   if player: 
      #winning score for the max player
      score = 5000001
   else: 
      #winning score for the min player
      score = 5000000

   rowScore = 0

   #check rows (horizontally)
   for row in state:
      for index in range(state.shape[1]-3):
         currentComb = [row[index+i] for i in range(4)]
         #add the current set score to the total score of the game
         rowScore = score_in_a_row(currentComb)
         if rowScore == score:
            return True

   #check columns (vertically)
   for row in np.flip(np.transpose(state)):
      for index in range(state.shape[0]-3):
         currentComb = [row[index+i] for i in range(4)]
         rowScore = score_in_a_row(currentComb)
         if rowScore == score:
            return True

   
   #check diagonally
   #positive sloped diagonal
   for row in range(state.shape[0]-3):
      for index in range(state.shape[1]-3):
         currentComb = [state[row+i, index+i] for i in range(4)]
         rowScore += score_in_a_row(currentComb)
         if rowScore == score:
               return True

   #negative sloped diagonal
   for row in range(state.shape[0]-3):
      for index in range(state.shape[1]-3):
         currentComb = [state[row+3-i, index+i] for i in range(4)]
         rowScore += score_in_a_row(currentComb)
         if rowScore == score:
               return True

   return False

def play_game(vs_server = False):
   """
   The reward for a game is as follows. You get a
   botaction = random.choice(list(avmoves)) reward from the
   server after each move, but it is 0 while the game is running
   loss = -1
   win = +1
   draw = +0.5
   error = -10 (you get this if you try to play in a full column)
   Currently the player always makes the first move
   """

   # default state
   state = np.zeros((6, 7), dtype=int)

   # setup new game
   if vs_server:
      # Start a new game
      res = call_server(-1) # -1 signals the system to start a new game. any running game is counted as a loss

      # This should tell you if you or the bot starts
      print(res.json()['msg'])
      botmove = res.json()['botmove']
      state = np.array(res.json()['state'])
   else:
      # reset game to starting state
      env.reset(board=None)
      # determine first player
      student_gets_move = random.choice([True, False])
      if student_gets_move:
         print('You start!')
         print()
      else:
         print('Bot starts!')
         print()

   # Print current gamestate
   print("Current state (1 are student discs, -1 are servers, 0 is empty): ")
   print(state)
   print()

   done = False
   d = 6
   cutoff_test = False
   eval_fn = None
   while not done:
      # Select your move
      start_time = time.time()
      stmove = student_move(state) # TODO: change input here
      
      # make both student and bot/server moves
      if vs_server:
         # Send your move to server and get response
         res = call_server(stmove)
         print(res.json()['msg'])

         # Extract response values
         result = res.json()['result']
         botmove = res.json()['botmove']
         state = np.array(res.json()['state'])
      else:
         if student_gets_move:
            # Execute your move
            avmoves = env.available_moves()
            if stmove not in avmoves:
               print("You tied to make an illegal move! Games ends.")
               break
            state, result, done, _ = env.step(stmove)

         student_gets_move = True # student only skips move first turn if bot starts

         # print or render state here if you like

         # select and make a move for the opponent, returned reward from students view
         if not done:
            state, result, done = opponents_move(env)
      
      print("--- Move executed %s in seconds ---" % (time.time() - start_time))

      # Check if the game is over
      if result != 0:
         done = True
         if not vs_server:
            print("Game over. ", end="")
         if result == 1:
            print("You won!")
         elif result == 0.5:
            print("It's a draw!")
         elif result == -1:
            print("You lost!")
         elif result == -10:
            print("You made an illegal move and have lost!")
         else:
            print("Unexpected result result={}".format(result))
         if not vs_server:
            print("Final state (1 are student discs, -1 are servers, 0 is empty): ")
      else:
         print("Current state (1 are student discs, -1 are servers, 0 is empty): ")

      # Print current gamestate
      print(state)
      print()

def main():
   # Parse command line arguments
   """parser = argparse.ArgumentParser()
   group = parser.add_mutually_exclusive_group()
   group.add_argument("-l", "--local", help = "Play locally", action="store_true")
   group.add_argument("-o", "--online", help = "Play online vs server", action="store_true")
   parser.add_argument("-s", "--stats", help = "Show your current online stats", action="store_true")
   args = parser.parse_args()

   # Print usage info if no arguments are given
   if len(sys.argv)==1:
      parser.print_help(sys.stderr)
      sys.exit(1)

   if args.local:
      play_game(vs_server = False)
   elif args.online:
      play_game(vs_server = True)

   if args.stats:
      stats = check_stats()
      print(stats)"""

   # TODO: Run program with "--online" when you are ready to play against the server
   # the results of your games there will be logged
   play_game(vs_server = True)
   # you can check your stats bu running the program with "--stats"

if __name__ == "__main__":
    main()
