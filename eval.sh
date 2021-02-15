#!/bin/bash
pip install pytrec_eval
python evaluation.py "results/run_test_t_a_lem_syn.txt" "touche2020-task2-relevance-withbaseline(1).qrels"