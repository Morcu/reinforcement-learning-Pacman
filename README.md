# Reinforcement Learning Pacman

**Automatic pacman player using reinforcement**

## Execution

write the following command:

Python busters.py -p QLearningAgent_100330657_100330670 -l labAAN -k N -t M

Where:
- p QLearningAgent_100330657_100330670: is the agent.
- l labAAN: the name of the map, for example labAA1 (N goes from 1 to 5).
- k N: will be the number of ghosts of the map to execute.
  - labAA1 --> N = 1
  - labAA2 --> N = 2
  - labAA3 --> N = 3
  - labAA4 --> N = 3
  - labAA5 --> N = 4
- t M: This time is optional for faster execution. (For example 0.001)


**_Each time a map is run it is advisable to re-update the qtable.txt file using the table stored in qtable_Principal.txt
This is due to the overwriting of the q_table._**
