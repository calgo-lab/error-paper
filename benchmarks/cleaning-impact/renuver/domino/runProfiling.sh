#!/bin/bash
# hospital - Domino doesn't work
#java -jar -Xms2g -Xmx52g CreateMatrix.jar "hospital.csv" "true" "," "empty" "false" "6" "true"
#java -jar -Xms2g -Xmx52g Domino.jar "datasets/hospital.csv" "true" "," "empty" "false" "6" "true"

# beers - works
#java -jar -Xms2g -Xmx52g CreateMatrix.jar "beers.csv" "true" "," "empty" "false" "6" "true"
#java -jar -Xms2g -Xmx52g Domino.jar "datasets/beers.csv" "true" "," "empty" "false" "6" "true"

# abalone - works
#java -jar -Xms2g -Xmx52g CreateMatrix.jar "abalone.csv" "true" ";" "?" "false" "6" "true"
#java -jar -Xms2g -Xmx52g Domino.jar "datasets/abalone.csv" "true" ";" "?" "false" "6" "true"

# flights - works
#java -jar -Xms2g -Xmx52g CreateMatrix.jar "flights.csv" "true" "," "empty" "false" "6" "true"
#java -jar -Xms2g -Xmx52g Domino.jar "datasets/flights.csv" "true" "," "empty" "false" "6" "true"

# rayyan - doesn't work, incorrectly parses string as date
#java -jar -Xms2g -Xmx52g CreateMatrix.jar "rayyan.csv" "true" "," "empty" "false" "6" "true"
#java -jar -Xms2g -Xmx52g Domino.jar "datasets/rayyan.csv" "true" "," "empty" "false" "6" "true"

# 151 - works
#java -jar -Xms2g -Xmx52g CreateMatrix.jar "151.csv" "true" "," "empty" "false" "6" "true"
#java -jar -Xms2g -Xmx52g Domino.jar "datasets/151.csv" "true" "," "empty" "false" "6" "true"

# 137 - works
#java -jar -Xms2g -Xmx52g CreateMatrix.jar "137.csv" "true" "," "empty" "false" "6" "true"
#java -jar -Xms2g -Xmx52g Domino.jar "datasets/137.csv" "true" "," "empty" "false" "6" "true"

# tax - works
#java -jar -Xms2g -Xmx52g CreateMatrix.jar "tax.csv" "true" "," "empty" "false" "6" "true"
#java -jar -Xms2g -Xmx52g Domino.jar "datasets/tax.csv" "true" "," "empty" "false" "6" "true"

# food - works
#java -jar -Xms2g -Xmx52g CreateMatrix.jar "food.csv" "true" "," "empty" "false" "6" "true"
java -jar -Xms2g -Xmx52g Domino.jar "datasets/food.csv" "true" "," "empty" "false" "6" "true"
