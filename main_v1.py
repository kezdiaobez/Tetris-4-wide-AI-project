from collections import defaultdict, deque
from collections import Counter
import heapq
import random
import numpy as np
import pygame
import copy
import time
import math
import orientations as os
pygame.init()
screen = pygame.display.set_mode((800, 600))
nextpiecestested= []
piecesleft = []
nextpiecesleft = []
#topnum = [100, 50, 50, 50, 50, 50]
#topnum = [20]*7
remaining = [x for x in range(7)]
#topnum2 = [20]*7
minthreshold = 20
maxthreshold = 200
maxdepth = 5
bfsdepth = 6
prev_combo = 0
minbeginning = 1
maxbeginning = 200
sum_broken_combos = []
emint = 10
emaxt = float('inf')
for _ in range(len(remaining)):
    idx = random.randint(0, len(remaining)-1)
    piecesleft.append(remaining[idx])
    del remaining[idx]
piecestested = []
aspireseq = []
firstiter = True
mainholdpiece = None

pieceL = [
    [0, 0, 1],
    [1, 1, 1],
    [0, 0, 0]
]
pieceJ = [
    [2, 0, 0],
    [2, 2, 2],
    [0, 0, 0]
]
pieceI = [
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 3, 3, 3, 3],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0]]
pieceS = [
    [0, 4, 4],
    [4, 4, 0],
    [0, 0, 0]
]
pieceZ = [
    [5, 5, 0],
    [0, 5, 5],
    [0, 0, 0]
]
pieceT = [
    [0, 6, 0],
    [6, 6, 6],
    [0, 0, 0]
]
pieceO = [
    [0, 7, 7],
    [0, 7, 7],
    [0, 0, 0]
]
namesJLSZT = {"pieceL", "pieceJ", "pieceS", "pieceZ", "pieceT"}

kickJLSZT = os.kickJLSZT
kickJLSZT2 = os.kickJLSZT2
kickO = os.kickO
kickO2 = os.kickO2
kickI = os.kickI
kickI2 = os.kickI2

pieces = [pieceL, pieceJ, pieceI, pieceS, pieceZ, pieceT, pieceO]
pieces2 = {"pieceL": os.piecesL,
    "pieceJ": os.piecesJ,
    "pieceI": os.piecesI,
    "pieceS": os.piecesS,
    "pieceZ": os.piecesZ,
    "pieceT": os.piecesT,
    "pieceO": os.piecesO}
pieces3 = {"pieceL": os.piecesL2,
    "pieceJ": os.piecesJ2,
    "pieceI": os.piecesI2,
    "pieceS": os.piecesS2,
    "pieceZ": os.piecesZ2,
    "pieceT": os.piecesT2,
    "pieceO": os.piecesO2}
names = ["pieceL", "pieceJ", "pieceI", "pieceS", "pieceZ", "pieceT", "pieceO"]
colors = [(0, 0, 0), (255, 153, 51), (0, 0, 255), (0, 255, 255), (100, 255, 100), (255, 50, 50), (120, 0, 255), (255, 255, 100), (128, 128, 128)]

def findlineclears(solutions, board, name):
    clears = []
    for solution in solutions:
        pos, x, y, spinpos = solution
        piece = Pieces(pos, name, x, y, spinpos)
        world_piece = piece.create_world_obj()
        succeed = False
        for i in range(len(piece.pos)):
            fail = False
            ypos = i+y-len(piece.pos)//2
            if(ypos<world.height and ypos>=0):
                succeed = all(a or b for a,b in zip(world_piece[ypos], board[ypos]))
                if(succeed):
                    break
        if(succeed):
            clears.append((piece.pos, piece.x, piece.y))
    return clears

class Treenode:
    #value at leaf node, score for every node for beam search
    def __init__(self, type_=None, piece = None, value=None, tempboard=None, probability=None, holdpiece=None, piecestested=None, canhold=None, depth=None, evalstuff = None, score = None, parent=None, firststuff = None, is_duplicate = None):
        self.children = []
        self.type_ = type_
        self.piece = piece
        self.value = value
        self.tempboard = tempboard
        self.probability = probability
        self.holdpiece = holdpiece
        self.piecestested = piecestested
        self.canhold = canhold
        self.depth = depth
        self.evalstuff = evalstuff
        self.score = score
        self.parent = parent
        self.firststuff = firststuff
        self.is_duplicate = is_duplicate
    def addmaxchild(self, childnode):
        self.children.append(childnode)
    def addchancechild(self, childnode):
        self.children.append(childnode) 

