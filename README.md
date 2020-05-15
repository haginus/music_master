# Music Master
A Python/Flask app that's given a song lyric/part and returns the next lyrics in a chat style.

# Backlog
### Front-end
- [x] Chatbox
- [x] Trimiterea de cereri AJAX către back-end pentru răspuns la query
- [x] Posibilitatea adăugării, editării și ștergerii pieselor (în zona de admin)
- [ ] Înfrumuțesarea zonelor de adăgare/editare piese în zona de admin
- [ ] Verificare sintaxă versuri la adăugarea pieselor (trebuie portat codul, la editare există deja)
### Back-end
- [x] Adăugare de piese
- [x] Adăugarea pieselor în index
- [x] Editarea/Ștergerea pieselor și reindexarea, respectiv scoaterea din index
- [x] Salvarea pieselor și indexului în fișiere, pentru persistență
- [x] Funcție de interpretare a query-ului introdus de utilizator
- [x] Funcție de căutare în index
- [x] Funcție de găsire a continuării cântecului
- [x] Funcție de adăugat emoji (pe baza unui dicționar)
- [x] Funcție de răpuns în JSON la query
- [x] Flask/Pagina principală
- [x] Flask/Zona de admin
- [ ] Flask/Sistem de logare pentru admini (în prezent oricine poate accesa zona de admin)
#### Bugs
- [ ] Există posibilitatea ca ștergerea pieselor să se fi stricat din cauza modificării metodei de indexare.
- [ ] Dacă nu există fișierele `songs.pkl` și `lyrics.pkl` care stochează cântecele și indexul, programul dă eroare. Ar trebui să le inițializeze cu două dicționare goale.

# Cum funcționează
Instalați dependecies și rulați `main.py`. Pentru adăugarea de cântece navigați la `localhost:port/songs`.
## Sintaxa versurilor
- `[ parte_cântec ]`: Înveliți părțile cântecului în paranteze pătrate. O parte poate fi de exemplu 2-3 versuri ale cântecului. În baza inputului introdus de utilizator, algoritul va da continuarea până la sfârșitul părții și, dacă este prea mică, va include următoarea parte.
- `( nexindexat )`: Înveliți bucăți pe care nu le doriți indexate între paranteze rotunde. Pot fi de exemplu interjecții, repetări în ecou pe background sau alte metode artistice. Acestea vor fi afișate la returnarea continuării. Un posibil uz este când solistul prelungește unele vocale și vrem să arătăm asta în versuri. De exemplu, pe versurile `nu pot să cred că m-ai uit(aaa)at / nu înțeleg, oare de ce ai plec(aaa)at?!` se vor indexa `uitat`, `plecat` și restul cuvintelor, însă afișarea va fi: `nu pot să cred că m-ai uitaaaat / nu înțeleg, oare de ce ai plecaaaat?!`

## Feedback
În cazul în care nu puteți rula programul, mă puteți contacta ca la o oră stabilită să îl rulez eu la mine pe calculator și fac un tunnel, să vă dau link-ul și să-l încercați.
