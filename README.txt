Para poder jugar con el agente automático se deberá escribir el siguiente comando:
python busters.py -p QLearningAgent_100330657_100330670 -l labAAN -k N -t 0.000000001

Donde:
-p QLearningAgent_100330657_100330670: es el agente elaborado en esta práctica.
-l labAAN: sera el nombre del mapa, por ejemplo labAA1.
-k N: será el número de fantasmas del mapa a ejecutar.
-t 0.0000000001: este tiempo es opcional para realizar la ejecución más rápido. Recomendado para mapas grandes.

*NOTA IMPORTANTE*
Cada vez que se ejecute un mapa sería recomendable volver a actualizar el fichero qtable.txt mediante la tabla almacenada en qtable_Principal.txt
Esto es debido a la sobreescritura explicada en la práctica.