class World:
    height = 20
    width = 4
    blockwidth = 20
    blockheight = 20
    centerx = 100
    centery = 100
    def __init__(self):
        self.board = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.heights = [0]*self.width

    def get_solution(self, firststuffs, stuffs):
        q = deque()
        root = Treenode(type_ = "chance", depth=0, probability = 1)
        for stuff, firststuff in zip(stuffs, firststuffs):
            board, rpiecestested, rholdpiece, rproj_combo, rpieces_wasted, rmax_broken_combo = stuff
            #print(rpiecestested)

            piecesleft = [x for x in range(7) if x not in rpiecestested]
            base = Treenode("max", None, None, board, 0.1, None, rpiecestested, True, 0, [rproj_combo, rpieces_wasted, rmax_broken_combo, rproj_combo], None, root, firststuff)
            base.firststuff = firststuff
            root.addmaxchild(base)
            if(rholdpiece is not None):
                rholdpiece = Pieces(pieces[rholdpiece], names[rholdpiece], 0, 0, 0)
            else:
                rholdpiece = None
            for item in piecesleft:
                name = names[item]
                piece = Pieces(pieces[item], name, 0, 0, 0)
                child = Treenode("chance", piece, None, board, 1/len(piecesleft), rholdpiece, rpiecestested, True, 1, [rproj_combo, rpieces_wasted, rmax_broken_combo, rproj_combo], None, base, firststuff)
                base.addchancechild(child)
                q.append(child)
        self.build_tree(q)
        results = self.expectimax(root)
        stuff = [(results[i][0], i, results[i][1]) for i in range(len(results))]
        _, _, move = max(stuff)
        return move

    def expectimax(self, curr):
        stuff = []
        for child in curr.children:
            stuff.append(self.expectimax(child))
        if(curr.children):
            if(curr.type_ == "max"):
                maxvalue = max([child.value for child in curr.children])
                curr.value = maxvalue
                if(curr.depth==0):
                    return (maxvalue, curr.firststuff)
            if(curr.type_ == "chance"):
                value = sum([child.probability*child.value for child in curr.children])
                curr.value = value
        else:
            counts, totalcount, minheight = self.getboardinfo(curr.tempboard)
            boardstate = self.board_state_eval(curr.tempboard, counts, totalcount, minheight)
            proj_combo, pieces_wasted, max_broken_combo, curr_combo = curr.evalstuff
            leafnodereached = curr.depth==maxdepth-1
            curr.value = self.expectimax_state(pieces_wasted, proj_combo, curr_combo, boardstate, max_broken_combo, leafnodereached)
            #curr.value = self.evaluate_state(pieces_wasted, proj_combo, curr_combo, boardstate, max_broken_combo)
        return stuff

    def getboardinfo(self, board):
        totalcount = 0
        heights = []
        counts = [0] * world.height
        minheight = None
        for y in range(world.height):
            counts[y] = board[y].count(0)
            totalcount+=(4-board[y].count(0))
            if minheight is None and board[y].count(0)<4:
                minheight = y
        if minheight is None:
            minheight = world.height
        return counts, totalcount, minheight

    def expectimax_state(self, pieces_wasted, proj_combo, curr_combo, boardstate, max_broken_combo, leafnodereached):
        leafnodereached = 1 if leafnodereached else 0
        if(pieces_wasted):
            return max_broken_combo + 0.1*proj_combo**2 - 20 + leafnodereached*proj_combo**2*10
        else:
            return proj_combo**2 + 0.1*proj_combo**2 + leafnodereached*proj_combo**2*10


    def evaluate_state(self, pieces_wasted, proj_combo, curr_combo, boardstate, max_broken_combo):
        if(pieces_wasted):
            return max_broken_combo + 0.9*boardstate - 20
        else:
            return proj_combo**2 + 0.4*boardstate + 20

    def evaluate_state2(self, boardstate, info, steps):
        pos, x, y = info
        index = None
        for sequence in aspireseq:
            if(piecesplaced+steps<len(sequence)):
                #sequences where the piecesplaced+steps exceeds range are
                #not optimal
                if(info == sequence[piecesplaced+steps]):
                    index = piecesplaced+steps
                    break
        if(index is None):
            return boardstate
        else:
            if(index>0):
                print("found good solve")
            else:
                print("not good solve")
            return index*1000000

    def board_state_eval(self, board, counts, totalcount, minheight):
        counts2 = counts
        #print(counts)
        numgood = totalcount//3
        broken = False
        if(minheight<17):
            for y in range(self.height):
                if(y>=minheight+3):
                    if(counts2[y]%3!=0 or (counts2[minheight+2]+counts2[minheight+1]+counts2[minheight])%3!=0):
                        broken = True
        else:
            if((counts2[17]+counts2[18]+counts2[19])%3!=0):
                broken = True
        #print(listt)
        numgood = 4 if numgood > 4 else numgood
        boardstate = 4.5*numgood if not broken else -10
        return boardstate

    def board_state_eval2(self, board):
        counts = [0]*self.height
        for y in range(world.height):
            for x in range(world.width):
                if(board[y][x] != 0):
                    counts[y]+=1
        broken = False
        numgood=0
        for y in range(world.height):
            if(counts[y]!=0 and counts[y]%3==0):
                numgood+=1
            if(counts[y]!=0 and counts[y]%3!=0):
                broken = True
                break
        if(board == [[0 for _ in range(len(board[0]))] for _ in range(len(board))]):
            broken = True
        numgood = 4 if numgood > 4 else numgood
        #if(not broken):
        #print("FOUND NOT BROKEN")
        var1= 1000*numgood if not broken else -100
        return var1, broken

    def build_tree(self, queue):
        t1=time.time()
        toaddlist = []
        q = queue
        getmovestime = 0
        calls = 0
        leaves = []
        ttable1 = {}
        while q:
            curr = q.popleft()
            if(curr.depth < maxdepth):
                if(curr.type_ == "chance"):
                    sortedpieces = tuple(sorted(curr.piecestested))
                    tupleboard = tuple(map(tuple, curr.tempboard))
                    if((curr.piece.name, sortedpieces, tupleboard, curr.holdpiece.name) in ttable1):
                        if(curr.canhold):
                            currentcombo = curr.evalstuff[0]
                            results = ttable1[(curr.piece.name, sortedpieces, tupleboard, curr.holdpiece.name, currentcombo)]
                            for result in results:
                                boards, holdpiecename, piecestested, evalstuffs, scores = result 
                                for i in range(len(boards)):
                                    pos = pieces[names.index(holdpiecename)]
                                    piece = Pieces(pos, holdpiecename, 0, 0, 0)
                                    child = Treenode("max", None, None, boards[i], curr.probability, piece, piecestested.copy(), curr.canhold, curr.depth+1, evalstuffs[i], scores[i], curr, None, True)
                                    curr.addmaxchild(child)
                                    toaddlist.append(child)
                    else:
                        toaddlist, toadd = self.build_tree_util(curr, curr.piece, curr.holdpiece, curr.piece, ttable1, toaddlist)
                        if(curr.holdpiece is not None):
                            if(curr.canhold):
                                toaddlist, toadd2 = self.build_tree_util(curr, curr.holdpiece, curr.piece, curr.piece, ttable1, toaddlist)
                                ttable1[(curr.piece.name, sortedpieces, tupleboard, curr.holdpiece.name, curr.evalstuff[0])] = (toadd, toadd2)
                        else:
                            newpiecestested = curr.piecestested + [names.index(curr.piece.name)]
                            if(len(newpiecestested)==7):
                                newpiecestested = []
                            newholdpiece = Pieces(curr.piece.pos, curr.piece.name, curr.piece.x, curr.piece.y, 0)
                            newtempboard = [[curr.tempboard[y][x] for x in range(self.width)] for y in range(self.height)]        
                            boardstate = self.board_state_eval(newtempboard)
                            proj_combo, pieces_wasted, max_broken_combo, curr_combo = curr.evalstuff
                            curr.score = self.evaluate_state(pieces_wasted, proj_combo, curr_combo, boardstate, max_broken_combo)
                            child = Treenode("max", None, None, newtempboard, curr.probability, newholdpiece, newpiecestested, False, curr.depth+1, curr.evalstuff, curr.score, curr, None, False)
                            toaddlist.append(child)
                if(len(q)==0 and len(toaddlist)>0):
                    print("length toaddlist", len(toaddlist))
                    scores = [x.score for x in toaddlist]
                    maxscore = max(scores)
                    num = scores.count(maxscore)
                    for curr in toaddlist:
                        if(curr.is_duplicate and curr.depth>4):
                            leaves.append(curr)
                    if(num>emint):
                        newaddlist = []
                        for node in toaddlist:
                            if(node.score==maxscore and len(newaddlist)<emaxt):
                                newaddlist.append(node)
                        for node in newaddlist:
                            curr = node
                            piecesleft = [x for x in range(7) if x not in curr.piecestested]
                            tempboard = [[curr.tempboard[y][x] for x in range(self.width)] for y in range(self.height)]
                            for item in piecesleft:
                                name = names[item]
                                piece = Pieces(pieces[item], name, 0, 0, 0)
                                child = Treenode("chance", piece, None, tempboard, 1/len(piecesleft), curr.holdpiece, curr.piecestested.copy(), curr.canhold, curr.depth, curr.evalstuff.copy(), curr.score, curr, None, curr.is_duplicate)
                                curr.addchancechild(child)
                                q.append(child)
                    else:
                        min_heap = []
                        heapq.heapify(min_heap)
                        unique_id = 0
                        for node in toaddlist:
                            if len(min_heap) < emint:
                                heapq.heappush(min_heap, (node.score, unique_id, node))
                                unique_id+=1
                            elif node.score > min_heap[0][0]:
                                heapq.heappop(min_heap)
                                heapq.heappush(min_heap, (node.score, unique_id, node))
                                unique_id+=1
                        while min_heap:
                            curr = heapq.heappop(min_heap)[2]
                            piecesleft = [x for x in range(7) if x not in curr.piecestested]
                            tempboard = [[curr.tempboard[y][x] for x in range(self.width)] for y in range(self.height)]
                            for item in piecesleft:
                                name = names[item]
                                piece = Pieces(pieces[item], name, 0, 0, 0)
                                child = Treenode("chance", piece, None, tempboard, 1/len(piecesleft), curr.holdpiece, curr.piecestested.copy(), curr.canhold, curr.depth, curr.evalstuff.copy(), curr.score, curr, None, curr.is_duplicate)
                                curr.addchancechild(child)
                                q.append(child)
                    toaddlist = []
                    ttable1 = {}
        print("length of leaves", len(leaves))
        """
        if(leaves):
            leaf = leaves[0]
            while leaf.parent!=None:
                #proj combo, pieces wasted, max broken combo, curr combo
                print("evalstuff", leaf.piecestested, "probability", leaf.probability, "type", leaf.type_)
                leaf = leaf.parent
        """

    def build_tree_util(self, curr, currentpiece, holdpiece, skippedpiece, ttable1, toaddlist):
        boards, scores, evalstuffs = [], [], []
        child_tempboard = curr.tempboard
        piecestested = curr.piecestested.copy()
        piecestested.append(names.index(skippedpiece.name))
        if(len(piecestested)==7):
            piecestested = []
        piece = Pieces(pieces[names.index(currentpiece.name)], currentpiece.name, 0, 0, 0)
        positions = piece.getmoves(child_tempboard)
        solutions = findlineclears(positions, child_tempboard, currentpiece.name)
        proj_combo, pieces_wasted, max_broken_combo, curr_combo = curr.evalstuff
        for pos, x, y, spinpos in positions:
            if((pos, x, y) in solutions):
                piece = Pieces(pos, currentpiece.name, x, y, spinpos)
                tempboard, counts, totalcount, minheight = piece.renderboard(child_tempboard)
                boardstate = self.board_state_eval(tempboard, counts, totalcount, minheight)
                new_proj_combo = proj_combo+1
                evalstuff = [new_proj_combo, pieces_wasted, max_broken_combo, curr_combo]
                score = self.evaluate_state(pieces_wasted, new_proj_combo, curr_combo, boardstate, max_broken_combo)
                child = Treenode("max", None, None, tempboard, curr.probability, holdpiece, piecestested.copy(), True, curr.depth+1, evalstuff, score, curr, None, False)
                curr.addmaxchild(child)
                toaddlist.append(child)
                boards.append(tempboard)
                scores.append(score)
                evalstuffs.append(evalstuff)
        #NOT CACHED: PROBABILITY, PARENT, DEPTH, CANHOLD
        toadd = (boards, holdpiece.name, piecestested.copy(), evalstuffs, scores)
        return toaddlist, toadd


    def bfs(self, newboard, holdpiece, piecestested, piecesleft, nextpiecesleft, nextpiecestested, curr_combo, phase_reached):
        soltuions = []
        firststuff = [phase_reached]
        expectimaxstuff = (curr_combo, 0, 0)
        state = True
        q = deque([(newboard, 0, 0, phase_reached, piecestested, piecesleft, nextpiecesleft, nextpiecestested, holdpiece, firststuff, expectimaxstuff, [])])
        solutions = []
        origpiecestested = []
        previouslevel = 0
        toaddlist = []
        while q:
            results = q.popleft()
            newboard, steps, queue_steps, phase_reached, piecestested, piecesleft, nextpiecesleft, nextpiecestested, holdpiece, firststuff, expectimaxstuff, history= results
            results = self.getnext(piecestested, piecesleft, nextpiecesleft, nextpiecestested)
            name = results[4]
            piecesleft =results[0]
            nextpiecesleft = results[1]
            nextpiecestested = results[2]
            piecestested = results[5]
            if(queue_steps<bfsdepth):
                toadd, toadd2 = [], []
                toadd3 = self.bfs_util(newboard, steps, queue_steps, phase_reached, piecesleft, nextpiecesleft, nextpiecestested, name, holdpiece, firststuff, expectimaxstuff, q, history, piecestested)
                if(holdpiece or holdpiece==0):
                    toadd = self.bfs_util(newboard, steps, queue_steps, phase_reached, piecesleft, nextpiecesleft, nextpiecestested, holdpiece, name, firststuff, expectimaxstuff, q, history, piecestested)
                else:
                    results = self.getnext(piecestested, piecesleft, nextpiecesleft, nextpiecestested)
                    name2 = results[4]
                    piecesleft = results[0]
                    nextpiecesleft = results[1]
                    nextpiecestested = results[2]
                    piecestested = results[5]
                    toadd2 = self.bfs_util(newboard, steps, queue_steps+1, phase_reached, piecesleft, nextpiecesleft, nextpiecestested, name2, name, firststuff, expectimaxstuff, q, history, piecestested)              
                toaddlist.extend(tuplee for tuplee in toadd3)
                toaddlist.extend(tuplee for tuplee in toadd)
                toaddlist.extend(tuplee for tuplee in toadd2)
                if(len(q)==0):
                    scores = [x[-2] for x in toaddlist]
                    maxscore = max(scores)
                    num = scores.count(max(scores))
                    if(main_phase_reached):
                        mthres = minthreshold
                        mxthres = maxthreshold
                    else:
                        mthres = minbeginning
                        mxthres = maxbeginning
                    if(num>=mthres):
                        newaddlist = []
                        for tuplee in toaddlist:
                            if(tuplee[-2]==maxscore and len(newaddlist)<mxthres):
                                newaddlist.append(tuplee[:-2]+(tuplee[-1],))
                        for tuplee in newaddlist:
                            q.append(tuplee)
                    else:                
                        min_heap = []
                        heapq.heapify(min_heap)
                        unique_id = 0
                        for row in toaddlist:
                            if len(min_heap) < mthres:
                                heapq.heappush(min_heap, (row[-2], unique_id, row[:-2] + (row[-1],)))
                                unique_id+=1
                            elif row[-2] > min_heap[0][0]:
                                heapq.heappop(min_heap)
                                heapq.heappush(min_heap, (row[-2], unique_id, row[:-2] + (row[-1],)))
                                unique_id+=1
                        while min_heap:
                            results = heapq.heappop(min_heap)
                            q.append(results[2])
                    toaddlist = []
            else:
                proj_combo, pieces_wasted, max_broken_combo = expectimaxstuff
                if(firstiter):
                    aspireseq.append(history)
                solutions.append((firststuff, [newboard, piecestested, holdpiece] + [proj_combo, pieces_wasted, max_broken_combo], history, steps, queue_steps))
        print("len solutions", len(solutions))
        return solutions

    def bfs_util(self, newboard, steps, queue_steps, phase_reached, piecesleft, nextpiecesleft, nextpiecestested, current, holdpiece, firststuff, expectimaxstuff, q, history, piecestested):
        toadd = []
        new_firststuff = firststuff
        phase_reached = firststuff[-1]
        new_expectimaxstuff = expectimaxstuff
        board = newboard
        piece = Pieces(pieces[current], names[current], 0, 0, 0)
        positions = piece.getmoves(board)
        solutions = findlineclears(positions, board, names[current])
        child_history = history.copy()
        for pos, x, y, spinpos in positions:
            child_phase_reached = phase_reached
            child_history = [row[:] for row in history]
            if((pos, x, y) in solutions):                
                piece = Pieces(pos, names[current], x, y, spinpos)
                child_board, counts, totalcount, minheight = piece.renderboard(board)
                if(not phase_reached):
                    child_history = history + [[pos, x, y]]
                proj_combo, pieces_wasted, max_broken_combo = expectimaxstuff
                proj_combo+=1
                if(not phase_reached):
                    boardstate, broken = self.board_state_eval2(child_board)
                    score = self.evaluate_state2(boardstate, [pos, x, y], steps)
                else:
                    boardstate = self.board_state_eval(child_board, counts, totalcount, minheight)
                    score = self.evaluate_state(pieces_wasted, proj_combo, curr_combo, boardstate, max_broken_combo)
                if(not phase_reached and not broken):
                    child_phase_reached = True
                if(steps==0):
                    new_firststuff = (holdpiece, piecestested.copy(), piecesleft.copy(), nextpiecesleft.copy(), nextpiecestested.copy(), proj_combo, piece, child_phase_reached)
                new_expectimaxstuff = (proj_combo, pieces_wasted, max_broken_combo)
                toadd.append((child_board, steps+1, queue_steps+1, child_phase_reached, piecestested.copy(), piecesleft.copy(), nextpiecesleft.copy(), nextpiecestested.copy(), holdpiece, new_firststuff, new_expectimaxstuff, score, child_history))
            else:
                piece = Pieces(pos, names[current], x, y, spinpos)
                child_board, counts, totalcount, minheight = piece.renderboard(board)
                if(not phase_reached):
                    child_history = history + [[pos, x, y]]
                proj_combo, pieces_wasted, max_broken_combo = expectimaxstuff
                if(proj_combo>max_broken_combo):
                    max_broken_combo = proj_combo
                proj_combo = 0
                pieces_wasted+=1
                if(not phase_reached):
                    boardstate, broken = self.board_state_eval2(child_board)                    
                    score = self.evaluate_state2(boardstate, [pos, x, y], steps)
                else:
                    boardstate = self.board_state_eval(child_board, counts, totalcount, minheight)
                    score = self.evaluate_state(pieces_wasted, proj_combo, curr_combo, boardstate, max_broken_combo)
                if(not phase_reached and not broken):
                    child_phase_reached = True
                if(steps==0):
                    new_firststuff = (holdpiece, piecestested.copy(), piecesleft.copy(), nextpiecesleft.copy(), nextpiecestested.copy(), proj_combo, piece, child_phase_reached)
                new_expectimaxstuff = (proj_combo, pieces_wasted, max_broken_combo)
                toadd.append((child_board, steps+1, queue_steps+1, child_phase_reached, piecestested.copy(), piecesleft.copy(), nextpiecesleft.copy(), nextpiecestested.copy(), holdpiece, new_firststuff, new_expectimaxstuff, score, child_history))
        return toadd

    def getnext(self, piecestaken, piecesleft, nextpiecesleft, nextpiecestaken):
        piecesleft = piecesleft.copy()
        nextpiecesleft = nextpiecesleft.copy()
        nextpiecestaken = nextpiecestaken.copy()
        name = piecesleft.pop(0)
        piecestaken.append(name)
        if(len(piecesleft) == 5):
            nextremaining = [x for x in range(7)]
            for _ in range(7):
                idx = random.randint(0, len(nextremaining)-1)
                nextpiecesleft.append(nextremaining[idx])
                del nextremaining[idx]
        if(len(piecesleft) < 5):
            nextpiecetaken = nextpiecesleft[0]
            nextpiecestaken.append(nextpiecetaken)
            del nextpiecesleft[0]
        if(len(piecesleft) == 0):
            piecesleft = nextpiecestaken + nextpiecesleft
            nextpiecestaken = []
            nextpiecesleft = []
            piecestaken = []
        if(len(piecesleft)>=5):
            newqueue = piecesleft[:5]
        else:
            newqueue = piecesleft + nextpiecestaken
        return piecesleft, nextpiecesleft, nextpiecestaken, newqueue, name, piecestaken

    def displayboard(self):
        rect = pygame.Rect(self.centerx, self.centery, self.blockwidth*self.width, self.blockheight * self.height)
        pygame.draw.rect(screen, (128, 128, 128), rect, 5)
        for i in range(world.height):
            for j in range(world.width):
                if(self.board[i][j]!=0):
                    pygame.draw.rect(screen, colors[self.board[i][j]], (self.centerx + j*self.blockwidth, self.centery + i*self.blockheight, self.blockwidth, self.blockheight))

    def displayhold(self, holdpiece):
        obj_width = 100
        obj_height = 100
        rect = pygame.Rect(self.centerx - obj_width, self.centery, obj_width, obj_height)
        pygame.draw.rect(screen, (128, 128, 128), rect, 5)
        if(holdpiece is not None):
            newholdpiece = Pieces(pieces[holdpiece], names[holdpiece], 2, 2, 0)
            self.displayobject2(newholdpiece, self.centerx - obj_width, self.centery)

    def displayobject2(self, piece, x, y):
        for i in range(len(piece.pos)):
            for j in range(len(piece.pos)):
                if(piece.pos[i][j]!=0):
                    pygame.draw.rect(screen, colors[piece.pos[i][j]], (x + j*world.blockwidth, y + i*world.blockwidth, world.blockwidth, world.blockheight))

    def displayqueue(self, queue):
        obj_width = 100
        obj_height = 500
        buffer = 10
        rect = pygame.Rect(self.centerx + self.blockwidth*4, self.centery, obj_width, obj_height)
        pygame.draw.rect(screen, (128, 128, 128), rect, 5)
        for i in range(len(queue)):
            piece = Pieces(pieces[queue[i]], names[queue[i]], 0, 0, 0)
            self.displayobject2(piece, self.centerx + self.blockwidth*4, self.centery+(3*self.blockheight+buffer)*i)
            
