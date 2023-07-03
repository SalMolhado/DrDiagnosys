#!/bin/bash

venvName="myenv"

if [ -d "$venvName" ]
then
    source $venvName/bin/activate
    python main.py
else
    echo "O ambiente virtual '$venvName' não existe."
fi
