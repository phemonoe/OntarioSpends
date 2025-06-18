#!/bin/bash
PAGE=$1
THREAD_NUM=$((($PAGE-1)%8+1))

wget --save-cookies cookies.txt \
     --keep-session-cookies \
     --post-data="NoPage=$PAGE&vVersion=Normal&vFinComp=Fin&vDebut=1998&vFin=2023&vLangue=Anglais&vProgramme=Aucun+crit%E8re&vChercheur=&vInstitut=Aucun+crit%E8re&vDiscipline=Aucun+crit%E8re&vCDisc=&vCDiscMin=&vCDiscMax=&vSujet=Aucun+crit%E8re&vCSujet=&vMinimum=&vMaximum=&vRecherche=optTitre&vTitre=&vChoix=Visualiser+les+projets&TypeRapport=HTML" \
     http://www.outil.ost.uqam.ca/CRSH/Resultat.aspx \
     -O "data/listing/results_page$PAGE.html"
sleep 0.5
