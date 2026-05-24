docker run -p 6333:6333 qdrant/qdrant, but then you will need to run venv/Scripts/activate then python insert_data.py

OR docker start 5ba5d869cb706abcc2564eaed79f83ce4e6a4b9acccc6fe3b154c8964c7cdf51 (OR name is "interesting_wilbur") IF ALREADY PRESENT


docker run -it --rm `
--name n8n_persistent `
-p 5678:5678 `
-v ${PWD}/n8n_data:/home/node/.n8n `
n8nio/n8n


Use this below (uses data stored for n8n)
docker run -it --rm --name n8n_persistent -p 5678:5678 -v "C:\Users\GM A\n8n_data:/home/node/.n8n" n8nio/n8n


start backend:
uvicorn app:app --reload --reload-include "app.py" --reload-include "embeddings.py" --reload-include "qdrant_db.py"

// to stop docker container
docker stop interesting_wilbur (or container id is "5ba5d869cb706abcc2564eaed79f83ce4e6a4b9acccc6fe3b154c8964c7cdf51")


iamsyedzahid@gmail.com

//n8n
docker stop 05fb377d81d7          
05fb377d81d7

//qdrant
docker stop 5ba5d869cb70
5ba5d869cb70