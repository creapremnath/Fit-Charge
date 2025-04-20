# FitCharge
FitCharge is the ultimate fitness and nutrition tracking app designed to keep you energized and on track with your health goals. Whether you're hitting the gym, counting macros, or just staying active, FitCharge helps you track workouts, monitor calories, and optimize your nutrition—all in one sleek and easy-to-use app.


#How to Run Application in Local Machine (Without Docker)


# activate virtual env in python
#windows:
 python -m venv venv

 cd venv/Scripts/bin
 activate
 cd ..
 cd ..

 #Mac or Linux:

 python3 -m venv venv

 source venv/bin/activate


#Run FastAPI Application:

cd Fit-charge
readme
uvicorn --reload src.main:app




#How to Run Application using Docker


#building Docker image
docker compose build -t fitcharge:v1

#To Run the Container
docker compose up -d


#To stop the container
docker compose down


#ip of postgres container
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' postgres_container