class Pieces:
    def __init__(self, pos, name, x, y, spinpos):
        self.pos = pos
        self.name = name
        self.x = x
        self.y = y
        self.spinpos = spinpos
            
    def spin(self, usekick, rotation, board=None):
        newpos = [[] for _ in range(len(self.pos))]
        if(usekick):
            newpos, newx, newy, newspinpos = self.kick(rotation, board)
            if(newpos != None):
                return newpos, newx, newy, newspinpos
            else:
                return None, None, None, None
        else:
            newpos, newspinpos = self.spin2(rotation)
            return newpos, self.x, self.y, newspinpos

    def spin2(self, rotation):
        newspinpos = (self.spinpos+rotation)%4
        newpos = pieces2[self.name][(self.spinpos+rotation)%4]
        return newpos, newspinpos
        
    def kick(self, rotation, board):
        offset = []
        offsetx = 0
        offsety = 0
        piece = Pieces(self.pos, self.name, self.x, self.y, self.spinpos)
        piece.pos, piece.spinpos = piece.spin2(rotation)
        orig_x = self.x
        orig_y = self.y
        spinpos1 = self.spinpos
        spinpos2 = (self.spinpos + rotation)%4
        name = names.index(self.name)
        if(name in [0, 1, 3, 4, 5]):
            if(rotation<0):
                offset = kickJLSZT[spinpos1]
            elif(rotation>0):
                offset = kickJLSZT2[spinpos2]
        elif(name == 6):
            if(rotation<0):
                offset = kickO[spinpos1]
            elif(rotation>0):
                offset = kickO2[spinpos2]
        elif(name == 2):
            if(rotation<0):
                offset = kickI[spinpos1]
            elif(rotation>0):
                offset = kickI2[spinpos2]
        for i in range(len(offset)):
            piece.x = orig_x + offset[i][0]
            #SRS uses positive y upward, but my coordinate system uses positive y downward
            piece.y = orig_y - offset[i][1]
            if(not piece.iscolliding(board)):
                return piece.pos, piece.x, piece.y, piece.spinpos
        return None, None, None, None

    def getmoves(self, board):
        #optimized
        piece = Pieces(pieces[names.index(self.name)], self.name, 0, 0, 0)
        positions = []
        pos = []
        min_x = world.height
        max_x = 0
        tobreak = False
        minheight = next(
            (y for y, row in enumerate(board) if any(row)),
            20
        )
        startx = 0
        starty = minheight-math.ceil(len(self.pos)/2)
        directions = ((0, 1), (-1, 0), (1, 0))
        q = deque([(piece.pos, startx, starty, 0)])
        traversed = set()
        solutions2 = set()
        solutions = []
        positions = set()
        while q:
            pos, x, y, spinpos = q.popleft()
            copypos = [row[:] for row in pos]
            piece.pos = copypos
            piece.spinpos = spinpos%4
            tuplepos = tuple(map(tuple, piece.pos))
            #print(len(traversed))
            for offsetx, offsety in directions:
                piece.x = x+offsetx
                piece.y = y+offsety
                if(piece.x>=0 and piece.x<4 and piece.y>=0 and piece.y<20 and (tuplepos, x+offsetx, y+offsety) not in traversed):
                    piecedown = Pieces(piece.pos, piece.name, x+offsetx, y+offsety+1, spinpos)
                    if(not piece.iscolliding(board)):
                        if(piecedown.iscolliding(board)):
                            world_obj = piece.create_world_obj()
                            tuplepiece = tuple(map(tuple, world_obj))
                            if(tuplepiece not in positions):
                                positions.add(tuplepiece)
                                solutions.append(([row[:] for row in piece.pos], x+offsetx, y+offsety, spinpos%4))
                            traversed.add((tuplepos, x+offsetx, y+offsety))
                            q.append((piece.pos, x+offsetx, y+offsety, spinpos%4))
                        else:
                            traversed.add((tuplepos, x+offsetx, y+offsety))
                            q.append((piece.pos, x+offsetx, y+offsety, spinpos%4))

            piece2 = Pieces(copypos, piece.name, x, y, spinpos)
            piece2.pos, newx2, newy2, piece2.spinpos = piece2.spin(True, -1, board)
            piece3 = Pieces(copypos, piece.name, x, y, spinpos)
            piece3.pos, newx3, newy3, piece3.spinpos = piece3.spin(True, 1, board)
            if(piece2.pos is not None):
                tuplepos2 = tuple(map(tuple, piece2.pos))
                piece2.x, piece2.y = newx2, newy2
                if((tuplepos2, newx2, newy2) not in traversed):
                    piecedown2 = Pieces(piece2.pos, piece.name, newx2, newy2+1, (spinpos-1)%4)
                    if(not piece2.iscolliding(board)):
                        if(piecedown2.iscolliding(board)):
                            world_obj2 = piece2.create_world_obj()
                            tuplepiece2 = tuple(map(tuple, world_obj2))
                            if(tuplepiece2 not in positions):
                                positions.add(tuplepiece2)
                                solutions.append((piece2.pos, newx2, newy2, (spinpos-1)%4))
                            traversed.add((tuplepos2, newx2, newy2))
                            q.append((piece2.pos, newx2, newy2, (spinpos-1)%4))
                        else:
                            traversed.add((tuplepos2, newx2, newy2))
                            q.append((piece2.pos, newx2, newy2, (spinpos-1)%4))
            if(piece3.pos is not None):
                tuplepos3 = tuple(map(tuple, piece3.pos))
                piece3.x, piece3.y = newx3, newy3
                if((tuplepos3, newx3, newy3) not in traversed):
                    piecedown3 = Pieces(piece3.pos, piece.name, newx3, newy3+1, (spinpos+1)%4)
                    if(not piece3.iscolliding(board)):
                        if(piecedown3.iscolliding(board)):
                            world_obj3 = piece3.create_world_obj()
                            tuplepiece3 = tuple(map(tuple, world_obj3))
                            if(tuplepiece3 not in positions):
                                positions.add(tuplepiece3)
                                solutions.append((piece3.pos, newx3, newy3, (spinpos+1)%4))
                            traversed.add((tuplepos3, newx3, newy3))
                            q.append((piece3.pos, newx3, newy3, (spinpos+1)%4))
                        else:
                            traversed.add((tuplepos3, newx3, newy3))
                            q.append((piece3.pos, newx3, newy3, (spinpos+1)%4))
        return solutions
    
    def displayobject(self, world):
        world_obj = self.create_world_obj()
        for i in range(world.height):
            for j in range(world.width):
                if(world_obj[i][j]!=0):
                    pygame.draw.rect(screen, colors[world_obj[i][j]], (world.centerx + j*world.blockwidth, world.centery + i*world.blockwidth, world.blockwidth, world.blockheight))

    def iscolliding(self, tempboard):
        squares = pieces3[self.name][self.spinpos]
        for x, y in squares:
            board_x = self.x + x - len(self.pos)//2
            board_y = self.y + y - len(self.pos)//2
            if(board_x<0 or board_x>=world.width):
                return True
            if(board_y<0 or board_y>=world.height):
                return True
            if tempboard[board_y][board_x]:
                return True

    def create_world_obj(self):
        squares = pieces3[self.name][self.spinpos]
        world_obj = [[0]*world.width for _ in range(world.height)]
        for x, y in squares:
            board_x = self.x + x - len(self.pos)//2
            board_y = self.y + y - len(self.pos)//2
            if(board_x>=0 and board_x<world.width and board_y>=0 and board_y<world.height):
                world_obj[board_y][board_x] = self.pos[y][x]
        return world_obj

    def renderboard(self, tempboard):
        resultboard = []
        world_obj = self.create_world_obj()
        count = 0
        counts = []
        totalcount = 0
        heights = []
        minheight = None
        for i in range(len(tempboard)):
            row, row2 = tempboard[i], world_obj[i]
            combined = [a + b for a, b in zip(row, row2)]
            numzeros = combined.count(0)
            if(len(combined)-numzeros>0 and minheight is None):
                minheight = i
            if all(combined):
                count += 1
            else:
                counts.append(len(combined)-numzeros)
                totalcount+=(len(combined)-numzeros)
                resultboard.append(combined)
        if minheight is None:
            minheight = world.height
        else:
            minheight+=count
        return [[0] * world.width for _ in range(count)] + resultboard, [0]*count + counts, totalcount, minheight

