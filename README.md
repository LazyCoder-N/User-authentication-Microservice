# User Authentication microservice
The Authentication Microservice is an independent application developed using Django, designed to handle secure user authentication. It includes features such as OTP-based verification, password recovery, and account updates. The microservice follows RESTful principles in its architecture. 


## Follow Below steps to start the project

### 1. Create a virtual environment
> You can create virtual enviroment by using below command
```
python3 -m venv venv
```

### 2. Activate virtual envoriment 
> Once the virtual enviroment is created use below command to start the enroviroment

> For Linux
```
source venv/bin/activate
```

> For windows
```
venv\Scripts\activate
```

### 3. Install requirements.txt
> After virtual enviroment is activate install all dependecies
```
pip install -r requirements.txt
```

### 4. Run server and complete migrations
> Once the dependecies are install try running the server to check if everthing is working fine
```
python manage.py runserver
```

> If server start without encountering any errors then you can do the migrations to create tables in database
```
python manage.py makemigrations
python manage.py migrate
```

### Once the migrations are completed start the server and you are good to go
