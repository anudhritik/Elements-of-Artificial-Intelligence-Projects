import gamePlay
from copy import deepcopy
from getAllPossibleMoves import getAllPossibleMoves

'''
My Strategy is as follows:
I am giving atmost importance to the kings by increasing their value and also giving more weight to the back row coins on either side
so that the chance of opponent cins becomes is minimized. I tried various other evaluation functions like giving more importance to the
center coins, double corner coins. But, unfortunately none of them gave me satisfying results. So, I decided to keep only the king
evaluation and back row coins evaluation. 
'''
def evaluation(board, color,opponentColor):
    new_value = 0
    # Loop through all board positions
    for piece in range(1,33):
        xy = gamePlay.serialToGrid(piece)
        x = xy[0]
        y = xy[1]
        if board[x][y] == color:
            new_value = new_value + 1
        if board[x][y] == opponentColor:
            new_value = new_value - 1
    #accumulated_value = new_value + king_evaluation(board, color, opponentColor) + center_evaluation(board, color, opponentColor) + doublecorner_evaluation(board, color, opponentColor)
    accumulated_value = new_value + king_evaluation(board,color,opponentColor) + protecting_backrowcoins_evaluation(board,color,opponentColor)   
    return accumulated_value

# Giving more weight to the king coins.

def king_evaluation(board, color, opponentColor):
    value = 0
    for piece in range(1, 33):
        xy = gamePlay.serialToGrid(piece)
        x = xy[0]
        y = xy[1]

        if board[x][y] == color.upper():
            value += 1
        elif board[x][y] == opponentColor.upper():
            value -= 1

    value = (value)*5
    return value

# Giving more importance to the back row coins 

def protecting_backrowcoins_evaluation(board,color,opponentColor):
    #calucating weightage for coins at the back , in order to avoid the opponent pawns becoming kings
    weightage = {0: 0, 1: -1, 2: 1, 3: 0, 4: 1, 5: 1, 6: 2, 7: 1, 8: 1, 9: 0,
            10: 7, 11: 4, 12: 2, 13: 2, 14: 9, 15: 8}
    value = 0
    coinvalue = 0
    if board[7][0] == color or opponentColor:
        coinvalue += 1
    if board[7][2] == color or opponentColor:
        coinvalue += 2
    if board[7][4] == color or opponentColor:
        coinvalue += 4
    if board[7][6] == color or opponentColor:
        coinvalue += 8
    totalweight = weightage[coinvalue]
    coinvalue = 0
    if board[0][1] == opponentColor or color:
        coinvalue += 8
    if board[0][3] == opponentColor or color:
        coinvalue += 4
    if board[0][5] == opponentColor or color:
        coinvalue += 2
    if board[0][7] == opponentColor or color:
        coinvalue += 1
    totalweight = totalweight-weightage[coinvalue]
    value *= 5*totalweight
    return value

# Tried using this evaluation function but not giving expected results.

def doublecorner_evaluation(board, color, opponentColor):
    weightage = 0
    if board[7][6] == color:
        if board[6][5] == color or board[6][7] == color:
            weightage += 3.0
    if board[0][1] == opponentColor:
        if board[1][0] == opponentColor or board[1][2] == opponentColor:
            weightage -= 3.0
    return weightage


# Tried using this evaluation function but not giving expected results. 

def center_evaluation(board,color,opponentColor):
    weightage = 0
    player_coins = player_kingcoins = opponent_coins = opponent_kingcoins = 0
    center=[14,15,18,19]
    for piece in center:
        xy = gamePlay.serialToGrid(piece)
        x = xy[0]
        y = xy[1]
        if board[x][y] == color:
            player_coins += 1
        if board[x][y] == color.upper():
                player_kingcoins += 1
        if board[x][y] == opponentColor:
            opponent_coins += 1
        if board[x][y] == opponentColor.upper():
            opponent_kingcoins += 1
    weightage += (player_coins - opponent_coins)*2
    weightage += (player_kingcoins - opponent_kingcoins)*5
    return weightage


def nextMove(board, color, time, movesRemaining):

    possibleMoves = getAllPossibleMoves(board, color)
    opponentColor = gamePlay.getOpponentColor(color) 

    #Trying to find the move where I have best score
    bestValue = None
    bestmove = possibleMoves[0]
    depth = 5
    alpha = float("-inf")
    beta = float("inf")
    for move in possibleMoves: 
        newBoard = deepcopy(board)
        gamePlay.doMove(newBoard,move) #
        #retrieves the value from minChance.
        #Here, alpha is the lower bound of the actual MiniMax value and beta is the upper bound of the actual MiniMax value.         
        score = minChance(newBoard, depth-1,color, opponentColor, alpha, beta) # This is the max turn(1st level of minimax), so next should be min's turn
        if bestValue == None or score > bestValue:
        #If the better score is found than the current best value then that move is considered as the best move. Hence, it is taken. 
            bestMove = move
            bestValue = score
        if bestValue > alpha:
            alpha = bestValue
    return bestMove

def minChance(newBoard,depth,color,opponentColor,alpha,beta):
    if depth == 0: #If the depth reaches the value 0, it means we have reached the leave node and now we need to estimate the value at that node using evaluation functions.
        return evaluation(newBoard,color,opponentColor)
    else:
        minimumScore = None
        moves = getAllPossibleMoves(newBoard, opponentColor)
        for move in moves:
            nextBoard = deepcopy(newBoard)
            gamePlay.doMove(nextBoard,move)
            #If the alpha score is less than the minimum score then rest of the nodes can be pruned. 
            if alpha == None or minimumScore == None or alpha < minimumScore: #None is less than everything and anything
                score = maxChance(nextBoard,depth-1, color, opponentColor, alpha, beta) # This is the min turn, so next should be max's turn. This process continues recursively. 
                if minimumScore == None or score < minimumScore:
                    minimumScore = score
                if minimumScore < beta:
                    beta = minimumScore

    return minimumScore

def maxChance(newBoard,depth,color,opponentColor,alpha,beta):
    if depth == 0: # If the depth reaches the value 0, it means we have reached the leave node and now we need to estimate the value at that node using evaluation functions. 
        return evaluation(newBoard,color,opponentColor)
    else:
        maxScore = None
        moves = getAllPossibleMoves(newBoard,color)
        for move in moves:
            nextBoard = deepcopy(newBoard)
            gamePlay.doMove(nextBoard,move)
            if beta > maxScore:
                    score = minChance(nextBoard,depth-1,color, opponentColor, alpha, beta) # This is the min turn, so next should be max's turn. This process continues recursively.
                    if score > maxScore: 
                        maxScore = score
                    if maxScore > alpha:
                        alpha = maxScore
    return maxScore
