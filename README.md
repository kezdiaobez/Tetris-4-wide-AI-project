# Tetris-4-wide-AI-project
Tetris AI that plays on 4-wide board to maximize combo. WUMBOTIZE EVERYONE! This project was inspired by bots on the tetrio platform, such as mochbot and zzztoj. The speed of the bot and the accuracy of the moves of the bot can be changed by adjusting the maxdepth variable, which controls the depth of the expectimax tree. I would recommend setting the maxdepth variable to 3-5. The optimized version main_v2 uses a bitboard system to significantly increase the performance. main_v1 uses a 2d array system, and I wrote all the code myself. For main_v2, I only used chatgpt to rewrite basic functions for clearing lines and board representation. The program includes the interface for the tetris game, which the bot is playing on. To run this program, download the files for orientations_v2 and main_v2, and make sure you have pygame installed.

<img width="490" height="450" alt="giphy (3)" src="https://github.com/user-attachments/assets/5be57faa-1ca9-4da9-b49d-9750df699883" />

Notes: I did not use any precomputed board states.
The bot only knows the pieces that are in the queue, and keeps track of which bag of pieces it is on by counting the number of pieces placed(there are 7 pieces in each bag). Since the order of the pieces within the bag that have not been used yet are unknown(no cheating), the bot's expectimax tree has to include all possible sequences of the unused pieces in the bag in any order. Since this likely creates a lot of identical states, transposition tables can help significantly with performance.

How it works: I used BFS to traverse known pieces and record the first move and the resulting game state after the first move, as well as each BFS game state at the cutoff depth. Then I constructed an expectimax tree from the BFS states for all possible orderings of the pieces remaining in the current bag. The expectimax algorithm evaluates these possibilities and selects the best BFS game state, which corresponds to the optimal first move(for the given search depth).
BFS:
<br>
<img width="480" height="404" alt="Screenshot 2026-11-07 at 7 42 09 PM" src="https://github.com/user-attachments/assets/cff49dcc-cc01-4bb5-be3b-f246c89a4a11" />

expectimax:
<img width="960" height="720" alt="Untitled drawing" src="https://github.com/user-attachments/assets/7c4585c1-a973-414e-9a9b-19982817dcfa" />

4 wide theory:
The bot's gameplay requires an optimal board for massive 4 wide combos. An optimal 4 wide board usually involves 3 blocks per row, for all rows except the top 3 rows, and the total number of blocks in the top 3 rows need to add up to a multple of 3. Ideally, the board has 6 blocks or more. At the start, the bot builds a board of this structure. Since there are 4 blocks in each piece, and the total number of blocks needs to be a multiple of 3 in order to be optimal, having 12 total blocks by placing 3 pieces reaches the optimal board the quickest. You will normally see pro 4-wide players(like wumbo) go for PC looping, but the 3-piece setup is most optimal for comboing.
For comboing, a single line clear clears 4 blocks, and placing a piece adds 4 blocks. Single line clears are optimal because they do not change the number of blocks on the board, unless the total number of blocks is 24, 36, etc... In this case, the AI may choose clearing non-single lines that temporarily break the optimal board state, but transition back into it. The bot uses SRS kick tables to perform spins that kick pieces unusually into slots. This is a standard feature of modern tetris games. I precomputed spins and kick table offsets for maximum speed.

Limitations:
For the board states that satisfy the above criteria, the board state evaluation function all gives them the same score. This is problematic because the beam search mainly uses board state and combo. It cannot distinguish between different states where the board  satisfies the criteria and the combo is continued. This project could be improved if there is a way to add additional criteria to the board state evaluation without losing information(I doubt there is way, feel free to prove me wrong). With the current code, lower search depths are necessary for good performance.