def pause(ms):
    start = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start < ms:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
        pygame.time.delay(10)
#"""
world = World()
world.displayhold(mainholdpiece)
#"""
main_phase_reached = False
piecesplaced = 0
curr_combo = 0
#"""
times = []
#"""
while True:
    print("world.board =", world.board)
    print("piecestested =", piecestested)
    print("piecesleft =", piecesleft)
    print("nextpiecestested =", nextpiecestested)
    print("nextpiecesleft =", nextpiecesleft)
    print("curr_combo =", curr_combo)
    print("mainholdpiece =", mainholdpiece)
    print("phase_reached", main_phase_reached)
    print("pieces_placed", piecesplaced)
    if len(times)!=0: print("AVERAGE TIME", sum(times)/len(times))
    #print("aspireseq", aspireseq)
    if(sum_broken_combos):
        print("AVERAGE MAX COMBO", sum(sum_broken_combos)/len(sum_broken_combos))
        print("ALL COMBOS", sum_broken_combos)
    solutions = world.bfs(world.board, mainholdpiece, piecestested, piecesleft, nextpiecesleft, nextpiecestested, curr_combo, main_phase_reached)
    maxvalue = float('-inf')
    bestmove = None
    #firststuff, finalstuff, history, steps, queue_steps = solutions
    firststuffs, finalstuffs = [], []
    for firststuff, finalstuff, _, _, _ in solutions:
        firststuffs.append(firststuff)
        finalstuffs.append(finalstuff)
    t1 = time.time()
    bestmove = world.get_solution(firststuffs, finalstuffs)
    t2 = time.time()
    print("TIME", t2-t1)
    times.append(t2-t1)
    mainholdpiece, piecestested, piecesleft, nextpiecesleft, nextpiecestested, curr_combo, piece, main_phase_reached = bestmove
    if(not main_phase_reached):
        newaspireseq = []
        #print("ASPIRESEQ", aspireseq)
        for seq in aspireseq:
            if [piece.pos, piece.x, piece.y] == seq[piecesplaced]:
                print("startindex", piecesplaced)
                newaspireseq.append(seq)
        aspireseq = newaspireseq
    if(firstiter):
        firstiter = False
    if(curr_combo == 0 and prev_combo!=0 and main_phase_reached):
        aspireseq = []
        firstiter = True
        main_phase_reached = False
        piecesplaced = -1
        if(prev_combo>4):
            sum_broken_combos.append(prev_combo)
    piece.displayobject(world)
    world.displayboard()
    world.displayhold(mainholdpiece)
    if(len(piecesleft)<=5):
        world.displayqueue((piecesleft + nextpiecestested)[:5])
    else:
        world.displayqueue(piecesleft[:5])
    pygame.display.update()
    pause(500)
    screen.fill((0, 0, 0))
    world.board, _, _, _ = piece.renderboard(world.board)
    world.displayboard()
    world.displayhold(mainholdpiece)
    if(len(piecesleft)<=5):
        world.displayqueue((piecesleft + nextpiecestested)[:5])
    else:
        world.displayqueue(piecesleft[:5])
    pygame.display.update()
    screen.fill((0, 0, 0))
    prev_combo=curr_combo
    piecesplaced+=1




